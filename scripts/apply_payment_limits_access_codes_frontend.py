from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def patch(path: str, transform):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    new = transform(text)
    if new == text:
        raise RuntimeError(f"No changes made to {path}")
    p.write_text(new, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Expected text not found for {label}")
    return text.replace(old, new, 1)


def sub_once(text: str, pattern: str, repl: str, label: str, flags=0) -> str:
    new, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"Expected one regex match for {label}, got {count}")
    return new


def order_transform(text: str) -> str:
    text = text.replace('assets/mycp-commerce.js?v=20261009', 'assets/mycp-commerce.js?v=20261010-2')
    text = replace_once(
        text,
        'const pricing={protocol:{label:"Customized Protocol",units:{1:29,3:87,5:145,10:290}},complete:{label:"Complete Treatment Package",units:{1:49,3:147,5:245,10:490}}};',
        'const pricing={protocol:{label:"Customized Protocol",max:8,units:{1:29,2:58,3:87,4:116,5:145,6:174,7:203,8:232}},complete:{label:"Complete Treatment Package",max:5,units:{1:49,2:98,3:147,4:196,5:245}}};',
        'order pricing limits'
    )
    text = replace_once(
        text,
        '<button class="package" type="button" data-package="protocol"><h3>Customized Protocol</h3><div class="price">$29 <small>one treatment</small></div><p>Customized SOP/protocol, clinic branding, editable Word file, PDF, and two revision rounds.</p></button>',
        '<button class="package" type="button" data-package="protocol"><h3>Customized Protocol</h3><div class="price">$29 <small>/ treatment</small></div><p>Customized SOP/protocol, clinic branding, editable Word file, PDF, and two revision rounds. <strong>Order up to 8 treatments.</strong></p></button>',
        'protocol card limit'
    )
    text = replace_once(
        text,
        '<button class="package selected" type="button" data-package="complete"><span class="popular">MOST POPULAR</span><h3>Complete Treatment Package</h3><div class="price">$49 <small>one treatment</small></div><p>For $20 more, add applicable consent, intake, treatment record, aftercare, checklists, and emergency guidance.</p></button>',
        '<button class="package selected" type="button" data-package="complete"><span class="popular">MOST POPULAR</span><h3>Complete Treatment Package</h3><div class="price">$49 <small>/ treatment</small></div><p>For $20 more, add applicable consent, intake, treatment record, aftercare, checklists, and emergency guidance. <strong>Order up to 5 treatments.</strong></p></button>',
        'complete card limit'
    )
    text = replace_once(
        text,
        '</div>\n          <span class="section-label">Treatments</span>\n          <div class="treatment-grid" id="treatmentGrid"></div>',
        '</div>\n          <div class="all-access-recommend" id="allAccessRecommend"><strong>Need more?</strong> Once you reach 9 Customized Protocols or 6 Complete Treatment Packages, the <b>$249 30-Day All Access</b> option is the better value. <a href="all-access.html#payment">Get 30-Day All Access →</a></div>\n          <span class="section-label">Treatments</span>\n          <div class="treatment-grid" id="treatmentGrid"></div>',
        'all access recommendation banner'
    )
    text = replace_once(
        text,
        '.package .popular{display:inline-block;background:#e7f7f7;color:var(--teal-dark);font-size:10px;font-weight:800;border-radius:999px;padding:5px 8px;margin-bottom:10px}',
        '.package .popular{display:inline-block;background:#e7f7f7;color:var(--teal-dark);font-size:10px;font-weight:800;border-radius:999px;padding:5px 8px;margin-bottom:10px}.all-access-recommend{display:none;margin-top:14px;padding:14px 16px;border:1px solid #bfe3e3;background:#eefafa;border-radius:14px;color:#245d66;font-size:13px}.all-access-recommend.show{display:block}.all-access-recommend a{display:inline-block;margin-left:6px;color:var(--teal-dark);font-weight:800;text-decoration:underline}',
        'recommendation styles'
    )
    text = replace_once(
        text,
        'function allTreatments(){return [...model.treatments,...model.custom]}\n    function total(){const count=allTreatments().length;if(!count)return 0;const units=pricing[model.package].units,dp=Array(count+1).fill(Infinity);dp[0]=0;for(let i=1;i<=count;i++)Object.keys(units).map(Number).forEach(n=>{if(n<=i)dp[i]=Math.min(dp[i],dp[i-n]+units[n])});return dp[count]}\n    function refreshTotal(){$("#sideTotal").textContent=`$${total()}`}',
        'function allTreatments(){return [...model.treatments,...model.custom]}\n    function planLimit(packageKey=model.package){return pricing[packageKey].max}\n    function overPlanLimit(packageKey=model.package){return allTreatments().length>planLimit(packageKey)}\n    function total(){const count=allTreatments().length;if(!count)return 0;return pricing[model.package].units[count]||0}\n    function showAllAccessRecommendation(){const el=$("#allAccessRecommend");if(el){el.classList.add("show");el.scrollIntoView({behavior:"smooth",block:"nearest"})}}\n    function refreshTotal(){const count=allTreatments().length;$("#sideTotal").textContent=overPlanLimit()?"$249 All Access":`$${total()}`;if(count>=planLimit())$("#allAccessRecommend")?.classList.add("show")}',
        'direct total and limits'
    )
    text = replace_once(
        text,
        "$$('.package').forEach(b=>b.onclick=()=>{$$('.package').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');model.package=b.dataset.package;model.documents=[];refreshTotal()});\n    $$('.treatment').forEach(b=>b.onclick=()=>{b.classList.toggle('selected');const n=b.dataset.name,idx=model.treatments.indexOf(n);idx<0?model.treatments.push(n):model.treatments.splice(idx,1);refreshTotal()});\n    $$('.choice').forEach(b=>b.onclick=()=>{b.classList.toggle('selected');const n=b.dataset.provider,idx=model.providers.indexOf(n);idx<0?model.providers.push(n):model.providers.splice(idx,1)});\n    $('#addCustom').onclick=()=>{const el=$('#customTreatment'),v=el.value.trim();if(v&&!allTreatments().some(x=>x.toLowerCase()===v.toLowerCase())){model.custom.push(v);el.value='';renderCustom();refreshTotal()}};",
        "$$('.package').forEach(b=>b.onclick=()=>{const candidate=b.dataset.package;if(allTreatments().length>planLimit(candidate)){showAllAccessRecommendation();return}$$('.package').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');model.package=candidate;model.documents=[];refreshTotal()});\n    $$('.treatment').forEach(b=>b.onclick=()=>{const n=b.dataset.name,idx=model.treatments.indexOf(n);if(idx<0&&allTreatments().length>=planLimit()){showAllAccessRecommendation();return}b.classList.toggle('selected');idx<0?model.treatments.push(n):model.treatments.splice(idx,1);refreshTotal()});\n    $$('.choice').forEach(b=>b.onclick=()=>{b.classList.toggle('selected');const n=b.dataset.provider,idx=model.providers.indexOf(n);idx<0?model.providers.push(n):model.providers.splice(idx,1)});\n    $('#addCustom').onclick=()=>{const el=$('#customTreatment'),v=el.value.trim();if(v&&!allTreatments().some(x=>x.toLowerCase()===v.toLowerCase())){if(allTreatments().length>=planLimit()){showAllAccessRecommendation();return}model.custom.push(v);el.value='';renderCustom();refreshTotal()}};",
        'selection limit handlers'
    )
    text = replace_once(
        text,
        '<div class="checkout-note" id="checkoutNote">Online checkout is available for packages containing exactly 1, 3, 5, or 10 treatments. Please adjust the quantity or contact us for a custom order.</div>',
        '<div class="checkout-note" id="checkoutNote">Customized Protocol orders are limited to 8 treatments and Complete Treatment Package orders are limited to 5. For larger orders, <a href="all-access.html#payment"><strong>get 30-Day All Access for $249</strong></a>.</div>',
        'checkout limit note'
    )
    return text


