/* MyClinicProtocols search + smart website support */
(function(){
  'use strict';

  const SUPPORT_EMAIL='myclinicprotocols@gmail.com';
  const ORDER_URL='order.html';
  const HOME_URL='index.html';
  const GUIDES_URL='resources.html';

  const PRICING={
    protocol:{label:'Customized Protocol',prices:{1:99,3:249,5:379,10:699}},
    complete:{label:'Complete Treatment Package',prices:{1:149,3:399,5:625,10:1099}}
  };

  const CATALOG=[
    {name:'Neuromodulators',category:'Injectables',aliases:['botox','dysport','xeomin','jeuveau','neurotoxin','wrinkle relaxer'],description:'Botox®, Dysport®, Xeomin®, Jeuveau®, and clinic-selected neuromodulator workflows.'},
    {name:'Dermal Fillers',category:'Injectables',aliases:['dermal filler','fillers','lip filler','cheek filler'],description:'Injection workflow, screening, documentation, aftercare, and adverse-event planning.'},
    {name:'Biostimulatory Injectables',category:'Injectables',aliases:['biostimulator','biostimulatory','sculptra'],description:'Clinic-selected biostimulatory injectable workflows.'},
    {name:'Hyaluronidase / Filler Dissolution',category:'Injectables',aliases:['hyaluronidase','filler dissolution','dissolve filler','filler dissolver'],description:'Elective and emergency filler-dissolution workflows.'},
    {name:'PDO Thread Treatments',category:'Injectables',aliases:['pdo thread','thread lift','threads'],description:'Thread treatment workflow and aftercare.'},
    {name:'Sclerotherapy',category:'Injectables',aliases:['sclerotherapy','spider vein injection'],description:'Spider-vein treatment workflow.'},

    {name:'Hair Growth with Exosomes',category:'Regenerative, Skin & Scalp',aliases:['hair exosome','exosome hair','exosomes for hair'],reviewOnly:true,description:'Product and regulatory review is required before MYCP accepts the protocol scope.'},
    {name:'PRP / PRF / PRFM',category:'Regenerative, Skin & Scalp',aliases:['prp','prf','prfm','platelet rich plasma','platelet rich fibrin'],description:'Regenerative preparation and treatment workflows.'},
    {name:'VAMP / PDRN Regenerative Treatments',category:'Regenerative, Skin & Scalp',aliases:['vamp','pdrn','regenerative treatment'],description:'Clinic-selected regenerative treatment workflow.'},
    {name:'Microneedling / SkinPen',category:'Regenerative, Skin & Scalp',aliases:['microneedling','skinpen','skin pen'],description:'Device-specific treatment, screening, safety, and aftercare.'},
    {name:'RF Microneedling',category:'Regenerative, Skin & Scalp',aliases:['rf microneedling','radiofrequency microneedling'],description:'Energy-device treatment and safety workflow.'},
    {name:'HydraFacial',category:'Regenerative, Skin & Scalp',aliases:['hydrafacial','hydra facial'],description:'Facial treatment workflow.'},
    {name:'Keravive Scalp Treatment',category:'Regenerative, Skin & Scalp',aliases:['keravive'],description:'Scalp-specific treatment and aftercare.'},
    {name:'Chemical Peels',orderValue:'Chemical Peel',category:'Regenerative, Skin & Scalp',aliases:['chemical peel','chemical peels','peel'],description:'Product, peel depth, screening, and aftercare workflow.'},
    {name:'Dermaplaning',category:'Regenerative, Skin & Scalp',aliases:['dermaplaning'],description:'Aesthetic treatment workflow.'},
    {name:'Acne Extractions & Blackhead Removal',category:'Regenerative, Skin & Scalp',aliases:['acne extraction','blackhead removal','comedone extraction'],description:'Skin-care extraction workflow.'},
    {name:'Hair Restoration Treatments',category:'Regenerative, Skin & Scalp',aliases:['hair restoration','hair loss treatment','scalp treatment'],description:'Scalp, PRP/PRF, and clinic-selected hair-restoration methods.'},

    {name:'Aerolase Treatments',category:'Laser & Energy Devices',aliases:['aerolase'],description:'Device- and indication-specific workflow.'},
    {name:'Laser Hair Removal',category:'Laser & Energy Devices',aliases:['laser hair removal','lhr'],description:'Screening, settings, safety, and aftercare.'},
    {name:'Laser Tattoo Removal',category:'Laser & Energy Devices',aliases:['tattoo removal','laser tattoo'],description:'Laser treatment and aftercare.'},
    {name:'Vascular / Spider Vein Laser',category:'Laser & Energy Devices',aliases:['vascular laser','spider vein laser','vein laser'],description:'Vascular laser workflow.'},
    {name:'IPL / BBL Photofacial',category:'Laser & Energy Devices',aliases:['ipl','bbl photofacial','photofacial','broadband light'],description:'Light-based treatment and safety workflow.'},
    {name:'Laser Skin Resurfacing',category:'Laser & Energy Devices',aliases:['laser resurfacing','skin resurfacing','ablative laser','non ablative laser'],description:'Ablative or non-ablative device workflow.'},

    {name:'Injectable GLP-1 / GIP Weight Management',category:'Weight Loss',aliases:['glp 1 injection','glp1 injection','semaglutide','tirzepatide','wegovy','zepbound','ozempic','mounjaro','weight loss injection','gip weight'],description:'Injectable weight-management workflow covering eligibility, titration, monitoring, adverse effects, maintenance, and escalation.'},
    {name:'Oral GLP-1 Weight Management',category:'Weight Loss',aliases:['oral glp 1','oral glp1','weight loss pill','oral weight loss'],description:'Oral incretin-based weight-management workflow with dosing/timing considerations, monitoring, adverse effects, and follow-up.'},
    {name:'GLP-1 Maintenance & Weight-Regain Prevention',category:'Weight Loss',aliases:['glp 1 maintenance','glp1 maintenance','weight regain','maintenance dose','post weight loss maintenance'],description:'Goal-weight transition, individualized maintenance planning, follow-up, and weight-regain response pathways.'},
    {name:'Muscle Preservation & Body Composition',category:'Weight Loss',aliases:['muscle preservation','muscle loss','lean mass','body composition'],description:'Protein/nutrition support, resistance training, lean-mass monitoring, and body-composition tracking.'},
    {name:'GLP-1 Side-Effect & Nutrition Support',category:'Weight Loss',aliases:['glp 1 side effect','glp1 side effect','nausea glp','constipation glp','nutrition glp'],description:'GI symptom screening, hydration, nutrition adequacy, common side-effect guidance, and escalation criteria.'},
    {name:'Menopause & Metabolic Weight Management',category:'Weight Loss',aliases:['menopause weight','perimenopause weight','postmenopause weight'],description:'Peri- and post-menopausal weight-management workflow with cardiometabolic and body-composition considerations.'},
    {name:'PCOS / Insulin-Resistance Weight Management',category:'Weight Loss',aliases:['pcos weight','insulin resistance weight','pcos glp'],description:'Metabolic assessment, lifestyle support, medication considerations, monitoring, and referral/escalation.'},
    {name:'Appetite & Food-Noise Monitoring',category:'Weight Loss',aliases:['food noise','appetite monitoring','satiety','cravings'],description:'Appetite, satiety, cravings, eating-pattern, adherence, and behavioral follow-up tracking.'},
    {name:'Retatrutide / Next-Generation Weight-Loss Therapies',category:'Weight Loss',aliases:['retatrutide','next generation weight loss'],reviewOnly:true,description:'This is listed for scope review only. Investigational therapies are not presented as standard purchasable protocols.'},

    {name:'Peptide Therapies',category:'Wellness & Medical Treatments',aliases:['peptide','peptides'],description:'Clinic-selected medication workflow. Exact product and scope details are reviewed during customization.'},
    {name:'Vitamin B12 / Lipo-B / Wellness Injections',orderValue:'IM / SQ Wellness Injections',category:'Wellness & Medical Treatments',aliases:['b12','vitamin b12','lipo b','mic b12','wellness injection','im injection','sq injection'],description:'Product-specific IM/SQ wellness-injection workflow.'},
    {name:'IV Hydration / Nutrient Therapy',category:'Wellness & Medical Treatments',aliases:['iv hydration','iv therapy','iv drip','nutrient therapy'],description:'Formula, infusion, and safety workflow.'},
    {name:'Blood Draws / Laboratory Services',category:'Wellness & Medical Treatments',aliases:['blood draw','phlebotomy','lab services','laboratory'],description:'Collection, handling, and result workflow.'},
    {name:'HRT / TRT',category:'Wellness & Medical Treatments',aliases:['hrt','trt','hormone replacement','testosterone replacement'],description:'Hormone-wellness workflow.'},
    {name:'Sexual Wellness Treatments',category:'Wellness & Medical Treatments',aliases:['sexual wellness'],description:'Clinic-selected treatment workflow.'},
    {name:'Red Light Therapy / Photobiomodulation',category:'Wellness & Medical Treatments',aliases:['red light therapy','photobiomodulation','pbm'],description:'Wellness treatment workflow.'},
    {name:'Ketamine Infusion (TRD)',category:'Wellness & Medical Treatments',aliases:['ketamine infusion','ketamine trd'],description:'Specialty infusion workflow.'},
    {name:'Spravato / Esketamine',category:'Wellness & Medical Treatments',aliases:['spravato','esketamine'],description:'Specialty treatment workflow.'},
    {name:'Detox Pills',category:'Wellness & Medical Treatments',aliases:['detox pill','detox pills'],reviewOnly:true,description:'Exact oral product and ingredients must be reviewed. MYCP does not assume a detoxification benefit.'},

    {name:'Liquid Lipo Package',category:'Body & Pelvic Floor',aliases:['liquid lipo'],reviewOnly:true,description:'Exact product, ingredients, route, and treatment area must be reviewed before scope is accepted.'},
    {name:'Body Sculpting / EMSCULPT',orderValue:'EMSCULPT / Body Contouring',category:'Body & Pelvic Floor',aliases:['emsculpt','body contouring','body sculpting'],description:'Device-specific body-contouring workflow and aftercare.'},
    {name:'Pelvic Floor Electromagnetic Treatments',category:'Body & Pelvic Floor',aliases:['pelvic floor','emsella','emchair'],description:'EMSELLA, EmChair, or clinic-selected device workflow.'},

    {name:'Medical Dermatology Standing Orders',category:'Dermatology & Minor Procedures',aliases:['dermatology standing order','medical dermatology'],description:'Dermatology standing-order workflows.'},
    {name:'Minor Aesthetic Procedures / Skin Tag Removal',category:'Dermatology & Minor Procedures',aliases:['skin tag','skin tag removal','minor aesthetic procedure'],description:'Clinic-selected minor-procedure workflow.'},
    {name:'Cryotherapy / Benign Lesion Removal',category:'Dermatology & Minor Procedures',aliases:['cryotherapy','benign lesion','lesion removal'],description:'Procedure and documentation workflow.'},
    {name:'Shave / Punch Biopsy',category:'Dermatology & Minor Procedures',aliases:['shave biopsy','punch biopsy','skin biopsy'],description:'Procedure and pathology workflow.'},
    {name:'Cyst / Wart Treatment',category:'Dermatology & Minor Procedures',aliases:['cyst treatment','wart treatment','wart removal'],description:'Clinic-selected treatment workflow.'},

    {name:'Vascular Occlusion Response',category:'Safety & Operations',aliases:['vascular occlusion','vo protocol'],description:'Recognition, response, escalation, and documentation workflow.'},
    {name:'Anaphylaxis Response',category:'Safety & Operations',aliases:['anaphylaxis','allergic emergency'],description:'Emergency response workflow.'},
    {name:'Syncope / Medical Emergency Response',category:'Safety & Operations',aliases:['syncope','fainting','medical emergency'],description:'Emergency response workflow.'},
    {name:'Laser Burn & Eye Safety',category:'Safety & Operations',aliases:['laser burn','eye safety','laser safety'],description:'Laser safety and response workflow.'},
    {name:'Infection Prevention / Bloodborne Pathogens',category:'Safety & Operations',aliases:['infection prevention','bloodborne pathogen','needlestick','needle stick'],description:'Exposure-prevention and response workflow.'},
    {name:'Medication Storage / Inventory / Cold Chain',category:'Safety & Operations',aliases:['medication storage','cold chain','inventory'],description:'Storage, tracking, and quality-control workflow.'},
    {name:'Adverse Event Documentation & Escalation',category:'Safety & Operations',aliases:['adverse event','incident escalation','complication documentation'],description:'Reporting, documentation, escalation, and follow-up workflow.'},
    {name:'Emergency Cart & Supply Checklist',category:'Safety & Operations',aliases:['emergency cart','crash cart','emergency supplies'],description:'Readiness and routine verification checklist.'}
  ];

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

  function normalize(value){
    return String(value||'')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g,'')
      .replace(/&/g,' and ')
      .replace(/[^a-z0-9]+/g,' ')
      .replace(/\s+/g,' ')
      .trim();
  }

  function editDistance(a,b){
    if(a===b) return 0;
    if(!a.length) return b.length;
    if(!b.length) return a.length;
    const prev=Array.from({length:b.length+1},(_,i)=>i);
    for(let i=1;i<=a.length;i++){
      let left=i;
      for(let j=1;j<=b.length;j++){
        const up=prev[j];
        const diag=prev[j-1];
        const next=Math.min(up+1,left+1,diag+(a[i-1]===b[j-1]?0:1));
        prev[j-1]=left;
        left=next;
      }
      prev[b.length]=left;
    }
    return prev[b.length];
  }

  function wordClose(a,b){
    if(a===b) return true;
    if(a.length<4 || b.length<4) return false;
    const max=Math.max(a.length,b.length);
    return editDistance(a,b) <= (max>=8?2:1);
  }

  function phraseMatches(query,phrase){
    const q=normalize(query);
    const p=normalize(phrase);
    if(!q || !p) return false;
    if(q.includes(p)) return true;
    const qWords=q.split(' ');
    const pWords=p.split(' ').filter(w=>w.length>2);
    if(!pWords.length) return false;
    const hits=pWords.filter(pw=>qWords.some(qw=>wordClose(qw,pw))).length;
    return hits===pWords.length || (pWords.length>=3 && hits/pWords.length>=0.75);
  }

  function hasAny(query,terms){
    return terms.some(term=>phraseMatches(query,term));
  }

  function liveCatalog(){
    const found=[];
    document.querySelectorAll('.protocol[data-value],.treatment[data-name]').forEach(el=>{
      const name=el.dataset.value||el.dataset.name;
      if(!name) return;
      const description=(el.querySelector('small')||el.querySelector('span span'))?.textContent?.trim()||'';
      found.push({name,category:'Website protocol library',aliases:[],description});
    });
    return found;
  }

  function catalogMatches(question){
    const pool=[...CATALOG,...liveCatalog()];
    const seen=new Set();
    const matches=[];
    pool.forEach(item=>{
      const key=normalize(item.name);
      if(seen.has(key)) return;
      const terms=[item.name,...(item.aliases||[])];
      if(terms.some(term=>phraseMatches(question,term))){
        seen.add(key);
        matches.push(item);
      }
    });
    return matches;
  }

  function links(...items){
    return items.filter(Boolean);
  }

  function response(text,actionLinks){
    return {text,links:actionLinks||[]};
  }

  function orderLink(item){
    if(item.reviewOnly){
      return {label:'Request scope review',href:`mailto:${SUPPORT_EMAIL}?subject=${encodeURIComponent('Protocol scope review: '+item.name)}`};
    }
    const value=item.orderValue||item.name;
    return {label:'Customize this protocol',href:`${ORDER_URL}?treatment=${encodeURIComponent(value)}`};
  }

  function protocolAnswer(matches,question){
    if(!matches.length) return null;
    if(matches.length===1){
      const item=matches[0];
      if(item.reviewOnly){
        return response(
          `${item.name} is listed under ${item.category} as a Request Review item rather than a standard one-click purchase. ${item.description} The MYCP team can review the exact product, intended use, and scope before confirming whether a protocol can be prepared.`,
          links(orderLink(item),{label:'Browse all protocols',href:`${HOME_URL}#protocols`})
        );
      }
      return response(
        `Yes — ${item.name} is available under ${item.category}. ${item.description} You can customize it around your clinic’s state, provider role, products/medications, concentrations or settings, equipment, methods, workflow, and branding.`,
        links(orderLink(item),{label:'Browse all protocols',href:`${HOME_URL}#protocols`})
      );
    }

    const names=matches.slice(0,6).map(x=>x.name).join('; ');
    return response(
      `I found several relevant MYCP options: ${names}${matches.length>6?' and more.':''} You can search the Protocol Library or the order form to narrow it down, and each selected treatment stays together in one clinic intake.`,
      links({label:'Browse matching protocols',href:`${HOME_URL}#protocols`},{label:'Build a package',href:ORDER_URL})
    );
  }

  function priceText(){
    return `Current founding pricing on the website is:
Customized Protocol — 1 treatment $99, 3 treatments $249, 5 treatments $379, or 10 treatments $699.
Complete Treatment Package — 1 treatment $149, 3 treatments $399, 5 treatments $625, or 10 treatments $1,099.

The Complete Treatment Package is the broader option because it includes the clinical protocol plus applicable consent, intake/eligibility, treatment record, pre/post-care, safety checklist, and emergency/adverse-event guidance.`;
  }

  function answerFor(question){
    const raw=(question||'').trim();
    const q=normalize(raw);
    if(!q) return response('Ask me anything about MyClinicProtocols — pricing, protocols, ordering, customization, delivery, revisions, state-specific setup, documents, payment, or support.');

    if(hasAny(q,['hello','hi','hey','good morning','good afternoon','good evening'])){
      return response(
        `Hi! I’m the MYCP website assistant. I can help with almost anything on MyClinicProtocols: finding a protocol, pricing, package differences, what documents are included, order steps, state-specific customization, provider roles, branding, delivery, revisions, PayPal checkout, and support.`,
        links({label:'Browse protocols',href:`${HOME_URL}#protocols`},{label:'Start an order',href:ORDER_URL})
      );
    }

    if(hasAny(q,['thank you','thanks','perfect','got it','great'])){
      return response('You’re welcome! If you need anything else, ask me about a treatment, package, order, delivery, revision, or state-specific question.');
    }

    if(hasAny(q,['patient specific','patient advice','diagnose','diagnosis','what should my patient','medical advice','clinical advice for a patient'])){
      return response(
        `I can explain MYCP products and website workflows, but I can’t provide patient-specific diagnosis, prescribing, dosing, or treatment advice. MYCP documents are prepared for review and final approval by the clinic’s appropriately qualified medical director or supervising provider.`,
        links({label:'Contact MYCP support',href:`mailto:${SUPPORT_EMAIL}?subject=MyClinicProtocols%20Support`})
      );
    }

    if(hasAny(q,['order status','where is my order','track my order','payment status','did my payment go through','receipt','invoice'])){
      return response(
        `I can explain the order process, but I can’t see an individual customer’s payment or order record from this chat. Please email ${SUPPORT_EMAIL} with your order reference and the email used at checkout. Do not include patient information.`,
        links({label:'Email order support',href:`mailto:${SUPPORT_EMAIL}?subject=Order%20status%20or%20payment%20support`})
      );
    }

    if(hasAny(q,['refund','cancel order','cancellation','chargeback'])){
      return response(
        `Refund or cancellation eligibility can depend on the order status and whether customized work has already started, so I don’t want to guess. Please contact ${SUPPORT_EMAIL} with your order reference for the current policy that applies to your purchase.`,
        links({label:'Email billing support',href:`mailto:${SUPPORT_EMAIL}?subject=Refund%20or%20cancellation%20question`})
      );
    }

    if(hasAny(q,['how do i order','how to order','place an order','start order','buy a protocol','purchase','checkout process'])){
      return response(
        `Ordering is straightforward:
1) Choose the Customized Protocol or Complete Treatment Package.
2) Select one or more treatments.
3) Enter your clinic, state, provider, and oversight details.
4) Add treatment-specific products, medications, formulas, devices, methods, and workflow notes.
5) Review your package and complete secure PayPal checkout.

The website then matches the intake to the verified payment before files are released.`,
        links({label:'Start my order',href:ORDER_URL},{label:'Browse protocols first',href:`${HOME_URL}#protocols`})
      );
    }

    if(hasAny(q,['paypal','payment method','pay','credit card','debit card','secure checkout'])){
      return response(
        `The website currently uses secure PayPal checkout. Your intake is matched to the verified PayPal payment before files are released. If checkout is temporarily unavailable, the site states that nothing was charged and you can try again or contact support.`,
        links({label:'Go to secure order page',href:ORDER_URL},{label:'Payment help',href:`mailto:${SUPPORT_EMAIL}?subject=Checkout%20or%20payment%20help`})
      );
    }

    if(hasAny(q,['2 treatments','4 treatments','6 treatments','7 treatments','8 treatments','9 treatments','custom quantity','other quantity','quantity not listed'])){
      return response(
        `Online checkout is currently set up for packages containing exactly 1, 3, 5, or 10 treatments. For another quantity, contact MYCP for a custom order rather than forcing the checkout.`,
        links({label:'Email for custom quantity',href:`mailto:${SUPPORT_EMAIL}?subject=Custom%20multi-treatment%20order`},{label:'View order page',href:ORDER_URL})
      );
    }

    if(hasAny(q,['price','pricing','cost','how much','bundle price','founding price','99','149','399','625','1099','699'])){
      return response(
        priceText(),
        links({label:'View pricing',href:`${HOME_URL}#pricing`},{label:'Build my package',href:ORDER_URL})
      );
    }

    if(hasAny(q,['which package','difference between packages','protocol vs complete','complete package','customized protocol'])){
      return response(
        `Choose the Customized Protocol if you mainly need the treatment protocol/SOP itself. Choose the Complete Treatment Package if you want the broader clinic documentation set around that treatment — protocol plus applicable consent, intake/eligibility, treatment record, pre/post-care, room/safety checklist, and emergency/adverse-event guidance. Both are customized to the clinic information you provide.`,
        links({label:'Compare pricing',href:`${HOME_URL}#pricing`},{label:'Choose a package',href:ORDER_URL})
      );
    }

    if(hasAny(q,['what is included','what do i get','documents included','forms included','consent','intake form','treatment record','aftercare','checklist','emergency guide','standing order','sop'])){
      return response(
        `MYCP can prepare the clinical protocol/SOP and, with the Complete Treatment Package, the applicable supporting set such as patient consent, intake/eligibility, treatment record, pre- and post-care, room/safety checklist, and emergency/adverse-event guidance. The exact set is organized around the treatment and clinic details you provide.`,
        links({label:'See package options',href:`${HOME_URL}#pricing`},{label:'Start customization',href:ORDER_URL})
      );
    }

    if(hasAny(q,['word','pdf','editable','edit the file','file format','downloadable'])){
      return response(
        `Yes. MYCP final deliverables are provided in editable Word format plus a clean PDF. That gives your clinic a working copy for edits/review and a polished PDF for records and approval.`,
        links({label:'See what you’re buying',href:HOME_URL})
      );
    }

    if(hasAny(q,['instant draft','draft after payment','immediate download','download after payment'])){
      return response(
        `The order flow provides an instant draft by website download with an email backup after verified payment. That draft is followed by the RN-reviewed version. The draft is not the final clinical approval — your clinic’s qualified reviewer still needs to review and approve the final content.`,
        links({label:'Start an order',href:ORDER_URL})
      );
    }

    if(hasAny(q,['delivery','turnaround','how long','when will i get','receive my files','rn reviewed','reviewed version'])){
      return response(
        `The website’s current workflow is: verified payment → instant draft by website download and email backup → RN-reviewed version, usually in about 1–2 hours and up to 24 hours depending on the documents/customization → revision period if needed.`,
        links({label:'Start an order',href:ORDER_URL},{label:'Time-sensitive question',href:`mailto:${SUPPORT_EMAIL}?subject=Delivery%20timing%20question`})
      );
    }

    if(hasAny(q,['revision','revisions','change my protocol','edit request','correction','14 days'])){
      return response(
        `Your package includes up to two consolidated revision rounds. The website asks customers to send consolidated comments during the revision period, and the current order flow references a 14-day revision window. Final clinical approval still remains with your clinic’s qualified medical director or supervising provider.`,
        links({label:'Revision support',href:`mailto:${SUPPORT_EMAIL}?subject=Revision%20request`})
      );
    }

    if(hasAny(q,['state specific','state-specific','my state','another state','multiple states','additional states','state requirement','state law'])){
      return response(
        `State is built into the MYCP intake. You can provide the clinic’s primary state and additional states so relevant jurisdiction-specific considerations can be addressed during customization. MYCP does not guarantee legal compliance or replace legal advice, and final review should be completed by the appropriately qualified supervising provider and, when needed, legal/compliance counsel.`,
        links({label:'Enter my state in the order form',href:ORDER_URL})
      );
    }

    if(hasAny(q,['compliant','compliance','legal','legally compliant','guarantee compliance','legal advice'])){
      return response(
        `MYCP is designed to make state, provider, workflow, and clinic-specific considerations easier to organize, but it does not guarantee legal compliance and does not replace legal or professional advice. Final protocols should be reviewed and approved by an appropriately qualified medical professional and, when needed, legal/compliance counsel.`,
        links({label:'About MYCP',href:`${HOME_URL}#about`})
      );
    }

    if(hasAny(q,['medical director','supervising provider','who approves','final approval','provider approval','do i need a doctor'])){
      return response(
        `MYCP prepares documentation for professional review; it does not replace any medical-director or supervising-provider relationship your clinic may be required to have. Final clinical approval remains with the clinic’s appropriately qualified medical director or supervising provider.`,
        links({label:'Learn how customization works',href:`${HOME_URL}#about`})
      );
    }

    if(hasAny(q,['provider role','who can use','rn','nurse practitioner','np','physician assistant','pa','md','do','lpn','lvn','aesthetician','esthetician'])){
      return response(
        `The order intake supports MD/DO, NP, PA, RN, LPN/LVN, aesthetician, and Other provider roles. The protocol structure starts with who is actually performing the service, and state/scope considerations still require qualified review.`,
        links({label:'Choose provider role',href:ORDER_URL})
      );
    }

    if(hasAny(q,['logo','branding','brand color','clinic name on','custom branding','white label'])){
      return response(
        `Yes. MYCP can incorporate your clinic name/details and logo, and the order form also captures brand color information. The goal is a polished package that looks like it belongs to your clinic rather than a generic download.`,
        links({label:'Customize my branding',href:ORDER_URL})
      );
    }

    if(hasAny(q,['custom treatment','not on the list','not listed','another treatment','add my own treatment','special request'])){
      return response(
        `If your treatment is not listed, the order form includes an option to add another treatment. Some products or emerging therapies need a scope/product review before MYCP confirms the work. You can also email support for a pre-purchase scope check.`,
        links({label:'Add a custom treatment',href:ORDER_URL},{label:'Ask for scope review',href:`mailto:${SUPPORT_EMAIL}?subject=Custom%20protocol%20scope%20review`})
      );
    }

    if(hasAny(q,['multiple treatments','more than one treatment','several treatments','bundle','combine protocols','multi treatment'])){
      return response(
        `Yes. You can select multiple treatments in one order and keep them together in a single clinic intake. The site has bundle pricing for 3, 5, and 10 treatments, in addition to a single-treatment option.`,
        links({label:'Build a multi-treatment package',href:ORDER_URL},{label:'See bundle pricing',href:`${HOME_URL}#pricing`})
      );
    }

    if(hasAny(q,['medication','concentration','dose','formula','equipment','device','technique','method','workflow','settings','brand of product'])){
      return response(
        `Yes — those details are part of customization. The order form lets you enter the product/medication/formula/device, concentration or treatment settings when applicable, technique/method, and workflow or special instructions. That information helps MYCP prepare documents around how your clinic actually operates.`,
        links({label:'Enter treatment details',href:ORDER_URL})
      );
    }

    if(hasAny(q,['phi','hipaa','patient name','patient information','protected health information','medical record'])){
      return response(
        `MYCP does not ask you to enter patient names, records, or protected health information into the order form or support chat. Please keep all submissions at the clinic/workflow level and do not send PHI by chat or email.`,
        links({label:'Order without patient information',href:ORDER_URL})
      );
    }

    if(hasAny(q,['guides','guide','articles','resources','blog','learn','education'])){
      return response(
        `Yes. MYCP has a Guides section with educational resources about med-spa protocol documentation and related topics. Use the Guides link in the main navigation to browse them.`,
        links({label:'Open MYCP Guides',href:GUIDES_URL})
      );
    }

    if(hasAny(q,['what is myclinicprotocols','what is mycp','about mycp','who are you','what do you do'])){
      return response(
        `MyClinicProtocols creates customized documentation resources for aesthetic, wellness, weight-management, dermatology, specialty-treatment, and clinic-safety workflows. The documents are RN-prepared and quality-checked, customized around your clinic details, and organized for qualified provider review. MYCP is more than a generic downloadable template.`,
        links({label:'About MYCP',href:`${HOME_URL}#about`},{label:'Browse protocols',href:`${HOME_URL}#protocols`})
      );
    }

    if(hasAny(q,['sample','preview','see what i am buying','example','what does it look like'])){
      return response(
        `The website includes a “See what you’re buying” area and customization examples showing how reviewed clinical references, clinic details, medications/formulas, equipment, workflow, revisions, and the final Word/PDF package fit together.`,
        links({label:'View website examples',href:HOME_URL})
      );
    }

    if(hasAny(q,['international','outside usa','outside us','canada','uk','australia','philippines'])){
      return response(
        `MYCP’s current website and state-specific workflow are primarily oriented to U.S. clinics. For a non-U.S. clinic, email support before purchasing so the team can confirm whether the requested scope can be supported.`,
        links({label:'Ask about non-U.S. scope',href:`mailto:${SUPPORT_EMAIL}?subject=Non-US%20clinic%20protocol%20question`})
      );
    }

    if(hasAny(q,['email','contact','human','person','customer service','support','talk to someone','speak to someone'])){
      return response(
        `You can reach MyClinicProtocols customer support at ${SUPPORT_EMAIL}. For order-specific questions, include your order reference and the email used at checkout, but do not include patient information.`,
        links({label:`Email ${SUPPORT_EMAIL}`,href:`mailto:${SUPPORT_EMAIL}?subject=MyClinicProtocols%20Support`})
      );
    }

    if(hasAny(q,['categories','what protocols','protocols available','what treatments','treatment list','what do you offer','services available'])){
      return response(
        `The MYCP library currently covers Injectables; Regenerative, Skin & Scalp; Laser & Energy Devices; Weight Loss; Wellness & Medical Treatments; Body & Pelvic Floor; Dermatology & Minor Procedures; and Safety & Operations. You can search the library by treatment, medication, device, or service name.`,
        links({label:'Browse protocol library',href:`${HOME_URL}#protocols`},{label:'Search inside the order form',href:ORDER_URL})
      );
    }

    const matches=catalogMatches(raw);
    const matchedAnswer=protocolAnswer(matches,raw);
    if(matchedAnswer) return matchedAnswer;

    if(hasAny(q,['find','search','locate','protocol','treatment'])){
      return response(
        `Use the search box in the Protocol Library or inside the order form. You can search by procedure, treatment, medication, device, or service name. If nothing matches, add a custom treatment or ask support for a scope review.`,
        links({label:'Browse protocols',href:`${HOME_URL}#protocols`},{label:'Open order form',href:ORDER_URL})
      );
    }

    return response(
      `I can answer most questions about the MYCP website — protocols, pricing, packages, included documents, state-specific customization, provider roles, branding, ordering, PayPal checkout, delivery, instant drafts, revisions, file formats, custom treatments, Guides, and support. I couldn’t confidently match that question, so I’d rather not guess. Try rephrasing it, or email ${SUPPORT_EMAIL} for a human answer.`,
      links({label:'Browse protocols',href:`${HOME_URL}#protocols`},{label:'Email support',href:`mailto:${SUPPORT_EMAIL}?subject=MyClinicProtocols%20Question`})
    );
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
        <div class="mycp-support-title"><div class="mycp-support-avatar">MY</div><div><strong>MYCP Assistant</strong><small>Smart website &amp; order support</small></div></div>
        <button class="mycp-support-close" type="button" aria-label="Close support">×</button>
      </div>
      <div class="mycp-support-body" id="mycpSupportBody" aria-live="polite">
        <div class="mycp-message bot">Hi! How can I help? Ask me anything about MyClinicProtocols, or type a treatment name to find a protocol.</div>
        <div class="mycp-quick-actions">
          <button type="button" data-q="Help me find a protocol">Find a protocol</button>
          <button type="button" data-q="What are the packages and prices?">Packages &amp; pricing</button>
          <button type="button" data-q="What documents are included?">What’s included</button>
          <button type="button" data-q="How long does delivery take?">Delivery</button>
          <button type="button" data-q="How do revisions work?">Revisions</button>
          <button type="button" data-q="How does state-specific customization work?">State-specific</button>
          <button type="button" data-q="How do I place an order?">Order help</button>
          <button type="button" data-q="How can I contact customer service?">Contact</button>
        </div>
      </div>
      <form class="mycp-support-compose">
        <input type="text" maxlength="320" placeholder="Ask about MYCP…" aria-label="Ask MYCP Assistant a question">
        <button class="mycp-support-send" type="submit">Send</button>
      </form>
      <a class="mycp-support-email" href="mailto:${SUPPORT_EMAIL}?subject=MyClinicProtocols%20Support">✉ Email ${SUPPORT_EMAIL}</a>
      <div class="mycp-support-privacy">Website and ordering support only — do not send patient information.</div>`;

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

    function appendMessage(payload,type){
      const data=typeof payload==='string'?{text:payload,links:[]}:payload;
      const message=document.createElement('div');
      message.className='mycp-message '+type;

      const text=document.createElement('div');
      text.className='mycp-message-text';
      text.textContent=data.text||'';
      message.appendChild(text);

      if(type==='bot' && Array.isArray(data.links) && data.links.length){
        const actions=document.createElement('div');
        actions.className='mycp-message-actions';
        data.links.slice(0,3).forEach(link=>{
          const a=document.createElement('a');
          a.className='mycp-message-link';
          a.textContent=link.label;
          a.href=link.href;
          actions.appendChild(a);
        });
        message.appendChild(actions);
      }

      body.appendChild(message);
      body.scrollTop=body.scrollHeight;
    }

    function ask(question){
      const text=(question||'').trim();
      if(!text) return;
      appendMessage(text,'user');
      window.setTimeout(()=>appendMessage(answerFor(text),'bot'),160);
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
