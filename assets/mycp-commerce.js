/* Shared checkout verification and privacy-safe ecommerce events. */
(function () {
  'use strict';
  const VERSION = '2026-10-10';
  const API = 'https://orders.myclinicprotocols.com';
  const names = {protocol: 'Customized Protocol', complete: 'Complete Treatment Package', all_access: '30-Day All Access'};
  function eventData(result) {
    const value = Number(result.amount), quantity = Number(result.treatmentCount);
    if (result.paymentMode !== 'live' || result.currency !== 'USD' ||
        !Number.isFinite(value) || value <= 0 || !Number.isInteger(quantity) ||
        quantity < 1 || quantity > 10 || !Object.hasOwn(names, result.package)) return null;
    return {currency: 'USD', value,
      page_location: location.origin + location.pathname,
      page_referrer: '',
      items: [{item_id: result.package, item_name: names[result.package],
        price: value / quantity, quantity}]};
  }
  function verifyQuote(result, expectedTotal) {
    if (result.pricingVersion !== VERSION || result.currency !== 'USD' ||
        Number(result.amount) !== expectedTotal) {
      throw new Error('We could not confirm your displayed price. Nothing was charged. Please refresh or contact myclinicprotocols@gmail.com.');
    }
    const url = new URL(result.approvalUrl);
    const host = result.paymentMode === 'sandbox' ? 'www.sandbox.paypal.com' :
      result.paymentMode === 'live' ? 'www.paypal.com' : '';
    if (url.protocol !== 'https:' || url.hostname !== host || url.username || url.password ||
        !result.orderReference || !result.paypalOrderId) {
      throw new Error('The secure payment link could not be verified. Nothing was charged. Please contact myclinicprotocols@gmail.com.');
    }
    return url.href;
  }
  function trackCheckout(result, packageKey, quantity) {
    const data = eventData({...result, package: packageKey, treatmentCount: quantity});
    if (data && typeof window.gtag === 'function') window.gtag('event', 'begin_checkout', data);
  }
  function trackPurchase(result) {
    if (!['COMPLETED','PROCESSING'].includes(result.status) || !/^MYCP-[A-Z0-9-]+$/.test(result.orderReference || '')) return;
    const data = eventData(result);
    if (!data || typeof window.gtag !== 'function') return;
    const key = 'mycp_purchase_' + result.orderReference;
    try { if (localStorage.getItem(key)) return; } catch (e) { /* Storage is optional. */ }
    window.gtag('event', 'purchase', {...data, transaction_id: result.orderReference});
    try { localStorage.setItem(key, '1'); } catch (e) { /* GA4 also deduplicates by transaction_id. */ }
  }
  window.MYCPCommerce = {API, VERSION, verifyQuote, trackCheckout, trackPurchase};
})();
