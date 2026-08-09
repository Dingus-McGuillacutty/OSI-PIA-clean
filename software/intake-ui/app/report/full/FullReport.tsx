"use client";

import { useEffect, useState } from "react";

const evidenceRows = [
  {
    area: "Systems and operations",
    interpretation:
      "Improves practical processes and creates guidance that supports repeatable work.",
    strength: "Strong evidence",
    sources: "Role records · Operational artifacts · Process documentation",
    confidence: 88,
    evidenceItems: 8,
    directItems: 5,
    corroboratingItems: 3,
    sourceGroups: 3,
    conflicts: 0,
    nextAction: "Add outcome evidence",
  },
  {
    area: "Coordination and delivery",
    interpretation:
      "Connects people, requirements, and activities across operational and project settings.",
    strength: "Supported",
    sources: "Project records · Group context · Coordination examples",
    confidence: 79,
    evidenceItems: 7,
    directItems: 3,
    corroboratingItems: 4,
    sourceGroups: 3,
    conflicts: 1,
    nextAction: "Clarify role scope",
  },
  {
    area: "Knowledge and development",
    interpretation:
      "Preserves working knowledge and helps others understand procedures and expectations.",
    strength: "Supported",
    sources: "Guidance artifacts · Training records · Knowledge-transfer examples",
    confidence: 76,
    evidenceItems: 6,
    directItems: 3,
    corroboratingItems: 3,
    sourceGroups: 3,
    conflicts: 0,
    nextAction: "Add transfer artifact",
  },
  {
    area: "Technical preparation",
    interpretation:
      "Coursework and credentials support preparation across security, response, planning, and learning domains.",
    strength: "Preparation evidence",
    sources: "Credential definitions · Course domains · Completion records",
    confidence: 68,
    evidenceItems: 9,
    directItems: 2,
    corroboratingItems: 7,
    sourceGroups: 3,
    conflicts: 0,
    nextAction: "Link learning to use",
  },
];