def index_transform(text: str) -> str:
    text = text.replace('href="all-access.html"', 'href="all-access.html#payment"')
    text = text.replace('Customized treatment protocol or SOP</li>', 'Customized treatment protocol or SOP</li><li>Order up to 8 treatments at $29 each</li>', 1)
    text = text.replace('Everything in Customized Protocol</li>', 'Everything in Customized Protocol</li><li>Order up to 5 treatments at $49 each</li>', 1)
    text = text.replace('One clinic can request as many eligible protocols and Complete Treatment Packages as needed during the active 30-day period.', 'Pay once, receive a unique 30-day access code, and request as many eligible protocols and Complete Treatment Packages as needed during the active period.')
    text = text.replace('Get 30-Day All Access</a>', 'Pay $249 &amp; Get Access Code</a>')
    text = text.replace('The $249 All Access pass is a one-time purchase valid for 30 days for one clinic/legal practice; it does not auto-renew.', 'The $249 All Access pass is recommended at 9+ Customized Protocols or 6+ Complete Treatment Packages. It is a one-time purchase valid for 30 days for one clinic/legal practice and does not auto-renew.')
    return text


def all_access_transform(text: str) -> str:
    text = text.replace('assets/mycp-commerce.js?v=20261010', 'assets/mycp-commerce.js?v=20261010-2')
    text = replace_once(text, '<section class="form-card">', '<section class="form-card" id="payment">', 'payment anchor')
    text = text.replace('<h2>Activate your All Access pass</h2>', '<h2>Secure payment. Activate your 30-day access</h2>')
    text = text.replace('We’ll use this clinic profile for your 30-day access. You can provide treatment-specific details each time you submit a request.', 'Pay first to activate access. After PayPal payment is verified, MYCP will issue a unique access code valid for 30 days. Treatment-specific details are submitted later when you use the code.')
    text = text.replace('<div class="highlight"><strong>No need to choose all your protocols today.</strong> Your 30-day period starts only after your payment is verified.</div>', '<div class="highlight"><strong>Payment first. Requests come after.</strong> Your 30-day period starts only after payment is verified. Your unique access code is then displayed on the confirmation page and can be used in the All Access Request Portal for the full 30 days.</div>')
    text = text.replace("try{localStorage.setItem('mycp_pending_payment',JSON.stringify({orderReference:result.orderReference,paypalOrderId:result.paypalOrderId}))}catch(e){}", "try{localStorage.setItem('mycp_pending_payment',JSON.stringify({orderReference:result.orderReference,paypalOrderId:result.paypalOrderId,package:'all_access',customerEmail:document.getElementById('email').value.trim()}))}catch(e){}")
    return text


