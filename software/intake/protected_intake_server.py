#!/usr/bin/env python3
"""Authenticated localhost UI for the PIA Phase 2B participant store.

artifact_id: component-pia-protected-intake-ui-001
authority: working
status: proposed
version: 0.5.0
lifecycle_state: formulation
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from software.intake.credential_intake_linkage import CredentialIntakeLinkage
from software.intake.capability_mapping_linkage import (
    ProtectedCapabilityMappingLinkage,
)
from software.intake.mapping_output_linkage import ProtectedMappingOutputLinkage
from software.intake.credential_lookup_router import CredentialLookupError
from software.intake.credential_registry_connector import (
    PRODUCTION_ENDPOINT,
    SANDBOX_ENDPOINT,
    CredentialEngineSearchConnector,
    CredentialRegistryError,
)
from software.intake.evidence_intake_linkage import (
    ProtectedEvidenceIntakeLinkage,
)
from software.intake.local_private_intake import (
    MAX_ARTIFACT_BYTES,
    IntakePreflightError,
    LocalIntakeError,
)
from software.intake.phase2b_security import (
    AuthSession,
    AuthSessionManager,
    LoginThrottle,
)
from software.intake.protected_participant_intake import (
    ProtectedParticipantIntakeStore,
)


LOCAL_HOST = "127.0.0.1"
AUTH_COOKIE = "PIA_PHASE2B_AUTH"
MAX_REQUEST_BYTES = (MAX_ARTIFACT_BYTES * 4 // 3) + (1024 * 1024)


def _shared_style() -> str:
    return """
    :root { color-scheme: light; --ink:#18323a; --muted:#60757b; --sage:#147a69;
      --deep:#07594c; --pale:#edf5f2; --line:#cadbd6; --paper:#fff;
      --warm:#f5f1e8; --danger:#9c3c32; }
    * { box-sizing:border-box; }
    body { margin:0; color:var(--ink); background:#f3f7f5;
      font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }
    main { width:min(1060px,calc(100% - 32px)); margin:34px auto 64px; }
    .eyebrow { color:var(--sage); font-size:.76rem; font-weight:800;
      letter-spacing:.13em; text-transform:uppercase; }
    h1 { max-width:820px; margin:10px 0 8px;
      font:700 clamp(2rem,5vw,3.45rem)/1.04 Georgia,serif; }
    h2 { margin:0 0 8px; font:700 1.48rem/1.15 Georgia,serif; }
    h3 { margin:0 0 6px; font:700 1.04rem/1.25 Georgia,serif; }
    p { color:var(--muted); line-height:1.55; }
    .bar { display:flex; justify-content:space-between; gap:16px; align-items:center; }
    .identity { color:var(--muted); font-size:.86rem; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
    .card,.notice { border:1px solid var(--line); border-radius:20px;
      background:var(--paper); padding:24px; }
    .card { margin-top:18px; }
    .notice { margin:18px 0; background:var(--pale); border-left:5px solid var(--sage); }
    .controls { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:15px; }
    .review-steps { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:6px;
      margin:20px 0 14px; padding:14px; border:1px solid var(--line);
      border-radius:15px; background:#fff; }
    .review-step { display:flex; gap:8px; align-items:center; min-width:0;
      color:var(--muted); font-size:.75rem; line-height:1.3; }
    .review-step b { display:grid; place-items:center; flex:0 0 28px; width:28px;
      height:28px; border-radius:50%; color:var(--deep); background:var(--pale); }
    .review-step.active { color:var(--ink); font-weight:800; }
    .review-step.active b { color:#fff; background:var(--sage); }
    .control { min-height:82px; padding:13px; border-radius:12px; background:white;
      border:1px solid var(--line); }
    .control strong { display:block; font-size:.86rem; margin-bottom:4px; }
    .control span { color:var(--muted); font-size:.78rem; line-height:1.35; }
    label { display:block; margin:15px 0 7px; font-size:.89rem; font-weight:750; }
    input,select,textarea { width:100%; border:1px solid #afc2bd; border-radius:11px;
      padding:12px 13px; color:var(--ink); background:#fff; font:inherit; }
    textarea { min-height:82px; resize:vertical; }
    button { margin-top:17px; border:0; border-radius:999px; padding:12px 19px;
      color:white; background:var(--sage); font:750 .94rem inherit; cursor:pointer; }
    button.secondary { color:var(--deep); background:var(--pale); border:1px solid var(--line); }
    button.danger { background:var(--danger); }
    button.text { margin:0; padding:8px 12px; color:var(--deep); background:transparent; }
    button:disabled { opacity:.45; cursor:not-allowed; }
    .check { display:flex; gap:10px; align-items:flex-start; padding:13px; margin-top:14px;
      border-radius:12px; background:var(--warm); }
    .check input { width:auto; margin-top:3px; }
    .check label { margin:0; }
    .status { margin-top:15px; padding:12px 14px; border-radius:11px;
      background:#f4f6f5; white-space:pre-wrap; overflow-wrap:anywhere; }
    .status.error { color:var(--danger); background:#fff1ef; }
    .hidden { display:none !important; }
    .quiet { color:var(--muted); font-size:.84rem; }
    .result { border-top:1px solid var(--line); margin-top:14px; padding-top:14px; }
    .resume-panel { margin-top:22px; padding-top:18px; border-top:1px solid var(--line); }
    .session-summary { margin-top:10px; padding:12px; border:1px solid var(--line);
      border-radius:12px; background:#fbfcfb; }
    .session-summary.current { border:2px solid var(--sage); background:var(--pale); }
    .session-heading { display:flex; flex-wrap:wrap; justify-content:space-between;
      align-items:center; gap:8px; }
    .session-badge { display:inline-block; padding:4px 8px; border-radius:999px;
      color:var(--deep); background:var(--pale); font-size:.7rem; font-weight:850;
      letter-spacing:.06em; text-transform:uppercase; }
    .session-badge.current { color:#fff; background:var(--deep); }
    .session-badge.empty { color:#6f5a3f; background:var(--warm); }
    .session-summary button { margin-top:9px; padding:8px 13px; font-size:.83rem; }
    details.empty-sessions { margin-top:14px; padding:12px; border-radius:12px;
      border:1px solid var(--line); background:#faf9f6; }
    details.empty-sessions summary { color:var(--deep); cursor:pointer; font-weight:800; }
    .candidate { margin-top:12px; padding:15px; border:1px solid var(--line);
      border-radius:13px; background:#fbfcfb; }
    .review-workbench { border-top:4px solid var(--sage); }
    .review-workbench #evidenceResults { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px; }
    .review-workbench #evidenceResults > .result { margin-top:0; padding:16px; border:1px solid var(--line); border-radius:14px; background:#fbfcfb; }
    .review-workbench details { margin-top:14px; }
    .review-workbench summary { cursor:pointer; color:var(--deep); font-weight:800; padding:10px 0; }
    .review-layout { display:grid; grid-template-columns:190px minmax(0,1fr) 280px; gap:16px; align-items:start; }
    .review-column { min-width:0; }
    .review-column h3 { color:var(--deep); }
    .review-selection { position:sticky; top:16px; padding:16px; border:1px solid var(--line); border-radius:14px; background:#fbfcfb; }
    .review-doc { padding:10px; margin-top:8px; border:1px solid var(--line); border-radius:10px; background:#fff; font-size:.82rem; }
    @media (max-width:850px) { .review-layout { grid-template-columns:1fr; } .review-selection { position:static; } }
    @media (max-width:760px) { .review-steps { grid-template-columns:repeat(3,1fr); }
      .review-step span { white-space:normal; } }
    .candidate p { margin:7px 0; color:var(--ink); }
    .actions { display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
    .actions button { margin:0; padding:8px 13px; font-size:.83rem; }
    .correction-editor { margin-top:12px; padding:14px; border-radius:12px;
      background:var(--warm); border:1px solid var(--line); }
    .correction-editor label { margin-top:0; }
    .review-guidance { margin-top:10px; color:var(--deep);
      font-size:.88rem; font-weight:700; line-height:1.45; }
    button.review-change { color:#fff; background:var(--deep);
      border:2px solid var(--deep); box-shadow:0 3px 9px rgba(7,89,76,.2); }
    button.review-change:hover { background:var(--sage); border-color:var(--sage); }
    .candidate.reviewed { border-left:5px solid var(--sage); background:var(--pale); }
    .candidate.excluded { border-left:5px solid #9a8870; background:#f8f6f2; }
    /* Participant mode keeps the shared layout but uses a warmer, welcoming accent. */
    body.participant-theme { --sage:#b56b45; --deep:#8b4a32; --pale:#fbefe8;
      --line:#e4c9bb; --warm:#f8eee8; }
    body.participant-theme .eyebrow { color:var(--sage); }
    body.participant-theme .session-summary.current { border-color:var(--sage); }
    .participant-stepper { display:grid; grid-template-columns:repeat(5,1fr); gap:8px;
      margin:22px 0; padding:12px; border:1px solid var(--line); border-radius:16px;
      background:var(--paper); }
    .participant-step { display:flex; gap:8px; align-items:center; min-width:0;
      color:var(--muted); font-size:.78rem; line-height:1.2; }
    .participant-step b { display:grid; place-items:center; flex:0 0 26px; height:26px;
      border-radius:50%; color:var(--deep); background:var(--pale); }
    .participant-step.active { color:var(--deep); font-weight:800; }
    .participant-step.active b { color:#fff; background:var(--sage); }
    .participant-theme button, .participant-theme select,
    .participant-theme input[type="checkbox"] { min-height:44px; }
    .participant-theme button { touch-action:manipulation; }
    .participant-grid { display:grid; grid-template-columns:1.15fr .85fr; gap:18px; }
    @media(max-width:760px) { .participant-stepper { display:flex; overflow-x:auto;
        gap:14px; padding:10px; } .participant-step { flex:0 0 auto; }
      .participant-grid { grid-template-columns:1fr; } }
    code { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:.84em;
      overflow-wrap:anywhere; }
    .login { width:min(500px,calc(100% - 32px)); margin:8vh auto; }
    @media(max-width:760px) { .grid,.controls { grid-template-columns:1fr; }
      main { margin-top:20px; } .bar { align-items:flex-start; } }
    """


def _login_page() -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PIA Protected Intake · Sign in</title><style>{_shared_style()}</style></head>
<body><main class="login">
  <div class="eyebrow">PIA · Phase 2B protected intake</div>
  <h1>Open the local participant workspace.</h1>
  <section class="notice"><strong>Local access only.</strong>
    <p>Participant material remains encrypted on this computer. Sign-in sessions
    stay in memory and end when the server restarts.</p></section>
  <section class="card review-workbench">
    <h2>Sign in</h2>
    <label for="account">Account ID</label>
    <input id="account" value="local-owner" autocomplete="username">
    <label for="passphrase">Passphrase</label>
    <input id="passphrase" type="password" autocomplete="current-password">
    <button id="login">Continue</button>
    <div id="status" class="status hidden"></div>
  </section>
</main>
<script>
const byId=(id)=>document.getElementById(id);
function status(message,error=false){{const el=byId("status");el.textContent=message;
  el.className="status"+(error?" error":"");}}
async function login(){{
  byId("login").disabled=true;
  try {{
    const response=await fetch("/api/login",{{method:"POST",
      headers:{{"Content-Type":"application/json"}},
      body:JSON.stringify({{account_id:byId("account").value,
        passphrase:byId("passphrase").value}})}});
    const data=await response.json();
    if(!response.ok) throw new Error(data.error||"Sign-in failed.");
    byId("passphrase").value="";
    location.reload();
  }} catch(error) {{status(error.message,true);byId("login").disabled=false;}}
}}
byId("login").addEventListener("click",login);
byId("passphrase").addEventListener("keydown",(event)=>{{if(event.key==="Enter")login();}});
</script></body></html>"""


def _participant_page(auth: AuthSession) -> str:
    """Participant-safe presentation branch; reviewer mechanics are excluded."""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PIA Participant Workspace</title><style>{_shared_style()}</style></head>
<body class="participant-theme"><main>
  <div class="bar"><div><div class="eyebrow">PIA · Participant workspace</div>
    <h1>Your evidence, in your own view.</h1></div>
    <div><div class="identity">{auth.subject} · participant</div><button id="participantLogout" class="text">Sign out</button></div></div>
  <section class="notice"><strong>Private participant space.</strong>
    <p>Your documents remain inside the protected local process. You decide what
    to provide, what wording to correct, and whether to withdraw authorization.</p>
  </section>
  <nav class="participant-stepper" aria-label="Participant process">
    <div class="participant-step active" aria-current="step"><b>1</b><span>Create workspace</span></div>
    <div class="participant-step"><b>2</b><span>Add documents</span></div>
    <div class="participant-step"><b>3</b><span>Review evidence</span></div>
    <div class="participant-step"><b>4</b><span>Review report</span></div>
    <div class="participant-step"><b>5</b><span>Finish</span></div>
  </nav>
  <div class="participant-grid">
  <section class="card"><div class="eyebrow">1 · Start your private workspace</div>
    <h2>Tell us how you would like to use PIA.</h2>
    <p class="quiet">You can use a private label instead of your name. These choices help keep the review focused and time-limited.</p>
    <label for="participantLabel">Private label for this workspace</label><input id="participantLabel" placeholder="For example, My professional review">
    <label for="participantPurpose">What would you like help understanding?</label><textarea id="participantPurpose" placeholder="For example, the capabilities my experience demonstrates"></textarea>
    <label for="participantScope">What would you like included?</label><select id="participantScope"><option value="evidence_report">Evidence review and participant report</option><option value="evidence_only">Evidence review only</option></select>
    <label for="participantRetention">How long should this workspace be kept?</label><select id="participantRetention"><option value="14_days">14 days</option></select>
    <div class="check"><input id="participantConsent" type="checkbox"><label for="participantConsent">I understand this is a private local workspace and I can withdraw my permission at any time.</label></div>
    <button id="participantSave">Save my choices</button><div id="participantSessionStatus" class="status hidden"></div>
  </section>
  <section class="card"><div class="eyebrow">2 · Your documents</div>
    <h2>Add what you want considered.</h2>
    <p class="quiet">Add a résumé, profile export, course record, project summary, or other supporting evidence. Nothing is shared outside this protected process.</p>
    <input id="participantFile" type="file" accept=".pdf,.doc,.docx,.rtf,.txt,.csv,.zip" hidden>
    <button id="participantChoose" class="secondary" type="button">Choose documents</button>
    <select id="participantDocumentType" disabled><option value="">Choose document type after selecting</option><option value="professional_profile">Professional profile</option><option value="career_document">Career document</option><option value="credential_learning">Credential or learning</option><option value="supporting_evidence">Supporting evidence</option></select>
    <button id="participantStage" class="secondary" disabled>Save selected document</button><div id="participantArtifactStatus" class="status">Create your private workspace before adding documents.</div>
  </section>
  </div>
  <section class="card"><div class="eyebrow">3 · Evidence feedback</div>
    <h2>Check what the source actually says.</h2>
    <p class="quiet">You can keep wording, correct it, exclude it, or ask for an item to be reviewed. Internal mapping and credential interpretation remain outside this view.</p>
    <div class="notice">Evidence review will appear here after documents are processed.</div><div id="participantArtifactResults"></div>
  </section>
  <section class="card"><div class="eyebrow">4 · Your report</div>
    <h2>Review what is ready to share.</h2>
    <p class="quiet">Your reviewed evidence can support a plain-language participant overview. If interpretation or mapping is needed, an authorized reviewer must complete that work before a report can be prepared.</p>
    <button id="participantReport" class="secondary" type="button">View participant overview</button><div id="participantReportStatus" class="status">Your report will become available after evidence review is complete.</div>
  </section>
  <section class="card"><div class="eyebrow">5 · Your control</div>
    <h2>Withdraw authorization.</h2>
    <p class="quiet">Withdrawal stops further processing. Any subsequent deletion follows the protected lifecycle rules and is handled by the authorized process.</p>
    <button id="participantWithdraw" class="danger" type="button">Withdraw authorization</button><div id="participantControlStatus" class="status"></div>
  </section>
</main><script>
const participantCsrf={json.dumps(auth.csrf_token)};
let participantSessionId="";
async function participantRequest(path,body){{const response=await fetch(path,{{method:"POST",headers:{{"Content-Type":"application/json","X-PIA-CSRF":participantCsrf}},body:JSON.stringify(body)}});const data=await response.json();if(!response.ok)throw new Error(data.error||"Request failed.");return data;}}
const participantStatus=(message,error=false)=>{{const el=document.getElementById("participantSessionStatus");el.textContent=message;el.className="status"+(error?" error":"");}};
function participantArtifactCard(artifact){{const box=document.createElement("div");box.className="result";const title=document.createElement("strong");title.textContent=artifact.original_filename||artifact.source_artifact_id;const detail=document.createElement("div");detail.className="quiet";detail.textContent=artifact.source_artifact_id+" · "+artifact.document_type.replaceAll("_"," ");const extract=document.createElement("button");extract.className="secondary";extract.textContent="Prepare evidence review";const reviewBox=document.createElement("div");extract.addEventListener("click",async()=>{{extract.disabled=true;extract.textContent="Preparing evidence review...";try{{const result=await participantRequest("/api/extractions",{{intake_session_id:participantSessionId,source_artifact_id:artifact.source_artifact_id}});extract.textContent="Evidence review ready";const candidates=Array.isArray(result.evidence_candidates)?result.evidence_candidates:[];if(!candidates.length){{const empty=document.createElement("div");empty.className="status";empty.textContent="No reviewable evidence was extracted from this document.";reviewBox.append(empty);}}candidates.forEach(candidate=>{{const item=document.createElement("div");item.className="candidate";const text=document.createElement("p");text.textContent=candidate.evidence_text;const actions=document.createElement("div");actions.className="actions";[["Keep this evidence","accepted"],["Exclude","rejected"]].forEach(([label,disposition])=>{{const action=document.createElement("button");action.textContent=label;action.className=disposition==="accepted"?"":"secondary";action.addEventListener("click",async()=>{{action.disabled=true;try{{await participantRequest("/api/evidence/review",{{intake_session_id:participantSessionId,evidence_id:candidate.evidence_id,disposition,corrected_text:"",reason:"participant review"}});item.className="candidate reviewed";actions.innerHTML="";const saved=document.createElement("div");saved.className="status";saved.textContent=disposition==="accepted"?"Included in your evidence review.":"Excluded from downstream use.";item.append(saved);const change=document.createElement("button");change.className="secondary";change.textContent="Change decision";change.addEventListener("click",()=>{{item.className="candidate";saved.remove();change.remove();actions.innerHTML="";[["Keep this evidence","accepted"],["Exclude","rejected"]].forEach(([againLabel,againDisposition])=>{{const again=document.createElement("button");again.textContent=againLabel;again.className=againDisposition==="accepted"?"":"secondary";again.addEventListener("click",()=>{{participantRequest("/api/evidence/review",{{intake_session_id:participantSessionId,evidence_id:candidate.evidence_id,disposition:againDisposition,corrected_text:"",reason:"participant review"}}).then(()=>{{item.className="candidate reviewed";actions.innerHTML="";const updated=document.createElement("div");updated.className="status";updated.textContent=againDisposition==="accepted"?"Included in your evidence review.":"Excluded from downstream use.";item.append(updated);}}).catch(error=>participantStatus(error.message,true));}});actions.append(again);}});}});actions.append(change);}}catch(error){{action.disabled=false;participantStatus(error.message,true);}}}});actions.append(action);}});item.append(text,actions);reviewBox.append(item);}});}}catch(error){{participantStatus(error.message,true);extract.disabled=false;extract.textContent="Prepare evidence review";}}}});box.append(title,detail,extract,reviewBox);document.getElementById("participantArtifactResults").prepend(box);}}
document.getElementById("participantSave").addEventListener("click",async()=>{{if(!document.getElementById("participantConsent").checked){{participantStatus("Record your authorization before continuing.",true);return;}}const button=document.getElementById("participantSave");button.disabled=true;try{{const selectedScope=document.getElementById("participantScope").value;const internalScope=selectedScope==="evidence_report"?"evidence_extraction|participant_report|capability_mapping|report_generation":"evidence_extraction";const result=await participantRequest("/api/sessions",{{participant_label:document.getElementById("participantLabel").value||"Private participant workspace",purpose:document.getElementById("participantPurpose").value,processing_scope:internalScope,consent_status:"granted",confidentiality:"participant_private",retention_class:document.getElementById("participantRetention").value}});participantSessionId=result.intake_session_id;document.getElementById("participantFile").disabled=false;document.getElementById("participantDocumentType").disabled=false;participantStatus("Private workspace ready. You can now add documents.");document.getElementById("participantArtifactStatus").textContent="Choose a document and its type, then save it to this protected workspace.";}}catch(error){{participantStatus(error.message,true);button.disabled=false;}}}});
function participantCanStage(){{const file=document.getElementById("participantFile").files[0];const type=document.getElementById("participantDocumentType").value;const ready=Boolean(participantSessionId&&file&&type);const button=document.getElementById("participantStage");button.disabled=!ready;button.textContent=file&&type?`Save ${{file.name}} as ${{type.replaceAll("_"," ")}}`:"Save selected document";if(file&&!type)document.getElementById("participantArtifactStatus").textContent=`Selected: ${{file.name}}. Choose a document type before saving.`;else if(file&&type)document.getElementById("participantArtifactStatus").textContent=`Ready to save: ${{file.name}} (${{type.replaceAll("_"," ")}}).`;}}
document.getElementById("participantFile").addEventListener("change",participantCanStage);document.getElementById("participantDocumentType").addEventListener("change",participantCanStage);
document.getElementById("participantChoose").addEventListener("click",()=>{{if(!participantSessionId){{participantStatus("Save your choices before adding documents.",true);return;}}document.getElementById("participantFile").click();}});
document.getElementById("participantStage").addEventListener("click",async()=>{{const file=document.getElementById("participantFile").files[0],type=document.getElementById("participantDocumentType").value;if(!participantSessionId||!file||!type)return;const button=document.getElementById("participantStage");button.disabled=true;try{{const bytes=new Uint8Array(await file.arrayBuffer());let binary="";for(let i=0;i<bytes.length;i+=0x8000)binary+=String.fromCharCode(...bytes.subarray(i,i+0x8000));const artifact=await participantRequest("/api/artifacts",{{intake_session_id:participantSessionId,original_filename:file.name,document_type:type,content_base64:btoa(binary)}});document.getElementById("participantArtifactStatus").textContent="Document saved in the protected workspace.";participantArtifactCard({{...artifact,original_filename:file.name}});document.getElementById("participantFile").value="";document.getElementById("participantDocumentType").value="";}}catch(error){{document.getElementById("participantArtifactStatus").textContent=error.message;}}participantCanStage();}});
document.getElementById("participantLogout").addEventListener("click",async()=>{{
  await fetch("/api/logout",{{method:"POST",headers:{{"X-PIA-CSRF":participantCsrf,"Content-Type":"application/json"}},body:"{{}}"}});
  location.reload();
}});
document.getElementById("participantReport").addEventListener("click",()=>{{const reviewed=[...document.querySelectorAll("#participantArtifactResults .candidate.reviewed")];const status=document.getElementById("participantReportStatus");if(!reviewed.length){{status.textContent="No evidence has been kept yet. Review and keep at least one source statement first.";return;}}status.innerHTML="";const heading=document.createElement("strong");heading.textContent="Your reviewed evidence summary";const note=document.createElement("p");note.textContent="These are the source statements you chose to keep. A reviewer-dependent capability report is separate and is not shown here.";status.append(heading,note);const list=document.createElement("ul");reviewed.forEach(item=>{{const entry=document.createElement("li");const text=item.querySelector("p");entry.textContent=text?text.textContent:"Reviewed evidence";list.append(entry);}});status.append(list);}});
document.getElementById("participantWithdraw").addEventListener("click",async()=>{{if(!participantSessionId){{participantStatus("Create a workspace before withdrawing authorization.",true);return;}}if(!window.confirm("Withdraw authorization for this private workspace? Further processing will stop."))return;const button=document.getElementById("participantWithdraw");button.disabled=true;try{{await participantRequest("/api/withdraw",{{intake_session_id:participantSessionId,reason:"participant withdrew authorization",delete_now:false}});document.getElementById("participantControlStatus").textContent="Authorization withdrawn. Further processing is now blocked.";document.getElementById("participantFile").disabled=true;document.getElementById("participantChoose").disabled=true;document.getElementById("participantStage").disabled=true;}}catch(error){{participantStatus(error.message,true);button.disabled=false;}}}});
</script></body></html>"""


def _session_continuation_view(
    session: dict[str, Any],
    *,
    credential_views: list[dict[str, Any]],
    mapping_views: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the bounded authenticated view used to resume local work."""

    latest_reviews: dict[str, str] = {}
    for event in session.get("evidence_review_events", []):
        target_id = str(event.get("target_record_id", ""))
        disposition = str(event.get("disposition", ""))
        if target_id and disposition:
            latest_reviews[target_id] = disposition

    extractions: list[dict[str, Any]] = []
    for extraction in session.get("evidence_extractions", []):
        candidates: list[dict[str, Any]] = []
        for candidate in extraction.get("evidence_candidates", []):
            evidence_id = str(candidate.get("evidence_id", ""))
            candidates.append(
                {
                    "evidence_id": evidence_id,
                    "evidence_type": candidate.get("evidence_type", ""),
                    "source_locator": candidate.get("source_locator", ""),
                    "evidence_text": candidate.get("evidence_text", ""),
                    "review_status": candidate.get(
                        "review_status", "unreviewed"
                    ),
                    "included_in_downstream": candidate.get(
                        "included_in_downstream", False
                    ),
                    "current_review_disposition": latest_reviews.get(
                        evidence_id, ""
                    ),
                }
            )
        extractions.append(
            {
                "extraction_id": extraction.get("extraction_id", ""),
                "source_artifact_id": extraction.get(
                    "source_artifact_id", ""
                ),
                "extraction_status": extraction.get(
                    "extraction_status", ""
                ),
                "warnings": extraction.get("warnings", []),
                "evidence_candidates": candidates,
            }
        )

    artifacts = [
        {
            "source_artifact_id": artifact.get(
                "source_artifact_id", ""
            ),
            "original_filename": artifact.get("original_filename", ""),
            "document_type": artifact.get("document_type", ""),
            "checksum": artifact.get("checksum", ""),
            "disposition": artifact.get("disposition", ""),
            "extraction_status": artifact.get(
                "extraction_status", "not_requested"
            ),
        }
        for artifact in session.get("artifacts", [])
    ]
    return {
        "session": {
            "intake_session_id": session["intake_session_id"],
            "participant_label": session["participant_label"],
            "purpose": session["purpose"],
            "processing_scope": session["processing_scope"],
            "processing_state": session["processing_state"],
            "consent_status": session["consent_status"],
            "confidentiality": session["confidentiality"],
            "retention_class": session["retention_class"],
            "retention_expires_at": session["retention_expires_at"],
            "updated_at": session["updated_at"],
        },
        "artifacts": artifacts,
        "evidence_extractions": extractions,
        "credential_resolutions": credential_views,
        "capability_mapping_proposals": mapping_views,
    }


def _reviewer_workbench_page(auth: AuthSession) -> str:
    """Decision-centered reviewer workspace; preserves protected APIs."""
    csrf = json.dumps(auth.csrf_token)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>PIA Review Workspace</title><style>{_shared_style()}
.review-shell{{width:min(1440px,calc(100% - 32px));}}.review-header{{display:flex;justify-content:space-between;align-items:start;gap:18px}}.review-grid{{display:grid;grid-template-columns:250px minmax(360px,1fr) 360px;gap:16px;margin-top:20px}}.pane{{border:1px solid var(--line);border-radius:16px;background:#fff;padding:16px;min-height:520px}}.pane h2{{font:700 1.15rem/1.2 Inter,sans-serif}}.document-row,.statement-row{{width:100%;text-align:left;color:var(--ink);background:#fff;border:1px solid var(--line);border-radius:10px;margin:8px 0;padding:12px;cursor:pointer}}.document-row.active,.statement-row.active{{border-color:var(--sage);background:var(--pale)}}.document-row small,.statement-row small{{display:block;color:var(--muted);margin-top:5px}}.decision-row{{display:flex;gap:8px;flex-wrap:wrap}}.decision-row button{{margin:0}}.workspace-bar{{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}}.workspace-bar input,.workspace-bar select{{width:auto;flex:1 1 170px}}.summary-strip{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px}}.metric{{padding:13px;border:1px solid var(--line);border-radius:12px;background:#fff}}.metric strong{{display:block;font-size:1.3rem;color:var(--deep)}}@media(max-width:950px){{.review-grid{{grid-template-columns:1fr}}.pane{{min-height:0}}.summary-strip{{grid-template-columns:repeat(2,1fr)}}}}</style></head>
<body class="reviewer-theme"><main class="review-shell"><div class="review-header"><div><div class="eyebrow">PIA · Protected evidence review</div><h1>Review evidence. Support capabilities.</h1><p>Simple decisions, protected audit history, and no publication from this workspace.</p></div><div class="identity">{auth.subject} · {auth.role}<button id="logout" class="text">Sign out</button></div></div>
<section class="notice"><strong>Protection controls are active.</strong><div class="controls"><div class="control"><strong>Encrypted at rest</strong><span>Protected with per-session keys.</span></div><div class="control"><strong>Inspected in memory</strong><span>Document bytes are checked before encrypted storage.</span></div><div class="control"><strong>Finite lifecycle</strong><span>Withdrawal and retention controls remain executable.</span></div></div></section><nav class="review-steps" aria-label="Reviewer workflow"><div class="review-step"><b>1</b><span>Workspace<br>Open</span></div><div class="review-step"><b>2</b><span>Add evidence<br>Ready</span></div><div class="review-step active" aria-current="step"><b>3</b><span>Review evidence<br>Current</span></div><div class="review-step"><b>4</b><span>Credential review<br>When needed</span></div><div class="review-step"><b>5</b><span>Summary<br>Draft</span></div><div class="review-step"><b>6</b><span>Finish<br>Open</span></div></nav>
<section class="card"><div class="eyebrow">Workspace</div><div class="workspace-bar"><button id="loadSessions" class="secondary">Open protected workspace</button><input id="file" type="file" accept=".pdf,.doc,.docx,.rtf,.txt,.csv,.zip" disabled><select id="documentType" disabled><option value="">Document type</option><option value="professional_profile">Professional profile</option><option value="career_document">Career document</option><option value="credential_learning">Credential or learning</option><option value="supporting_evidence">Supporting evidence</option></select><button id="stage" disabled>Add evidence</button></div><div id="workspaceStatus" class="status">Open a protected workspace to begin.</div><div id="sessions"></div></section>
<section class="review-grid"><aside class="pane"><h2>Documents</h2><div id="documents"><p class="quiet">No workspace selected.</p></div></aside><section class="pane"><h2>Extracted statements</h2><div id="statements"><p class="quiet">Select a document to review its extracted statements.</p></div></section><aside class="pane"><h2>Selected statement</h2><div id="selection"><p class="quiet">Select a statement to accept, edit, or reject it.</p></div></aside></section>
<section class="summary-strip"><div class="metric"><strong id="acceptedCount">0</strong>Accepted</div><div class="metric"><strong id="editedCount">0</strong>Edited</div><div class="metric"><strong id="rejectedCount">0</strong>Rejected</div><div class="metric"><strong id="pendingCount">0</strong>Remaining</div></section>
</main><script>const CSRF={csrf};let sessionId="",workspace=null,selectedArtifact="",selectedCandidate=null;const byId=id=>document.getElementById(id);async function request(path,body=null,method="POST"){{const options={{method,headers:{{"X-PIA-CSRF":CSRF}}}};if(body!==null){{options.headers["Content-Type"]="application/json";options.body=JSON.stringify(body)}}const response=await fetch(path,options);const data=await response.json();if(!response.ok)throw new Error(data.error||"Request failed.");return data}}function status(message,error=false){{const el=byId("workspaceStatus");el.textContent=message;el.className="status"+(error?" error":"")}}function recount(){{const all=workspace?.evidence_extractions?.flatMap(x=>x.evidence_candidates)||[];byId("acceptedCount").textContent=all.filter(x=>x.current_review_disposition==="accepted").length;byId("editedCount").textContent=all.filter(x=>x.current_review_disposition==="corrected").length;byId("rejectedCount").textContent=all.filter(x=>x.current_review_disposition==="rejected").length;byId("pendingCount").textContent=all.filter(x=>!x.current_review_disposition).length}}function render(){{const docs=byId("documents");docs.replaceChildren();const artifactMap=new Map((workspace?.artifacts||[]).map(x=>[x.source_artifact_id,x]));workspace?.artifacts?.forEach(a=>{{const b=document.createElement("button");b.className="document-row"+(a.source_artifact_id===selectedArtifact?" active":"");b.textContent=a.original_filename;const s=document.createElement("small");s.textContent=a.document_type.replaceAll("_"," ");b.append(s);b.onclick=()=>{{selectedArtifact=a.source_artifact_id;render()}};docs.append(b)}});const list=byId("statements");list.replaceChildren();const extraction=workspace?.evidence_extractions?.find(x=>x.source_artifact_id===selectedArtifact);if(!extraction){{list.innerHTML="<p class='quiet'>Select a document with extracted statements.</p>"}}else extraction.evidence_candidates.forEach(c=>{{const b=document.createElement("button");b.className="statement-row"+(c.evidence_id===selectedCandidate?.evidence_id?" active":"");b.textContent=c.evidence_text;const s=document.createElement("small");s.textContent=c.source_locator+" · "+(c.current_review_disposition||"Needs review");b.append(s);b.onclick=()=>{{selectedCandidate=c;render()}};list.append(b)}});const panel=byId("selection");panel.replaceChildren();if(selectedCandidate){{const text=document.createElement("p");text.textContent=selectedCandidate.evidence_text;const source=document.createElement("p");source.className="quiet";source.textContent=selectedCandidate.source_locator;const controls=document.createElement("div");controls.className="decision-row";[["Accept","accepted",""],["Edit","corrected","secondary"],["Reject","rejected","danger"]].forEach(([label,decision,klass])=>{{const button=document.createElement("button");button.textContent=label;button.className=klass;button.onclick=async()=>{{let corrected="";if(decision==="corrected"){{corrected=prompt("Correct the source-grounded wording:",selectedCandidate.evidence_text)||"";if(!corrected)return}}try{{const result=await request("/api/evidence/review",{{intake_session_id:sessionId,evidence_id:selectedCandidate.evidence_id,disposition:decision,corrected_text:corrected,reason:"reviewer decision"}});Object.assign(selectedCandidate,result.evidence_candidate);status("Decision recorded in the protected audit history.");render();recount()}}catch(error){{status(error.message,true)}}}};controls.append(button)}});panel.append(text,source,controls)}}recount()}}async function openWorkspace(id){{try{{workspace=await request("/api/sessions/resume",{{intake_session_id:id}});sessionId=workspace.session.intake_session_id;selectedArtifact=workspace.artifacts?.[0]?.source_artifact_id||"";selectedCandidate=null;byId("file").disabled=false;byId("documentType").disabled=false;byId("stage").disabled=false;status("Protected workspace open: "+sessionId);render()}}catch(error){{status(error.message,true)}}}}byId("loadSessions").onclick=async()=>{{try{{const result=await request("/api/sessions",null,"GET");const target=byId("sessions");target.replaceChildren();result.sessions.forEach(item=>{{const b=document.createElement("button");b.className="secondary";b.textContent="Open "+item.participant_label+" · "+item.artifact_count+" document(s)";b.onclick=()=>openWorkspace(item.intake_session_id);target.append(b)}})}}catch(error){{status(error.message,true)}}}};byId("stage").onclick=async()=>{{const file=byId("file").files[0],type=byId("documentType").value;if(!sessionId||!file||!type){{status("Choose a document and its type first.",true);return}}try{{const bytes=new Uint8Array(await file.arrayBuffer());let binary="";for(let i=0;i<bytes.length;i+=0x8000)binary+=String.fromCharCode(...bytes.subarray(i,i+0x8000));const artifact=await request("/api/artifacts",{{intake_session_id:sessionId,original_filename:file.name,document_type:type,content_base64:btoa(binary)}});await request("/api/extractions",{{intake_session_id:sessionId,source_artifact_id:artifact.source_artifact_id}});await openWorkspace(sessionId);status("Document added and statements prepared for review.")}}catch(error){{status(error.message,true)}}}};byId("logout").onclick=async()=>{{await request("/api/logout",{{}});location.reload()}};</script></body></html>"""


def _main_page(
    auth: AuthSession,
    *,
    external_lookup_configured: bool,
) -> str:
    csrf = json.dumps(auth.csrf_token)
    identity = json.dumps({"subject": auth.subject, "role": auth.role})
    owner_only = "" if auth.role == "owner" else "disabled"
    theme_class = "participant-theme" if auth.role == "participant" else "reviewer-theme"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PIA Protected Participant Intake</title><style>{_shared_style()}</style></head>
<body class="{theme_class}"><main>
  <div class="bar"><div class="eyebrow">PIA · Phase 2B protected intake</div>
    <div><span class="identity">{auth.subject} · {auth.role}</span>
      <button id="logout" class="text">Sign out</button></div></div>
  <h1>Collect evidence inside its protection boundary.</h1>
  <p>This local workspace requires authorization before documents can enter
  the participant evidence process.</p>

  <section class="notice">
    <strong>Protection controls are active.</strong>
    <div class="controls">
      <div class="control"><strong>Encrypted at rest</strong>
        <span>AES-256-GCM with per-session keys protected for this Windows user.</span></div>
      <div class="control"><strong>Inspected in memory</strong>
        <span>Windows AMSI checks document bytes before encrypted storage.</span></div>
      <div class="control"><strong>Finite lifecycle</strong>
        <span>Withdrawal blocks processing; deletion and retention are executable.</span></div>
    </div>
  </section>

  <div class="grid">
    <section class="card">
      <div class="eyebrow">1 · Authorization</div><h2>Create participant session</h2>
      <label for="participant">Private participant label</label>
      <input id="participant" value="Synthetic Intake Subject Alpha" maxlength="80">
      <label for="purpose">Purpose</label>
      <textarea id="purpose">Participant-authorized professional evidence analysis and report development.</textarea>
      <label for="scope">Processing scope</label>
      <select id="scope">
        <option value="evidence_extraction|credential_definition|capability_mapping|report_generation">Evidence, credentials, capability mapping, and reports</option>
        <option value="evidence_extraction">Document extraction and evidence review only</option>
        <option value="credential_definition">Credential definition only</option>
        <option value="report_generation">Report development only</option>
      </select>
      <label for="retention">Retention</label>
      <select id="retention">
        <option value="30_days">30 days</option><option value="90_days">90 days</option>
        <option value="365_days">365 days</option>
      </select>
      <label for="confidentiality">Confidentiality</label>
      <select id="confidentiality"><option value="participant_private">Participant private</option>
        <option value="restricted">Restricted</option></select>
      <div class="check"><input id="consent" type="checkbox">
        <label for="consent">I have recorded authorization for this purpose, scope, and retention period.</label></div>
      <button id="create">Create protected session</button>
      <div id="sessionStatus" class="status hidden"></div>
      <div class="resume-panel">
        <h3>Continue or manage protected work</h3>
        <p class="quiet">Sessions with saved documents or review work appear
        first. Empty sessions are separated below so they are not mistaken for
        completed or active evidence work.</p>
        <button id="loadSessions" class="secondary">Review saved sessions</button>
        <div id="sessionResults"></div>
      </div>
    </section>

    <section class="card">
      <div class="eyebrow">2 · Protected staging</div><h2>Add a document</h2>
      <p class="quiet">Documents are inspected in memory, encrypted, fingerprinted, and
      checked for exact duplicates before acceptance.</p>
      <div class="check"><div><strong>Image files are not supported yet.</strong>
        <div class="quiet">PNG, JPG/JPEG, HEIC, TIFF, screenshots, and scanned or
        image-only PDFs cannot currently be extracted. For now, provide a
        locally prepared TXT or DOCX transcription with the original retained
        separately. Do not use an unapproved cloud OCR service for participant
        material.</div></div></div>
      <label for="file">Document</label>
      <input id="file" type="file" accept=".pdf,.doc,.docx,.rtf,.txt,.csv,.zip" disabled>
      <label for="documentType">Document type</label>
      <select id="documentType" disabled><option value="">Choose a type</option>
        <option value="professional_profile">Professional profile</option>
        <option value="career_document">Career document</option>
        <option value="credential_learning">Credential or learning</option>
        <option value="supporting_evidence">Supporting evidence</option></select>
      <button id="stage" disabled>Inspect and encrypt document</button>
      <div id="artifactStatus" class="status hidden"></div><div id="results"></div>
    </section>
  </div>

  <section class="card">
    <div class="eyebrow">3 · Evidence review</div>
    <h2>Check what the documents actually say.</h2>
    <p class="quiet">Extraction creates source-grounded candidates only. Keep,
    correct, or exclude each item before it can move downstream. No capability
    interpretation or scoring occurs here.</p>
    <div id="evidenceStatus" class="status hidden"></div>
    <div class="review-layout"><aside class="review-column"><h3>Documents</h3><div id="reviewDocuments"><div class="quiet">Documents appear here after staging.</div></div></aside><div class="review-column"><h3>Extracted statements</h3><div id="evidenceResults"></div></div><aside class="review-selection" id="reviewSelection"><h3>Selected statement</h3><p class="quiet">Choose a statement to inspect its source, decision, and review controls.</p></aside></div>
  </section>

  <section id="credentialSection" class="card">
    <div class="eyebrow">4 · Credential meaning</div>
    <h2>Check what a credential represents.</h2>
    <p class="quiet">Enter only the public credential name, issuer, and version.
    PIA checks the governed local library first. Participant identity,
    completion dates, certificate numbers, documents, and private notes never
    enter the public-reference request.</p>
    <div class="grid">
      <div>
        <label for="credentialTitle">Credential title</label>
        <input id="credentialTitle" maxlength="240"
          placeholder="Physical Security Professional">
        <label for="credentialIssuer">Issuing organization, if known</label>
        <input id="credentialIssuer" maxlength="200"
          placeholder="ASIS International">
        <label for="credentialVersion">Version or edition, if known</label>
        <input id="credentialVersion" maxlength="200"
          placeholder="Body of Knowledge updated 2022">
      </div>
      <div>
        <label for="credentialType">Credential type</label>
        <select id="credentialType">
          <option value="">Not sure</option>
          <option value="certification">Certification</option>
          <option value="license">License</option>
          <option value="certificate">Certificate</option>
          <option value="course_completion">Course completion</option>
          <option value="badge">Badge</option>
          <option value="degree">Degree</option>
          <option value="other">Other</option>
        </select>
        <label for="credentialJurisdiction">Jurisdiction, if relevant</label>
        <input id="credentialJurisdiction" maxlength="100"
          placeholder="International, US, Illinois">
        <div class="notice"><strong>Public registry</strong>
          <p>{"Configured for unresolved local matches."
              if external_lookup_configured
              else "Not configured. Unresolved credentials remain available for manual public-source review."}</p>
        </div>
      </div>
    </div>
    <button id="resolveCredential" disabled>Check credential meaning</button>
    <div id="credentialStatus" class="status hidden"></div>
    <div id="credentialResults"></div>
  </section>

  <section id="mappingSection" class="card">
    <div class="eyebrow">5 · Mapping handoff</div>
    <h2>What might the accepted evidence support?</h2>
    <p class="quiet">This creates a review-required analytical proposal. It does
    not accept a capability, create a participant score, write to a graph, or
    generate a report.</p>
    <div id="mappingQueue" class="notice hidden">
      <strong>Review queue</strong>
      <p>Choose a saved unresolved proposal to open its decision controls.</p>
      <label for="mappingQueueSelect">Stored mapping proposals</label>
      <select id="mappingQueueSelect"><option value="">No unresolved proposals</option></select>
      <button id="openMappingReview" class="secondary" disabled>Open selected proposal</button>
    </div>
    <div id="mappingLedger" class="notice hidden"></div>
    <label for="mappingEvidence">Accepted evidence</label>
    <select id="mappingEvidence" disabled><option value="">Review evidence first</option></select>
    <label for="mappingReplacement">Replace an accepted mapping (optional)</label>
    <select id="mappingReplacement" disabled><option value="">Create a new mapping</option></select>
    <label for="mappingCapability">Working capability</label>
    <select id="mappingCapability" disabled><option value="">Choose a capability</option></select>
    <div class="grid">
      <div>
        <label for="mappingInference">Strength of support</label>
        <select id="mappingInference" disabled><option value="directly_demonstrated">Directly demonstrated</option><option value="strongly_inferred">Strongly inferred</option><option value="contextually_suggested">Contextually suggested</option></select>
        <label for="mappingConfidence" class="technical-field">Internal confidence</label>
        <input id="mappingConfidence" type="number" min="0" max="1" step="0.01" value="0.70" disabled style="display:none">
        <label for="mappingBasis" class="technical-field">Internal confidence basis</label>
        <textarea id="mappingBasis" maxlength="2000" disabled style="display:none"></textarea>
      </div>
      <div>
        <label for="mappingBehavior">Why is this capability supported?</label>
        <textarea id="mappingBehavior" maxlength="2000" disabled></textarea>
        <label for="mappingBoundary">What this does not establish</label>
        <textarea id="mappingBoundary" maxlength="2000" disabled></textarea>
      </div>
    </div>
    <label for="mappingScope">Known limits or scope</label>
    <textarea id="mappingScope" maxlength="2000" disabled></textarea>
    <label for="mappingIndependence" class="technical-field">Source-independence note</label>
    <textarea id="mappingIndependence" maxlength="2000" disabled style="display:none"></textarea>
    <button id="prepareMappingDraft" class="secondary" disabled>Prepare conservative draft</button>
    <button id="proposeMapping" disabled>Submit capability support for review</button>
    <div id="mappingStatus" class="status hidden"></div><div id="mappingResults"></div>
    <div class="notice"><strong>Draft output handoff</strong>
      <p>Create a transient participant overview and an exact dry-run projection
      manifest from accepted mappings only. No graph write or report publication occurs.</p>
      <button id="previewOutput" class="secondary" disabled>Prepare draft output</button>
      <div id="outputStatus" class="status hidden"></div><div id="outputResults"></div>
    </div>
  </section>

  <div class="grid">
    <section class="card">
      <div class="eyebrow">6 · Participant control</div><h2>Withdraw or delete</h2>
      <p class="quiet">Withdrawal immediately blocks further processing. The owner can
      also erase the session key and remove encrypted participant files.</p>
      <label for="withdrawReason">Reason</label>
      <textarea id="withdrawReason" placeholder="Record the participant request or authorization change."></textarea>
      <div class="check"><input id="deleteNow" type="checkbox" {owner_only}>
        <label for="deleteNow">Delete participant content immediately after withdrawal.</label></div>
      <button id="withdraw" class="danger" disabled>Withdraw authorization</button>
      <div id="lifecycleStatus" class="status hidden"></div>
    </section>
    <section class="card">
      <div class="eyebrow">Assurance</div><h2>Check the protected store</h2>
      <p class="quiet">Validate encrypted content, checksums, audit-chain integrity,
      authorization state, and retention deadlines.</p>
      <button id="validate" class="secondary">Validate store</button>
      <button id="retentionPreview" class="secondary" {owner_only}>Preview retention</button>
      <button id="retentionApply" class="danger" {owner_only}>Apply expired retention</button>
      <div id="assuranceStatus" class="status hidden"></div>
    </section>
  </div>

  <section class="card"><div class="eyebrow">Working boundary</div>
    <h2>Protected intake with reviewable evidence.</h2>
    <p>Supported documents are decrypted and parsed in memory, while extracted
    text and review decisions remain encrypted at rest. Reviewed evidence may
    later enter governed mapping. Extraction itself never creates a capability
    conclusion. Credential reference resolution remains behind its separate
    minimization and independent-review gates.</p></section>
</main>
<script>
const byId=(id)=>document.getElementById(id);
const CSRF={csrf}; const IDENTITY={identity}; let sessionId="";
if(IDENTITY.role==="participant")byId("mappingSection").classList.add("hidden");
if(IDENTITY.role==="participant")byId("credentialSection").classList.add("hidden");
let duplicateCreationConfirmed=false;
function status(target,message,error=false){{target.textContent=message;
  target.className="status"+(error?" error":"");}}
async function request(path,body=null,method="POST"){{
  const options={{method,headers:{{"X-PIA-CSRF":CSRF}}}};
  if(body!==null){{options.headers["Content-Type"]="application/json";
    options.body=JSON.stringify(body);}}
  const response=await fetch(path,options); const data=await response.json();
  if(response.status===401){{location.reload();throw new Error("Your local session ended.");}}
  if(!response.ok)throw new Error(data.error||"The protected intake request failed.");
  return data;
}}
byId("logout").addEventListener("click",async()=>{{try{{await request("/api/logout",{{}});}}
  finally{{location.reload();}}}});
function clearWorkspace(){{
  byId("results").replaceChildren();
  byId("reviewDocuments").replaceChildren();
  byId("evidenceResults").replaceChildren();
  byId("credentialResults").replaceChildren();
  byId("artifactStatus").className="status hidden";
  byId("evidenceStatus").className="status hidden";
  byId("credentialStatus").className="status hidden";
  byId("mappingStatus").className="status hidden";
  byId("outputStatus").className="status hidden";
  byId("outputResults").replaceChildren();
  byId("mappingResults").replaceChildren();
  refreshMappingQueue();
  byId("mappingEvidence").replaceChildren(new Option("Review evidence first",""));
  setMappingEnabled(false);
}}
const mappingControlIds=["mappingEvidence","mappingCapability","mappingInference",
  "mappingConfidence","mappingBasis","mappingBehavior","mappingBoundary",
  "mappingScope","mappingIndependence","mappingReplacement","prepareMappingDraft","proposeMapping"];
function setMappingEnabled(enabled){{
  mappingControlIds.forEach(id=>byId(id).disabled=!enabled);
  byId("previewOutput").disabled=!enabled;
}}
function renderOutput(result){{
  const box=document.createElement("div");box.className="result";
  const heading=document.createElement("strong");heading.textContent=result.participant_preview.title;
  box.append(heading);
  if(result.participant_preview.quality_findings.length){{
    const held=document.createElement("div");held.className="status error";
    held.textContent="This participant overview is not ready to share yet. "+result.participant_preview.quality_findings.length+" mapping record(s) need clearer evidence framing.";
    box.append(held);
    const details=document.createElement("details");
    const summary=document.createElement("summary");summary.textContent="View the mapping updates needed";
    const list=document.createElement("ul");
    result.participant_preview.quality_findings.forEach(item=>{{
      const entry=document.createElement("li");entry.textContent=item.mapping_id+": "+item.reason+". "+item.next_action;list.append(entry);
    }});
    details.append(summary,list);box.append(details);
  }} else {{
    result.participant_preview.interpretations.forEach(item=>{{
      const line=document.createElement("div");line.className="quiet";
      line.textContent=item.participant_summary+" "+item.inference_level.replaceAll("_"," ")+" · confidence "+item.confidence+" · "+item.mapping_ids.length+" supporting mapping(s). Boundary: "+item.negative_boundaries.join(" | ");
      box.append(line);
    }});
  }}
  const technical=document.createElement("div");technical.className="quiet";
  technical.textContent="Technical companion retains "+result.technical_companion.interpretations.length+" individual accepted mapping(s), including their evidence basis and boundaries.";
  box.append(technical);
  const manifest=document.createElement("div");manifest.className="quiet";
  manifest.textContent="Dry-run manifest: "+result.projection_manifest.projection_manifest_id+" · assurance "+result.projection_manifest.assurance_status+" · no graph write.";
  const sandbox=document.createElement("div");sandbox.className="quiet";
  sandbox.textContent="Sandbox projection assurance: "+result.sandbox_projection_assurance.status+" · "+result.sandbox_projection_assurance.records.length+" exact SUPPORTS record(s) · offline only.";
  box.append(manifest,sandbox);byId("outputResults").replaceChildren(box);
  const feedback=document.createElement("textarea");feedback.placeholder="Request an update to this draft output";feedback.maxLength=500;
  const requestUpdate=document.createElement("button");requestUpdate.className="secondary";requestUpdate.textContent="Request an update";
  requestUpdate.addEventListener("click",async()=>{{try{{const saved=await request("/api/outputs/feedback",{{intake_session_id:sessionId,note:feedback.value}});status(byId("outputStatus"),"Update request recorded as "+saved.output_feedback_event_id+". The evidence and mappings are unchanged.");}}catch(error){{status(byId("outputStatus"),error.message,true);}}}});
  box.append(feedback,requestUpdate);byId("outputResults").replaceChildren(box);
}}
byId("previewOutput").addEventListener("click",async()=>{{
  try{{const result=await request("/api/outputs/preview",{{intake_session_id:sessionId}});
    renderOutput(result);status(byId("outputStatus"),"Draft output prepared from accepted mappings only.");
  }}catch(error){{status(byId("outputStatus"),error.message,true);}}
}});
function addMappingEvidence(candidate){{
  if(!candidate.included_in_downstream||candidate.review_status!=="reviewed")return;
  const select=byId("mappingEvidence");
  if([...select.options].some(option=>option.value===candidate.evidence_id))return;
  const text=(candidate.evidence_text||"").slice(0,120);
  select.add(new Option(candidate.evidence_id+" — "+text,candidate.evidence_id));
}}
function refreshMappingQueue(){{
  const select=byId("mappingQueueSelect");
  const pending=[...byId("mappingResults").querySelectorAll("[data-mapping-id]")]
    .filter(box=>["proposed","needs_review"].includes(box.dataset.mappingStatus));
  select.replaceChildren(new Option(
    pending.length?"Choose a stored proposal":"No unresolved proposals", ""));
  pending.forEach((box,index)=>{{
    select.add(new Option(
      (index+1)+". "+box.dataset.mappingName+" — "+
      box.dataset.mappingStatus.replaceAll("_"," ")+" ("+box.dataset.mappingId+")",
      box.id
    ));
  }});
  byId("mappingQueue").className=pending.length?"notice":"notice hidden";
  byId("openMappingReview").disabled=!pending.length;
  const all=[...byId("mappingResults").querySelectorAll("[data-mapping-id]")];
  const ledger=byId("mappingLedger");ledger.replaceChildren();
  if(!all.length){{ledger.className="notice hidden";return;}}
  const label=document.createElement("strong");label.textContent="Mapping ledger";
  const list=document.createElement("ul");
  all.sort((a,b)=>a.dataset.mappingId.localeCompare(b.dataset.mappingId)).forEach(box=>{{
    const row=document.createElement("li");
    row.textContent=box.dataset.mappingId+" — "+box.dataset.mappingStatus.replaceAll("_"," ")+": "+box.dataset.mappingName+(box.dataset.mappingLineage?" ("+box.dataset.mappingLineage+")":"");
    list.append(row);
  }});
  ledger.append(label,list);ledger.className="notice";
}}
byId("openMappingReview").addEventListener("click",()=>{{
  const selected=byId("mappingQueueSelect").value;
  if(!selected)return;
  const target=byId(selected);
  if(!target)return;
  target.scrollIntoView({{behavior:"smooth",block:"center"}});
  target.classList.add("current");
  setTimeout(()=>target.classList.remove("current"),1800);
}});
function renderMapping(item){{
  const box=document.createElement("div");box.className="result";
  box.id="mapping-"+item.mapping_id;
  box.dataset.mappingId=item.mapping_id;
  box.dataset.mappingName=item.capability_name;
  box.dataset.mappingStatus=item.review_status;
  box.dataset.mappingLineage=item.supersedes_mapping_id
    ?"replaces "+item.supersedes_mapping_id
    :(item.replaces_mapping_id?"revision of "+item.replaces_mapping_id:"");
  if(item.review_status==="accepted"){{
    const replacement=byId("mappingReplacement");
    if(![...replacement.options].some(option=>option.value===item.mapping_id)){{
      replacement.add(new Option("Replace "+item.mapping_id+" — "+item.capability_name,item.mapping_id));
    }}
  }}
  const title=document.createElement("strong");
  title.textContent=item.capability_name+" · "+item.review_status.replaceAll("_"," ");
  const detail=document.createElement("div");detail.className="quiet";
  detail.textContent=item.mapping_id+" · "+item.inference_level.replaceAll("_"," ")+" · confidence "+item.confidence;
  const limit=document.createElement("div");limit.className="quiet";
  limit.textContent="Boundary: "+item.negative_boundary;
  box.append(title,detail,limit);
  if(item.review_status==="proposed"||item.review_status==="needs_review"){{
    const review=document.createElement("details");
    const reviewSummary=document.createElement("summary");
    reviewSummary.textContent="Review this proposal";review.append(reviewSummary);
    const reason=document.createElement("textarea");reason.maxLength=500;
    reason.placeholder="Independent reviewer reason";
    const actions=document.createElement("div");actions.className="actions";
    const accept=document.createElement("button");accept.textContent="Accept mapping";
    const reject=document.createElement("button");reject.className="secondary";reject.textContent="Reject mapping";
    const narrow=document.createElement("button");narrow.className="secondary";narrow.textContent="Narrow scope";
    const narrowed=document.createElement("div");narrowed.className="hidden";
    const scope=document.createElement("textarea");scope.placeholder="Narrowed scope limit";
    const boundary=document.createElement("textarea");boundary.placeholder="Narrowed negative boundary";
    narrowed.append(scope,boundary);
    async function reviewMapping(disposition){{
      [accept,reject,narrow].forEach(button=>button.disabled=true);
      try{{
        const result=await request("/api/mappings/review",{{
          intake_session_id:sessionId,mapping_id:item.mapping_id,disposition,
          reason:reason.value,narrowed_scope_limit:scope.value,
          narrowed_negative_boundary:boundary.value
        }});
        box.remove();
        renderMapping(result.mapping);
        status(byId("mappingStatus"),"Mapping review saved. Earlier proposal history is retained.");
      }}catch(error){{status(byId("mappingStatus"),error.message,true);
        [accept,reject,narrow].forEach(button=>button.disabled=false);}}
    }}
    accept.addEventListener("click",()=>reviewMapping("accepted"));
    reject.addEventListener("click",()=>reviewMapping("rejected"));
    narrow.addEventListener("click",()=>{{narrowed.classList.remove("hidden");
      narrow.textContent="Save narrowed mapping";narrow.onclick=()=>reviewMapping("narrowed");}});
    actions.append(accept,reject,narrow);review.append(reason,narrowed,actions);box.append(review);
  }}
  byId("mappingResults").prepend(box);refreshMappingQueue();
}}
async function loadMappingVocabulary(){{
  try{{
    const result=await request("/api/mappings/vocabulary",{{}});
    const select=byId("mappingCapability");
    if(select.options.length>1)return;
    result.capabilities.forEach(item=>select.add(new Option(
      item.capability_name+" ("+item.profile_capability_id+")",
      item.profile_capability_id
    )));
  }}catch(error){{status(byId("mappingStatus"),error.message,true);}}
}}
function activateSession(session,message){{
  sessionId=session.intake_session_id;
  duplicateCreationConfirmed=false;
  byId("participant").value=session.participant_label||byId("participant").value;
  byId("purpose").value=session.purpose||byId("purpose").value;
  if(session.processing_scope)byId("scope").value=session.processing_scope;
  if(session.retention_class)byId("retention").value=session.retention_class;
  if(session.confidentiality)byId("confidentiality").value=session.confidentiality;
  byId("file").disabled=false;byId("documentType").disabled=false;
  byId("stage").disabled=false;byId("withdraw").disabled=false;
  const scopes=(session.processing_scope||"").split("|");
  byId("resolveCredential").disabled=!scopes.includes("credential_definition");
  const mappingEnabled=scopes.includes("capability_mapping")||scopes.includes("participant_report")||scopes.includes("evidence_report");
  setMappingEnabled(mappingEnabled);
  if(mappingEnabled)loadMappingVocabulary();
  byId("create").textContent="Session currently open";
  byId("create").disabled=true;
  status(byId("sessionStatus"),message+"\\nSession: "+sessionId+
    "\\nRetention ends: "+session.retention_expires_at);
}}
function formatSessionDate(value){{
  const parsed=new Date(value);
  return Number.isNaN(parsed.getTime())?value:parsed.toLocaleString();
}}
function sessionProgressLabel(item){{
  if(!item.has_saved_work)return "Empty — no saved evidence";
  if(item.evidence_pending_count>0)return "Evidence review pending";
  if(item.evidence_candidate_count>0)return "Evidence review complete";
  if(item.credential_count>0)return "Credential work saved";
  return "Documents saved";
}}
function renderSessionSummary(item){{
  const isCurrent=item.intake_session_id===sessionId;
  const box=document.createElement("div");
  box.className="session-summary"+(isCurrent?" current":"");
  const heading=document.createElement("div");heading.className="session-heading";
  const title=document.createElement("strong");title.textContent=item.participant_label;
  const badge=document.createElement("span");
  badge.className="session-badge"+
    (isCurrent?" current":(!item.has_saved_work?" empty":""));
  badge.textContent=isCurrent?"Current session":sessionProgressLabel(item);
  heading.append(title,badge);
  const detail=document.createElement("div");detail.className="quiet";
  detail.textContent="Session reference "+item.intake_session_id+
    " · Created "+formatSessionDate(item.created_at);
  const updated=document.createElement("div");updated.className="quiet";
  updated.textContent="Last updated "+formatSessionDate(item.updated_at);
  const counts=document.createElement("div");counts.className="quiet";
  counts.textContent=item.artifact_count+" document(s) · "+
    item.evidence_reviewed_count+" evidence item(s) reviewed · "+
    item.evidence_pending_count+" awaiting review · "+
    item.credential_count+" credential check(s)";
  box.append(heading,detail,updated,counts);
  if(isCurrent){{
    const currentNote=document.createElement("div");currentNote.className="quiet";
    currentNote.textContent="This session is open in the workspace below.";
    box.append(currentNote);return box;
  }}
  if(!item.has_saved_work){{
    const emptyNote=document.createElement("div");emptyNote.className="quiet";
    emptyNote.textContent="Nothing has been added to this session. Open it only "+
      "if you want to continue or withdraw it.";
    box.append(emptyNote);
  }}
  const resume=document.createElement("button");
  resume.textContent=item.has_saved_work
    ?"Continue this saved work":"Open this empty session";
  resume.addEventListener("click",async()=>{{
    resume.disabled=true;
    try{{
      const result=await request("/api/sessions/resume",{{
        intake_session_id:item.intake_session_id
      }});
      clearWorkspace();restoreSession(result);
      activateSession(result.session,"Protected session resumed.");
      await loadActiveSessions();
    }}catch(error){{
      status(byId("sessionStatus"),error.message,true);resume.disabled=false;
    }}
  }});
  box.append(resume);return box;
}}
async function loadActiveSessions(){{
  const button=byId("loadSessions");button.disabled=true;
  const target=byId("sessionResults");target.replaceChildren();
  try{{
    const result=await request("/api/sessions",null,"GET");
    if(!result.sessions.length){{
      const empty=document.createElement("p");empty.className="quiet";
      empty.textContent="No active protected sessions are available.";
      target.append(empty);
    }}else{{
      const saved=result.sessions.filter(item=>item.has_saved_work);
      const emptySessions=result.sessions.filter(item=>!item.has_saved_work);
      const savedHeading=document.createElement("div");savedHeading.className="eyebrow";
      savedHeading.textContent="Sessions with saved work";
      target.append(savedHeading);
      if(saved.length){{
        saved.forEach(item=>target.append(renderSessionSummary(item)));
      }}else{{
        const note=document.createElement("p");note.className="quiet";
        note.textContent="No sessions currently contain saved documents, evidence, "+
          "or credential work.";
        target.append(note);
      }}
      if(emptySessions.length){{
        const emptyGroup=document.createElement("details");
        emptyGroup.className="empty-sessions";
        emptyGroup.open=emptySessions.some(
          item=>item.intake_session_id===sessionId
        );
        const emptySummary=document.createElement("summary");
        emptySummary.textContent="Empty sessions ("+emptySessions.length+
          ") — no documents or evidence";
        emptyGroup.append(emptySummary);
        emptySessions.forEach(
          item=>emptyGroup.append(renderSessionSummary(item))
        );
        target.append(emptyGroup);
      }}
      if(result.truncated){{
        const note=document.createElement("p");note.className="quiet";
        note.textContent="Only the 100 most recently updated sessions are shown.";
        target.append(note);
      }}
    }}
  }}catch(error){{status(byId("sessionStatus"),error.message,true);}}
  finally{{button.disabled=false;button.textContent="Refresh session list";}}
}}
byId("loadSessions").addEventListener("click",loadActiveSessions);
function resetDuplicateCreationGuard(){{
  duplicateCreationConfirmed=false;
  if(!sessionId)byId("create").textContent="Create protected session";
}}
byId("participant").addEventListener("input",resetDuplicateCreationGuard);
byId("create").addEventListener("click",async()=>{{
  if(!byId("consent").checked){{status(byId("sessionStatus"),
    "Record authorization before creating the session.",true);return;}}
  const createButton=byId("create");createButton.disabled=true;
  try{{
    if(!duplicateCreationConfirmed){{
      const index=await request("/api/sessions",null,"GET");
      const proposedLabel=byId("participant").value.trim().toLocaleLowerCase();
      const matching=index.sessions.filter(
        item=>item.participant_label.trim().toLocaleLowerCase()===proposedLabel
      );
      if(matching.length){{
        duplicateCreationConfirmed=true;
        await loadActiveSessions();
        status(byId("sessionStatus"),
          matching.length+" open session(s) already use this private label. "+
          "Review the saved sessions below and continue one if it belongs to "+
          "the same participant. If a separate session is intentional, choose "+
          "Create a separate session anyway.");
        createButton.textContent="Create a separate session anyway";
        createButton.disabled=false;
        return;
      }}
    }}
    const result=await request("/api/sessions",{{
      participant_label:byId("participant").value,purpose:byId("purpose").value,
      processing_scope:byId("scope").value,consent_status:"granted",
      confidentiality:byId("confidentiality").value,retention_class:byId("retention").value}});
    clearWorkspace();
    activateSession(result,"Protected session ready.");
    await loadActiveSessions();
  }}catch(error){{status(byId("sessionStatus"),error.message,true);
    createButton.disabled=false;}}
}});
function renderEvidenceCandidate(candidate){{
  const box=document.createElement("div");box.className="candidate";
  const meta=document.createElement("div");meta.className="quiet";
  meta.textContent=candidate.evidence_id+" · "+
    candidate.evidence_type.replaceAll("_"," ")+" · "+candidate.source_locator;
  const text=document.createElement("p");text.textContent=candidate.evidence_text;
  const decision=document.createElement("div");decision.className="status hidden";
  const revisionHint=document.createElement("div");
  revisionHint.className="review-guidance hidden";
  const actions=document.createElement("div");actions.className="actions";
  const keep=document.createElement("button");keep.textContent="Keep this evidence";
  const correct=document.createElement("button");correct.className="secondary";
  correct.textContent="Correct wording";
  const exclude=document.createElement("button");exclude.className="secondary";
  exclude.textContent="Exclude";
  const revise=document.createElement("button");revise.className="review-change hidden";
  revise.textContent="Change review decision";
  const editor=document.createElement("div");editor.className="correction-editor hidden";
  const editorLabel=document.createElement("label");
  editorLabel.textContent="Correct the source-grounded wording";
  const correction=document.createElement("textarea");correction.maxLength=2000;
  const editorActions=document.createElement("div");editorActions.className="actions";
  const saveCorrection=document.createElement("button");
  saveCorrection.textContent="Save corrected wording";
  const cancelCorrection=document.createElement("button");
  cancelCorrection.className="secondary";cancelCorrection.textContent="Cancel";
  editorActions.append(saveCorrection,cancelCorrection);
  editor.append(editorLabel,correction,editorActions);
  let revising=false;
  const decisionLabels={{
    accepted:"Included as submitted",
    corrected:"Included with corrected wording",
    rejected:"Excluded from downstream use",
    disputed:"Held from downstream use as disputed"
  }};
  function enableActions(){{
    keep.disabled=false;correct.disabled=false;exclude.disabled=false;
    saveCorrection.disabled=false;cancelCorrection.disabled=false;
  }}
  function showSavedDecision(updated,disposition){{
    revising=false;
    text.textContent=updated.evidence_text;
    meta.textContent=updated.evidence_id+" · "+
      updated.evidence_type.replaceAll("_"," ")+" · "+
      updated.review_status.replaceAll("_"," ");
    box.className="candidate "+(updated.included_in_downstream
      ?"reviewed":"excluded");
    decision.textContent="Current review: "+decisionLabels[disposition]+
      ". Earlier review decisions remain in the protected audit history.";
    decision.className="status";
    revisionHint.className="review-guidance hidden";
    editor.classList.add("hidden");
    actions.classList.add("hidden");
    revise.className="review-change";
    enableActions();
    addMappingEvidence(updated);
  }}
  async function review(disposition,correctedText=""){{
    keep.disabled=true;correct.disabled=true;exclude.disabled=true;
    saveCorrection.disabled=true;cancelCorrection.disabled=true;
    try{{
      const result=await request("/api/evidence/review",{{
        intake_session_id:sessionId,evidence_id:candidate.evidence_id,
        disposition,corrected_text:correctedText,reason:""
      }});
      showSavedDecision(result.evidence_candidate,disposition);
    }}catch(error){{
      status(byId("evidenceStatus"),error.message,true);
      enableActions();
    }}
  }}
  keep.addEventListener("click",()=>review("accepted"));
  correct.addEventListener("click",()=>{{
    correction.value=text.textContent;
    actions.classList.add("hidden");revise.className="review-change hidden";
    if(revising){{
      revisionHint.textContent="Edit the wording below. The current review stays "+
        "in effect until the correction is saved.";
      revisionHint.className="review-guidance";
    }}
    editor.classList.remove("hidden");correction.focus();
  }});
  exclude.addEventListener("click",()=>review("rejected"));
  revise.addEventListener("click",()=>{{
    revising=true;
    revisionHint.textContent="Select a replacement below. The current review stays "+
      "in effect until a new decision is saved.";
    revisionHint.className="review-guidance";
    actions.classList.remove("hidden");revise.className="review-change hidden";
  }});
  saveCorrection.addEventListener("click",()=>{{
    const revised=correction.value.trim();
    if(!revised){{
      revisionHint.textContent="Corrected wording cannot be empty.";
      revisionHint.className="status error";return;
    }}
    review("corrected",revised);
  }});
  cancelCorrection.addEventListener("click",()=>{{
    editor.classList.add("hidden");actions.classList.remove("hidden");
    if(revising){{
      revisionHint.textContent="Select a replacement below. The current review stays "+
        "in effect until a new decision is saved.";
      revisionHint.className="review-guidance";
    }}else{{
      decision.className="status hidden";
      revisionHint.className="review-guidance hidden";
    }}
  }});
  actions.append(keep,correct,exclude);
  box.append(meta,text,decision,revisionHint,actions,editor,revise);
  box.addEventListener("click",()=>{{const panel=byId("reviewSelection");panel.replaceChildren();const heading=document.createElement("h3");heading.textContent="Selected statement";const statement=document.createElement("p");statement.textContent=text.textContent;const source=document.createElement("div");source.className="quiet";source.textContent=meta.textContent;panel.append(heading,statement,source,decision.cloneNode(true));}});
  if(candidate.current_review_disposition){{
    showSavedDecision(candidate,candidate.current_review_disposition);
  }}
  return box;
}}
function renderExtraction(extraction){{
  const group=document.createElement("div");group.className="result";
  const heading=document.createElement("strong");
  heading.textContent="Evidence from "+extraction.source_artifact_id;
  const triage=document.createElement("div");triage.className="notice";
  const reviewWorkspace=document.createElement("details");reviewWorkspace.open=true;
  const reviewSummary=document.createElement("summary");
  reviewSummary.textContent="Open evidence review";
  reviewWorkspace.append(reviewSummary);
  function updateTriageSummary(){{
    const candidates=extraction.evidence_candidates;
    const reviewed=candidates.filter(item=>item.review_status==="reviewed").length;
    const pending=candidates.filter(item=>item.review_status!=="reviewed").length;
    const included=candidates.filter(item=>item.included_in_downstream).length;
    const groups=new Map();
    candidates.forEach(item=>{{
      const key=(item.evidence_text||"").toLowerCase().replace(/\\s+/g," ").trim();
      if(key)groups.set(key,[...(groups.get(key)||[]),item.evidence_id]);
    }});
    const duplicateGroups=[...groups.values()].filter(ids=>ids.length>1);
    const tokenSets=candidates.map(item=>{{
      const tokens=new Set((item.evidence_text||"").toLowerCase().match(/[a-z0-9]{3,}/g)||[]);
      return {{id:item.evidence_id,tokens}};
    }});
    for(let i=0;i<tokenSets.length;i++)for(let j=i+1;j<tokenSets.length;j++){{
      const left=tokenSets[i].tokens,right=tokenSets[j].tokens;
      if(left.size<6||right.size<6)continue;
      const overlap=[...left].filter(token=>right.has(token)).length;
      const union=new Set([...left,...right]).size;
      if(union&&overlap/union>=0.82)duplicateGroups.push([tokenSets[i].id,tokenSets[j].id]);
    }}
    const duplicates=[...new Map(duplicateGroups.map(ids=>[ids.slice().sort().join(","),ids])).values()];
    const cues=candidates.filter(item=>{{
      const text=(item.evidence_text||"").trim();
      return text.length<60||!/[.!?]$/.test(text);
    }}).length;
    reviewSummary.textContent="Open evidence review ("+pending+" remaining · "+included+" eligible)";
    triage.textContent=reviewed+" reviewed · "+included+" eligible for mapping · "+pending+" still needing a decision. "+
      "Only eligible evidence appears in the mapping selector."+
      (duplicates.length?" Possible duplicate group(s): "+duplicates.map(ids=>ids.join(", ")).join("; ")+". Review once, then decide what to retain.":"")+
      (cues?" Quality cue: "+cues+" item(s) are short or lack sentence-ending context; inspect before mapping.":"");
  }}
  group.append(heading,triage,reviewWorkspace);
  updateTriageSummary();
  extraction.evidence_candidates.forEach(
    candidate=>reviewWorkspace.append(renderEvidenceCandidate(candidate))
  );
  byId("evidenceResults").prepend(group);
}}
function renderArtifact(artifact){{
  const item=document.createElement("div");item.className="result";
  const title=document.createElement("strong");
  title.textContent=artifact.original_filename;
  const detail=document.createElement("div");detail.className="quiet";
  detail.textContent=artifact.source_artifact_id+" · "+artifact.document_type+
    " · "+artifact.checksum.slice(0,18)+"…";
  const extract=document.createElement("button");extract.className="secondary";
  if(artifact.extraction_status==="not_requested"){{
    extract.textContent="Extract reviewable evidence";
    extract.addEventListener("click",()=>extractEvidence(
      artifact.source_artifact_id,extract));
  }}else{{
    extract.textContent=artifact.extraction_status==="complete"
      ?"Evidence already extracted":"Extraction needs attention";
    extract.disabled=true;
  }}
  item.append(title,detail,extract);byId("results").prepend(item);const doc=document.createElement("div");doc.className="review-doc";doc.textContent=artifact.original_filename;byId("reviewDocuments").prepend(doc);
}}
function restoreSession(result){{
  result.artifacts.forEach(renderArtifact);
  result.evidence_extractions.forEach(renderExtraction);
  result.credential_resolutions.forEach(
    item=>byId("credentialResults").prepend(renderCredential(item))
  );
  result.capability_mapping_proposals.forEach(renderMapping);
  if(result.evidence_extractions.length){{
    const count=result.evidence_extractions.reduce(
      (total,item)=>total+item.evidence_candidates.length,0);
    status(byId("evidenceStatus"),count+
      " saved evidence item(s) restored for continued review.");
  }}
  if(result.credential_resolutions.length){{
    status(byId("credentialStatus"),result.credential_resolutions.length+
      " prior credential check(s) restored.");
  }}
  if(result.capability_mapping_proposals.length){{
    status(byId("mappingStatus"),result.capability_mapping_proposals.length+
      " review-required mapping proposal(s) restored.");
  }}
}}
async function extractEvidence(sourceArtifactId,button){{
  button.disabled=true;
  try{{
    const result=await request("/api/extractions",{{
      intake_session_id:sessionId,source_artifact_id:sourceArtifactId
    }});
    if(result.extraction_status==="failed"){{
      status(byId("evidenceStatus"),result.warnings.join("\\n"),true);
    }}else if(result.extraction_status==="review_required"){{
      status(byId("evidenceStatus"),result.warnings.join("\\n"),true);
    }}else{{
      status(byId("evidenceStatus"),
        result.evidence_candidates.length+
        " source-grounded item(s) are ready for review.");
    }}
    renderExtraction(result);
    button.textContent=result.extraction_status==="failed"
      ?"Extraction needs attention"
      :(result.disposition==="existing_extraction"
        ?"Evidence already extracted":"Evidence extracted");
  }}catch(error){{
    status(byId("evidenceStatus"),error.message,true);button.disabled=false;
  }}
}}
byId("stage").addEventListener("click",async()=>{{
  const file=byId("file").files[0],documentType=byId("documentType").value;
  if(!sessionId||!file||!documentType){{status(byId("artifactStatus"),
    "Choose a document and its type first.",true);return;}}
  if(file.size>{MAX_ARTIFACT_BYTES}){{status(byId("artifactStatus"),
    "The document exceeds the 25 MB limit.",true);return;}}
  byId("stage").disabled=true;
  try{{const bytes=new Uint8Array(await file.arrayBuffer());let binary="";
    for(let i=0;i<bytes.length;i+=0x8000)binary+=String.fromCharCode(...bytes.subarray(i,i+0x8000));
    const result=await request("/api/artifacts",{{intake_session_id:sessionId,
      original_filename:file.name,document_type:documentType,content_base64:btoa(binary)}});
    status(byId("artifactStatus"),result.disposition==="exact_duplicate"
      ?"Exact duplicate recorded; no additional encrypted copy was created."
      :"Inspection passed. The encrypted document and integrity record were stored.");
    renderArtifact({{...result,original_filename:file.name,
      extraction_status:"not_requested"}});
    byId("file").value="";byId("documentType").value="";
  }}catch(error){{status(byId("artifactStatus"),error.message,true);}}
  finally{{byId("stage").disabled=false;}}
}});
function renderCredential(item){{
  const box=document.createElement("div");box.className="result";
  const title=document.createElement("strong");
  title.textContent=item.credential_title+
    (item.issuer_hint?" · "+item.issuer_hint:"");
  const disposition=document.createElement("div");disposition.className="quiet";
  disposition.textContent="Status: "+item.routing_outcome.replaceAll("_"," ")+
    (item.external_candidate_count
      ?" · "+item.external_candidate_count+" public candidate(s)":"");
  const next=document.createElement("p");next.textContent=item.next_action;
  box.append(title,disposition,next);
  if(item.participant_clarification_required){{
    const prompt=document.createElement("label");
    prompt.textContent=item.clarification_prompt;
    const answer=document.createElement("input");answer.maxLength=300;
    answer.placeholder=item.routing_outcome==="confirm_version"
      ?"Enter the year, version, or named edition"
      :"Enter the exact issuer name";
    const button=document.createElement("button");
    button.className="secondary";button.textContent="Update and check again";
    button.addEventListener("click",async()=>{{
      if(!answer.value.trim())return;
      button.disabled=true;
      try{{
        const updated=await request("/api/credentials/clarify",{{
          intake_session_id:sessionId,
          credential_entry_id:item.credential_entry_id,
          field:item.routing_outcome==="confirm_version"
            ?"version_hint":"issuer_hint",
          response:answer.value
        }});
        box.replaceWith(renderCredential(updated));
      }}catch(error){{
        status(byId("credentialStatus"),error.message,true);
        button.disabled=false;
      }}
    }});
    box.append(prompt,answer,button);
  }}
  return box;
}}
byId("proposeMapping").addEventListener("click",async()=>{{
  if(!sessionId||!byId("mappingEvidence").value||!byId("mappingCapability").value){{
    status(byId("mappingStatus"),"Choose accepted evidence and a working capability first.",true);return;
  }}
  const button=byId("proposeMapping");button.disabled=true;
  try{{
    const result=await request("/api/mappings/propose",{{
      intake_session_id:sessionId,evidence_id:byId("mappingEvidence").value,
      profile_capability_id:byId("mappingCapability").value,
      inference_level:byId("mappingInference").value,
      evidence_role:"behavioral_demonstration",
      claim_scope:"demonstrated_application",
      application_status:"described_in_source",
      confidence:byId("mappingConfidence").value,
      confidence_basis:byId("mappingBasis").value,
      aligned_experience_ids:"",
      alignment_basis:"No separate experience record is asserted in this protected handoff.",
      credential_definition_status:"",credential_definition_source:"",
      credential_definition_uri:"",credential_domain_scope:"",
      definition_expansion_required:false,
      behavioral_basis:byId("mappingBehavior").value,
      negative_boundary:byId("mappingBoundary").value,
      scope_limit:byId("mappingScope").value,
      source_independence_note:byId("mappingIndependence").value
      ,replaces_mapping_id:byId("mappingReplacement").value
    }});
    renderMapping(result);
    status(byId("mappingStatus"),"Review-required proposal saved. It has not been accepted or projected.");
  }}catch(error){{status(byId("mappingStatus"),error.message,true);}}
  finally{{button.disabled=false;}}
}});
byId("prepareMappingDraft").addEventListener("click",()=>{{
  if(!byId("mappingEvidence").value||!byId("mappingCapability").value){{
    status(byId("mappingStatus"),"Choose accepted evidence and a working capability first.",true);return;
  }}
  if(!byId("mappingBasis").value.trim())byId("mappingBasis").value="The selected evidence was reviewed and retained as a source-grounded statement. This is a bounded interpretation of the wording provided, not an independent assessment.";
  if(!byId("mappingBehavior").value.trim())byId("mappingBehavior").value="The source describes a behavior, activity, or responsibility relevant to the selected capability.";
  if(!byId("mappingBoundary").value.trim())byId("mappingBoundary").value="This does not establish overall competence, formal authority, outcome quality, or a durable trait.";
  if(!byId("mappingScope").value.trim())byId("mappingScope").value="Limited to the behavior described in the submitted source and its stated context.";
  if(!byId("mappingIndependence").value.trim())byId("mappingIndependence").value="This interpretation is based on the selected evidence item; corroboration from independent sources is not asserted.";
  status(byId("mappingStatus"),"Conservative draft prepared. Review and edit each field before creating the proposal.");
}});
byId("resolveCredential").addEventListener("click",async()=>{{
  const title=byId("credentialTitle").value.trim();
  if(!sessionId||!title){{
    status(byId("credentialStatus"),
      "Create a protected session and enter a credential title.",true);return;
  }}
  byId("resolveCredential").disabled=true;
  try{{
    const result=await request("/api/credentials",{{
      intake_session_id:sessionId,
      credential_title:title,
      issuer_hint:byId("credentialIssuer").value,
      version_hint:byId("credentialVersion").value,
      credential_type_hint:byId("credentialType").value,
      jurisdiction_hint:byId("credentialJurisdiction").value
    }});
    status(byId("credentialStatus"),
      "Credential checked through the protected minimization gate.");
    byId("credentialResults").prepend(renderCredential(result));
    byId("credentialTitle").value="";
    byId("credentialIssuer").value="";
    byId("credentialVersion").value="";
    byId("credentialType").value="";
    byId("credentialJurisdiction").value="";
  }}catch(error){{status(byId("credentialStatus"),error.message,true);}}
  finally{{byId("resolveCredential").disabled=false;}}
}});
byId("withdraw").addEventListener("click",async()=>{{
  if(!sessionId) return;
  const completedSessionId=sessionId;
  const reason=byId("withdrawReason").value;
  if(!reason.trim()){{status(byId("lifecycleStatus"),"Record a withdrawal reason.",true);return;}}
  if(!confirm("Withdraw authorization for this participant session?"))return;
  try{{const result=await request("/api/withdraw",{{intake_session_id:sessionId,reason,
      delete_now:byId("deleteNow").checked}});
    status(byId("lifecycleStatus"),result.deleted
      ?"Authorization withdrawn and participant content deleted.\\nRemoved session: "+
        completedSessionId
      :"Authorization withdrawn. Further processing is blocked.\\nSession removed "+
        "from active work: "+completedSessionId);
    sessionId="";clearWorkspace();byId("sessionResults").replaceChildren();
    byId("stage").disabled=true;byId("withdraw").disabled=true;
    byId("resolveCredential").disabled=true;
    resetDuplicateCreationGuard();byId("create").disabled=false;
    status(byId("sessionStatus"),
      "No protected session is currently open.\\nLast removed session: "+
      completedSessionId);
    await loadActiveSessions();
  }}catch(error){{status(byId("lifecycleStatus"),error.message,true);}}
}});
byId("validate").addEventListener("click",async()=>{{
  try{{const result=await request("/api/validate",null,"GET");
    status(byId("assuranceStatus"),result.accepted
      ?"Protected store validation passed.\\nSessions: "+result.counts.sessions+
       " · Artifacts: "+result.counts.artifacts+" · Audit events: "+result.counts.audit_events
      :"Validation found "+result.counts.errors+" blocking issue(s).",!result.accepted);
  }}catch(error){{status(byId("assuranceStatus"),error.message,true);}}
}});
async function retention(apply){{
  if(apply&&!confirm("Delete every participant session whose retention period has expired?"))return;
  try{{const result=await request("/api/retention",{{dry_run:!apply}});
    const items=apply?result.deleted_session_ids:result.expired_session_ids;
    status(byId("assuranceStatus"),(apply?"Retention applied. Deleted: ":"Retention preview. Expired: ")+
      (items.length?items.join(", "):"None"));
  }}catch(error){{status(byId("assuranceStatus"),error.message,true);}}
}}
byId("retentionPreview").addEventListener("click",()=>retention(false));
byId("retentionApply").addEventListener("click",()=>retention(true));
</script></body></html>"""


def create_server(
    store: ProtectedParticipantIntakeStore,
    *,
    port: int = 8789,
    credential_linkage: CredentialIntakeLinkage | None = None,
    evidence_linkage: ProtectedEvidenceIntakeLinkage | None = None,
    mapping_linkage: ProtectedCapabilityMappingLinkage | None = None,
) -> ThreadingHTTPServer:
    auth_sessions = AuthSessionManager()
    throttle = LoginThrottle()
    linkage = credential_linkage or CredentialIntakeLinkage(store)
    evidence = evidence_linkage or ProtectedEvidenceIntakeLinkage(store)
    mapping = mapping_linkage or ProtectedCapabilityMappingLinkage(store)
    output = ProtectedMappingOutputLinkage(store)

    class Handler(BaseHTTPRequestHandler):
        server_version = "PIAProtectedIntake/0.3"

        def log_message(self, format: str, *args: Any) -> None:
            print(f"{self.log_date_time_string()} {format % args}")

        def _security_headers(self, content_type: str) -> None:
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; style-src 'unsafe-inline'; "
                "script-src 'unsafe-inline'; connect-src 'self'; "
                "img-src 'self' data:; form-action 'self'; frame-ancestors 'none'",
            )

        def _json(
            self,
            status: HTTPStatus,
            value: dict[str, Any],
            *,
            cookie: str | None = None,
        ) -> None:
            body = json.dumps(value).encode("utf-8")
            self.send_response(status)
            self._security_headers("application/json; charset=utf-8")
            if cookie is not None:
                self.send_header("Set-Cookie", cookie)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _html(self, value: str) -> None:
            body = value.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self._security_headers("text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _origin_ok(self) -> bool:
            origin = self.headers.get("Origin")
            return not origin or origin == f"http://{LOCAL_HOST}:{self.server.server_port}"

        def _cookie_token(self) -> str:
            cookie = SimpleCookie()
            try:
                cookie.load(self.headers.get("Cookie", ""))
            except Exception:
                return ""
            morsel = cookie.get(AUTH_COOKIE)
            return morsel.value if morsel else ""

        def _auth(self) -> AuthSession | None:
            return auth_sessions.verify(
                self._cookie_token(),
                client_address=self.client_address[0],
                user_agent=self.headers.get("User-Agent", ""),
            )

        def _csrf_ok(self, auth: AuthSession) -> bool:
            return (
                self._origin_ok()
                and self.headers.get("X-PIA-CSRF", "") == auth.csrf_token
            )

        def _body(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise IntakePreflightError("The request length is invalid.") from exc
            if length <= 0 or length > MAX_REQUEST_BYTES:
                raise IntakePreflightError("The request is empty or too large.")
            try:
                value = json.loads(self.rfile.read(length))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise IntakePreflightError("The request is not valid JSON.") from exc
            if not isinstance(value, dict):
                raise IntakePreflightError("The request body must be an object.")
            return value

        def _require_auth(self, *, csrf: bool) -> AuthSession | None:
            auth = self._auth()
            if auth is None:
                self._json(HTTPStatus.UNAUTHORIZED, {"error": "Sign-in required."})
                return None
            if csrf and not self._csrf_ok(auth):
                self._json(
                    HTTPStatus.FORBIDDEN,
                    {"error": "Request authorization failed."},
                )
                return None
            return auth

        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if path == "/":
                auth = self._auth()
                if auth is None:
                    page = _login_page()
                elif auth.role == "participant":
                    page = _participant_page(auth)
                else:
                    page = _reviewer_workbench_page(auth)
                self._html(page)
                return
            if path == "/api/status":
                self._json(
                    HTTPStatus.OK,
                    {
                        "status": "ready",
                        "mode": "participant",
                        "authentication": "required",
                        "encryption_at_rest": "aes-256-gcm",
                        "malware_inspection": store.scanner.provider_name,
                        "remote_processing": "disabled",
                        "graph_projection": "disabled",
                        "evidence_extraction": "local_review_required",
                        "credential_resolution": "catalog_first",
                        "external_credential_lookup": (
                            "configured"
                            if linkage.external_lookup_configured
                            else "not_configured"
                        ),
                    },
                )
                return
            if path == "/api/validate":
                auth = self._require_auth(csrf=True)
                if auth is None:
                    return
                self._json(HTTPStatus.OK, store.validate())
                return
            if path == "/api/sessions":
                auth = self._require_auth(csrf=True)
                if auth is None:
                    return
                try:
                    self._json(
                        HTTPStatus.OK,
                        store.list_resumable_sessions(
                            actor_subject=auth.subject,
                            actor_role=auth.role,
                        ),
                    )
                except (IntakePreflightError, LocalIntakeError) as exc:
                    self._json(
                        HTTPStatus.BAD_REQUEST,
                        {"error": str(exc)},
                    )
                return
            self._json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

        def do_POST(self) -> None:
            path = urlsplit(self.path).path
            if path == "/api/login":
                if not self._origin_ok():
                    self._json(
                        HTTPStatus.FORBIDDEN,
                        {"error": "Request origin failed."},
                    )
                    return
                if not throttle.allowed(self.client_address[0]):
                    self._json(
                        HTTPStatus.TOO_MANY_REQUESTS,
                        {"error": "Too many failed sign-in attempts. Try again later."},
                    )
                    return
                try:
                    body = self._body()
                    account_id = str(body.get("account_id", "")).strip()
                    identity = store.authenticator.authenticate(
                        account_id,
                        str(body.get("passphrase", "")),
                    )
                    if identity is None:
                        throttle.record_failure(self.client_address[0])
                        self._json(
                            HTTPStatus.UNAUTHORIZED,
                            {"error": "The account ID or passphrase is incorrect."},
                        )
                        return
                    throttle.clear(self.client_address[0])
                    token, auth = auth_sessions.create(
                        subject=identity["subject"],
                        role=identity["role"],
                        client_address=self.client_address[0],
                        user_agent=self.headers.get("User-Agent", ""),
                    )
                    store._append_audit(
                        "local_account_signed_in",
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                        details={"web_session": "memory-only"},
                    )
                    cookie = (
                        f"{AUTH_COOKIE}={token}; Path=/; HttpOnly; "
                        "SameSite=Strict; Max-Age=28800"
                    )
                    self._json(
                        HTTPStatus.OK,
                        {"subject": auth.subject, "role": auth.role},
                        cookie=cookie,
                    )
                except (IntakePreflightError, LocalIntakeError) as exc:
                    self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            auth = self._require_auth(csrf=True)
            if auth is None:
                return
            try:
                body = self._body()
                if path == "/api/logout":
                    store._append_audit(
                        "local_account_signed_out",
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                        details={"web_session": "revoked"},
                    )
                    auth_sessions.revoke(self._cookie_token())
                    self._json(
                        HTTPStatus.OK,
                        {"status": "signed_out"},
                        cookie=(
                            f"{AUTH_COOKIE}=; Path=/; HttpOnly; "
                            "SameSite=Strict; Max-Age=0"
                        ),
                    )
                    return
                if path == "/api/sessions":
                    session = store.create_session(
                        participant_label=str(body.get("participant_label", "")),
                        purpose=str(body.get("purpose", "")),
                        processing_scope=str(body.get("processing_scope", "")),
                        consent_status=str(body.get("consent_status", "")),
                        confidentiality=str(body.get("confidentiality", "")),
                        retention_class=str(body.get("retention_class", "")),
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                    )
                    self._json(
                        HTTPStatus.CREATED,
                        {
                            "intake_session_id": session["intake_session_id"],
                            "participant_id": session["participant_id"],
                            "participant_label": session[
                                "participant_label"
                            ],
                            "purpose": session["purpose"],
                            "processing_scope": session[
                                "processing_scope"
                            ],
                            "processing_state": session["processing_state"],
                            "confidentiality": session[
                                "confidentiality"
                            ],
                            "retention_class": session[
                                "retention_class"
                            ],
                            "retention_expires_at": session["retention_expires_at"],
                        },
                    )
                    return
                if path == "/api/sessions/resume":
                    session = store.resume_session(
                        str(body.get("intake_session_id", "")),
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                    )
                    self._json(
                        HTTPStatus.OK,
                        _session_continuation_view(
                            session,
                            credential_views=linkage.status(
                                session_id=str(
                                    session["intake_session_id"]
                                ),
                                actor_role=auth.role,
                            ),
                            mapping_views=mapping.status(
                                session_id=str(
                                    session["intake_session_id"]
                                ),
                                actor_role=auth.role,
                            ),
                        ),
                    )
                    return
                if path == "/api/artifacts":
                    try:
                        content = base64.b64decode(
                            str(body.get("content_base64", "")),
                            validate=True,
                        )
                    except (ValueError, binascii.Error) as exc:
                        raise IntakePreflightError(
                            "The document content is not valid base64."
                        ) from exc
                    artifact = store.stage_upload(
                        session_id=str(body.get("intake_session_id", "")),
                        original_filename=str(body.get("original_filename", "")),
                        content=content,
                        document_type=str(body.get("document_type", "")),
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                    )
                    self._json(
                        HTTPStatus.CREATED,
                        {
                            "source_artifact_id": artifact["source_artifact_id"],
                            "document_type": artifact["document_type"],
                            "checksum": artifact["checksum"],
                            "disposition": artifact["disposition"],
                            "malware_scan_status": artifact["malware_scan_status"],
                        },
                    )
                    return
                if path == "/api/extractions":
                    unexpected = sorted(
                        set(body)
                        - {
                            "intake_session_id",
                            "source_artifact_id",
                        }
                    )
                    if unexpected:
                        raise IntakePreflightError(
                            "Evidence-extraction fields are not permitted: "
                            + ", ".join(unexpected)
                        )
                    result = evidence.extract(
                        session_id=str(
                            body.get("intake_session_id", "")
                        ),
                        source_artifact_id=str(
                            body.get("source_artifact_id", "")
                        ),
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                    )
                    self._json(HTTPStatus.CREATED, result)
                    return
                if path == "/api/evidence/review":
                    unexpected = sorted(
                        set(body)
                        - {
                            "intake_session_id",
                            "evidence_id",
                            "disposition",
                            "corrected_text",
                            "reason",
                        }
                    )
                    if unexpected:
                        raise IntakePreflightError(
                            "Evidence-review fields are not permitted: "
                            + ", ".join(unexpected)
                        )
                    result = evidence.review(
                        session_id=str(
                            body.get("intake_session_id", "")
                        ),
                        evidence_id=str(body.get("evidence_id", "")),
                        disposition=str(body.get("disposition", "")),
                        corrected_text=str(
                            body.get("corrected_text", "")
                        ),
                        reason=str(body.get("reason", "")),
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                    )
                    self._json(HTTPStatus.OK, result)
                    return
                if path == "/api/mappings/propose":
                    allowed = {
                        "intake_session_id",
                        "evidence_id",
                        "profile_capability_id",
                        "inference_level",
                        "evidence_role",
                        "claim_scope",
                        "application_status",
                        "confidence",
                        "confidence_basis",
                        "aligned_experience_ids",
                        "alignment_basis",
                        "credential_definition_status",
                        "credential_definition_source",
                        "credential_definition_uri",
                        "credential_domain_scope",
                        "definition_expansion_required",
                        "behavioral_basis",
                        "negative_boundary",
                        "scope_limit",
                        "source_independence_note",
                        "replaces_mapping_id",
                    }
                    unexpected = sorted(set(body) - allowed)
                    if unexpected:
                        raise IntakePreflightError(
                            "Capability-mapping fields are not permitted: "
                            + ", ".join(unexpected)
                        )
                    proposal = {
                        key: value
                        for key, value in body.items()
                        if key not in {"intake_session_id", "evidence_id"}
                    }
                    result = mapping.propose(
                        session_id=str(body.get("intake_session_id", "")),
                        evidence_id=str(body.get("evidence_id", "")),
                        proposal=proposal,
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                    )
                    self._json(HTTPStatus.CREATED, result)
                    return
                if path == "/api/mappings/review":
                    allowed = {
                        "intake_session_id",
                        "mapping_id",
                        "disposition",
                        "reason",
                        "narrowed_scope_limit",
                        "narrowed_negative_boundary",
                    }
                    unexpected = sorted(set(body) - allowed)
                    if unexpected:
                        raise IntakePreflightError(
                            "Capability-mapping review fields are not permitted: "
                            + ", ".join(unexpected)
                        )
                    result = mapping.review(
                        session_id=str(body.get("intake_session_id", "")),
                        mapping_id=str(body.get("mapping_id", "")),
                        disposition=str(body.get("disposition", "")),
                        reason=str(body.get("reason", "")),
                        narrowed_scope_limit=str(
                            body.get("narrowed_scope_limit", "")
                        ),
                        narrowed_negative_boundary=str(
                            body.get("narrowed_negative_boundary", "")
                        ),
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                    )
                    self._json(HTTPStatus.OK, result)
                    return
                if path == "/api/mappings/status":
                    unexpected = sorted(
                        set(body) - {"intake_session_id"}
                    )
                    if unexpected:
                        raise IntakePreflightError(
                            "Mapping-status fields are not permitted: "
                            + ", ".join(unexpected)
                        )
                    self._json(
                        HTTPStatus.OK,
                        {
                            "capability_mapping_proposals": mapping.status(
                                session_id=str(
                                    body.get("intake_session_id", "")
                                ),
                                actor_role=auth.role,
                            )
                        },
                    )
                    return
                if path == "/api/outputs/preview":
                    unexpected = sorted(set(body) - {"intake_session_id"})
                    if unexpected:
                        raise IntakePreflightError(
                            "Output-preview fields are not permitted: "
                            + ", ".join(unexpected)
                        )
                    self._json(
                        HTTPStatus.OK,
                        output.preview(
                            session_id=str(body.get("intake_session_id", "")),
                            actor_role=auth.role,
                        ),
                    )
                    return
                if path == "/api/outputs/feedback":
                    if sorted(set(body) - {"intake_session_id", "note"}):
                        raise IntakePreflightError("Output-feedback fields are not permitted.")
                    self._json(HTTPStatus.CREATED, store.request_output_update(session_id=str(body.get("intake_session_id", "")), note=str(body.get("note", "")), actor_subject=auth.subject, actor_role=auth.role))
                    return
                if path == "/api/mappings/vocabulary":
                    if body:
                        raise IntakePreflightError(
                            "Capability vocabulary fields are not permitted."
                        )
                    self._json(
                        HTTPStatus.OK,
                        {"capabilities": mapping.vocabulary()},
                    )
                    return
                if path == "/api/extractions/status":
                    unexpected = sorted(
                        set(body) - {"intake_session_id"}
                    )
                    if unexpected:
                        raise IntakePreflightError(
                            "Extraction-status fields are not permitted: "
                            + ", ".join(unexpected)
                        )
                    result = evidence.status(
                        session_id=str(
                            body.get("intake_session_id", "")
                        ),
                        actor_role=auth.role,
                    )
                    self._json(
                        HTTPStatus.OK,
                        {"evidence_extractions": result},
                    )
                    return
                if path == "/api/credentials":
                    unexpected = sorted(
                        set(body)
                        - {
                            "intake_session_id",
                            "credential_title",
                            "issuer_hint",
                            "version_hint",
                            "credential_type_hint",
                            "jurisdiction_hint",
                        }
                    )
                    if unexpected:
                        raise IntakePreflightError(
                            "Credential request fields are not permitted: "
                            + ", ".join(unexpected)
                        )
                    result = linkage.resolve(
                        session_id=str(
                            body.get("intake_session_id", "")
                        ),
                        descriptor={
                            "credential_title": body.get(
                                "credential_title", ""
                            ),
                            "issuer_hint": body.get("issuer_hint", ""),
                            "version_hint": body.get("version_hint", ""),
                            "credential_type_hint": body.get(
                                "credential_type_hint", ""
                            ),
                            "jurisdiction_hint": body.get(
                                "jurisdiction_hint", ""
                            ),
                        },
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                    )
                    self._json(HTTPStatus.CREATED, result)
                    return
                if path == "/api/credentials/clarify":
                    unexpected = sorted(
                        set(body)
                        - {
                            "intake_session_id",
                            "credential_entry_id",
                            "field",
                            "response",
                        }
                    )
                    if unexpected:
                        raise IntakePreflightError(
                            "Clarification fields are not permitted: "
                            + ", ".join(unexpected)
                        )
                    result = linkage.clarify(
                        session_id=str(
                            body.get("intake_session_id", "")
                        ),
                        credential_entry_id=str(
                            body.get("credential_entry_id", "")
                        ),
                        field=str(body.get("field", "")),
                        response=str(body.get("response", "")),
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                    )
                    self._json(HTTPStatus.OK, result)
                    return
                if path == "/api/credentials/status":
                    result = linkage.status(
                        session_id=str(
                            body.get("intake_session_id", "")
                        ),
                        actor_role=auth.role,
                    )
                    self._json(
                        HTTPStatus.OK,
                        {"credential_resolutions": result},
                    )
                    return
                if path == "/api/withdraw":
                    result = store.withdraw_session(
                        str(body.get("intake_session_id", "")),
                        reason=str(body.get("reason", "")),
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                        delete_now=body.get("delete_now") is True,
                    )
                    self._json(
                        HTTPStatus.OK,
                        {
                            "status": "withdrawn",
                            "deleted": result.get("participant_content_retained")
                            is False,
                        },
                    )
                    return
                if path == "/api/retention":
                    result = store.enforce_retention(
                        actor_subject=auth.subject,
                        actor_role=auth.role,
                        dry_run=body.get("dry_run") is not False,
                    )
                    self._json(HTTPStatus.OK, result)
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            except (
                CredentialLookupError,
                IntakePreflightError,
                LocalIntakeError,
            ) as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    return ThreadingHTTPServer((LOCAL_HOST, port), Handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run authenticated PIA protected intake, evidence review, and "
            "credential linkage."
        )
    )
    parser.add_argument("--storage-root", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8789)
    parser.add_argument(
        "--enforce-retention-on-start",
        action="store_true",
        help="Delete expired sessions before accepting requests.",
    )
    parser.add_argument(
        "--enable-external-credential-lookup",
        action="store_true",
        help=(
            "Enable the server-side Credential Engine connector for local "
            "catalog misses. Participant content is never included."
        ),
    )
    parser.add_argument(
        "--credential-engine-environment",
        choices=("production", "sandbox"),
        default="production",
    )
    parser.add_argument(
        "--credential-engine-api-key-env",
        default="PIA_CREDENTIAL_ENGINE_API_KEY",
        help="Environment-variable name containing the server-side API key.",
    )
    args = parser.parse_args(argv)
    try:
        store = ProtectedParticipantIntakeStore.open(args.storage_root)
        if args.enforce_retention_on_start:
            store.enforce_retention(
                actor_subject="system-retention",
                actor_role="owner",
                dry_run=False,
            )
        connector = None
        if args.enable_external_credential_lookup:
            if not args.credential_engine_api_key_env.startswith("PIA_"):
                raise CredentialRegistryError(
                    "The API-key environment variable must use the PIA_ prefix."
                )
            api_key = os.environ.get(
                args.credential_engine_api_key_env, ""
            )
            if not api_key:
                raise CredentialRegistryError(
                    "External credential lookup was enabled, but the named "
                    "API-key environment variable is empty."
                )
            connector = CredentialEngineSearchConnector(
                api_key=api_key,
                endpoint=(
                    SANDBOX_ENDPOINT
                    if args.credential_engine_environment == "sandbox"
                    else PRODUCTION_ENDPOINT
                ),
            )
        linkage = CredentialIntakeLinkage(
            store,
            connector=connector,
        )
        server = create_server(
            store,
            port=args.port,
            credential_linkage=linkage,
        )
    except (CredentialRegistryError, OSError, LocalIntakeError) as exc:
        parser.error(str(exc))

    print(f"PIA protected participant intake: http://{LOCAL_HOST}:{server.server_port}/")
    print(
        "Boundary: protected evidence extraction is local and review-gated; "
        "only minimized public credential descriptors may reach an "
        "explicitly enabled registry."
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
