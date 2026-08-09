"use client";

import { useMemo, useState } from "react";

type TargetId = "linkedin" | "resume" | "cv";
type Decision = "use" | "keep";
type Screen = "report" | "editor" | "ready";

type Suggestion = {
  id: string;
  label: string;
  current: string;
  proposed: string;
  explanation: string;
  evidence: string[];
  multiline?: boolean;
};

type DocumentTarget = {
  id: TargetId;
  name: string;
  description: string;
  items: string;
  suggestions: Suggestion[];
};

const targets: DocumentTarget[] = [
  {
    id: "linkedin",
    name: "LinkedIn profile",
    description:
      "Create an editable headline, About section, and capability list.",
    items: "Headline · About · Skills",
    suggestions: [
      {
        id: "linkedin-headline",
        label: "Headline",
        current: "Security and operations professional",
        proposed:
          "Security Operations | Incident Coordination | Program Development",
        explanation:
          "The report supports a clearer combination of operational, coordination, and program-building work.",
        evidence: [
          "Repeated security-operations responsibilities",
          "Cross-role incident coordination",
          "Documented program and process development",
        ],
      },
      {
        id: "linkedin-about",
        label: "About section",
        current:
          "Experienced professional with a background in security and operations.",
        proposed:
          "I strengthen security operations by connecting practical response work, cross-functional coordination, and durable program development. Across varied roles, I have helped teams clarify procedures, preserve operational knowledge, and move complex work toward reliable execution.",
        explanation:
          "This summary reflects the recurring pattern in the overview without adding an unsupported title, rank, or result.",
        evidence: [
          "Operational improvement pattern",
          "Knowledge-preservation evidence",
          "Coordination across group contexts",
        ],
        multiline: true,
      },
      {
        id: "linkedin-skills",
        label: "Capability section",
        current: "Security · Operations",
        proposed:
          "Incident Coordination · Operational Planning · Knowledge Transfer · Process Improvement · Stakeholder Communication",
        explanation:
          "These are supported capability labels, not a claim that every capability has the same evidence strength.",
        evidence: [
          "Capability evidence mapping",
          "Credential preparation with stated limits",
          "Role and project evidence",
        ],
      },
    ],
  },
  {
    id: "resume",
    name: "Résumé",
    description:
      "Create a concise professional summary and stronger evidence-based bullets.",
    items: "Summary · Accomplishment · Technical capabilities",
    suggestions: [
      {
        id: "resume-summary",
        label: "Professional summary",
        current:
          "Security professional experienced in operations, training, and project support.",
        proposed:
          "Security operations professional with experience coordinating incident response, improving operational processes, developing practical guidance, and supporting cross-functional delivery. Brings a systems-oriented approach to translating complex requirements into usable procedures and sustained team capability.",
        explanation:
          "The revised summary connects supported patterns while avoiding an overall score or inflated seniority claim.",
        evidence: [
          "Security and operational experience",
          "Process and guidance development",
          "Cross-functional delivery evidence",
        ],
        multiline: true,
      },
      {
        id: "resume-accomplishment",
        label: "Accomplishment bullet",
        current: "Helped maintain procedures and supported team operations.",
        proposed:
          "Developed and maintained operational guidance that clarified recurring work, preserved institutional knowledge, and supported more consistent team execution.",
        explanation:
          "The draft makes the demonstrated contribution clearer without inventing a percentage, scale, or business outcome.",
        evidence: [
          "Procedure-development artifacts",
          "Knowledge-preservation pattern",
          "Team-context evidence",
        ],
        multiline: true,
      },
      {
        id: "resume-capabilities",
        label: "Technical capabilities",
        current: "Security operations · Documentation",
        proposed:
          "Security Operations · Incident Coordination · Operational Documentation · Process Analysis · Knowledge Management · Project Coordination",
        explanation:
          "The list combines technical and delivery capabilities supported across the evidence package.",
        evidence: [
          "Role evidence",
          "Project evidence",
          "Relevant coursework and credentials",
        ],
      },
    ],
  },
  {
    id: "cv",
    name: "Chronological CV",
    description:
      "Create fuller role, project, education, and credential entries in time order.",
    items: "Role detail · Project entry · Credential context",
    suggestions: [
      {
        id: "cv-role",
        label: "Role detail",
        current: "Supported department security operations and documentation.",
        proposed:
          "Supported department security operations through response coordination, procedure development, operational documentation, and cross-role communication. Preserved working knowledge and helped translate requirements into repeatable practice.",
        explanation:
          "The expanded entry retains chronological context while making the evidenced work more explicit.",
        evidence: [
          "Role records",
          "Operational artifacts",
          "Group-context inference with limits",
        ],
        multiline: true,
      },
      {
        id: "cv-project",
        label: "Project entry",
        current: "Assisted with process improvement projects.",
        proposed:
          "Contributed to process-improvement efforts by examining recurring operational problems, coordinating input, documenting practical changes, and supporting adoption within the working group.",
        explanation:
          "The language represents collaborative contribution without claiming sole ownership or unsupported outcomes.",
        evidence: [
          "Project descriptions",
          "Shared problem-solving context",
          "Process-improvement pattern",
        ],
        multiline: true,
      },
      {
        id: "cv-credential",
        label: "Credential context",
        current: "Selected security and professional-development coursework.",
        proposed:
          "Selected security and professional-development coursework supporting preparation in physical security, network defense, incident coordination, operational planning, and adult learning.",
        explanation:
          "Coursework is presented as educational preparation, not proof of workplace performance.",
        evidence: [
          "Credential definitions",
          "Course domains",
          "Educational-evidence boundary",
        ],
        multiline: true,
      },
    ],
  },
];

