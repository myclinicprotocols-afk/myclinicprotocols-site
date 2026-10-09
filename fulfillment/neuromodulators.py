"""Production neuromodulator master content used by the fulfillment service.

Customer output receives only the selected clinic's applicable state language.
The internal 50-state matrix, source notes, and generator controls are not
included in customer packages.
"""

from __future__ import annotations


STATE_RULES = {
    "Alabama": ("RESTRICTED / PROHIBITED", "CRNP only when Board-approved specialty protocol and collaborative-practice requirements are satisfied; physician may inject. RN cosmetic injection is not supported by the reviewed Board guidance.", "Board-approved CRNP specialty protocol/application; physician collaboration, training, and competency documentation are required."),
    "Alaska": ("VERIFIED", "RN/LPN may administer when trained and competent and acting on a patient-specific treatment plan; no independent diagnosis or prescribing.", "Initial provider assessment/order is required; changes in the treatment plan require additional provider evaluation."),
    "Arizona": ("VERIFIED", "RN/LPN may perform within individual scope after a valid order and required assessment; APRN only within role/population focus and competency.", "Documented good-faith examination before the first procedure, provider supervision/availability, and competence are required."),
    "Arkansas": ("MANUAL REVIEW", "Automatic RN/LPN injector authorization is not released from general medication-administration authority alone.", "MyClinicProtocols must complete a current Arkansas nursing, medical-practice, prescriber/delegation, and ownership review before the state-specific authorization section is finalized."),
    "California": ("VERIFIED", "RN or PA may inject under physician supervision/direction; LVN/MA injection is not supported by the reviewed guidance.", "Appropriate prior physician examination, standardized procedures, supervising-physician availability, and physician-controlled medical-practice requirements must be satisfied."),
    "Colorado": ("MANUAL REVIEW", "RN injection is not auto-authorized from general nursing scope alone.", "Current Colorado delegation, prescriber examination/order, supervision, and entity rules require manual compliance review before final state-specific release."),
    "Connecticut": ("VERIFIED", "RN/APRN pathway is conditional; LPN injection is not supported by the reviewed Board decision.", "Training, ongoing competency, consultation/supervision resources, and appropriate patient assessment are required."),
    "Delaware": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Manual Board/statute review is required before final state-specific release."),
    "Florida": ("MANUAL REVIEW", "APRN/physician prescribing must comply with Florida law; the RN injector pathway remains manual until confirmed for the clinic structure.", "Verify prescriber authority, patient-specific order/evaluation, RN scope, physician delegation, and clinic ownership before final state-specific release."),
    "Georgia": ("VERIFIED", "RN injection is conditional; LPN injection is not supported by the reviewed guidance.", "Individualized order plus prescriber history/physical, competency, onsite policies, and emergency procedures are required."),
    "Hawaii": ("MANUAL REVIEW", "A potential RN pathway exists, but it is not auto-released without current confirmation.", "Supervising physician/order/delegation and the current Board position require manual confirmation before final state-specific release."),
    "Idaho": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current Idaho nursing practice, medical delegation, prescriber, and ownership requirements require manual review before final state-specific release."),
    "Illinois": ("VERIFIED", "Use only licensed clinicians whose professional act permits the delegated/administered service; estheticians/cosmetologists may not inject.", "Prescriber/physician governance, license-specific scope, infection-control, and professional-entity requirements must be applied."),
    "Indiana": ("MANUAL REVIEW", "Automatic state release is not used for injector authorization.", "Current legal/Board review is required before any state-specific injector authorization language is finalized."),
    "Iowa": ("VERIFIED", "Delegation is conditional to qualified licensed/certified personnel within individual scope.", "Medical-director evaluation, delegation/supervision, and med-spa compliance requirements must be satisfied."),
    "Kansas": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current Kansas nursing practice, Healing Arts delegation, prescriber order, and entity requirements require manual review before final state-specific release."),
    "Kentucky": ("VERIFIED", "RN and LPN pathways are conditional; APRN practice depends on APRN scope/population.", "Prescription and provider good-faith examination are required; RN/LPN may not independently prescribe, order, or determine treatment."),
    "Louisiana": ("VERIFIED", "RN may inject botulinum toxin conditionally under the reviewed Board statement; this authorization does not extend beyond the applicable neuromodulator pathway.", "Qualified-prescriber order, training/competency, practice-setting, and emergency standards are required."),
    "Maine": ("VERIFIED", "Neuromodulator performance must remain within the clinician's existing legal scope; med-spa practice does not expand professional scope.", "Apply Maine nursing/medical scope, prescribing, telehealth, and business standards, including applicable clinic requirements."),
    "Maryland": ("VERIFIED", "RN injection is conditional; LPN has category limitations; a nurse may not diagnose, prescribe, or independently develop the treatment plan.", "Patient-specific order, prescriber assessment, required prescriber availability, and annual competency requirements must be satisfied."),
    "Massachusetts": ("VERIFIED", "RN/LPN may perform ordered cosmetic/dermatologic procedures when educated and competent; non-APRN RN/LPN may not diagnose, prescribe, or independently select medication/dose.", "Documented assessment and patient-specific prescriber order must identify the patient, medication/substance, dose, route, anatomical site, directions, and signature; clinic policies must address consent, evaluation, self-care, follow-up, referral, side-effect management, and emergent care."),
    "Michigan": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current Michigan Public Health Code, medical delegation, prescriber order, and entity requirements require manual review before final state-specific release."),
    "Minnesota": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current Minnesota nursing practice, prescriber/delegation, and entity requirements require manual review before final state-specific release."),
    "Mississippi": ("RESTRICTED / PROHIBITED", "RN/LPN: do not inject botulinum toxin under the reviewed Board FAQ. APRN may perform within APRN scope and documented training/competency.", "The package must not authorize RN/LPN injection; APRN/physician pathway and clinic-specific authority must be confirmed."),
    "Missouri": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current nursing-practice, prescriber-order/delegation, supervision, and business requirements require manual review before final state-specific release."),
    "Montana": ("VERIFIED", "RN/LPN may perform conditionally; APRN may perform within scope.", "A prescribed medical treatment plan, training/education, supervision, and no independent RN/LPN diagnosis or prescribing are required."),
    "Nebraska": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current Nebraska nursing and medicine scope/delegation requirements require manual review before final state-specific release."),
    "Nevada": ("RESTRICTED / PROHIBITED", "The package must not issue an RN/LPN injector authorization from the nursing pathway without additional Nevada-specific licensed-provider analysis.", "Use the current Nevada aesthetic-practice decision and route the clinic to manual clinician-type review before state-specific authorization is finalized."),
    "New Hampshire": ("MANUAL REVIEW", "A potential RN pathway requires current Board of Medicine/delegation confirmation.", "Ordering provider, APRN/physician presence or availability, and delegation requirements require manual confirmation before final state-specific release."),
    "New Jersey": ("MANUAL REVIEW", "The package is not auto-released solely from older Board minutes or general scope language.", "Current nursing-practice, medical-board/delegation, and prescriber-evaluation requirements require manual review before final state-specific release."),
    "New Mexico": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized from certification alone.", "Current nursing/medical scope, prescriber order, and business requirements require manual review before final state-specific release."),
    "New York": ("VERIFIED", "RN/LPN may administer within nursing scope on an appropriate patient-specific order; NP/physician may prescribe within scope.", "Patient-specific prescriber order/evaluation is required; a nurse may not independently diagnose or determine treatment."),
    "North Carolina": ("VERIFIED", "RN injection is conditional; LPN injection is conditional with onsite supervision. Both require an order from a physician, NP, PA, or other legally authorized prescriber.", "Prescriber evaluation/assessment and order, documented education/competency, agency policies, and emergency procedures are required; LPN onsite-supervision requirements must be followed."),
    "North Dakota": ("VERIFIED", "RN injection is conditional; no independent diagnosis or prescribing.", "Documented initial prescriber evaluation, treatment plan, specialized education/competency, and prescriber reassessment for treatment-plan changes are required."),
    "Ohio": ("MANUAL REVIEW", "RN injection is not auto-authorized from general scope language alone.", "Patient-specific order, medical delegation, and supervisory requirements require manual confirmation before final state-specific release."),
    "Oklahoma": ("VERIFIED", "RN/LPN pathways are conditional; APRN practice remains subject to scope and prescribing rules.", "Valid individualized order, provider-patient relationship/evaluation, education/competency, policies, and emergency readiness are required."),
    "Oregon": ("VERIFIED", "Performance is conditional on individual scope and documented competence.", "A licensed-independent-practitioner-authored plan/order is required; nurse individual-scope determination, LPN clinical direction/supervision, and no independent diagnosis/prescribing must be observed."),
    "Pennsylvania": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current Nursing Board/Medical Board scope, prescription, delegation, and entity requirements require manual review before final state-specific release."),
    "Rhode Island": ("VERIFIED", "A conditional licensed-delegate pathway applies; the prescriber/supervisor must meet applicable Medical Spas Safety Act requirements.", "Medical-director, delegation, training, facility, and supervision requirements must be applied."),
    "South Carolina": ("VERIFIED", "RN injection is conditional under the current joint advisory and applicable Board guidance.", "Provider initial assessment, competency, facility policies, and procedure-specific supervision/availability requirements must be satisfied."),
    "South Dakota": ("VERIFIED", "RN/LPN pathways are conditional.", "Medical plan/order, education, agency approval, and qualified-provider supervision are required."),
    "Tennessee": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current Tennessee nursing/medical practice, medication-order, and supervision requirements require manual review before final state-specific release."),
    "Texas": ("VERIFIED", "RN pathway is conditional; LVN pathway is conditional and directed; APRN practice remains subject to physician delegation/prescriptive-authority rules.", "Patient-specific appropriate order, scope decision model, medical supervision, and Texas nonsurgical-cosmetic delegation requirements must be satisfied."),
    "Utah": ("VERIFIED", "RN practice is conditional under the statutory supervisor/delegation framework; APRN may be a qualifying supervisor where law permits.", "In-person evaluation/treatment plan or permitted delegated evaluation, supervisor authorization, training/competence, and the correct supervision level are required."),
    "Vermont": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current Vermont scope/delegation and Board/medical-practice requirements require manual review before final state-specific release."),
    "Virginia": ("MANUAL REVIEW", "Nursing authority is not inferred from rules governing other professions.", "Current Virginia Board of Nursing/Medicine scope, order, and delegation requirements require manual review before final state-specific release."),
    "Washington": ("VERIFIED", "RN/LPN/PA may be delegated within lawful scope and documented training.", "Physician preprocedure evaluation and ultimate responsibility, training, documentation, and current onsite/availability requirements must be followed."),
    "West Virginia": ("VERIFIED", "RN pathway is conditional; APRN pathway is conditional within advanced-practice scope.", "FDA-approved products, prescriber order, education/competency, and qualified supervision are required."),
    "Wisconsin": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current Wisconsin nursing practice, medical delegation, prescriber, and entity requirements require manual review before final state-specific release."),
    "Wyoming": ("MANUAL REVIEW", "RN authority is not inferred from rules governing other professions.", "Current Wyoming nursing/medical practice and delegation requirements require manual review before final state-specific release."),
    "District of Columbia": ("MANUAL REVIEW", "RN/LPN injection is not auto-authorized.", "Current DC nursing scope, medical delegation, prescriber-order, and facility/business requirements require manual review before final state-specific release."),
}