def request_transform(text: str) -> str:
    text = text.replace('assets/mycp-commerce.js?v=20261010', 'assets/mycp-commerce.js?v=20261010-2')
    text = text.replace('Use the same All Access order reference and email for every request during your active 30-day period.', 'Enter the unique access code issued after payment and the purchasing email. The same code works for the full active 30-day period.')
    text = replace_once(text, '<div class="field"><label class="req" for="reference">All Access order reference</label><input id="reference" placeholder="MYCP-20261010-XXXXXXXX" autocomplete="off"></div>', '<div class="field"><label class="req" for="accessCode">30-Day Access Code</label><input id="accessCode" placeholder="MYCP-XXXX-XXXX-XXXX-XXXX" autocomplete="off" autocapitalize="characters"></div>', 'access code input')
    pattern = r"const params=new URLSearchParams\(location\.search\),ref=document\.getElementById\('reference'\);if\(params\.get\('ref'\)\)ref\.value=params\.get\('ref'\);\n  const submit=.*?\n  \}\);"
    replacement = """const accessCode=document.getElementById('accessCode'),emailField=document.getElementById('email');
  try{const saved=JSON.parse(localStorage.getItem('mycp_all_access_pass')||'null');if(saved?.accessCode)accessCode.value=saved.accessCode;if(saved?.customerEmail)emailField.value=saved.customerEmail}catch(e){}
  const submit=document.getElementById('submit'),status=document.getElementById('status');
  submit.addEventListener('click',async()=>{
    const email=emailField.value.trim(),treatment=document.getElementById('treatment').value.trim(),code=accessCode.value.trim().toUpperCase();
    if(!code||!email||!emailField.validity.valid||!treatment){status.textContent='Please enter your 30-Day Access Code, purchasing email, and requested protocol.';status.classList.add('show');return;}
    submit.disabled=true;submit.textContent='Submitting request…';status.textContent='Verifying your active 30-Day Access Code…';status.classList.add('show');
    try{
      const response=await fetch(`${MYCPCommerce.API}/api/all-access/request`,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({accessCode:code,customerEmail:email,treatment,requestType:document.getElementById('requestType').value,notes:document.getElementById('details').value.trim()})});
      const result=await response.json().catch(()=>({}));if(!response.ok)throw new Error(result.detail||'Unable to submit request');
      status.innerHTML=`<strong>Request received - ${result.requestReference}</strong><br>Your access code is active through ${new Date(result.accessExpiresAt).toLocaleDateString(undefined,{year:'numeric',month:'long',day:'numeric'})}. You can submit another request anytime during the active period.`;
      try{localStorage.setItem('mycp_all_access_pass',JSON.stringify({accessCode:code,customerEmail:email,accessExpiresAt:result.accessExpiresAt}))}catch(e){}
      document.getElementById('treatment').value='';document.getElementById('details').value='';
    }catch(error){status.textContent=error.message||'We could not submit the request. Please verify your access code and purchasing email.'}
    finally{submit.disabled=false;submit.textContent='Submit All Access Request'}
  });"""
    return sub_once(text, pattern, replacement, 'request portal script', flags=re.S)


