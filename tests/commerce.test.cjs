const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'assets/mycp-commerce.js'), 'utf8');
function setup(storageFails = false) {
  const events = [], saved = new Map();
  const sandbox = {URL, location: {origin: 'https://myclinicprotocols.com', pathname: '/checkout-return.html'},
    window: {gtag: (...args) => events.push(args)}, localStorage: {
      getItem: key => {if (storageFails) throw Error('blocked'); return saved.get(key);},
      setItem: (key, value) => {if (storageFails) throw Error('blocked'); saved.set(key, value);}
    }};
  vm.runInNewContext(source, sandbox);
  return {api: sandbox.window.MYCPCommerce, events};
}
const paid = {status: 'COMPLETED', orderReference: 'MYCP-TEST-123', amount: '49.00', currency: 'USD',
  paymentMode: 'live', package: 'complete', treatmentCount: 1};
const quote = {...paid, pricingVersion: '2026-10-09', paypalOrderId: 'TEST123',
  approvalUrl: 'https://www.paypal.com/checkoutnow?token=TEST123'};

test('mismatched or missing server prices and unsafe payment links stop checkout', () => {
  const {api} = setup();
  assert.equal(api.verifyQuote(quote, 49), quote.approvalUrl);
  for (const change of [{amount: '149.00'}, {amount: undefined}, {currency: 'EUR'},
      {pricingVersion: 'old'}, {approvalUrl: 'https://example.com'},
      {approvalUrl: 'https://www.paypal.com.evil.example/checkout'}, {paymentMode: 'unknown'}]) {
    assert.throws(() => api.verifyQuote({...quote, ...change}, 49));
  }
});
test('only verified live revenue is reported and reloads do not repeat purchases', () => {
  const {api, events} = setup();
  for (const change of [{status: 'PENDING'}, {paymentMode: 'sandbox'}, {paymentMode: 'unknown'},
      {amount: 'invalid'}, {currency: 'EUR'}, {orderReference: ''}]) {
    api.trackPurchase({...paid, ...change});
  }
  assert.equal(events.length, 0);
  api.trackPurchase(paid); api.trackPurchase(paid);
  assert.equal(events.length, 1);
  assert.equal(events[0][1], 'purchase');
  assert.equal(events[0][2].transaction_id, paid.orderReference);
  assert.equal(events[0][2].value, 49);
  assert.equal(events[0][2].items[0].item_name, 'Complete Treatment Package');
});
test('analytics excludes clinic data, treatment details, payment tokens and download links', () => {
  const {api, events} = setup();
  api.trackPurchase({...paid, customerEmail: 'private@example.com', clinic: {name: 'Private clinic'},
    treatments: ['Private treatment'], paypalOrderId: 'SECRET-TOKEN', downloadUrl: 'https://example.com/signed-secret'});
  const payload = JSON.stringify(events);
  for (const secret of ['private@example.com', 'Private clinic', 'Private treatment', 'SECRET-TOKEN', 'signed-secret']) {
    assert.equal(payload.includes(secret), false);
  }
  assert.equal(events[0][2].page_location.includes('?'), false);
});
test('blocked local storage cannot stop purchase reporting or checkout', () => {
  const {api, events} = setup(true);
  assert.doesNotThrow(() => api.trackPurchase(paid));
  assert.equal(events[0][2].transaction_id, paid.orderReference);
  assert.equal(api.verifyQuote(quote, 49), quote.approvalUrl);
});
test('checkout starts use generic package data and exclude sandbox transactions', () => {
  const {api, events} = setup();
  api.trackCheckout({...quote, paymentMode: 'sandbox'}, 'complete', 1);
  assert.equal(events.length, 0);
  api.trackCheckout(quote, 'complete', 1);
  assert.equal(events[0][1], 'begin_checkout');
  assert.equal(events[0][2].value, 49);
});

test('homepage, order calculator, support answers and structured offers agree on prices', () => {
  const index = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
  const order = fs.readFileSync(path.join(root, 'order.html'), 'utf8');
  const support = fs.readFileSync(path.join(root, 'assets/mycp-search-support.js'), 'utf8');
  const tables = [
    vm.runInNewContext('(' + index.match(/const bundlePrices=(\{[\s\S]*?\n  \});/)[1] + ')'),
    vm.runInNewContext('(' + order.match(/const pricing=(\{[^\n]+\});/)[1] + ')'),
    vm.runInNewContext('(' + support.match(/const PRICING=(\{[\s\S]*?\n  \});/)[1] + ')')
  ];
  for (const [key, label, unit] of [['protocol', 'Customized Protocol', 29], ['complete', 'Complete Treatment Package', 49]]) {
    for (const count of [1, 3, 5, 10]) {
      assert.equal(tables[0][label][count], unit * count);
      assert.equal(tables[1][key].units[count], unit * count);
      assert.equal(tables[2][key].prices[count], unit * count);
    }
    for (const file of ['index.html', 'med-spa-protocol-templates.html']) {
      const html = fs.readFileSync(path.join(root, file), 'utf8');
      const offers = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)]
        .map(match => JSON.parse(match[1]));
      assert.match(JSON.stringify(offers), new RegExp('"name":"' + label + '","price":"' + unit + '"'));
    }
  }
});

test('return page confirms token-only orders even when browser storage is blocked', async () => {
  const html = fs.readFileSync(path.join(root, 'checkout-return.html'), 'utf8');
  const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
  for (const success of [true, false]) {
    const elements = new Map(), events = [], calls = [];
    const sandbox = {URL, URLSearchParams, location: {origin: 'https://myclinicprotocols.com',
      pathname: '/checkout-return.html', search: '?token=RETURN123'},
      document: {getElementById: id => {
        if (!elements.has(id)) elements.set(id, {textContent: '', classList: {add() {}}});
        return elements.get(id);
      }}, localStorage: {getItem() {throw Error('blocked');}, setItem() {throw Error('blocked');}, removeItem() {throw Error('blocked');}},
      gtag: (...args) => events.push(args),
      fetch: async (url, options) => {
        calls.push([url, JSON.parse(options.body)]);
        return {ok: success, json: async () => success ? {...paid, downloadUrl: 'https://example.com/download'} : {detail: 'Not verified'}};
      }};
    sandbox.window = sandbox;
    vm.runInNewContext(source, sandbox);
    await vm.runInNewContext(script, sandbox);
    assert.equal(calls[0][1].paypalOrderId, 'RETURN123');
    assert.equal(calls[0][1].orderReference, undefined);
    if (success) {
      assert.match(elements.get('title').textContent, /Payment confirmed/);
      assert.equal(events[0][1], 'purchase');
    } else {
      assert.match(elements.get('title').textContent, /still confirming/);
      assert.equal(events.length, 0);
    }
  }
});