def state_language(state: str) -> str:
    status, scope, controls = STATE_RULES.get(
        state,
        ("MANUAL REVIEW", "No automated state-specific injector authorization is issued for this jurisdiction.", "A current state compliance review is required before final state-specific authorization is released."),
    )
    if status == "VERIFIED":
        intro = "MyClinicProtocols state-specific verification status: VERIFIED for rules-based population, subject to RN quality review and clinic approval."
    elif status == "RESTRICTED / PROHIBITED":
        intro = "MyClinicProtocols state-specific verification status: RESTRICTED / PROHIBITED pathway. The identified restriction must be followed."
    else:
        intro = "MyClinicProtocols state-specific verification status: MANUAL REVIEW. The clinical initial version may be prepared, but state-specific authorization must be finalized during compliance/RN review before clinical implementation."
    return f"{intro} {scope} {controls}"


MASTER_PROTOCOL = r'''CLINICAL MASTER TEMPLATE
Neuromodulator Clinical Protocol and SOP
Botulinum toxin type A • Cosmetic use • Product-specific dosing • State-specific release
1. Purpose and scope
This master protocol establishes a standardized workflow for cosmetic botulinum toxin type A treatment. It is designed for clinic customization and final approval by the clinic’s qualified medical director or supervising prescriber. It does not substitute for product prescribing information, hands-on injection training, individual clinical judgment, or state scope-of-practice requirements.
The template can support BOTOX Cosmetic (onabotulinumtoxinA), Dysport (abobotulinumtoxinA), XEOMIN (incobotulinumtoxinA), Jeuveau (prabotulinumtoxinA-xvfs), DAXXIFY (daxibotulinumtoxinA-lanm), LETYBO (letibotulinumtoxinA-wlbg), or another legally marketed product selected by the clinic. Only products specifically authorized by the clinic may be used.
2. Critical product rule: units are not interchangeable
Potency units are product-specific. Do not convert, equate, or substitute units across botulinum toxin products. Reconstitution, concentration, dose, approved indications, storage, and administration technique must follow the current U.S. prescribing information (PI) for the exact product and the clinic’s approved order set.
3. State-specific authorization
Before release to a clinic, the package inserts only the rules relevant to the clinic’s state. The final package must identify who may prescribe, who may inject, whether an examination or prescriber order is required before treatment, required supervision/delegation, documentation requirements, and any facility or ownership restrictions that materially affect this service.
State-specific clinic summary: [[STATE_SPECIFIC_NEUROMODULATOR_REQUIREMENTS]]
4. Qualifications and competency
Active license/credential that authorizes the activity in the clinic’s jurisdiction and under the clinic’s approved delegation/supervision structure.
Documented neuromodulator education plus hands-on competency in facial anatomy, product preparation, injection technique, complication recognition, emergency response, and patient counseling.
Current training in Standard Precautions, bloodborne-pathogen/sharps safety, medication storage, documentation, photography/privacy, and adverse-event reporting.
Competency revalidation after a material change in product, labeling, technique, law, or clinic policy, and at the interval defined by the medical director.
5. Patient assessment and eligibility
A qualified prescriber or other clinician authorized by state law performs or reviews the required evaluation before treatment. The assessment must be sufficient to establish medical appropriateness, identify product-specific precautions, and define a treatment plan.
Do not treat until resolved or specifically cleared
Known hypersensitivity to the selected botulinum toxin preparation or any component in that formulation.
Infection, open wound, significant inflammation, or other condition at a proposed injection site.
New or unstable dysphagia, dyspnea, significant neuromuscular weakness, or a condition that may increase susceptibility to systemic toxin effects.
Clinically significant medication interaction risk, including agents that interfere with neuromuscular transmission or muscle relaxants, unless reviewed by the prescriber.
Unresolved prior adverse reaction to botulinum toxin or recent treatment with another botulinum toxin product without review of product, date, dose, and cumulative exposure.
Anatomy substantially altered by recent facial/neck surgery, trauma, disease, or procedure when the injector has not completed an appropriate reassessment.
Any condition that makes elective cosmetic treatment inappropriate under the current product label, medical-director policy, or individualized risk-benefit assessment.
Pregnancy and lactation
Because cosmetic treatment is elective and product labels contain limited human pregnancy/lactation data, the clinic must follow its medical-director policy and current PI. The final intake and consent should not inaccurately label pregnancy or breastfeeding as a universal FDA contraindication unless the selected product’s current label states that.
Assessment elements
Patient goals, treatment history, prior product(s), response, complications, and date of last botulinum toxin treatment.
Medical history including neuromuscular disease, dysphagia/dyspnea, facial weakness, ocular surface disease, prior surgery, Bell palsy/facial nerve history, and relevant cardiovascular/neurologic conditions.
Medications/supplements with attention to aminoglycosides or other neuromuscular transmission modifiers, muscle relaxants, anticholinergics, anticoagulants/antiplatelets, and recent antibiotics.
Baseline dynamic and resting examination: brow position, eyelid position, asymmetry, frontalis recruitment, corrugator/procerus activity, orbicularis activity, smile pattern, lower-face balance, masseter function if considered, and platysma bands if considered.
Baseline photographs using standardized views and expressions with consent.
6. Approved vs. off-label treatment areas
Cosmetic indications differ by product and may change. The clinic’s final version must identify which requested areas are FDA-approved for the selected product and which are off-label. Off-label treatment requires prescriber authorization, appropriate informed consent, injector competency, and compliance with state law and clinic policy.
7. Required equipment and supplies
Clinic-authorized, lawfully obtained botulinum toxin product in original packaging; current PI and medication guide/patient counseling information available.
Product-specific sterile diluent and reconstitution supplies exactly as required by the PI; sterile syringes and appropriately sized needles.
Labels for product name, lot, expiration, concentration, reconstitution date/time, beyond-use time/date per PI, and preparer initials.
Alcohol or clinic-approved skin antiseptic; gauze/cotton; gloves and other PPE based on anticipated exposure; sharps container.
Standardized photography setup and treatment record/injection map.
Emergency equipment and medications appropriate to the clinic’s services and medical-director emergency plan; emergency contact pathway immediately available.
8. Product receipt, storage and preparation
Verify product name, strength, intact packaging/tamper features, lot, expiration, and storage conditions on receipt and before use.
Store unopened product exactly as required by the current PI. Do not use a vial that was improperly stored, compromised, expired, or of uncertain provenance.
Before reconstitution, perform hand hygiene, prepare a clean medication area, and verify the product-specific diluent and volume.
Reconstitute using aseptic technique and only the product-specific instructions. Do not use a dilution or concentration simply because it is customary for another toxin.
Label immediately with product, final concentration, date/time, preparer, lot/expiration, and the PI-based deadline for use/storage.
Discard residual medication and single-dose vial contents according to the PI, law, and clinic policy. Do not pool residual drug from single-dose vials.
9. Standard treatment workflow
1 Confirm patient and authorization
Use two identifiers. Confirm the required evaluation/order is complete, consent is signed, the selected product is authorized, and the injector is permitted to perform the service under the clinic’s state-specific structure.
2 Review interval and cumulative exposure
Document the date, product and estimated dose of prior toxin treatment, including treatments performed elsewhere when known. Review recent or planned toxin use for other indications.
3 Perform dynamic anatomy assessment
Examine the patient at rest and during purposeful animation. Identify asymmetry, compensatory muscle recruitment, brow/eyelid position, smile mechanics, lower-face function and prior surgical changes. The plan is individualized; do not inject from a static template alone.
4 Photograph and map
Capture standardized baseline images and mark planned regions. Use patient-right/patient-left language. If treating an off-label area, confirm the consent specifically reflects that use.
5 Conduct the final time-out
State patient, product, concentration, lot/expiration, target areas, planned total units, allergies/precautions, and emergency contact pathway. Confirm the plan matches the prescriber order and product PI.
6 Position and prepare
Position the patient to allow accurate assessment and safe access. Clean the skin with the clinic-approved antiseptic and allow it to dry. Keep hair, cosmetics and nonsterile items clear of the injection field.
7 Draw up product
Use aseptic technique. Draw only the amount needed for the planned treatment. Reconfirm concentration before calculating volume. Never convert units between brands.
8 Treat one anatomical region at a time
Use the product-specific PI and medical-director-approved technique for depth, location, dose and safety margins. Maintain awareness of nearby structures and avoid injecting through infected or compromised skin.
9 Reassess throughout
Monitor pain, vasovagal symptoms, unexpected weakness, visual symptoms, dysphagia/dyspnea, allergic symptoms, and patient distress. Stop when findings are inconsistent with an expected cosmetic injection response.
10 Reconcile delivered dose
Before discharge, total the units and volume administered by area and confirm the amount does not exceed the authorized treatment plan or applicable PI maximum.
11 Provide aftercare and emergency instructions
Review expected local effects, follow-up timing, and red-flag symptoms. Give the clinic’s emergency contact information and instruct the patient to seek urgent/emergency care for swallowing, speech, breathing, or generalized weakness symptoms.
12 Complete documentation
Record product, lot, expiration, dilution/concentration, amount administered per site/area, exact injection map, patient tolerance, photos, adverse events, instructions and follow-up plan. Sign with performer credentials and required supervising/prescriber review.
10. Treatment-area locator
Locator only - not a universal injection-point, depth, or dosing diagram. Use current product PI, individualized anatomy and documented injector competency.
11. Stop criteria and emergency escalation
Stop the procedure for patient request, syncope/presyncope, unexpected severe pain, acute neurologic or visual symptoms, suspected hypersensitivity, respiratory symptoms, swallowing/speech difficulty, or any event the injector cannot immediately explain and manage.
Activate emergency medical services for airway/breathing/circulation compromise, anaphylaxis, significant neurologic deficit, or other life-threatening findings.
Botulinum toxin effects can spread beyond the injection site. Patients must be counseled that generalized weakness, diplopia/ptosis, dysphagia, dysphonia/dysarthria, or breathing difficulty can occur hours to weeks after injection and require urgent assessment.
Notify the medical director/supervising prescriber according to clinic policy. Complete incident/adverse-event documentation and FDA MedWatch/manufacturer reporting when appropriate.
12. Common adverse effects and targeted follow-up
Localized pain, erythema, edema, ecchymosis: assess severity; supportive measures consistent with patient history and clinic policy; document.
Headache/transient flu-like symptoms: assess for red flags; provide clinician-approved supportive advice; document.
Asymmetry/under-response: do not reflexively re-treat early; reassess after the expected effect has stabilized.
Brow/eyelid ptosis: document onset, exam and photos; notify prescriber/medical director; evaluate ocular symptoms; prescription treatment requires an individualized prescriber order.
Smile/lower-face dysfunction: assess functional impact including speech/eating; notify prescriber; avoid additional toxin that could worsen weakness.
Dysphagia, dysphonia, generalized weakness, dyspnea: urgent/emergency evaluation based on severity; consider distant spread of toxin effect.
Hypersensitivity/anaphylaxis: follow emergency protocol; activate emergency services when indicated; document/report.
13. Follow-up
Clinic-defined check-in and formal outcome assessment based on the selected product and treated area; many aesthetic practices assess peak effect around 2 weeks, but the protocol should not override the PI or individualized plan.
Repeat standardized photographs and dynamic examination when clinically useful.
Document patient-reported satisfaction, residual movement, asymmetry, adverse effects and any plan for future cycles.
Any touch-up or correction is a new clinical decision requiring documentation of rationale, product, units, sites and cumulative exposure.
14. Documentation requirements
Evaluation/order and state-required prescriber involvement; consent; baseline exam and photographs.
Product name, generic name when useful, lot, expiration, vial strength, diluent, concentration, reconstitution date/time, and preparer.
Units and volume administered by anatomical region/site, injection map, needle/syringe as required by policy, and total units.
Off-label areas identified as such in the clinical record and consent when applicable.
Tolerance, immediate findings, aftercare, emergency instructions, follow-up plan, and any adverse event/escalation.
Injector signature/credentials and medical director/supervising prescriber review or availability when required.
15. References and release controls
BOTOX Cosmetic (onabotulinumtoxinA) U.S. Prescribing Information, revised 10/2024; current DailyMed/FDA label must be checked at release.
XEOMIN (incobotulinumtoxinA) U.S. Prescribing Information, revised 06/2026; current DailyMed/FDA label must be checked at release.
DAXXIFY (daxibotulinumtoxinA-lanm) U.S. Prescribing Information, updated 01/2026; current DailyMed/FDA label must be checked at release.
FDA Drug Trials Snapshot: LETYBO (letibotulinumtoxinA-wlbg), approval 02/29/2024.
Current U.S. prescribing information for every toxin brand selected by the clinic, plus current state professional-practice rules and clinic medical-director policy.
Release note: MyClinicProtocols prepares and quality-checks this package for completeness, consistency and professional presentation. Final clinical approval remains with the purchasing clinic’s qualified medical director or supervising provider.
Clinic authorization field
Clinic: [[CLINIC_NAME]]
State: [[STATE]]
Medical director / supervising prescriber: [[MEDICAL_DIRECTOR_NAME, CREDENTIALS]]
Authorized injector credentials: [[AUTHORIZED_CREDENTIALS]]
Authorized products: [[AUTHORIZED_PRODUCTS]]
Effective / review date: [[EFFECTIVE_DATE]] / [[REVIEW_DATE]]
'''


