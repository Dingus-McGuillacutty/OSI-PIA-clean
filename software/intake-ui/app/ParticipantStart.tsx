"use client";

import { useMemo, useState } from "react";

type SelectedDocument = {
  id: string;
  name: string;
  size: number;
  documentType: DocumentTypeId | "";
};

const documentTypes = [
  {
    value: "professional-profile",
    label: "Professional profile",
  },
  {
    value: "career-document",
    label: "Career document",
  },
  {
    value: "credential-learning",
    label: "Credential or learning record",
  },
  {
    value: "supporting-evidence",
    label: "Supporting evidence",
  },
] as const;

type DocumentTypeId = (typeof documentTypes)[number]["value"];

function readableSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ParticipantStart() {
  const [participantLabel, setParticipantLabel] = useState("Participant 001");
  const [documents, setDocuments] = useState<SelectedDocument[]>([]);
  const [privacyAcknowledged, setPrivacyAcknowledged] = useState(false);

  const totalSize = useMemo(
    () => documents.reduce((sum, document) => sum + document.size, 0),
    [documents],
  );
  const classifiedCount = documents.filter(
    (document) => document.documentType,
  ).length;
  const allDocumentsClassified =
    documents.length > 0 && classifiedCount === documents.length;

  function chooseDocuments(files: FileList | null) {
    if (!files) return;

    setDocuments((current) => {
      const existing = new Set(
        current.map((document) => `${document.name}:${document.size}`),
      );
      const additions = Array.from(files)
        .filter((file) => !existing.has(`${file.name}:${file.size}`))
        .map((file) => ({
          id: `${file.name}-${file.size}-${file.lastModified}`,
          name: file.name,
          size: file.size,
          documentType: "",
        }));
      return [...current, ...additions];
    });
  }

  function removeDocument(id: string) {
    setDocuments((current) =>
      current.filter((document) => document.id !== id),
    );
  }

  function setDocumentType(id: string, documentType: DocumentTypeId | "") {
    setDocuments((current) =>
      current.map((document) =>
        document.id === id ? { ...document, documentType } : document,
      ),
    );
  }

  return (
    <main className="participant-start-shell">
      <header className="page-header">
        <div>
          <p className="brand">PIA</p>
          <p className="session-label">Private participant intake · Example session</p>
        </div>
        <div className="header-actions">
          <a className="privacy-link" href="/privacy">
            Privacy commitments
          </a>
          <a className="quiet-button" href="/report">
            Preview report
          </a>
        </div>
      </header>

      <section className="participant-start-hero">
        <div>
          <p className="eyebrow">Begin your evidence review</p>
          <h1>Your experience tells a bigger story.</h1>
          <p>
            Start with the documents you already have. PIA will organize the
            evidence, identify what needs clarification, and keep you in
            control of every interpretation.
          </p>
          <ol aria-label="Participant intake steps">
            <li className="active">
              <span>1</span>
              <strong>Start privately</strong>
            </li>
            <li>
              <span>2</span>
              <strong>Add documents</strong>
            </li>
            <li>
              <span>3</span>
              <strong>Review evidence</strong>
            </li>
          </ol>
        </div>
        <figure>
          <img
            alt="PIA professional identity and technical evidence report preview"
            height="1024"
            src="/og-v5.png"
            width="1536"
          />
          <figcaption>
            Private · Traceable · Participant-controlled
          </figcaption>
        </figure>
      </section>

      <aside className="intake-assurance-row">
        <div>
          <strong>Private by design</strong>
          <span>No name or email required</span>
          <span>Files stay in this browser session</span>
          <span>Nothing is added to the graph without review</span>
        </div>
        <a href="/privacy">See privacy guarantees and boundaries</a>
      </aside>

      <section className="participant-intake-card">
        <div className="participant-intake-heading">
          <div>
            <p className="eyebrow">Participant reference and initial documents</p>
            <h2>Start privately with what you already have.</h2>
            <p>
              Use a private study label, then add your initial files. You will
              identify each document type after it is selected.
            </p>
          </div>
          <span>{documents.length} selected</span>
        </div>

        <div className="participant-label-row">
          <div>
            <strong>Participant label</strong>
            <span>
              No name or email is required. This reference disappears on reload.
            </span>
          </div>
          <input
            aria-label="Participant label"
            onChange={(event) => setParticipantLabel(event.target.value)}
            value={participantLabel}
          />
        </div>

        <label
          className="document-drop-zone"
          onDragOver={(event) => event.preventDefault()}
          onDrop={(event) => {
            event.preventDefault();
            chooseDocuments(event.dataTransfer.files);
          }}
        >
          <input
            accept=".pdf,.doc,.docx,.rtf,.txt,.csv,.zip"
            multiple
            onChange={(event) => {
              chooseDocuments(event.target.files);
              event.currentTarget.value = "";
            }}
            type="file"
          />
          <span aria-hidden="true">+</span>
          <strong>Drop or choose initial documents</strong>
          <small>
            PDF, DOC, DOCX, RTF, TXT, CSV, and ZIP · Nothing is uploaded
          </small>
        </label>

        {documents.length ? (
          <div className="selected-document-list">
            <div className="selected-document-summary">
              <strong>
                {classifiedCount} of {documents.length} document types defined
              </strong>
              <span>{readableSize(totalSize)} selected in this session</span>
            </div>
            {documents.map((document) => (
              <article key={document.id}>
                <div className="selected-document-name">
                  <strong>{document.name}</strong>
                  <span>{readableSize(document.size)}</span>
                </div>
                <label>
                  <span>Document type</span>
                  <select
                    aria-label={`Document type for ${document.name}`}
                    onChange={(event) =>
                      setDocumentType(
                        document.id,
                        event.target.value as DocumentTypeId | "",
                      )
                    }
                    value={document.documentType}
                  >
                    <option value="">Choose type</option>
                    {documentTypes.map((documentType) => (
                      <option
                        key={documentType.value}
                        value={documentType.value}
                      >
                        {documentType.label}
                      </option>
                    ))}
                  </select>
                </label>
                <button
                  aria-label={`Remove ${document.name}`}
                  onClick={() => removeDocument(document.id)}
                  type="button"
                >
                  Remove
                </button>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-document-note">
            No documents selected yet. You can continue without documents and
            add evidence during credential review.
          </p>
        )}

        <label className="privacy-acknowledgement">
          <input
            checked={privacyAcknowledged}
            onChange={(event) =>
              setPrivacyAcknowledged(event.target.checked)
            }
            type="checkbox"
          />
          <span>
            <strong>I understand this is a session-only prototype.</strong>
            <small>
              Selected documents are not uploaded, analyzed, or retained by
              this screen.
            </small>
          </span>
        </label>

        <div className="participant-start-actions">
          <a href="/credentials">Continue without documents</a>
          <button
            className="button button-primary"
            disabled={!allDocumentsClassified || !privacyAcknowledged}
            onClick={() => {
              window.location.href = "/credentials";
            }}
            type="button"
          >
            Continue with selected documents
          </button>
        </div>
      </section>

      <p className="prototype-note centered">
        Working prototype: participant labels and selected documents disappear
        when the page reloads.
      </p>
    </main>
  );
}
