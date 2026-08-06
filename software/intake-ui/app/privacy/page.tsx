import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy commitments",
  description:
    "PIA privacy guarantees, current prototype boundaries, and required production safeguards.",
};

const currentCommitments = [
  {
    title: "Private by default",
    text: "Participant information is treated as private unless a clear purpose, consent basis, and authorization establish another boundary.",
  },
  {
    title: "No participant PII in the repository",
    text: "Automated governance checks prevent participant datasets, participant reports, and participant-linked graph exports from entering the tracked source repository.",
  },
  {
    title: "No silent storage in this prototype",
    text: "Choices, notes, document selections, and report composition remain in browser memory and disappear when the page reloads.",
  },
  {
    title: "Private browser-created downloads",
    text: "Editable drafts are created in the browser rather than uploaded by this interface. The site connection is HTTPS, so delivery is encrypted in transit.",
  },
  {
    title: "No silent external sharing",
    text: "Participant information is not transmitted to another service without an authorized purpose and a visible processing boundary.",
  },
  {
    title: "Participant correction remains available",
    text: "Interpretations are revisable. Participants must be able to correct, dispute, export, or withdraw information within the governing retention rules.",
  },
];

const productionRequirements = [
  "Encryption at rest for any retained original, working copy, or exported report",
  "Least-privilege access separated by intake, evidence, interpretation, and reporting role",
  "Explicit retention and deletion periods, including withdrawal handling",
  "Purpose-bound consent before participant data is collected or processed",
  "Auditable records of authorized remote processing and external transmission",
  "Separate restricted originals and sanitized working representations",
];

export default function PrivacyPage() {
  return (
    <main className="privacy-page-shell">
      <header className="page-header">
        <div>
          <p className="brand">PIA</p>
          <p className="session-label">Privacy foundation</p>
        </div>
        <a className="quiet-button" href="/report/full">
          Back to full report
        </a>
      </header>

      <section className="privacy-page-heading">
        <p className="eyebrow">Foundational commitment</p>
        <h1>Your evidence is yours.</h1>
        <p>
          Privacy is not an optional setting in PIA. It is a boundary on how
          evidence may be collected, interpreted, retained, shared, and used.
        </p>
      </section>

      <section className="privacy-status-card">
        <div>
          <span>Current test interface</span>
          <strong>No real participant data is required or retained here.</strong>
        </div>
        <p>
          The guarantees below describe this working prototype. Production use
          with participant data requires the additional safeguards listed
          separately.
        </p>
      </section>

      <section className="privacy-commitment-grid">
        {currentCommitments.map((commitment) => (
          <article key={commitment.title}>
            <span aria-hidden="true">✓</span>
            <div>
              <h2>{commitment.title}</h2>
              <p>{commitment.text}</p>
            </div>
          </article>
        ))}
      </section>

      <section className="production-boundary">
        <div>
          <p className="eyebrow">Before production participant intake</p>
          <h2>Required safeguards—not future conveniences</h2>
          <p>
            PIA will not describe retained participant data as protected until
            these controls are implemented, tested, and governed.
          </p>
        </div>
        <ul>
          {productionRequirements.map((requirement) => (
            <li key={requirement}>{requirement}</li>
          ))}
        </ul>
      </section>

      <section className="privacy-page-footer">
        <div>
          <p className="eyebrow">Participant agency</p>
          <h2>Understand, correct, or stop the process.</h2>
          <p>
            No report should become more authoritative than the evidence and
            consent that support it.
          </p>
        </div>
        <a className="button button-primary" href="/report">
          Return to participant overview
        </a>
      </section>
    </main>
  );
}