PATIENT_CONSENT = r'''CLINICAL MASTER TEMPLATE
Neuromodulator Treatment
Patient Informed Consent
Botulinum toxin type A • Cosmetic treatment
Clinic: [[CLINIC_NAME]]    State: [[STATE]]    Emergency contact: [[EMERGENCY_PHONE]]
Treatment being considered
I am requesting cosmetic treatment with a botulinum toxin type A product selected by my treating clinician. I understand the specific brand, treatment areas and planned dose will be documented in my treatment record. Different toxin products are not interchangeable and their units cannot be directly converted from one brand to another.
How the treatment works
Botulinum toxin temporarily reduces muscle activity at the injected sites. Cosmetic results are temporary and vary by product, area, anatomy, dose and individual response. More than one treatment cycle may be needed to maintain a result.
Potential benefits
Temporary softening of dynamic lines or muscle-related cosmetic concerns in the planned treatment area.
Improved facial balance or contour when clinically appropriate.
No guarantee has been made regarding the degree, duration or symmetry of response.
Common and expected effects
Brief discomfort, redness, swelling, tenderness or small bumps at injection sites.
Bruising or headache.
Temporary asymmetry or incomplete response.
Temporary change in facial expression, muscle strength or movement in or near the treated area.
Important risks
Eyelid or brow droop, dry eye, tearing, blurred/double vision or other local muscle weakness depending on the treated area.
Unwanted smile, lip, chewing or neck changes when lower-face, masseter or platysma areas are treated.
Allergic/hypersensitivity reaction; severe reactions are uncommon but can require emergency treatment.
Rare but serious spread of toxin effect beyond the injection area, which can cause generalized muscle weakness, double vision, drooping eyelids, difficulty speaking, swallowing or breathing. These symptoms can occur hours to weeks after treatment and can be life-threatening.
Unexpected or prolonged weakness, infection, pain, or another complication not specifically listed.
Pregnancy, breastfeeding and medical conditions
I have disclosed whether I am pregnant, planning pregnancy, breastfeeding, have a neuromuscular condition, swallowing/breathing problems, facial weakness, prior facial/neck surgery, or other condition that may affect treatment. Because this is an elective cosmetic service, the clinic may defer treatment based on the selected product’s current prescribing information and medical-director policy.
Medications and prior toxin treatment
I have disclosed prescription drugs, over-the-counter drugs and supplements, especially muscle relaxants, aminoglycoside antibiotics or other drugs that affect neuromuscular transmission, anticoagulants/antiplatelets, and all botulinum toxin treatments I have received recently, including product and date when known.
Approved and off-label use
FDA-approved cosmetic indications differ by product. My clinician has explained whether each planned area is within the selected product’s current FDA-approved cosmetic indication or is an off-label use. Off-label use means the product is legally prescribed for a use not specifically listed in that product’s FDA-approved labeling.
Alternatives
Alternatives may include no treatment, skin care, energy-based procedures, fillers/biostimulatory treatments, surgery, or another treatment depending on my concern. These alternatives have different risks and benefits.
Aftercare and follow-up
I will follow the clinic’s current aftercare instructions and contact the clinic for unexpected effects. I understand that urgent symptoms such as trouble breathing or swallowing, severe generalized weakness, or a serious allergic reaction require emergency medical evaluation rather than waiting for a routine clinic reply.
Photography and privacy
[ ] I consent to clinical photographs for my medical record.
[ ] I separately authorize use of de-identified or identifiable images for education/marketing only if I sign the clinic’s separate photo/media authorization.
Acknowledgment
[ ] I have had the opportunity to ask questions and received understandable answers.
[ ] I understand results are not guaranteed and temporary.
[ ] I understand botulinum toxin products are not interchangeable.
[ ] I have disclosed my relevant history, medications, allergies and recent botulinum toxin treatments.
[ ] I understand the specific product, dose and injection sites will be documented in my treatment record.
[ ] I consent to the planned neuromodulator treatment.
Planned area / selected product / FDA-approved for this product? / patient initials
____________________________________________
____________________________________________
____________________________________________
____________________________________________
Patient signature: ______________________________    Printed name: __________________________    Date/time: ________________
Treating clinician: _____________________________    Credential: _____________________________    Date/time: ________________
Interpreter / witness if used: __________________    Relationship: __________________________
'''


