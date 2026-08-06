#!/usr/bin/env python3
"""Localhost-only browser interface for the PIA Phase 2 synthetic sandbox.

artifact_id: component-pia-local-private-intake-ui-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from software.intake.local_private_intake import (
    MAX_ARTIFACT_BYTES,
    IntakePreflightError,
    LocalIntakeError,
    LocalIntakeStore,
)


MAX_REQUEST_BYTES = (MAX_ARTIFACT_BYTES * 4 // 3) + (1024 * 1024)
LOCAL_HOST = "127.0.0.1"


def _page(csrf_token: str) -> str:
    safe_token = json.dumps(csrf_token)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PIA Local Intake Sandbox</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #18323a; --muted: #60757b; --sage: #147a69; --pale: #edf5f2;
      --line: #cadbd6; --paper: #ffffff; --warm: #f5f1e8; --danger: #9c3c32;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; color: var(--ink); background: #f3f7f5;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    }}
    main {{ width: min(960px, calc(100% - 32px)); margin: 36px auto 64px; }}
    header {{ margin-bottom: 22px; }}
    .eyebrow {{ color: var(--sage); font-size: .78rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }}
    h1 {{ max-width: 760px; margin: 10px 0 8px; font: 700 clamp(2rem, 5vw, 3.5rem)/1.04 Georgia, serif; }}
    h2 {{ margin: 0 0 8px; font: 700 1.55rem/1.15 Georgia, serif; }}
    p {{ color: var(--muted); line-height: 1.55; }}
    .notice, .card {{ border: 1px solid var(--line); border-radius: 20px; background: var(--paper); padding: 24px; }}
    .notice {{ margin-bottom: 18px; background: var(--pale); border-left: 5px solid var(--sage); }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .card {{ margin-top: 18px; }}
    label {{ display: block; margin: 16px 0 7px; font-size: .9rem; font-weight: 750; }}
    input, select, textarea {{
      width: 100%; border: 1px solid #afc2bd; border-radius: 11px; padding: 12px 13px;
      color: var(--ink); background: white; font: inherit;
    }}
    textarea {{ min-height: 84px; resize: vertical; }}
    .check {{ display: flex; gap: 10px; align-items: flex-start; padding: 14px; margin-top: 16px; background: var(--warm); border-radius: 12px; }}
    .check input {{ width: auto; margin-top: 4px; }}
    button {{
      margin-top: 18px; border: 0; border-radius: 999px; padding: 12px 19px;
      color: white; background: var(--sage); font: 750 .95rem inherit; cursor: pointer;
    }}
    button:disabled {{ opacity: .45; cursor: not-allowed; }}
    .quiet {{ color: var(--muted); font-size: .86rem; }}
    .status {{ margin-top: 16px; padding: 12px 14px; border-radius: 11px; background: #f4f6f5; white-space: pre-wrap; }}
    .status.error {{ color: var(--danger); background: #fff1ef; }}
    .hidden {{ display: none; }}
    .result {{ border-top: 1px solid var(--line); margin-top: 15px; padding-top: 15px; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: .86em; overflow-wrap: anywhere; }}
    @media (max-width: 720px) {{ .grid {{ grid-template-columns: 1fr; }} main {{ margin-top: 20px; }} }}
  </style>
</head>
<body>
<main>
  <header>
    <div class="eyebrow">PIA · Phase 2 local sandbox</div>
    <h1>Start a governed intake session.</h1>
    <p>This is the first working local intake layer. It records authorization and purpose before accepting synthetic documents.</p>
  </header>

  <section class="notice">
    <strong>Synthetic test data only.</strong>
    <p>This page runs on this computer and does not connect to the hosted prototype, a remote AI service, or Neo4j. Encryption at rest and malware scanning are not implemented yet, so real participant documents are blocked at this stage.</p>
  </section>

  <div class="grid">
    <section class="card">
      <div class="eyebrow">1 · Preflight</div>
      <h2>Define this test.</h2>
      <label for="participant">Participant label</label>
      <input id="participant" value="Synthetic Intake Subject Alpha" maxlength="80">
      <label for="purpose">Purpose</label>
      <textarea id="purpose">Synthetic testing of the PIA intake and document-staging workflow.</textarea>
      <label for="scope">Processing scope</label>
      <select id="scope">
        <option value="credential_definition|capability_mapping|report_generation">Credentials, capability mapping, and report testing</option>
        <option value="credential_definition">Credential definition only</option>
        <option value="report_generation">Report testing only</option>
      </select>
      <label for="confidentiality">Confidentiality</label>
      <select id="confidentiality">
        <option value="participant_private">Participant-private test boundary</option>
        <option value="restricted">Restricted test boundary</option>
        <option value="internal">Internal synthetic test</option>
      </select>
      <div class="check">
        <input id="consent" type="checkbox">
        <label for="consent" style="margin:0">I confirm this dataset is synthetic and authorized for this stated test purpose.</label>
      </div>
      <button id="create">Create intake session</button>
      <div id="sessionStatus" class="status hidden"></div>
    </section>

    <section class="card">
      <div class="eyebrow">2 · Documents</div>
      <h2>Stage a test document.</h2>
      <p class="quiet">A SHA-256 fingerprint is created for each file. Exact duplicates are recorded without storing another copy.</p>
      <label for="file">Document</label>
      <input id="file" type="file" accept=".pdf,.doc,.docx,.rtf,.txt,.csv,.zip" disabled>
      <label for="documentType">Document type</label>
      <select id="documentType" disabled>
        <option value="">Choose a type</option>
        <option value="professional_profile">Professional profile</option>
        <option value="career_document">Career document</option>
        <option value="credential_learning">Credential or learning</option>
        <option value="supporting_evidence">Supporting evidence</option>
      </select>
      <button id="stage" disabled>Stage selected document</button>
      <div id="artifactStatus" class="status hidden"></div>
      <div id="results"></div>
    </section>
  </div>

  <section class="card">
    <div class="eyebrow">Current boundary</div>
    <h2>What this increment proves.</h2>
    <p>Session preflight, purpose and consent capture, local document staging, provenance metadata, content checksums, exact-duplicate detection, and an append-only audit trail are working. Extraction, credential explication, graph projection, encrypted participant storage, authentication, withdrawal, and deletion remain later governed work.</p>
  </section>
</main>
<script>
const TOKEN = {safe_token};
let sessionId = "";
const byId = (id) => document.getElementById(id);
function status(target, message, error = false) {{
  target.textContent = message;
  target.className = "status" + (error ? " error" : "");
}}
async function post(path, body) {{
  const response = await fetch(path, {{
    method: "POST",
    headers: {{ "Content-Type": "application/json", "X-PIA-Local-Token": TOKEN }},
    body: JSON.stringify(body)
  }});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "The local intake request failed.");
  return data;
}}
byId("create").addEventListener("click", async () => {{
  if (!byId("consent").checked) {{
    status(byId("sessionStatus"), "Confirm the synthetic-data authorization before continuing.", true);
    return;
  }}
  byId("create").disabled = true;
  try {{
    const result = await post("/api/sessions", {{
      participant_label: byId("participant").value,
      purpose: byId("purpose").value,
      processing_scope: byId("scope").value,
      confidentiality: byId("confidentiality").value,
      consent_status: "granted",
      retention_class: "synthetic_test"
    }});
    sessionId = result.intake_session_id;
    status(byId("sessionStatus"), "Session ready: " + sessionId);
    byId("file").disabled = false;
    byId("documentType").disabled = false;
    byId("stage").disabled = false;
  }} catch (error) {{
    status(byId("sessionStatus"), error.message, true);
    byId("create").disabled = false;
  }}
}});
byId("stage").addEventListener("click", async () => {{
  const file = byId("file").files[0];
  const documentType = byId("documentType").value;
  if (!sessionId || !file || !documentType) {{
    status(byId("artifactStatus"), "Choose a document and its type first.", true);
    return;
  }}
  if (file.size > {MAX_ARTIFACT_BYTES}) {{
    status(byId("artifactStatus"), "The selected document exceeds the 25 MB limit.", true);
    return;
  }}
  byId("stage").disabled = true;
  try {{
    const bytes = new Uint8Array(await file.arrayBuffer());
    let binary = "";
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {{
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }}
    const result = await post("/api/artifacts", {{
      intake_session_id: sessionId,
      original_filename: file.name,
      document_type: documentType,
      content_base64: btoa(binary)
    }});
    status(byId("artifactStatus"), result.disposition === "exact_duplicate"
      ? "Exact duplicate recognized. No additional file copy was stored."
      : "Document staged locally and its integrity fingerprint verified.");
    const item = document.createElement("div");
    item.className = "result";
    item.innerHTML = "<strong>" + file.name.replace(/[&<>\"']/g, "") + "</strong><br>"
      + "<span class='quiet'>" + result.source_artifact_id + " · " + result.document_type
      + " · <code>" + result.checksum.slice(0, 18) + "…</code></span>";
    byId("results").prepend(item);
    byId("file").value = "";
    byId("documentType").value = "";
  }} catch (error) {{
    status(byId("artifactStatus"), error.message, true);
  }} finally {{
    byId("stage").disabled = false;
  }}
}});
</script>
</body>
</html>"""


