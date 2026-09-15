/* MyClinicProtocols search + support enhancements */
(function(){
  'use strict';

  const SUPPORT_EMAIL='myclinicprotocols@gmail.com';

  function searchMarkup(id,placeholder,extraClass){
    const wrap=document.createElement('div');
    wrap.className='mycp-search-wrap'+(extraClass?' '+extraClass:'');
    wrap.innerHTML=`
      <label class="mycp-visually-hidden" for="${id}">Search treatments and protocols</label>
      <svg class="mycp-search-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"></circle><path d="M16.5 16.5 21 21" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path></svg>
      <input class="mycp-search-input" id="${id}" type="search" autocomplete="off" placeholder="${placeholder}" aria-label="Search treatments and protocols">
      <button class="mycp-search-clear" type="button" aria-label="Clear search">×</button>`;
    return wrap;
  }

  function filterGroupedGrid(grid,query,cardSelector,titleSelector,empty){
    const q=(query||'').trim().toLowerCase();
    const children=Array.from(grid.children);
    const cards=children.filter(el=>el.matches(cardSelector));

    cards.forEach(card=>{
      const haystack=(card.textContent||'').toLowerCase();
      card.hidden=!!q && !haystack.includes(q);
    });

    const titles=children.filter(el=>el.matches(titleSelector));
    titles.forEach(title=>{
      let node=title.nextElementSibling;
      let any=false;
      while(node && !node.matches(titleSelector)){
        if(node.matches(cardSelector) && !node.hidden) any=true;
        node=node.nextElementSibling;
      }
      title.hidden=!any;
    });

    const hasVisible=cards.some(card=>!card.hidden);
    if(empty) empty.hidden=hasVisible;
  }

  function installSearch(grid,settings){
    if(!grid || document.getElementById(settings.id)) return;
    const wrap=searchMarkup(settings.id,settings.placeholder,settings.extraClass||'');
    grid.parentNode.insertBefore(wrap,grid);

    const empty=document.createElement('div');
    empty.className='mycp-search-empty';
    empty.hidden=true;
    empty.textContent=settings.emptyText||'No matching treatments found. Try another search term.';
    grid.insertAdjacentElement('afterend',empty);

    const input=wrap.querySelector('input');
    const clear=wrap.querySelector('.mycp-search-clear');
    let busy=false;

    const run=()=>{
      if(busy) return;
      busy=true;
      filterGroupedGrid(grid,input.value,settings.cardSelector,settings.titleSelector,empty);
      wrap.classList.toggle('has-value',!!input.value);
      busy=false;
    };

    input.addEventListener('input',run);
    input.addEventListener('search',run);
    clear.addEventListener('click',()=>{
      input.value='';
      run();
      input.focus();
    });

    if(settings.observe){
      const observer=new MutationObserver(()=>run());
      observer.observe(grid,{childList:true,subtree:true});
    }
    run();
  }

  function installProtocolSearch(){
    const grid=document.querySelector('#protocols .protocol-grid');
    installSearch(grid,{
      id:'mycpProtocolSearch',
      placeholder:'Search protocols, treatments, or services…',
      cardSelector:'.protocol',
      titleSelector:'.protocol-group-title',
      emptyText:'No matching protocols found. Try a procedure, medication, device, or service name.'
    });
  }

  function installOrderSearch(){
    const grid=document.getElementById('treatmentGrid');
    installSearch(grid,{
      id:'mycpTreatmentSearch',
      placeholder:'Search treatments…',
      extraClass:'mycp-order-search',
      cardSelector:'.treatment',
      titleSelector:'.treatment-group-title',
      emptyText:'No matching treatments found. You can also add another treatment below.',
      observe:true
    });
  }

  function answerFor(question){
    const q=(question||'').toLowerCase();
    if(/price|pricing|cost|package|99|149/.test(q)){
      return 'The Customized Protocol starts at $99 for one treatment. The Complete Treatment Package starts at $149 for one treatment and includes the protocol plus applicable consent, intake, treatment record, aftercare, checklists, and emergency guidance.';
    }
    if(/multiple|several|more than one|bundle|many treatment/.test(q)){
      return 'Yes. You can select multiple treatments in one order. Keep choosing everything your clinic needs and the order will stay together in one clinic intake.';
    }
    if(/receive|included|what do i get|documents|word|pdf|editable/.test(q)){
      return 'Your package is prepared around the treatment and clinic details you provide. Final deliverables are organized for your clinic and provided in editable Word and PDF formats. Complete packages also include the applicable supporting forms and guidance shown in the package description.';
    }
    if(/state|state-specific|specific state|compliance/.test(q)){
      return 'Select your clinic state during the intake. MyClinicProtocols uses that information to organize relevant state-specific considerations for review. Final clinical and legal approval remains with the clinic’s qualified supervising provider or medical director.';
    }
    if(/medication|dose|formula|equipment|device|method|brand|custom/.test(q)){
      return 'Yes. During the intake you can provide the medications, concentrations, formulas, equipment, devices, techniques, and workflows your clinic actually uses so the package can be customized around them.';
    }
    if(/revision|change|edit|correction/.test(q)){
      return 'Revision options are included with your order. Submit your clinic’s consolidated comments during the revision period so the requested updates can be reviewed and incorporated according to your package terms.';
    }
    if(/delivery|how long|when|turnaround|time/.test(q)){
      return 'Delivery timing depends on the package and customization requested. Your order flow and confirmation will show the applicable timing. For a time-sensitive order, email the support team before purchasing.';
    }
    if(/email|human|person|support|contact|help|talk/.test(q)){
      return `You can reach MyClinicProtocols support at ${SUPPORT_EMAIL}. Please do not include patient names, medical records, or protected health information in your message.`;
    }
    if(/find|search|locate|protocol|treatment/.test(q)){
      return 'Use the treatment search box on the Protocols page or inside the order form. You can search by procedure, treatment, medication, device, or service name.';
    }
    return `I can help with packages, pricing, included documents, treatment selection, customization, revisions, and general ordering questions. For anything else, email ${SUPPORT_EMAIL} and the team can assist you.`;
  }

  function installSupport(){
    if(document.querySelector('.mycp-support-launcher')) return;

    const launcher=document.createElement('button');
    launcher.className='mycp-support-launcher';
    launcher.type='button';
    launcher.setAttribute('aria-expanded','false');
    launcher.setAttribute('aria-controls','mycpSupportPanel');
    launcher.innerHTML='<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 18.5 3.5 21v-5.1A8.5 8.5 0 1 1 12 20.5c-1.9 0-3.7-.6-5.1-1.6L5 18.5Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"></path><path d="M8 11.5h8M8 8.5h5" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path></svg><span>Need help?</span>';

    const panel=document.createElement('section');
    panel.className='mycp-support-panel';
    panel.id='mycpSupportPanel';
    panel.setAttribute('aria-label','MyClinicProtocols customer support');
    panel.innerHTML=`
      <div class="mycp-support-head">
        <div class="mycp-support-title"><div class="mycp-support-avatar">MY</div><div><strong>MYCP Assistant</strong><small>Automated customer support</small></div></div>
        <button class="mycp-support-close" type="button" aria-label="Close support">×</button>
      </div>
      <div class="mycp-support-body" id="mycpSupportBody" aria-live="polite">
        <div class="mycp-message bot">Hi! I can help you find a protocol, understand the packages, or answer common ordering questions. Please don’t include patient names or protected health information.</div>
        <div class="mycp-quick-actions">
          <button type="button" data-q="Which package should I choose?">Packages & pricing</button>
          <button type="button" data-q="Can I order multiple treatments?">Multiple treatments</button>
          <button type="button" data-q="What documents do I receive?">What’s included</button>
          <button type="button" data-q="How do revisions work?">Revisions</button>
        </div>
      </div>
      <form class="mycp-support-compose">
        <input type="text" maxlength="240" placeholder="Ask a question…" aria-label="Ask MYCP Assistant a question">
        <button class="mycp-support-send" type="submit">Send</button>
      </form>
      <a class="mycp-support-email" href="mailto:${SUPPORT_EMAIL}?subject=MyClinicProtocols%20Support">✉ Email ${SUPPORT_EMAIL}</a>
      <div class="mycp-support-privacy">General customer support only — do not send patient information.</div>`;

    document.body.appendChild(launcher);
    document.body.appendChild(panel);

    const close=panel.querySelector('.mycp-support-close');
    const body=panel.querySelector('#mycpSupportBody');
    const form=panel.querySelector('form');
    const input=form.querySelector('input');

    function openPanel(){
      panel.classList.add('open');
      launcher.setAttribute('aria-expanded','true');
      setTimeout(()=>input.focus(),60);
    }
    function closePanel(){
      panel.classList.remove('open');
      launcher.setAttribute('aria-expanded','false');
      launcher.focus();
    }
    function appendMessage(text,type){
      const message=document.createElement('div');
      message.className='mycp-message '+type;
      message.textContent=text;
      body.appendChild(message);
      body.scrollTop=body.scrollHeight;
    }
    function ask(question){
      const text=(question||'').trim();
      if(!text) return;
      appendMessage(text,'user');
      window.setTimeout(()=>appendMessage(answerFor(text),'bot'),180);
    }

    launcher.addEventListener('click',()=>panel.classList.contains('open')?closePanel():openPanel());
    close.addEventListener('click',closePanel);
    panel.querySelectorAll('.mycp-quick-actions button').forEach(btn=>btn.addEventListener('click',()=>ask(btn.dataset.q)));
    form.addEventListener('submit',event=>{
      event.preventDefault();
      const question=input.value;
      input.value='';
      ask(question);
    });
    document.addEventListener('keydown',event=>{
      if(event.key==='Escape' && panel.classList.contains('open')) closePanel();
    });
  }

  function boot(){
    installProtocolSearch();
    installOrderSearch();
    installSupport();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot);
  else boot();
})();