INTAKE_ELIGIBILITY = r'''CLINICAL MASTER TEMPLATE
Neuromodulator Intake and Eligibility
Screening • Medical history • Facial assessment • Prescriber review
1. Treatment goals and history
[ ] Glabella / frown lines
[ ] Forehead lines
[ ] Crow’s feet
[ ] Neck / platysma bands
[ ] Bunny lines
[ ] Lip flip
[ ] Gummy smile
[ ] DAO / downturned corners
[ ] Chin / mentalis
[ ] Masseter / lower-face contour
[ ] Other: __________________________
Prior botulinum toxin treatment? [ ] No  [ ] Yes   Most recent date: __________  Product: __________  Approx. units: ______  Areas: ____________________
Prior adverse effect, asymmetry, ptosis, difficulty chewing/swallowing, allergic reaction, or poor response? ______________________________________________________________
2. Medical screening
[ ] Known allergy/hypersensitivity to a botulinum toxin product or ingredient
[ ] Current infection, rash, open wound, or significant inflammation at a proposed injection site
[ ] History of myasthenia gravis, Lambert-Eaton syndrome, motor neuron disease, ALS, or other neuromuscular disorder
[ ] Current or prior swallowing difficulty, aspiration, significant voice change, or breathing impairment
[ ] Facial nerve palsy, facial weakness, eyelid/brow ptosis, significant dry eye, or corneal problems
[ ] Recent facial/neck surgery, trauma, dental procedure, energy-based treatment, filler, thread lift, or other relevant procedure
[ ] Significant cardiovascular, neurologic, autoimmune, or systemic illness requiring clinician review
[ ] Bleeding disorder or easy bruising
[ ] Pregnant, trying to become pregnant, or breastfeeding
[ ] Other active condition or recent health change that may affect an elective cosmetic procedure
3. Medication and exposure review
[ ] Aminoglycoside antibiotic or other medication that may interfere with neuromuscular transmission
[ ] Muscle relaxant
[ ] Anticholinergic medication
[ ] Anticoagulant / antiplatelet medication
[ ] Recent botulinum toxin for migraine, spasticity, sweating, bladder, salivary gland, or another therapeutic indication
[ ] Recent vaccination, acute illness, or new medication relevant to clinical judgment
[ ] Other medication/supplement concern: ______________________________
4. Baseline facial and neck assessment
Brow position / asymmetry: _____________________________________________
Upper eyelid position / ptosis: _______________________________________
Frontalis recruitment / forehead height: ______________________________
Glabellar muscle strength / pattern: __________________________________
Lateral canthal animation: ____________________________________________
Smile / lip competence / oral commissure: _____________________________
Mentalis / lower-face pattern: ________________________________________
Masseter bulk / clenching if relevant: ________________________________
Platysma bands / neck function if relevant: ___________________________
Prior scars / altered anatomy: ________________________________________
5. Standardized photography
[ ] Neutral face  [ ] Maximum frown  [ ] Maximum brow elevation  [ ] Full smile
[ ] Squint / crow’s-feet animation  [ ] Lower-face/neck animation when relevant  [ ] Oblique views as indicated
6. Eligibility decision
[ ] Eligible as planned
[ ] Eligible with modified plan / precautions
[ ] Prescriber or medical-director review required before treatment
[ ] Defer - temporary contraindication / unresolved issue
[ ] Do not treat under current clinic protocol
Clinical rationale / required follow-up: __________________________________________________________________________________________
7. Product and treatment plan
Clinic/state: [[CLINIC_NAME]] / [[STATE]]
Selected product: [[PRODUCT]]
Indication / cosmetic goal: [[INDICATION]]
Planned areas: [[PLANNED_AREAS]]
Approved vs. off-label status reviewed: [ ] Yes
Planned total units / product-specific dose: [[DOSE_PLAN]]
Required supervision / prescriber involvement: [[STATE_SPECIFIC_REQUIREMENT]]
Follow-up interval: [[FOLLOW_UP_WINDOW]]
Clinician attestation: I reviewed the history, examination, current product information and clinic/state requirements and determined the documented plan is appropriate.
Signature/date: ____________________________________________
'''


