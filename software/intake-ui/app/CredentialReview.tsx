"use client";

import { useState } from "react";
import type { ChangeEvent } from "react";

type Decision = "applied" | "preparation" | "correct";
type QueueState = "ready" | "source" | "complete";

type Credential = {
  id: string;
  title: string;
  issuer: string;
  year: string;
  state: QueueState;
  meaning: string;
  domains: string[];
  limit: string;
};

const credentials: Credential[] = [
  {
    id: "sicp",
    title: "Incident Coordination Professional",
    issuer: "Synthetic Response Institute",
    year: "2026",
    state: "ready",
    meaning:
      "Preparation in incident coordination, cross-role communication, and bounded response planning.",
    domains: ["Incident coordination", "Communication", "Response planning"],
    limit:
      "The credential alone does not prove workplace use, performance quality, or decision authority.",
  },
  {
    id: "spco",
    title: "Security Project Coordination",
    issuer: "Synthetic Security Council",
    year: "2024",
    state: "ready",
    meaning:
      "Preparation in planning security work, coordinating dependencies, and communicating project status.",
    domains: ["Project planning", "Coordination", "Status communication"],
    limit:
      "The credential does not by itself establish project ownership, scale, or delivery results.",
  },
  {
    id: "wlf",
    title: "Workforce Learning Facilitation",
    issuer: "Synthetic Learning Guild",
    year: "2023",
    state: "ready",
    meaning:
      "Preparation in facilitating adult learning, explaining procedures, and supporting knowledge transfer.",
    domains: ["Facilitation", "Knowledge transfer", "Learning support"],
    limit:
      "Completion does not prove teaching effectiveness or formal responsibility for a learning program.",
  },
  {
    id: "ndf",
    title: "Network Defense Foundations",
    issuer: "Synthetic Technology Academy",
    year: "2022",
    state: "ready",
    meaning:
      "Foundational preparation in network risk, defensive controls, and security monitoring concepts.",
    domains: ["Network risk", "Defensive controls", "Monitoring"],
    limit:
      "Coursework is educational evidence, not proof of production-level technical performance.",
  },
  {
    id: "lcw",
    title: "Leading Collaborative Work",
    issuer: "Issuer source needed",
    year: "2021",
    state: "source",
    meaning: "",
    domains: [],
    limit: "",
  },
  {
    id: "bcm",
    title: "Business Continuity Methods",
    issuer: "Edition not yet confirmed",
    year: "2020",
    state: "source",
    meaning: "",
    domains: [],
    limit: "",
  },
  {
    id: "cfs",
    title: "Customer-Facing Systems",
    issuer: "Synthetic Service Institute",
    year: "2019",
    state: "complete",
    meaning: "",
    domains: [],
    limit: "",
  },
  {
    id: "fsa",
    title: "Foundations of Safety Administration",
    issuer: "Synthetic Safety Board",
    year: "2018",
    state: "complete",
    meaning: "",
    domains: [],
    limit: "",
  },
];

const decisionOptions: {
  value: Decision;
  label: string;
  detail: string;
}[] = [
  {
    value: "applied",
    label: "I used this in my work",
    detail: "PIA may look for connections to roles, projects, or accomplishments.",
  },
  {
    value: "preparation",
    label: "Training only so far",
    detail: "Keep it as educational preparation without claiming workplace use.",
  },
  {
    value: "correct",
    label: "This needs a correction",
    detail: "Flag the title or suggested meaning for a closer review.",
  },
];

