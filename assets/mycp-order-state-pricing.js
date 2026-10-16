/* MYCP order-form enhancements: required clinic contact + state-specific protocol pricing. */
(function(){
  'use strict';

  const UNIT_PRICE={protocol:29,complete:49};
  const LIMIT={protocol:8,complete:5};

  function $(selector){return document.querySelector(selector)}
  function $$(selector){return [...document.querySelectorAll(selector)]}
  function additionalStates(){
    return ($('#additionalStates')?.value||'').split(',').map(x=>x.trim()).filter(Boolean);
  }
  function stateCount(){return ($('#state')?.value?1:0)+additionalStates().length}
  function treatmentCount(){
    return $$('.treatment.selected[data-name]').length+$$('#customChips .chip').length;
  }
  function packageKey(){return $('.package.selected[data-package]')?.dataset.package||'complete'}
  function protocolUnits(){return treatmentCount()*Math.max(1,stateCount())}
  function calculatedTotal(){return protocolUnits()*(UNIT_PRICE[packageKey()]||0)}
  function overLimit(){return protocolUnits()>(LIMIT[packageKey()]||0)}

  function addStyles(){
    if($('#mycpStatePricingStyles'))return;
    const style=document.createElement('style');
    style.id='mycpStatePricingStyles';
    style.textContent=`
      .state-pricing-note{margin-top:10px;padding:11px 13px;border:1px solid #c9e5e5;border-radius:11px;background:#f2fbfb;color:#355e69;font-size:11.5px;line-height:1.55}
      .state-pricing-note strong{color:#075f65}
      .state-pricing-warning{margin-top:8px;color:#9a6424;font-weight:700}
    `;
    document.head.appendChild(style);
  }

  function reviseClinicFields(){
    const website=$('#website');
    if(website){
      const field=website.closest('.field');
      const label=field?.querySelector('label');
      website.id='contactName';
      website.name='contactName';
      website.type='text';
      website.value='';
      website.placeholder='Full name';
      website.setAttribute('autocomplete','name');
      website.required=true;
      if(label){label.htmlFor='contactName';label.textContent='Contact name';label.classList.add('required')}
    }
    const phone=$('#phone');
    if(phone){
      phone.required=true;
      const label=phone.closest('.field')?.querySelector('label');
      if(label)label.classList.add('required');
    }
    const error=$('#error2');
    if(error)error.textContent='Please enter the clinic name, contact name, a valid order email, phone number, and primary state.';
  }

  function reviseStateNote(){
    const picker=$('#additionalStatesPicker');
    if(!picker)return;
    const existing=picker.querySelector('.multi-state-note');
    if(existing)existing.remove();
    if(picker.querySelector('.state-pricing-note'))return;
    const note=document.createElement('div');
    note.className='state-pricing-note';
    note.innerHTML='<strong>State-specific pricing:</strong> Each protocol package is prepared for one state because scope-of-practice, supervision, and documentation requirements can vary by jurisdiction. If you select additional states, a separate state-specific version will be prepared for each selected state and charged at the standard per-protocol rate.';
    picker.appendChild(note);
  }

  function validClinicContact(){
    const contact=$('#contactName')?.value.trim();
    const phone=$('#phone')?.value.trim();
    return Boolean(contact&&phone);
  }

  function updateTotals(){
    const count=treatmentCount();
    if(!count)return;
    const side=$('#sideTotal');
    if(side)side.textContent=overLimit()?'$249 All Access':`$${calculatedTotal()}`;

    const review=$('#reviewBox');
    if(review&&$('.panel[data-panel="5"]')?.classList.contains('active')){
      const totalRow=review.querySelector('.total-row strong');
      if(totalRow)totalRow.textContent=overLimit()?'$249 All Access':`$${calculatedTotal()}`;
      if(!review.querySelector('[data-mycp-contact]')){
        const clinicRow=review.querySelector('.review-row');
        if(clinicRow){
          const row=document.createElement('div');
          row.className='review-row';row.dataset.mycpContact='1';
          row.innerHTML=`<span>Contact name</span><strong>${($('#contactName')?.value||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}</strong>`;
          clinicRow.insertAdjacentElement('afterend',row);
        }
      }
      if(!review.querySelector('[data-mycp-state-versions]')){
        const stateRow=[...review.querySelectorAll('.review-row')].find(r=>r.querySelector('span')?.textContent==='Additional states');
        if(stateRow){
          const row=document.createElement('div');
          row.className='review-row';row.dataset.mycpStateVersions='1';
          row.innerHTML=`<span>State-specific protocol versions</span><strong>${protocolUnits()} total (${treatmentCount()} treatment${treatmentCount()===1?'':'s'} × ${Math.max(1,stateCount())} state${Math.max(1,stateCount())===1?'':'s'})</strong>`;
          stateRow.insertAdjacentElement('afterend',row);
        }
      }
    }
  }

  function validateClinicStep(event){
    if(validClinicContact())return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const error=$('#error2');
    if(error){error.classList.add('show');error.scrollIntoView({behavior:'smooth',block:'center'})}
  }

  function validateCheckout(event){
    if(!validClinicContact()){
      event.preventDefault();event.stopImmediatePropagation();
      const status=$('#checkoutStatus');
      if(status){status.textContent='Please return to Clinic details and enter the required contact name and phone number.';status.classList.add('show')}
      return;
    }
    if(overLimit()){
      event.preventDefault();event.stopImmediatePropagation();
      const note=$('#checkoutNote');
      if(note){
        note.innerHTML=`This order creates ${protocolUnits()} state-specific protocol versions. Standard ${packageKey()==='complete'?'Complete Treatment Package':'Customized Protocol'} checkout supports up to ${LIMIT[packageKey()]} versions per order. <a href="all-access.html#payment"><strong>30-Day All Access is $249</strong></a> and is the best option for this volume.`;
        note.classList.add('show');
      }
    }
  }

  function installFetchPricing(){
    if(window.__mycpStatePricingFetchInstalled)return;
    window.__mycpStatePricingFetchInstalled=true;
    const originalFetch=window.fetch.bind(window);
    window.fetch=async function(input,init){
      const url=typeof input==='string'?input:input?.url||'';
      if(url.includes('/api/checkout/create')&&init?.body){
        try{
          const payload=JSON.parse(init.body);
          const primary=payload.clinic?.state||$('#state')?.value||'';
          const extra=(payload.clinic?.additionalStates||'').split(',').map(x=>x.trim()).filter(Boolean).filter(x=>x!==primary);
          const states=[primary,...extra].filter(Boolean);
          const originalTreatments=[...(payload.treatments||[])];
          const stateSpecificTreatments=[];
          originalTreatments.forEach(treatment=>states.forEach(state=>stateSpecificTreatments.push(`${treatment} — ${state}`)));
          payload.clinic=payload.clinic||{};
          payload.clinic.contactName=$('#contactName')?.value.trim()||'';
          payload.clinic.phone=$('#phone')?.value.trim()||payload.clinic.phone||'';
          delete payload.clinic.website;
          payload.details=payload.details||{};
          payload.details.stateSpecificOrder={primaryState:primary,additionalStates:extra,stateCount:states.length,originalTreatments};
          payload.treatments=stateSpecificTreatments.length?stateSpecificTreatments:originalTreatments;
          payload.expectedTotal=payload.treatments.length*(UNIT_PRICE[payload.package]||0);
          init={...init,body:JSON.stringify(payload)};
        }catch(e){/* Let the server handle malformed requests safely. */}
      }
      return originalFetch(input,init);
    };
  }

  function installCommercePricing(){
    if(!window.MYCPCommerce||window.__mycpStatePricingCommerceInstalled)return;
    window.__mycpStatePricingCommerceInstalled=true;
    const originalVerify=window.MYCPCommerce.verifyQuote.bind(window.MYCPCommerce);
    const originalTrack=window.MYCPCommerce.trackCheckout.bind(window.MYCPCommerce);
    window.MYCPCommerce.verifyQuote=function(result){return originalVerify(result,calculatedTotal())};
    window.MYCPCommerce.trackCheckout=function(result,key){return originalTrack(result,key,protocolUnits())};
  }

  function boot(){
    if(!$('#additionalStatesPicker'))return;
    addStyles();
    reviseClinicFields();
    reviseStateNote();
    installFetchPricing();
    installCommercePricing();

    const clinicNext=$('.panel[data-panel="2"] .next');
    if(clinicNext)clinicNext.addEventListener('click',validateClinicStep,true);
    const checkout=$('#checkout');
    if(checkout)checkout.addEventListener('click',validateCheckout,true);

    document.addEventListener('click',()=>setTimeout(updateTotals,0));
    document.addEventListener('input',()=>setTimeout(updateTotals,0));
    document.addEventListener('change',()=>setTimeout(updateTotals,0));
    const observer=new MutationObserver(()=>updateTotals());
    observer.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['class','value']});
    updateTotals();
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);
  else boot();
})();