TREATMENT_RECORD = r'''CLINICAL MASTER TEMPLATE
Neuromodulator Treatment Record
Product traceability • Dose reconciliation • Injection mapping • Outcome documentation
1. Pre-treatment verification
[ ] Required evaluation/order completed
[ ] Consent signed and off-label areas specifically reviewed
[ ] No material health/medication change since evaluation
[ ] Baseline photos obtained
[ ] Product-specific PI / clinic protocol available
[ ] Emergency pathway confirmed
2. Product preparation and traceability
Brand/generic: ____________________  Vial strength: __________  Lot: __________  Expiration: __________
Diluent/volume: __________________  Final concentration: __________________
Reconstituted date/time: __________  PI-based discard/use-by: __________  Prepared by: __________
3. Injection record by area
# / Anatomic area or muscle / Patient R-L / Units / Volume / Notes or exact site
1 ______________________________________________________________________
2 ______________________________________________________________________
3 ______________________________________________________________________
4 ______________________________________________________________________
5 ______________________________________________________________________
6 ______________________________________________________________________
7 ______________________________________________________________________
8 ______________________________________________________________________
9 ______________________________________________________________________
10 _____________________________________________________________________
11 _____________________________________________________________________
12 _____________________________________________________________________
Total units administered: __________     Total volume: __________     Unused product disposition: __________________________________________
4. Treatment-area locator / charting map
Use the map to localize treatment documentation. Mark actual injection points in the medical record or EHR. This is not a dosing guide.
Additional map notes: ____________________________________________________________________________________________________________
5. Immediate response
[ ] Tolerated as expected  [ ] Minor bleeding / bruising  [ ] Vasovagal symptoms  [ ] Unexpected pain
[ ] Visual or neurologic symptom  [ ] Hypersensitivity concern  [ ] Other: __________________________
Interventions / observations: _____________________________________________________________________________________________________
6. Discharge and follow-up
[ ] Aftercare reviewed / provided  [ ] Emergency red flags reviewed  [ ] Clinic contact information provided
[ ] Follow-up scheduled / recommended  [ ] Adverse event report initiated if applicable
Follow-up date/window: __________________  Outcome plan: _______________________________________________________________________________
Patient: __________________  DOB: __________  Date/time: __________  Injector/credential: __________________
Prescriber/supervisor if required: __________________  Clinic/state: [[CLINIC_NAME]] / [[STATE]]
Injector signature/date: ______________________________________________
Prescriber / medical-director review if required: __________________________
'''