def checkout_return_transform(text: str) -> str:
    text = text.replace('assets/mycp-commerce.js?v=20261010', 'assets/mycp-commerce.js?v=20261010-2')
    text = replace_once(text, '.error{background:#fff4f2;color:#962f24}', '.error{background:#fff4f2;color:#962f24}.license{display:none;margin:18px 0;padding:18px;border:2px solid var(--teal);border-radius:14px;background:#f2ffff}.license.show{display:block}.license small{display:block;color:var(--muted);font-weight:700;margin-bottom:7px}.license code{display:block;font-size:22px;font-weight:900;letter-spacing:.06em;word-break:break-all;color:var(--navy)}.copy{margin-top:10px;border:1px solid var(--line);background:#fff;color:var(--navy);padding:9px 12px;border-radius:9px;font-weight:800;cursor:pointer}', 'license styles')
    text = replace_once(text, '    <div class="status" id="status" role="status">Verifying payment</div>\n    <a class="btn" id="download" href="#">Download Initial Version DOCX + PDF Package</a>', '    <div class="status" id="status" role="status">Verifying payment</div>\n    <div class="license" id="license"><small>Your 30-Day Access Code</small><code id="accessCode"></code><button class="copy" id="copyCode" type="button">Copy access code</button></div>\n    <a class="btn" id="download" href="#">Download Initial Version DOCX + PDF Package</a>', 'license markup')
    text = replace_once(text, "const API=MYCPCommerce.API,status=document.getElementById('status'),title=document.getElementById('title'),message=document.getElementById('message'),download=document.getElementById('download');", "const API=MYCPCommerce.API,status=document.getElementById('status'),title=document.getElementById('title'),message=document.getElementById('message'),download=document.getElementById('download'),license=document.getElementById('license'),accessCode=document.getElementById('accessCode'),copyCode=document.getElementById('copyCode');", 'checkout return element refs')
    old = """if(result.package==='all_access'){
        title.textContent=\"Your 30-Day All Access is active\";
        const expiry=result.accessExpiresAt?new Date(result.accessExpiresAt).toLocaleDateString(undefined,{year:'numeric',month:'long',day:'numeric'}):'30 days from activation';
        message.textContent=`Payment confirmed. Your clinic can submit eligible protocol requests through ${expiry}.`;
        status.textContent=`Order ${reference} - All Access active`;
        download.textContent=\"Submit a Protocol Request\";download.href=result.requestUrl||`all-access-request.html?ref=${encodeURIComponent(reference)}`;download.classList.add('show');
        const details=document.querySelector('.details');if(details)details.innerHTML='<strong>30-DAY ALL ACCESS</strong><br>Submit as many eligible Customized Protocol or Complete Treatment Package requests as your clinic needs during the active 30-day period. This pass is for one clinic/legal practice, is non-transferable, and does not auto-renew. Specialty or investigational requests may require scope review. Final clinical approval remains with your clinic’s appropriately qualified medical director or supervising provider.';
      }"""
    new = """if(result.package==='all_access'){
        title.textContent=\"Your 30-Day All Access is active\";
        const expiry=result.accessExpiresAt?new Date(result.accessExpiresAt).toLocaleDateString(undefined,{year:'numeric',month:'long',day:'numeric'}):'30 days from activation';
        message.textContent=`Payment confirmed. Your clinic can submit eligible protocol requests through ${expiry}. Save the access code below - it is your 30-day license.`;
        status.textContent=`Order ${reference} - All Access active`;
        if(result.accessCode){accessCode.textContent=result.accessCode;license.classList.add('show');try{localStorage.setItem('mycp_all_access_pass',JSON.stringify({accessCode:result.accessCode,customerEmail:pending?.customerEmail||'',accessExpiresAt:result.accessExpiresAt}))}catch(e){}}
        copyCode.onclick=async()=>{try{await navigator.clipboard.writeText(accessCode.textContent);copyCode.textContent='Copied'}catch(e){copyCode.textContent='Select and copy the code'}};
        download.textContent=\"Open All Access Request Portal\";download.href=result.requestUrl||'all-access-request.html';download.classList.add('show');
        const details=document.querySelector('.details');if(details)details.innerHTML='<strong>30-DAY ALL ACCESS LICENSE</strong><br>Your access code is valid for one clinic/legal practice for 30 days from verified payment. Use the same code and purchasing email whenever you submit a request. It is non-transferable and does not auto-renew. Specialty or investigational requests may require scope review. Final clinical approval remains with your clinic’s appropriately qualified medical director or supervising provider.';
      }"""
    text = replace_once(text, old, new, 'all access confirmation logic')
    return text


