import assert from "node:assert/strict";
import { access } from "node:fs/promises";
import test from "node:test";

const templateRoot = new URL("../", import.meta.url);

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request(`http://localhost${path}`, {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the private participant start and document intake", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(
    html,
    /<title>Begin private participant intake · PIA intake<\/title>/i,
  );
  assert.match(html, /Your experience tells a bigger story/);
  assert.match(html, /Drop or choose initial documents/);
  assert.match(html, /Participant reference and initial documents/);
  assert.match(html, /document type/i);
  assert.match(html, /No name or email required/);
  assert.match(html, /Nothing is uploaded/);
  assert.match(html, /Continue with selected documents/);
  assert.match(html, /og-v5\.png/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton/i);
});

test("server-renders the congruent quick credential review queue", async () => {
  const response = await render("/credentials");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(
    html,
    /<title>Quick credential check-in · PIA intake<\/title>/i,
  );
  assert.match(html, /A few quick choices will make your experience clearer/);
  assert.match(html, /Your evidence is yours/);
  assert.match(html, /Participant-controlled/);
  assert.match(html, /og-v5\.png/);
  assert.match(html, /Which answer is closest/);
  assert.match(html, /I used this in my work/);
  assert.match(html, /Training only so far/);
  assert.match(html, /This needs a correction/);
  assert.match(html, /Add detail or a source/);
  assert.match(html, /This test screen stores nothing/);
  assert.match(html, /Privacy commitments/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton/i);
});

test("server-renders the optional report-to-document handoff", async () => {
  const response = await render("/report");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(html, /Your participant overview is ready/);
  assert.match(html, /Put this report to work/);
  assert.match(html, /LinkedIn profile/);
  assert.match(html, /Résumé/);
  assert.match(html, /Chronological CV/);
  assert.match(html, /Your source stays unchanged/);
  assert.match(html, /No automatic publishing/);
  assert.match(html, /View full report/);
  assert.match(html, /Add executive summary to full report/);
  assert.match(html, /View technical breakdown/);
  assert.match(html, /Add to full report/);
  assert.match(html, /Private by design/);
});

test("server-renders the complete evidence report", async () => {
  const response = await render("/report/full");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(html, /The evidence behind the professional overview/);
  assert.match(html, /Executive summary/);
  assert.match(html, /Professional narrative/);
  assert.match(html, /Capability and evidence register/);
  assert.match(html, /Confidence and evidence statistics/);
  assert.match(html, /30/);
  assert.match(html, /evidence references reviewed/);
  assert.match(html, /Update my evidence/);
  assert.doesNotMatch(html, />Reviewable</);
  assert.match(html, /changes report composition only/);
});

test("server-renders the privacy commitments and production boundary", async () => {
  const response = await render("/privacy");
  assert.equal(response.status, 200);

  const html = await response.text();
  assert.match(html, /Your evidence is yours/);
  assert.match(html, /No participant PII in the repository/);
  assert.match(html, /No silent storage in this prototype/);
  assert.match(html, /encrypted in transit/);
  assert.match(html, /Encryption at rest/);
  assert.match(html, /Required safeguards—not future conveniences/);
});

test("removes the disposable starter preview", async () => {
  await assert.rejects(access(new URL("../app/_sites-preview", templateRoot)));
});