PRE_POST_CARE = r'''CLINICAL MASTER TEMPLATE
Neuromodulator Pre- and Post-Treatment Care
Patient handout • Product-neutral • Clinic-customizable
Before your appointment
Tell the clinic about all recent botulinum toxin treatments, including cosmetic and therapeutic treatments, even if performed elsewhere.
Tell the clinician about new illness, infection, rash, medication changes, pregnancy/breastfeeding status, muscle weakness, swallowing/breathing problems, or a recent facial/neck procedure.
Do not stop prescribed anticoagulants, antiplatelets, antibiotics or other medicines solely for a cosmetic appointment unless the prescribing clinician tells you to do so.
Arrive with the treatment area clean when practical and follow any clinic-specific makeup, skin-care or photography instructions.
After treatment - what is usually expected
Small bumps, redness or tenderness at injection sites may occur briefly.
Bruising can occur.
Headache or temporary local muscle weakness can occur.
The onset and peak of effect depend on the product and area; your clinician will tell you when to assess your result.
Protect the treatment result
Follow the clinic’s product- and area-specific instructions. Avoid rubbing or manipulating injection sites unless your treating clinician specifically directs otherwise. Resume exercise, heat exposure, facials, massage, dental work and other activities according to the clinic’s current evidence-informed policy rather than a one-size-fits-all restriction.
Call the clinic promptly for
Unexpected or worsening eyelid/brow droop, significant asymmetry, eye irritation/vision symptoms, smile or chewing difficulty, or persistent pain/swelling.
A rash, hives, facial swelling or other suspected allergic reaction.
Any result or symptom that concerns you.
Seek urgent/emergency medical care for
Difficulty breathing, swallowing or speaking.
Generalized or spreading muscle weakness.
Severe allergic reaction, fainting that does not promptly resolve, or any other life-threatening symptom.
Clinic: [[CLINIC_NAME]]    Routine contact: [[CLINIC_PHONE]]    Emergency instructions: [[EMERGENCY_INSTRUCTIONS]]
'''


