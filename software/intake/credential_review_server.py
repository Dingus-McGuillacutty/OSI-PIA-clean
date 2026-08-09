#!/usr/bin/env python3
"""Local participant-free Phase 3A credential review workbench.

artifact_id: component-pia-credential-review-workbench-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import argparse
import json
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from software.intake.credential_definition_catalog import (
    DEFAULT_CATALOG,
    DEFAULT_CONTRACT,
)
from software.intake.credential_definition_review import (
    CredentialDefinitionReviewService,
    CredentialReviewError,
    CredentialReviewRequest,
)


LOCAL_HOST = "127.0.0.1"
MAX_REQUEST_BYTES = 256 * 1024


def _page(local_token: str, write_enabled: bool) -> str:
    token = json.dumps(local_token)
    write_value = "true" if write_enabled else "false"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PIA Credential Definition Review</title>
  <style>
    :root {{
      color-scheme: light; --ink:#19343a; --muted:#60767b; --sage:#147a69;
      --deep:#0c5d50; --pale:#edf5f2; --line:#c9dcd6; --paper:#fff;
      --warm:#f5f1e8; --warn:#9a5b21; --danger:#9c3c32;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; color:var(--ink); background:#f2f6f4;
      font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }}
    main {{ width:min(1180px,calc(100% - 30px)); margin:30px auto 60px; }}
    h1 {{ margin:9px 0; max-width:850px; font:700 clamp(2rem,5vw,3.65rem)/1.03 Georgia,serif; }}
    h2 {{ margin:0 0 8px; font:700 1.55rem/1.15 Georgia,serif; }}
    h3 {{ margin:18px 0 7px; font-size:1rem; }}
    p {{ color:var(--muted); line-height:1.55; }}
    .eyebrow {{ color:var(--sage); font-size:.76rem; font-weight:850;
      letter-spacing:.14em; text-transform:uppercase; }}
    .notice,.card {{ border:1px solid var(--line); border-radius:20px;
      background:var(--paper); padding:22px; }}
    .notice {{ margin:20px 0; border-left:5px solid var(--sage); background:var(--pale); }}
    .notice.write {{ border-left-color:var(--warn); background:#fff8eb; }}
    .layout {{ display:grid; grid-template-columns:minmax(260px,.72fr) minmax(0,1.8fr); gap:18px; }}
    .queue {{ position:sticky; top:18px; align-self:start; }}
    .queue button {{ width:100%; margin:9px 0 0; text-align:left; border:1px solid var(--line);
      color:var(--ink); background:#f8faf9; border-radius:13px; padding:13px; cursor:pointer; }}
    .queue button.active {{ border-color:var(--sage); background:var(--pale); }}
    .queue small,.quiet {{ color:var(--muted); font-size:.84rem; }}
    .row {{ display:flex; justify-content:space-between; gap:14px; align-items:flex-start; }}
    .badge {{ display:inline-block; border-radius:999px; padding:5px 9px; background:var(--pale);
      color:var(--deep); font-size:.76rem; font-weight:800; }}
    .block {{ margin-top:14px; padding:16px; background:#f7f9f8; border-radius:14px; }}
    .source {{ border-left:3px solid var(--sage); }}
    .domain {{ display:grid; grid-template-columns:70px 1fr; gap:12px; }}
    .weight {{ color:var(--deep); font-weight:850; font-size:1.05rem; }}
    a {{ color:var(--deep); overflow-wrap:anywhere; }}
    label {{ display:block; margin:14px 0 6px; font-size:.88rem; font-weight:800; }}
    input,select,textarea {{ width:100%; border:1px solid #adc3bd; border-radius:10px;
      padding:11px 12px; color:var(--ink); background:white; font:inherit; }}
    textarea {{ min-height:88px; resize:vertical; }}
    .checks {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:14px; }}
    .check {{ display:flex; gap:10px; align-items:flex-start; padding:13px; background:var(--warm); border-radius:11px; }}
    .check input {{ width:auto; margin-top:3px; }}
    .check label {{ margin:0; font-weight:650; }}
    .actions {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:16px; }}
    .actions button {{ border:0; border-radius:999px; padding:11px 18px; color:white;
      background:var(--sage); font-weight:800; cursor:pointer; }}
    .actions .secondary {{ color:var(--deep); background:var(--pale); border:1px solid var(--line); }}
    .actions button:disabled {{ opacity:.42; cursor:not-allowed; }}
    .status {{ margin-top:14px; padding:13px; border-radius:11px; background:var(--pale);
      color:var(--deep); white-space:pre-wrap; }}
    .status.error {{ color:var(--danger); background:#fff0ed; }}
    .hidden {{ display:none; }}
    .boundary {{ border-left:4px solid var(--sage); padding-left:13px; }}
    code {{ font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:.82em; overflow-wrap:anywhere; }}
    @media(max-width:800px) {{ .layout {{ grid-template-columns:1fr; }} .queue {{ position:static; }}
      .checks {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <header>
    <div class="eyebrow">PIA · Phase 3A · Participant-free reference review</div>
    <h1>Review what a credential means.</h1>
    <p>Inspect the issuer sources, bounded summary, and domain elements before making the definition reusable.</p>
  </header>
  <section id="modeNotice" class="notice">
    <strong id="modeTitle"></strong>
    <p id="modeText"></p>
  </section>
  <div class="layout">
    <aside class="card queue">
      <div class="eyebrow">Review queue</div>
      <h2>Definition packages</h2>
      <p class="quiet">Only shared public-reference material appears here.</p>
      <div id="queue"></div>
    </aside>
    <section class="card">
      <div id="empty">
        <div class="eyebrow">Select a package</div>
        <h2>Nothing has been changed.</h2>
        <p>Choose a definition from the queue to inspect its proposal, public sources, domains, and limits.</p>
      </div>
      <div id="workspace" class="hidden">
        <div class="row">
          <div>
            <div class="eyebrow">Credential definition</div>
            <h2 id="title"></h2>
            <div id="version" class="quiet"></div>
          </div>
          <span id="reviewState" class="badge"></span>
        </div>
        <div class="block boundary">
          <strong>Negative boundary</strong>
          <p id="boundary"></p>
        </div>
        <h3>Bounded definition</h3>
        <p id="summary"></p>
        <div id="sources"></div>
        <div id="domains"></div>
        <div class="block">
          <div class="eyebrow">Accountable decision</div>
          <label for="reviewer">Reviewer actor ID</label>
          <input id="reviewer" value="credential-reviewer-local-001" maxlength="80">
          <div class="quiet">Use an accountable process identity, not a participant name or email.</div>
          <label for="role">Reviewer role</label>
          <select id="role">
            <option value="credential_definition_reviewer">Credential definition reviewer</option>
            <option value="assurance_reviewer">Assurance reviewer</option>
            <option value="governance_reviewer">Governance reviewer</option>
          </select>
          <label for="decision">Decision</label>
          <select id="decision">
            <option value="accepted_with_limits">Accept with explicit limits</option>
            <option value="accepted">Accept</option>
            <option value="revision_requested">Request revision</option>
            <option value="disputed">Dispute</option>
            <option value="rejected">Reject</option>
          </select>
          <label for="basis">Review basis</label>
          <textarea id="basis" placeholder="State what was checked and why the decision is warranted."></textarea>
          <label for="limits">Limitations</label>
          <textarea id="limits" placeholder="Required for acceptance with limits. State version, effective-date, source, or scope limits."></textarea>
          <div class="checks">
            <div class="check"><input id="sourceCheck" type="checkbox"><label for="sourceCheck">I inspected the listed sources and integrity metadata.</label></div>
            <div class="check"><input id="boundaryCheck" type="checkbox"><label for="boundaryCheck">I checked the negative boundary and did not infer participant claims.</label></div>
          </div>
          <div class="actions">
            <button id="preview" class="secondary">Preview decision</button>
            <button id="apply" disabled>Apply reviewed change</button>
          </div>
          <div id="status" class="status hidden"></div>
        </div>
      </div>
    </section>
  </div>
</main>
<script>
const TOKEN={token};
const WRITE_ENABLED={write_value};
let packages=[];
let selected=null;
const byId=(id)=>document.getElementById(id);
const notice=byId("modeNotice");
if(WRITE_ENABLED){{
  notice.classList.add("write");
  byId("modeTitle").textContent="Controlled write mode is enabled.";
  byId("modeText").textContent="Preview first. Applying a decision updates the participant-free catalog and appends review history. It does not touch participant intake or a graph.";
}}else{{
  byId("modeTitle").textContent="Preview-only mode.";
  byId("modeText").textContent="You can inspect and validate projected decisions, but this server cannot change the catalog. Restart with the explicit write option only when an accountable review is ready.";
}}
function showStatus(message,error=false){{
  byId("status").textContent=message;
  byId("status").className="status"+(error?" error":"");
}}
async function request(path,options={{}}){{
  options.headers={{...(options.headers||{{}}),"X-PIA-Local-Token":TOKEN}};
  const response=await fetch(path,options);
  const data=await response.json();
  if(!response.ok) throw new Error(data.error||"The local review request failed.");
  return data;
}}
function text(tag,value,className=""){{
  const node=document.createElement(tag); node.textContent=value||""; if(className)node.className=className; return node;
}}
function renderQueue(){{
  const target=byId("queue"); target.replaceChildren();
  if(!packages.length){{ target.append(text("p","No definitions are currently ready for review.","quiet")); return; }}
  packages.forEach((item,index)=>{{
    const def=item.credential_definition;
    const button=document.createElement("button");
    button.className=selected===item?"active":"";
    button.append(text("strong",def.canonical_title));
    button.append(document.createElement("br"));
    button.append(text("small",(def.acronym||"No acronym")+" · "+def.review_status));
    button.addEventListener("click",()=>selectPackage(index));
    target.append(button);
  }});
}}
function selectPackage(index){{
  selected=packages[index]; renderQueue();
  byId("empty").classList.add("hidden"); byId("workspace").classList.remove("hidden");
  const def=selected.credential_definition;
  byId("title").textContent=def.canonical_title+" ("+def.acronym+")";
  byId("version").textContent=selected.credential_issuer.canonical_name+" · "+def.version_label;
  byId("reviewState").textContent=def.definition_status+" / "+def.review_status;
  byId("boundary").textContent=def.negative_boundary;
  byId("summary").textContent=def.domain_summary;
  const sourceBox=byId("sources"); sourceBox.replaceChildren(); sourceBox.append(text("h3","Issuer sources"));
  selected.sources.forEach(source=>{{
    const block=text("div","", "block source");
    block.append(text("strong",source.document_title));
    block.append(text("p",source.relevant_section_locator));
    const link=document.createElement("a"); link.href=source.resolved_uri; link.target="_blank"; link.rel="noopener noreferrer"; link.textContent="Open issuer source";
    block.append(link); block.append(document.createElement("br"));
    block.append(text("code",source.content_checksum+" · "+source.content_size_bytes+" bytes"));
    sourceBox.append(block);
  }});
  const domainBox=byId("domains"); domainBox.replaceChildren(); domainBox.append(text("h3","Assessed domains"));
  selected.domain_elements.forEach(domain=>{{
    const block=text("div","", "block domain");
    block.append(text("div",(domain.weight_percent||"—")+"%","weight"));
    const detail=document.createElement("div"); detail.append(text("strong",domain.title)); detail.append(text("p",domain.summary)); detail.append(text("small",domain.source_locator,"quiet")); block.append(detail);
    domainBox.append(block);
  }});
  byId("apply").disabled=true; byId("status").className="status hidden";
}}
function payload(){{
  return {{
    credential_definition_id:selected.credential_definition.credential_definition_id,
    reviewer_actor_id:byId("reviewer").value,
    reviewer_role:byId("role").value,
    decision:byId("decision").value,
    review_basis:byId("basis").value,
    limitations:byId("limits").value,
    review_cycle:"annual",
    sources_reviewed:byId("sourceCheck").checked,
    boundary_reviewed:byId("boundaryCheck").checked
  }};
}}
byId("preview").addEventListener("click",async()=>{{
  if(!selected)return;
  byId("preview").disabled=true; byId("apply").disabled=true;
  try{{
    const result=await request("/api/review/preview",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify(payload())}});
    showStatus("Preview passed catalog validation.\\nProjected resolver state: "+result.projected_resolution_status+"\\nReview records to append: "+result.review_record_ids.length+"\\nParticipant claims established: 0");
    byId("apply").disabled=!WRITE_ENABLED;
  }}catch(error){{ showStatus(error.message,true); }}
  finally{{ byId("preview").disabled=false; }}
}});
byId("apply").addEventListener("click",async()=>{{
  if(!selected||!WRITE_ENABLED)return;
  if(!window.confirm("Apply this reviewed decision to the participant-free catalog?"))return;
  byId("apply").disabled=true;
  try{{
    const body={{...payload(),confirm_catalog_change:"APPLY REVIEW"}};
    const result=await request("/api/review/apply",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify(body)}});
    showStatus("Review applied and the installed catalog revalidated.\\nDecision: "+result.decision+"\\nReview records appended: "+result.review_record_ids.length);
    await loadQueue();
  }}catch(error){{ showStatus(error.message,true); }}
}});
async function loadQueue(){{
  try{{ packages=await request("/api/review-queue"); selected=null; renderQueue();
    byId("workspace").classList.add("hidden"); byId("empty").classList.remove("hidden");
  }}catch(error){{ byId("queue").append(text("p",error.message,"quiet")); }}
}}
loadQueue();
</script>
</body>
</html>"""


class CredentialReviewHTTPServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        service: CredentialDefinitionReviewService,
        *,
        allow_catalog_writes: bool,
    ) -> None:
        super().__init__(server_address, CredentialReviewHandler)
        self.service = service
        self.allow_catalog_writes = allow_catalog_writes
        self.local_token = secrets.token_urlsafe(32)


class CredentialReviewHandler(BaseHTTPRequestHandler):
    server: CredentialReviewHTTPServer

    def do_GET(self) -> None:  # noqa: N802
        try:
            path = urlsplit(self.path).path
            if path == "/":
                self._send_html(
                    _page(
                        self.server.local_token,
                        self.server.allow_catalog_writes,
                    )
                )
            elif path == "/api/status":
                self._send_json(
                    {
                        **self.server.service.status(),
                        "write_enabled": self.server.allow_catalog_writes,
                    }
                )
            elif path == "/api/review-queue":
                self._require_token()
                self._send_json(self.server.service.list_review_queue())
            else:
                self._send_json(
                    {"error": "Route not found."}, HTTPStatus.NOT_FOUND
                )
        except CredentialReviewError as exc:
            self._send_json(
                {"error": str(exc)}, HTTPStatus.BAD_REQUEST
            )

    def do_POST(self) -> None:  # noqa: N802
        try:
            self._require_token()
            body = self._read_json()
            request = CredentialReviewRequest.from_mapping(body)
            path = urlsplit(self.path).path
            if path == "/api/review/preview":
                self._send_json(self.server.service.preview(request))
            elif path == "/api/review/apply":
                if not self.server.allow_catalog_writes:
                    self._send_json(
                        {
                            "error": (
                                "Catalog writes are disabled. Restart with "
                                "--allow-catalog-writes after review."
                            )
                        },
                        HTTPStatus.FORBIDDEN,
                    )
                elif body.get("confirm_catalog_change") != "APPLY REVIEW":
                    self._send_json(
                        {"error": "Explicit catalog-change confirmation is required."},
                        HTTPStatus.BAD_REQUEST,
                    )
                else:
                    self._send_json(self.server.service.apply(request))
            else:
                self._send_json(
                    {"error": "Route not found."}, HTTPStatus.NOT_FOUND
                )
        except CredentialReviewError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            self._send_json(
                {"error": f"Invalid request: {exc}"},
                HTTPStatus.BAD_REQUEST,
            )

    def _require_token(self) -> None:
        if not secrets.compare_digest(
            self.headers.get("X-PIA-Local-Token", ""),
            self.server.local_token,
        ):
            raise CredentialReviewError("Local request token is missing or invalid.")

    def _read_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Content-Length must be numeric.") from exc
        if length <= 0 or length > MAX_REQUEST_BYTES:
            raise ValueError("Request size is invalid.")
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0]
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json.")
        value = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object.")
        return value

    def _send_html(self, value: str) -> None:
        body = value.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self._security_headers("text/html; charset=utf-8", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(
        self, value: Any, status: HTTPStatus = HTTPStatus.OK
    ) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._security_headers("application/json; charset=utf-8", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _security_headers(self, content_type: str, content_length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            (
                "default-src 'none'; style-src 'unsafe-inline'; "
                "script-src 'unsafe-inline'; connect-src 'self'; "
                "img-src 'self'; base-uri 'none'; frame-ancestors 'none'; "
                "form-action 'self'"
            ),
        )

    def log_message(self, format: str, *args: object) -> None:
        return


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the localhost-only participant-free Phase 3A review workbench."
        )
    )
    parser.add_argument("--catalog-root", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--port", type=int, default=8790)
    parser.add_argument(
        "--allow-catalog-writes",
        action="store_true",
        help="Permit confirmed review decisions to update the catalog.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    service = CredentialDefinitionReviewService(
        args.catalog_root, args.contract
    )
    status = service.status()
    server = CredentialReviewHTTPServer(
        (LOCAL_HOST, args.port),
        service,
        allow_catalog_writes=args.allow_catalog_writes,
    )
    mode = "controlled write" if args.allow_catalog_writes else "preview-only"
    print(
        f"PIA Phase 3A review workbench ({mode})\n"
        f"Catalog contract: {status['contract_version']}\n"
        f"Open http://{LOCAL_HOST}:{args.port}/\n"
        "Press Ctrl+C to stop."
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