export function FullReport() {
  const [summaryIncluded, setSummaryIncluded] = useState(false);
  const [technicalIncluded, setTechnicalIncluded] = useState(false);

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    setSummaryIncluded(query.get("execsum") === "included");
    setTechnicalIncluded(query.get("tech") === "included");
  }, []);

  return (
    <main className="full-report-shell">
      <header className="page-header">
        <div>
          <p className="brand">PIA</p>
          <p className="session-label">Full evidence report · Example session</p>
        </div>
        <div className="header-actions">
          <a className="privacy-link" href="/privacy">
            Privacy commitments
          </a>
          <a className="quiet-button" href="/report">
            Back to participant overview
          </a>
        </div>
      </header>

      <section className="full-report-heading">
        <div>
          <p className="eyebrow">Full participant report</p>
          <h1>The evidence behind the professional overview.</h1>
          <p>
            This view preserves the fuller narrative, capability patterns,
            evidence basis, limits, and development questions behind the
            shorter participant overview.
          </p>
        </div>
        <div className="full-report-meta">
          <span>Working example</span>
          <strong>Evidence-linked and revisable</strong>
          <p>No overall score · No ranking · No automatic identity claim</p>
          <div className="full-report-meta-actions">
            <a href="#technical-breakdown">View technical breakdown</a>
            <button
              onClick={() => setTechnicalIncluded((current) => !current)}
              type="button"
            >
              {technicalIncluded ? "Technical breakdown added" : "Add technical breakdown"}
            </button>
          </div>
        </div>
      </section>

      <aside className="privacy-assurance-strip">
        <div>
          <strong>Private by design</strong>
          <span>No participant PII in the repository</span>
          <span>Session-only choices in this prototype</span>
          <span>Downloads use an encrypted connection</span>
        </div>
        <a href="/privacy">See the privacy guarantees and boundaries</a>
      </aside>

      <nav aria-label="Full report sections" className="report-section-map">
        <a href="#executive-summary">Executive summary</a>
        <a href="#professional-narrative">Professional narrative</a>
        <a href="#capability-evidence">Capability evidence</a>
        <a href="#technical-breakdown">Technical breakdown</a>
        <a href="#update-evidence">Update my evidence</a>
      </nav>

      <section className="full-report-section" id="executive-summary">
        <div className="full-section-heading">
          <div>
            <p className="eyebrow">Optional report element</p>
            <h2>Executive summary</h2>
          </div>
          <span className={summaryIncluded ? "included" : ""}>
            {summaryIncluded ? "Included by participant" : "Not yet included"}
          </span>
        </div>

        <div className="executive-summary-block">
          <p>
            Across the evidence reviewed, a consistent pattern appears: this
            participant strengthens practical systems, connects people and
            work, and preserves knowledge so others can use it. Their
            professional value is expressed not through one title, but through
            recurring contributions to operational clarity, coordination,
            knowledge continuity, and reliable execution.
          </p>
        </div>

        <div className="full-section-actions">
          <button
            className={`button ${
              summaryIncluded ? "button-secondary" : "button-primary"
            }`}
            onClick={() => setSummaryIncluded((current) => !current)}
            type="button"
          >
            {summaryIncluded
              ? "Remove from this report"
              : "Add executive summary to this report"}
          </button>
          <small>
            This changes report composition only. It does not change the graph
            or evidence state.
          </small>
        </div>
      </section>

      <section className="full-report-section" id="professional-narrative">
        <div className="full-section-heading">
          <div>
            <p className="eyebrow">Integrated interpretation</p>
            <h2>Professional narrative</h2>
          </div>
          <span>Pattern-oriented</span>
        </div>

        <div className="narrative-columns">
          <article>
            <h3>How value appears across roles</h3>
            <p>
              The record suggests a professional who makes complicated work
              more usable. Across different contexts, the participant returns
              to a similar set of contributions: identifying operational
              friction, clarifying expectations, coordinating action, and
              creating guidance that remains useful after the immediate task is
              complete.
            </p>
          </article>
          <article>
            <h3>How the pattern connects</h3>
            <p>
              Security operations, project coordination, documentation,
              learning support, and process improvement are not treated as
              isolated topics. The evidence supports a connected pattern of
              practical systems thinking, cross-role communication, and
              knowledge continuity.
            </p>
          </article>
        </div>
      </section>

      <section className="full-report-section" id="capability-evidence">
        <div className="full-section-heading">
          <div>
            <p className="eyebrow">Traceable interpretation</p>
            <h2>Capability and evidence register</h2>
          </div>
          <a className="section-action-link" href="/credentials">
            Update my evidence
          </a>
        </div>

        <div className="evidence-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Area</th>
                <th>What the evidence supports</th>
                <th>Evidence strength</th>
                <th>Source groups</th>
              </tr>
            </thead>
            <tbody>
              {evidenceRows.map((row) => (
                <tr key={row.area}>
                  <th scope="row">{row.area}</th>
                  <td>{row.interpretation}</td>
                  <td>
                    <span>{row.strength}</span>
                  </td>
                  <td>{row.sources}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="full-report-section" id="technical-breakdown">
        <div className="full-section-heading">
          <div>
            <p className="eyebrow">Optional technical companion</p>
            <h2>Confidence and evidence statistics</h2>
          </div>
          <span className={technicalIncluded ? "included" : ""}>
            {technicalIncluded ? "Included by participant" : "Previewing only"}
          </span>
        </div>

        <p className="technical-intro">
          This dashboard is a synthetic working example. Confidence describes
          how well the current evidence supports each interpretation; it is not
          a capability score or comparison with other people.
        </p>

        <div className="technical-summary-grid">
          <article>
            <strong>4</strong>
            <span>mapped capability areas</span>
          </article>
          <article>
            <strong>30</strong>
            <span>evidence references reviewed</span>
          </article>
          <article>
            <strong>13</strong>
            <span>direct evidence items</span>
          </article>
          <article>
            <strong>1</strong>
            <span>bounded conflict to clarify</span>
          </article>
        </div>

        <div className="technical-card-grid">
          {evidenceRows.map((row) => (
            <article key={row.area}>
              <div className="technical-card-heading">
                <div>
                  <p>{row.strength}</p>
                  <h3>{row.area}</h3>
                </div>
                <strong>{row.confidence}%</strong>
              </div>
              <div
                aria-label={`${row.area} working confidence ${row.confidence} percent`}
                className="confidence-track"
                role="img"
              >
                <span style={{ width: `${row.confidence}%` }} />
              </div>
              <dl>
                <div>
                  <dt>Evidence items</dt>
                  <dd>{row.evidenceItems}</dd>
                </div>
                <div>
                  <dt>Direct</dt>
                  <dd>{row.directItems}</dd>
                </div>
                <div>
                  <dt>Corroborating</dt>
                  <dd>{row.corroboratingItems}</dd>
                </div>
                <div>
                  <dt>Source groups</dt>
                  <dd>{row.sourceGroups}</dd>
                </div>
                <div>
                  <dt>Conflicts</dt>
                  <dd>{row.conflicts}</dd>
                </div>
              </dl>
              <a href="/credentials">{row.nextAction}</a>
            </article>
          ))}
        </div>

        <div className="full-section-actions">
          <button
            className={`button ${
              technicalIncluded ? "button-secondary" : "button-primary"
            }`}
            onClick={() => setTechnicalIncluded((current) => !current)}
            type="button"
          >
            {technicalIncluded
              ? "Remove technical breakdown"
              : "Add technical breakdown to this report"}
          </button>
          <small>
            Inclusion changes report composition only. Evidence and confidence
            calculations remain unchanged.
          </small>
        </div>
      </section>

      <section className="full-report-section" id="update-evidence">
        <div className="full-section-heading">
          <div>
            <p className="eyebrow">Participant correction and development</p>
            <h2>Update my evidence</h2>
          </div>
          <a className="section-action-link" href="/credentials">
            Add evidence or clarification
          </a>
        </div>

        <div className="boundary-grid">
          <article>
            <h3>What remains bounded</h3>
            <p>
              Credential completion supports preparation but does not establish
              performance. Group context can support a shared-work inference
              but does not prove leadership authority, sole ownership, or
              outcome quality.
            </p>
          </article>
          <article>
            <h3>What would strengthen the report</h3>
            <p>
              Add project outcomes, examples of applied credential knowledge,
              artifacts showing technical depth, or clarification of your role
              and contribution. New evidence remains subject to the same
              consent and privacy boundaries.
            </p>
            <a href="/credentials">Update my evidence</a>
          </article>
        </div>
      </section>

      <section className="full-report-footer">
        <div>
          <p className="eyebrow">Optional next step</p>
          <h2>Use the report when you are ready.</h2>
          <p>
            Return to the participant overview to create evidence-bounded
            LinkedIn, résumé, or CV suggestions.
          </p>
        </div>
        <a className="button button-primary" href="/report#document-update">
          Review document options
        </a>
      </section>

      <p className="prototype-note centered">
        Working prototype: this synthetic report and its composition choices
        disappear when the page reloads.
      </p>
    </main>
  );
}