ROOM_SAFETY = r'''CLINICAL MASTER TEMPLATE
Neuromodulator Room Setup and Safety Checklist
Medication safety • Aseptic technique • Traceability • Emergency readiness
Opening / room readiness
[ ] Treatment area clean and uncluttered
[ ] Hand-hygiene supplies available
[ ] Sharps container within safe reach and below fill line
[ ] Emergency equipment/medications checked per clinic policy
[ ] Emergency contact / EMS activation process visible to staff
[ ] Camera / EHR / forms ready with privacy safeguards
Medication safety
[ ] Selected product is clinic-authorized and from lawful supply chain
[ ] Carton/vial tamper features intact
[ ] Correct product, strength, lot and expiration verified
[ ] Storage temperature / conditions within current PI requirements
[ ] Current PI available
[ ] Correct diluent verified
[ ] Clean medication-preparation area established
[ ] Final concentration independently rechecked when required by clinic policy
[ ] Vial/syringe labeled with product, concentration, date/time, preparer and use-by/discard time
Before patient enters / before injection
[ ] Correct patient / planned areas / product / order verified
[ ] Consent and required evaluation complete
[ ] Baseline photos obtained if indicated
[ ] Gloves/PPE available
[ ] Skin antiseptic, sterile syringes/needles and gauze ready
[ ] No recalled, expired, compromised or improperly stored product present
Emergency readiness check
[ ] Emergency medications/equipment within documented readiness interval
[ ] EMS activation pathway and clinic address available
[ ] Medical director / prescriber escalation contact current
[ ] Staff know location of emergency supplies and incident form
Closeout
[ ] Used sharps discarded immediately
[ ] Residual single-dose vial product handled per PI/policy
[ ] Lot/expiration/dose/site documentation complete
[ ] Room/equipment cleaned and disinfected
[ ] Adverse event / variance documented and escalated if needed
[ ] Medication inventory reconciled
Staff initials: __________   Date: __________
Variance / corrective action: ____________________________________________________________________________________________________
Product / strength: ______________________________
Storage requirement / current reading: ______________________________
Lot / expiration: ______________________________
Reconstitution / preparation time: ______________________________
PI-based use-by / discard time: ______________________________
'''