def commerce_transform(text: str) -> str:
    text = text.replace("const VERSION = '2026-10-10';", "const VERSION = '2026-10-10-2';")
    return text


def support_transform(text: str) -> str:
    text = text.replace("protocol:{label:'Customized Protocol',prices:{1:29,3:87,5:145,10:290}}", "protocol:{label:'Customized Protocol',prices:{1:29,2:58,3:87,4:116,5:145,6:174,7:203,8:232},max:8}")
    text = text.replace("complete:{label:'Complete Treatment Package',prices:{1:49,3:147,5:245,10:490}}", "complete:{label:'Complete Treatment Package',prices:{1:49,2:98,3:147,4:196,5:245},max:5}")
    text = text.replace('Customized Protocol - 1 treatment $29, 3 treatments $87, 5 treatments $145, or 10 treatments $290.', 'Customized Protocol - $29 per treatment, up to 8 treatments per order. For 9 or more, 30-Day All Access at $249 is recommended.')
    text = text.replace('Complete Treatment Package - 1 treatment $49, 3 treatments $147, 5 treatments $245, or 10 treatments $490.', 'Complete Treatment Package - $49 per treatment, up to 5 treatments per order. For 6 or more, 30-Day All Access at $249 is recommended.')
    return text


patch('order.html', order_transform)
patch('index.html', index_transform)
patch('all-access.html', all_access_transform)
patch('all-access-request.html', request_transform)
patch('checkout-return.html', checkout_return_transform)
patch('assets/mycp-commerce.js', commerce_transform)
patch('assets/mycp-search-support.js', support_transform)