export function CredentialReview() {
  const readyCredentials = credentials.filter((item) => item.state === "ready");
  const sourceNeededCredentials = credentials.filter(
    (item) => item.state === "source",
  );
  const [activeId, setActiveId] = useState(readyCredentials[0].id);
  const [decisions, setDecisions] = useState<Record<string, Decision>>({});
  const [draftDecision, setDraftDecision] = useState<Decision | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [note, setNote] = useState("");
  const [sourceLink, setSourceLink] = useState("");
  const [fileName, setFileName] = useState("");
  const [view, setView] = useState<"review" | "complete" | "paused">("review");

  const activeCredential =
    readyCredentials.find((item) => item.id === activeId) ?? readyCredentials[0];
  const reviewedCount = Object.keys(decisions).length;
  const totalRecognized =
    credentials.filter((item) => item.state === "complete").length + reviewedCount;
  const remainingCount = readyCredentials.length - reviewedCount;

  const activePosition =
    readyCredentials.findIndex((item) => item.id === activeCredential.id) + 1;

  function selectCredential(id: string) {
    setActiveId(id);
    setDraftDecision(decisions[id] ?? null);
    setDetailsOpen(false);
    setNote("");
    setSourceLink("");
    setFileName("");
    setView("review");
  }

  function saveAndContinue() {
    if (!draftDecision) return;

    const nextDecisions = {
      ...decisions,
      [activeCredential.id]: draftDecision,
    };
    setDecisions(nextDecisions);

    const nextCredential = readyCredentials.find(
      (item) => !nextDecisions[item.id],
    );

    if (!nextCredential) {
      setView("complete");
      return;
    }

    setActiveId(nextCredential.id);
    setDraftDecision(null);
    setDetailsOpen(false);
    setNote("");
    setSourceLink("");
    setFileName("");
  }

  function handleFile(event: ChangeEvent<HTMLInputElement>) {
    setFileName(event.target.files?.[0]?.name ?? "");
  }

  if (view === "paused") {
    return (
      <main className="page-shell">
        <section className="completion-card">
          <span className="completion-mark soft" aria-hidden="true">
            ↗
          </span>
          <p className="eyebrow">Review paused</p>
          <h1>Your place is held for this example session.</h1>
          <p>
            You have reviewed {reviewedCount} of {readyCredentials.length} ready
            credentials. In the working prototype, this place lasts only until
            the page reloads.
          </p>
          <div className="completion-actions">
            <button
              className="button button-primary"
              onClick={() => setView("review")}
              type="button"
            >
              Return to quick review
            </button>
          </div>
          <p className="prototype-note centered">
            A production intake service would save this checkpoint privately.
          </p>
        </section>
      </main>
    );
  }

  if (view === "complete") {
    return (
      <main className="page-shell">
        <section className="completion-card">
          <span className="completion-mark" aria-hidden="true">
            ✓
          </span>
          <p className="eyebrow">Quick review complete</p>
          <h1>You answered everything that was ready today.</h1>
          <p>
            Four credential meanings now have your context. Two items still need
            a source before PIA can explain them responsibly.
          </p>
          <div className="completion-summary">
            <span>
              <strong>{totalRecognized}</strong> recognized
            </span>
            <span>
              <strong>2</strong> need a source
            </span>
            <span>
              <strong>0</strong> waiting on you
            </span>
          </div>
          <div className="completion-actions">
            <button
              className="button button-secondary"
              onClick={() => {
                selectCredential(readyCredentials[0].id);
              }}
              type="button"
            >
              Review my answers
            </button>
            <button
              className="button button-primary"
              onClick={() => window.location.assign("/report")}
              type="button"
            >
              View example end report
            </button>
          </div>
          <p className="prototype-note centered">
            Working prototype: answers and selected files disappear when the page
            reloads.
          </p>
        </section>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <header className="page-header">
        <div>
          <p className="brand">PIA</p>
          <p className="session-label">Private intake · Example session</p>
        </div>
        <div className="header-actions">
          <a className="privacy-link" href="/privacy">
            Privacy commitments
          </a>
          <a className="quiet-button" href="/report">
            Preview end report
          </a>
          <button
            className="quiet-button"
            onClick={() => setView("paused")}
            type="button"
          >
            Save and finish later
          </button>
        </div>
      </header>

      <section className="intake-hero">
        <div className="intake-hero-copy">
          <p className="eyebrow">Credential evidence intake</p>
          <h1>A few quick choices will make your experience clearer.</h1>
          <p>
            We found eight trainings and credentials. Four already have a draft
            explanation. Choose the closest answer for each one; details are
            optional.
          </p>
          <div className="intake-hero-tags" aria-label="Intake commitments">
            <span>Private</span>
            <span>Traceable</span>
            <span>Participant-controlled</span>
          </div>
        </div>
        <figure className="intake-hero-visual">
          <img
            alt="PIA professional identity and technical evidence report preview"
            height="1024"
            src="/og-v5.png"
            width="1536"
          />
          <figcaption>
            Your evidence remains the foundation of every interpretation.
          </figcaption>
        </figure>
      </section>

      <aside className="intake-assurance-row">
        <div>
          <strong>Your evidence is yours.</strong>
          <span>No score or ranking</span>
          <span>Nothing is added to the graph without review</span>
          <span>This prototype stores nothing after reload</span>
        </div>
        <a href="/privacy">See privacy commitments</a>
      </aside>

      <section className="intake-workspace-heading">
        <div>
          <p className="eyebrow">Review workspace</p>
          <h2>Confirm what each credential contributes.</h2>
        </div>
        <p>Check the meaning, choose the closest fit, and continue.</p>
      </section>

      <ol aria-label="Review flow" className="flow-strip">
        <li className="active">
          <span>1</span>
          <div>
            <strong>Check</strong>
            <small>Read the short meaning</small>
          </div>
        </li>
        <li>
          <span>2</span>
          <div>
            <strong>Choose</strong>
            <small>Select the closest fit</small>
          </div>
        </li>
        <li>
          <span>3</span>
          <div>
            <strong>Continue</strong>
            <small>PIA handles the detail</small>
          </div>
        </li>
      </ol>

      <section className="overview-bar" aria-label="Credential review summary">
        <div>
          <strong>{totalRecognized}</strong>
          <span>recognized</span>
        </div>
        <div>
          <strong>2</strong>
          <span>need a source</span>
        </div>
        <div>
          <strong>{remainingCount}</strong>
          <span>need a quick answer</span>
        </div>
        <div className="overall-progress">
          <div>
            <span>Today’s review</span>
            <strong>{reviewedCount} of {readyCredentials.length}</strong>
          </div>
          <div
            aria-label={`${reviewedCount} of ${readyCredentials.length} reviewed`}
            aria-valuemax={readyCredentials.length}
            aria-valuemin={0}
            aria-valuenow={reviewedCount}
            className="progress-track"
            role="progressbar"
          >
            <span
              className="progress-fill"
              style={{ width: `${(reviewedCount / readyCredentials.length) * 100}%` }}
            />
          </div>
        </div>
      </section>

      <div className="review-layout">
        <aside className="credential-queue">
          <div className="queue-heading">
            <div>
              <p className="eyebrow">Ready now</p>
              <h2>Quick review</h2>
            </div>
            <span>{remainingCount} left</span>
          </div>

          <div className="queue-list">
            {readyCredentials.map((credential, index) => {
              const decision = decisions[credential.id];
              return (
                <button
                  aria-current={credential.id === activeCredential.id}
                  className="queue-item"
                  key={credential.id}
                  onClick={() => selectCredential(credential.id)}
                  type="button"
                >
                  <span className={`queue-number ${decision ? "done" : ""}`}>
                    {decision ? "✓" : index + 1}
                  </span>
                  <span>
                    <strong>{credential.title}</strong>
                    <small>
                      {decision
                        ? decisionOptions.find((item) => item.value === decision)
                            ?.label
                        : `${credential.issuer} · ${credential.year}`}
                    </small>
                  </span>
                </button>
              );
            })}
          </div>

          <details className="source-group">
            <summary>
              <strong>Needs a source</strong>
              <span>{sourceNeededCredentials.length}</span>
            </summary>
            <p>
              You can add a link or document later. These do not block today’s
              quick review.
            </p>
            <ul>
              {sourceNeededCredentials.map((credential) => (
                <li key={credential.id}>
                  <strong>{credential.title}</strong>
                  <span>{credential.issuer}</span>
                </li>
              ))}
            </ul>
          </details>
        </aside>

        <section
          aria-labelledby="active-credential-title"
          className="review-card"
        >
          <div className="review-card-header">
            <div>
              <p className="step-label">
                Credential {activePosition} of {readyCredentials.length}
              </p>
              <h2 id="active-credential-title">{activeCredential.title}</h2>
              <p>
                {activeCredential.issuer} · {activeCredential.year}
              </p>
            </div>
            <span className="status-pill">Draft meaning ready</span>
          </div>

          <div className="meaning-block">
            <p className="eyebrow">What this may show</p>
            <p className="meaning-copy">{activeCredential.meaning}</p>
            <div className="domain-list" aria-label="Suggested areas">
              {activeCredential.domains.map((domain) => (
                <span key={domain}>{domain}</span>
              ))}
            </div>
            <p className="limit-note">
              <strong>PIA keeps this boundary:</strong> {activeCredential.limit}
            </p>
          </div>

          <fieldset className="decision-panel">
            <legend>Which answer is closest?</legend>
            <p>Choose one. You can revise it later.</p>
            <div className="decision-list">
              {decisionOptions.map((option) => (
                <label
                  className={`decision-option ${
                    draftDecision === option.value ? "selected" : ""
                  }`}
                  key={option.value}
                >
                  <input
                    checked={draftDecision === option.value}
                    name="credential-decision"
                    onChange={() => setDraftDecision(option.value)}
                    type="radio"
                    value={option.value}
                  />
                  <span className="radio-mark" aria-hidden="true" />
                  <span>
                    <strong>{option.label}</strong>
                    <small>{option.detail}</small>
                  </span>
                </label>
              ))}
            </div>
          </fieldset>

          <div className="optional-panel">
            <button
              aria-expanded={detailsOpen}
              className="optional-toggle"
              onClick={() => setDetailsOpen((current) => !current)}
              type="button"
            >
              <span>
                <strong>Add detail or a source</strong>
                <small>Optional — skip this if the answer above is enough.</small>
              </span>
              <span aria-hidden="true">{detailsOpen ? "−" : "+"}</span>
            </button>

            {detailsOpen ? (
              <div className="optional-fields">
                <label>
                  <span>Short note</span>
                  <textarea
                    onChange={(event) => setNote(event.target.value)}
                    placeholder="Where did you use it, or what needs correction?"
                    value={note}
                  />
                </label>
                <div className="source-fields">
                  <label>
                    <span>Source link</span>
                    <input
                      onChange={(event) => setSourceLink(event.target.value)}
                      placeholder="https://"
                      type="url"
                      value={sourceLink}
                    />
                  </label>
                  <label className="file-field">
                    <span>Supporting file</span>
                    <input
                      accept=".pdf,.doc,.docx,.txt,.rtf,.csv"
                      onChange={handleFile}
                      type="file"
                    />
                    {fileName ? <small>{fileName}</small> : null}
                  </label>
                </div>
              </div>
            ) : null}
          </div>

          <div className="action-row">
            <button
              className="button button-secondary"
              onClick={() => {
                const nextCredential = readyCredentials.find(
                  (item) =>
                    item.id !== activeCredential.id && !decisions[item.id],
                );
                if (nextCredential) selectCredential(nextCredential.id);
              }}
              type="button"
            >
              Skip for now
            </button>
            <button
              className="button button-primary"
              disabled={!draftDecision}
              onClick={saveAndContinue}
              type="button"
            >
              {remainingCount === 1 && !decisions[activeCredential.id]
                ? "Finish quick review"
                : "Save and show next"}
            </button>
          </div>

          <p className="prototype-note">
            This test screen stores nothing. Your choice, notes, and selected
            files disappear when the page reloads.
          </p>
        </section>
      </div>
    </main>
  );
}