const capabilityCards = [
  {
    title: "Systems and operations",
    level: "Strong evidence",
    text: "Improving processes, building practical guidance, and strengthening repeatable execution.",
    evidence: "Role records · Operational artifacts · Process documentation",
  },
  {
    title: "Coordination and delivery",
    level: "Supported",
    text: "Connecting people, requirements, and work across projects and operational settings.",
    evidence: "Project records · Group context · Coordination examples",
  },
  {
    title: "Knowledge and development",
    level: "Supported",
    text: "Preserving working knowledge, explaining procedures, and helping others build capability.",
    evidence: "Guidance artifacts · Training records · Knowledge-transfer examples",
  },
];

export function DocumentationUpdate() {
  const [screen, setScreen] = useState<Screen>("report");
  const [targetId, setTargetId] = useState<TargetId>("linkedin");
  const [decisions, setDecisions] = useState<Record<string, Decision>>({});
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [copied, setCopied] = useState(false);
  const [reportKept, setReportKept] = useState(false);
  const [summaryIncluded, setSummaryIncluded] = useState(false);
  const [technicalIncluded, setTechnicalIncluded] = useState(false);

  const target =
    targets.find((candidate) => candidate.id === targetId) ?? targets[0];
  const decidedCount = target.suggestions.filter(
    (suggestion) => decisions[suggestion.id],
  ).length;
  const fullReportQuery = [
    summaryIncluded ? "execsum=included" : "",
    technicalIncluded ? "tech=included" : "",
  ]
    .filter(Boolean)
    .join("&");
  const fullReportUrl = `/report/full${
    fullReportQuery ? `?${fullReportQuery}` : ""
  }`;

  const draftText = useMemo(() => {
    const lines = [
      `PIA ${target.name} draft`,
      "Example participant · Working prototype",
      "",
    ];

    for (const suggestion of target.suggestions) {
      const decision = decisions[suggestion.id];
      const value =
        decision === "use"
          ? drafts[suggestion.id] ?? suggestion.proposed
          : suggestion.current;
      lines.push(suggestion.label.toUpperCase(), value, "");
    }

    lines.push(
      "Draft boundary: This output reflects participant-approved choices from an evidence-based report. It should be reviewed before external use.",
    );
    return lines.join("\n");
  }, [decisions, drafts, target]);

  function chooseTarget(id: TargetId) {
    const nextTarget =
      targets.find((candidate) => candidate.id === id) ?? targets[0];
    setTargetId(id);
    setDecisions({});
    setDrafts(
      Object.fromEntries(
        nextTarget.suggestions.map((suggestion) => [
          suggestion.id,
          suggestion.proposed,
        ]),
      ),
    );
    setCopied(false);
    setScreen("editor");
  }

  function setDecision(id: string, decision: Decision) {
    setDecisions((current) => ({ ...current, [id]: decision }));
  }

  async function copyDraft() {
    await navigator.clipboard.writeText(draftText);
    setCopied(true);
  }

  function downloadDraft() {
    const blob = new Blob([draftText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `pia-${target.id}-draft.txt`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  if (screen === "ready") {
    return (
      <main className="report-shell">
        <header className="page-header">
          <div>
            <p className="brand">PIA</p>
            <p className="session-label">Document update · Example session</p>
          </div>
          <div className="header-actions">
            <a className="privacy-link" href="/privacy">
              Privacy commitments
            </a>
            <a className="quiet-button" href="/credentials">
              Return to credential review
            </a>
          </div>
        </header>

        <section className="draft-ready-card">
          <span className="completion-mark" aria-hidden="true">
            ✓
          </span>
          <p className="eyebrow">Separate draft ready</p>
          <h1>Your original {target.name.toLowerCase()} remains unchanged.</h1>
          <p>
            The draft contains only the suggestions you approved or edited.
            Review it once more, then copy or download it for use outside PIA.
          </p>

          <div className="draft-preview">
            <div className="draft-preview-header">
              <strong>{target.name} draft</strong>
              <span>{target.suggestions.length} decisions recorded</span>
            </div>
            <pre>{draftText}</pre>
          </div>

          <div className="completion-actions">
            <button
              className="button button-secondary"
              onClick={() => setScreen("editor")}
              type="button"
            >
              Revise choices
            </button>
            <button
              className="button button-secondary"
              onClick={copyDraft}
              type="button"
            >
              {copied ? "Copied" : "Copy draft"}
            </button>
            <button
              className="button button-primary"
              onClick={downloadDraft}
              type="button"
            >
              Download editable draft
            </button>
          </div>

          <p className="prototype-note centered">
            Working prototype: the draft is created in this browser and is not
            stored by PIA.
          </p>
        </section>
      </main>
    );
  }

  if (screen === "editor") {
    return (
      <main className="report-shell">
        <header className="page-header">
          <div>
            <p className="brand">PIA</p>
            <p className="session-label">Document update · Example session</p>
          </div>
          <div className="header-actions">
            <a className="privacy-link" href="/privacy">
              Privacy commitments
            </a>
            <button
              className="quiet-button"
              onClick={() => setScreen("report")}
              type="button"
            >
              Back to report
            </button>
          </div>
        </header>

        <section className="document-editor-intro">
          <p className="eyebrow">Optional document update</p>
          <div className="editor-title-row">
            <div>
              <h1>Review your {target.name.toLowerCase()} suggestions.</h1>
              <p>
                Use, edit, or reject each change. Nothing is published or added
                to the evidence graph.
              </p>
            </div>
            <div className="decision-progress">
              <strong>
                {decidedCount} of {target.suggestions.length}
              </strong>
              <span>decisions complete</span>
            </div>
          </div>
        </section>

        <div className="control-notice">
          <span aria-hidden="true">✓</span>
          <div>
            <strong>You stay in control.</strong>
            <p>
              PIA creates a separate draft. Your original document and accepted
              report remain unchanged.
            </p>
          </div>
        </div>

        <nav aria-label="Document type" className="document-switcher">
          {targets.map((candidate) => (
            <button
              aria-current={candidate.id === target.id}
              key={candidate.id}
              onClick={() => chooseTarget(candidate.id)}
              type="button"
            >
              {candidate.name}
            </button>
          ))}
        </nav>

        <section className="suggestion-stack">
          {target.suggestions.map((suggestion, index) => {
            const decision = decisions[suggestion.id];
            const editableValue = drafts[suggestion.id] ?? suggestion.proposed;
            return (
              <article className="suggestion-card" key={suggestion.id}>
                <div className="suggestion-heading">
                  <span>{index + 1}</span>
                  <div>
                    <p className="eyebrow">Suggested update</p>
                    <h2>{suggestion.label}</h2>
                  </div>
                  {decision ? (
                    <strong className={`decision-state ${decision}`}>
                      {decision === "use" ? "Use draft" : "Keep current"}
                    </strong>
                  ) : (
                    <strong className="decision-state">Choose below</strong>
                  )}
                </div>

                <div className="comparison-grid">
                  <div className="current-copy">
                    <p>Current wording</p>
                    <div>{suggestion.current}</div>
                  </div>
                  <div className="proposed-copy">
                    <p>PIA suggestion — editable</p>
                    {suggestion.multiline ? (
                      <textarea
                        aria-label={`Editable ${suggestion.label} suggestion`}
                        onChange={(event) =>
                          setDrafts((current) => ({
                            ...current,
                            [suggestion.id]: event.target.value,
                          }))
                        }
                        value={editableValue}
                      />
                    ) : (
                      <input
                        aria-label={`Editable ${suggestion.label} suggestion`}
                        onChange={(event) =>
                          setDrafts((current) => ({
                            ...current,
                            [suggestion.id]: event.target.value,
                          }))
                        }
                        value={editableValue}
                      />
                    )}
                  </div>
                </div>

                <details className="evidence-details">
                  <summary>Why PIA suggested this</summary>
                  <p>{suggestion.explanation}</p>
                  <div>
                    {suggestion.evidence.map((item) => (
                      <span key={item}>{item}</span>
                    ))}
                  </div>
                </details>

                <div className="suggestion-actions">
                  <button
                    className={`button button-secondary ${
                      decision === "keep" ? "selected-action" : ""
                    }`}
                    onClick={() => setDecision(suggestion.id, "keep")}
                    type="button"
                  >
                    Keep current
                  </button>
                  <button
                    className={`button button-primary ${
                      decision === "use" ? "selected-action" : ""
                    }`}
                    onClick={() => setDecision(suggestion.id, "use")}
                    type="button"
                  >
                    Use this draft
                  </button>
                </div>
              </article>
            );
          })}
        </section>

        <div className="editor-footer">
          <div>
            <strong>{decidedCount} decisions saved in this session</strong>
            <span>
              Finish all {target.suggestions.length} to create the separate
              draft.
            </span>
          </div>
          <button
            className="button button-primary"
            disabled={decidedCount !== target.suggestions.length}
            onClick={() => setScreen("ready")}
            type="button"
          >
            Create approved draft
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="report-shell">
      <header className="page-header">
        <div>
          <p className="brand">PIA</p>
          <p className="session-label">Participant overview · Example session</p>
        </div>
        <div className="header-actions">
          <a className="privacy-link" href="/privacy">
            Privacy commitments
          </a>
          <a className="quiet-button" href="/credentials">
            Back to credential review
          </a>
        </div>
      </header>

      <aside className="privacy-assurance-strip compact">
        <div>
          <strong>Private by design</strong>
          <span>No participant PII in the repository</span>
          <span>Session-only choices in this prototype</span>
          <span>Browser-created downloads</span>
        </div>
        <a href="/privacy">See guarantees and production boundaries</a>
      </aside>

      <section className="report-hero">
        <div>
          <p className="eyebrow">Your participant overview is ready</p>
          <h1>Your experience tells a bigger story.</h1>
          <p>
            Across the evidence reviewed, a consistent pattern appears: you
            strengthen practical systems, connect people and work, and preserve
            knowledge so others can use it.
          </p>
          <div className="report-hero-actions">
            <a
              className="button button-secondary"
              href={fullReportUrl}
            >
              View full report
            </a>
            <button
              className={`button ${
                summaryIncluded ? "button-secondary summary-included" : "button-primary"
              }`}
              onClick={() => setSummaryIncluded((current) => !current)}
              type="button"
            >
              {summaryIncluded
                ? "Executive summary added"
                : "Add executive summary to full report"}
            </button>
          </div>
          {summaryIncluded ? (
            <p className="summary-confirmation">
              Included in this session’s full-report view. You can remove it
              before export.
            </p>
          ) : null}
        </div>
        <div className="report-assurance">
          <span>Evidence-linked</span>
          <strong>No score or ranking</strong>
          <p>
            Every interpretation can be reviewed, revised, or traced back to
            supporting material.
          </p>
        </div>
      </section>

      <section aria-labelledby="report-patterns-title" className="report-patterns">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Report highlights</p>
            <h2 id="report-patterns-title">Patterns supported by your evidence</h2>
          </div>
          <span>3 connected areas</span>
        </div>
        <div className="capability-card-grid">
          {capabilityCards.map((card) => (
            <article key={card.title}>
              <span>{card.level}</span>
              <h3>{card.title}</h3>
              <p>{card.text}</p>
              <details>
                <summary>View supporting evidence</summary>
                <small>{card.evidence}</small>
              </details>
            </article>
          ))}
        </div>
      </section>

      <section className="technical-companion-callout">
        <div>
          <p className="eyebrow">Optional technical companion</p>
          <h2>Want the confidence and evidence details?</h2>
          <p>
            View working confidence levels, evidence counts, source-group
            coverage, and bounded conflicts for each mapped capability.
          </p>
        </div>
        <div className="technical-companion-actions">
          <a
            className="button button-secondary"
            href={`${fullReportUrl}#technical-breakdown`}
          >
            View technical breakdown
          </a>
          <button
            className={`button ${
              technicalIncluded ? "button-secondary summary-included" : "button-primary"
            }`}
            onClick={() => setTechnicalIncluded((current) => !current)}
            type="button"
          >
            {technicalIncluded
              ? "Technical breakdown added"
              : "Add to full report"}
          </button>
        </div>
      </section>

      <section className="document-handoff" id="document-update">
        <div className="handoff-heading">
          <div>
            <p className="eyebrow">Optional next step</p>
            <h2>Put this report to work.</h2>
            <p>
              Choose a document and PIA will prepare evidence-bounded
              suggestions. You approve every change before receiving a separate
              editable draft.
            </p>
          </div>
          <div className="handoff-boundary">
            <strong>Your source stays unchanged</strong>
            <span>No automatic publishing</span>
            <span>No new claims beyond the report</span>
          </div>
        </div>

        <div className="document-card-grid">
          {targets.map((targetOption) => (
            <article key={targetOption.id}>
              <div className="document-icon" aria-hidden="true">
                {targetOption.id === "linkedin"
                  ? "in"
                  : targetOption.id === "resume"
                    ? "R"
                    : "CV"}
              </div>
              <h3>{targetOption.name}</h3>
              <p>{targetOption.description}</p>
              <small>{targetOption.items}</small>
              <button
                className="button button-primary"
                onClick={() => chooseTarget(targetOption.id)}
                type="button"
              >
                Review suggestions
              </button>
            </article>
          ))}
        </div>

        <button
          className="not-now-button"
          onClick={() => setReportKept(true)}
          type="button"
        >
          {reportKept ? "Report kept — no document changes selected" : "Keep my report as it is"}
        </button>
      </section>

      <p className="prototype-note centered">
        Working prototype: example report and drafts are synthetic and disappear
        when the page reloads.
      </p>
    </main>
  );
}