ADVERSE_EVENT_GUIDE = r'''CLINICAL MASTER TEMPLATE
Neuromodulator Adverse Event Quick Guide
Recognition • Triage • Escalation • Documentation
This guide supports rapid recognition and escalation. It does not replace emergency medical judgment, the clinic emergency plan, or product-specific prescribing information.
1. Emergency symptoms - activate emergency response
Difficulty breathing, airway swelling, cyanosis, severe wheeze, or anaphylaxis: activate EMS/emergency protocol immediately; maintain airway/breathing/circulation support within staff training; notify the medical director.
New significant dysphagia, inability to handle secretions, severe dysphonia, or generalized/progressive weakness: urgent/emergency evaluation; consider distant spread of toxin effect.
Acute neurologic deficit, severe visual symptom, or loss of consciousness not promptly resolving: emergency evaluation/EMS based on severity.
2. Same-day clinician / medical-director review
Suspected hypersensitivity without airway compromise: stop treatment; assess severity; follow clinic allergic-reaction pathway; escalate if progression.
Significant eyelid/brow ptosis, diplopia, or ocular surface symptoms: document exam/photos; notify prescriber; urgent ophthalmic evaluation when vision, corneal exposure, or neurologic findings warrant.
Marked smile, lip, chewing, or neck weakness: assess functional impact; notify prescriber; document treated sites/dose; provide safety counseling.
Persistent severe headache, unusual pain, or infection concern: evaluate for alternate diagnosis and treatment need.
3. Common non-emergency findings
Bruising/local tenderness/transient bumps: document as needed; supportive care per clinic policy; review worsening signs.
Mild headache: assess for red flags, medication contraindications, and alternate causes before giving advice.
Asymmetry/under-response: reassess after the expected effect has stabilized; avoid premature re-treatment.
4. Ptosis / functional change documentation
[ ] Onset date/time recorded
[ ] Product / concentration / units / sites verified
[ ] Baseline photos reviewed
[ ] Current photos obtained
[ ] Vision, ocular surface, swallowing, speech, chewing and breathing screened as relevant
[ ] Prescriber / medical director notified
[ ] Prescription medication, if considered, ordered individually by an authorized prescriber
[ ] Follow-up plan documented
5. Adverse-event documentation
Document patient identifiers and event date/time; detailed symptoms, onset, severity, objective findings/vitals when appropriate; product, lot, expiration, dilution/concentration, units/sites; interventions, response, referrals/EMS, follow-up, and medical-director notifications; manufacturer/FDA MedWatch reporting when indicated; and internal quality review/corrective actions when applicable.
6. Do not
Do not dismiss swallowing, speech, breathing, or generalized weakness symptoms as routine aftercare.
Do not give prescription treatment for a complication without a patient-specific prescriber order.
Do not re-treat asymmetry before appropriate clinical reassessment and stabilization of effect.
Do not obscure or alter the original treatment record; add a dated amendment when additional information becomes available.
Emergency number/process: [[EMERGENCY_INSTRUCTIONS]]    Medical director: [[MEDICAL_DIRECTOR_CONTACT]]
'''


TREATMENT_AUTHORIZATION = r'''CLINICAL MASTER TEMPLATE
Neuromodulator Treatment Authorization / Standing Order Template
Customize to state law, selected product(s), credentials and clinic workflow
1. Clinic and authority
Clinic legal name: [[CLINIC_NAME]]
State / practice location: [[STATE / ADDRESS]]
Medical director / authorizing prescriber: [[NAME, CREDENTIALS, LICENSE]]
Authorized injector roles: [[STATE-SPECIFIC AUTHORIZED ROLES]]
Effective / review dates: [[EFFECTIVE_DATE]] / [[REVIEW_DATE]]
2. Authorized service
The qualified personnel identified above are authorized to perform cosmetic botulinum toxin type A treatment only within their legal scope, documented competency, the patient-specific evaluation/order requirements applicable in this state, this clinic protocol, and the current prescribing information for the selected product.
3. Authorized products
Product-specific units are not interchangeable. No cross-brand conversion factor is authorized.
Authorized product(s): [[AUTHORIZED_PRODUCTS]]
4. Conditions of authorization
Required pre-treatment exam/evaluation and prescribing/order process completed as required by state law and clinic policy.
Patient-specific contraindications/precautions reviewed and consent obtained, including off-label use when applicable.
Injector has documented competency for the exact product and areas performed.
Only clinic-approved concentrations, dose limits, treatment areas and techniques are used.
Emergency response, adverse-event escalation, documentation and follow-up requirements in the complete package are followed.
The authorizing prescriber is available or present to the extent required by state law and the clinic’s supervision/delegation plan.
5. State-specific conditions
[[STATE_SPECIFIC_NEUROMODULATOR_REQUIREMENTS]]
6. Signature and approval
This standing-order template does not create authority that state law does not permit. Patient-specific orders/prescriptions remain required whenever applicable.
Medical director / authorizing prescriber signature: ____________________________________  Date: __________
Clinic representative / administrator: ______________________________________________  Date: __________
'''


DOCUMENTS = [
    ("01-neuromodulators-clinical-protocol-and-sop", "Neuromodulator Clinical Protocol and SOP", MASTER_PROTOCOL),
    ("02-neuromodulators-patient-consent", "Neuromodulator Patient Informed Consent", PATIENT_CONSENT),
    ("03-neuromodulators-intake-and-eligibility", "Neuromodulator Intake and Eligibility", INTAKE_ELIGIBILITY),
    ("04-neuromodulators-treatment-record", "Neuromodulator Treatment Record", TREATMENT_RECORD),
    ("05-neuromodulators-pre-and-post-care", "Neuromodulator Pre- and Post-Treatment Care", PRE_POST_CARE),
    ("06-neuromodulators-room-setup-and-safety-checklist", "Neuromodulator Room Setup and Safety Checklist", ROOM_SAFETY),
    ("07-neuromodulators-adverse-event-quick-guide", "Neuromodulator Adverse Event Quick Guide", ADVERSE_EVENT_GUIDE),
    ("09-neuromodulators-treatment-authorization", "Neuromodulator Treatment Authorization / Standing Order", TREATMENT_AUTHORIZATION),
]