def create_server(
    store: LocalIntakeStore,
    *,
    port: int = 8788,
) -> tuple[ThreadingHTTPServer, str]:
    store.initialize()
    csrf_token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        server_version = "PIALocalIntake/0.1"

        def log_message(self, format: str, *args: Any) -> None:
            print(f"{self.log_date_time_string()} {format % args}")

        def _security_headers(self, content_type: str) -> None:
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; style-src 'unsafe-inline'; "
                "script-src 'unsafe-inline'; connect-src 'self'; "
                "img-src 'self' data:; form-action 'self'; frame-ancestors 'none'",
            )

        def _json(self, status: HTTPStatus, value: dict[str, Any]) -> None:
            body = json.dumps(value).encode("utf-8")
            self.send_response(status)
            self._security_headers("application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _authorized(self) -> bool:
            origin = self.headers.get("Origin")
            expected_origin = f"http://{LOCAL_HOST}:{self.server.server_port}"
            if origin and origin != expected_origin:
                return False
            return secrets.compare_digest(
                self.headers.get("X-PIA-Local-Token", ""),
                csrf_token,
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

        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if path == "/":
                body = _page(csrf_token).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self._security_headers("text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if path == "/api/status":
                self._json(
                    HTTPStatus.OK,
                    {
                        "status": "ready",
                        "mode": "synthetic",
                        "host": LOCAL_HOST,
                        "remote_processing": "disabled",
                        "graph_projection": "disabled",
                    },
                )
                return
            self._json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

        def do_POST(self) -> None:
            if not self._authorized():
                self._json(HTTPStatus.FORBIDDEN, {"error": "Request authorization failed."})
                return
            try:
                body = self._body()
                path = urlsplit(self.path).path
                if path == "/api/sessions":
                    session = store.create_session(
                        participant_id=store.next_synthetic_participant_id(),
                        participant_label=str(body.get("participant_label", "")),
                        purpose=str(body.get("purpose", "")),
                        processing_scope=str(body.get("processing_scope", "")),
                        consent_status=str(body.get("consent_status", "")),
                        confidentiality=str(body.get("confidentiality", "")),
                        retention_class=str(body.get("retention_class", "")),
                    )
                    self._json(
                        HTTPStatus.CREATED,
                        {
                            "intake_session_id": session["intake_session_id"],
                            "participant_id": session["participant_id"],
                            "processing_state": session["processing_state"],
                        },
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
                    )
                    self._json(
                        HTTPStatus.CREATED,
                        {
                            "source_artifact_id": artifact["source_artifact_id"],
                            "document_type": artifact["document_type"],
                            "checksum": artifact["checksum"],
                            "disposition": artifact["disposition"],
                            "duplicate_of_source_artifact_id": artifact[
                                "duplicate_of_source_artifact_id"
                            ],
                        },
                    )
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            except (IntakePreflightError, LocalIntakeError) as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    server = ThreadingHTTPServer((LOCAL_HOST, port), Handler)
    return server, csrf_token


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the localhost-only PIA Phase 2 synthetic intake sandbox."
    )
    parser.add_argument(
        "--storage-root",
        required=True,
        type=Path,
        help="Absolute private sandbox path outside the Git repository.",
    )
    parser.add_argument("--port", type=int, default=8788)
    args = parser.parse_args(argv)

    try:
        store = LocalIntakeStore(args.storage_root, mode="synthetic")
        server, _ = create_server(store, port=args.port)
    except (OSError, LocalIntakeError) as exc:
        parser.error(str(exc))

    print(f"PIA synthetic intake sandbox: http://{LOCAL_HOST}:{server.server_port}/")
    print("Boundary: synthetic test data only; no graph or remote processing.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
