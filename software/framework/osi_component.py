"""Common assurance interface for reusable OSI–PIA components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field as dataclass_field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import json
import uuid


class Disposition(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class FindingSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"
    REVIEW = "review"


@dataclass(frozen=True)
class Finding:
    """Traceable result emitted by an assurance rule.

    A Finding is the gate between component-specific evaluation and the
    standard AssuranceResult. It preserves the rule, source location, and
    explicit logic chain that produced the result.
    """

    severity: FindingSeverity
    code: str
    message: str
    dimension: str
    rule_id: str
    source_reference: str = ""
    file: str = ""
    row: Optional[int] = None
    field: Optional[str] = None
    evidence: List[str] = dataclass_field(default_factory=list)
    logic_chain: List[str] = dataclass_field(default_factory=list)
    confidence: Optional[float] = None
    uncertainty: str = ""

    def reference(self) -> str:
        if self.source_reference:
            return self.source_reference

        parts = [part for part in [self.file] if part]
        if self.row is not None:
            parts.append(f"row={self.row}")
        if self.field:
            parts.append(f"field={self.field}")
        return ":".join(parts)

    def render(self) -> str:
        reference = self.reference()
        prefix = f"{reference}: " if reference else ""
        return f"{prefix}{self.code}: {self.message}"


@dataclass
class AssuranceResult:
    dimension: str
    disposition: Disposition
    message: str = ""
    errors: List[str] = dataclass_field(default_factory=list)
    warnings: List[str] = dataclass_field(default_factory=list)
    metrics: Dict[str, Any] = dataclass_field(default_factory=dict)
    evidence: List[str] = dataclass_field(default_factory=list)
    findings: List[Finding] = dataclass_field(default_factory=list)

    @classmethod
    def from_findings(
        cls,
        dimension: str,
        findings: List[Finding],
        pass_message: str,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> "AssuranceResult":
        errors = [f.render() for f in findings if f.severity == FindingSeverity.ERROR]
        warnings = [f.render() for f in findings if f.severity == FindingSeverity.WARNING]
        reviews = [f for f in findings if f.severity == FindingSeverity.REVIEW]

        if errors:
            disposition = Disposition.FAIL
        elif reviews:
            disposition = Disposition.REQUIRES_HUMAN_REVIEW
        elif warnings:
            disposition = Disposition.PASS_WITH_WARNINGS
        else:
            disposition = Disposition.PASS

        return cls(
            dimension=dimension,
            disposition=disposition,
            message=pass_message if not findings else f"{len(findings)} finding(s).",
            errors=errors,
            warnings=warnings,
            metrics=metrics or {},
            evidence=[f.reference() for f in findings if f.reference()],
            findings=findings,
        )


@dataclass
class AssuranceReport:
    component_id: str
    component_version: str
    contract_version: str
    run_id: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: str = dataclass_field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    input_reference: str = ""
    configuration_reference: str = ""
    results: List[AssuranceResult] = dataclass_field(default_factory=list)
    overall_disposition: Disposition = Disposition.NOT_APPLICABLE
    reviewer: str = ""
    waivers: List[str] = dataclass_field(default_factory=list)

    def finalize(self) -> "AssuranceReport":
        dispositions = [result.disposition for result in self.results]
        priority = [
            Disposition.FAIL,
            Disposition.REQUIRES_HUMAN_REVIEW,
            Disposition.PASS_WITH_WARNINGS,
            Disposition.PASS,
            Disposition.NOT_APPLICABLE,
        ]
        self.overall_disposition = next(
            (item for item in priority if item in dispositions),
            Disposition.NOT_APPLICABLE,
        )
        return self

    def to_json(self, indent: int = 2) -> str:
        payload = asdict(self.finalize())
        return json.dumps(payload, indent=indent, default=str)


class OSIComponent(ABC):
    """Base assurance interface shared by engines and other OSI components."""

    component_id: str
    component_version: str
    contract_version: str

    def assure(
        self,
        input_reference: str = "",
        configuration_reference: str = "",
    ) -> AssuranceReport:
        report = AssuranceReport(
            component_id=self.component_id,
            component_version=self.component_version,
            contract_version=self.contract_version,
            input_reference=input_reference,
            configuration_reference=configuration_reference,
        )

        checks = [
            self.test_contract,
            self.test_validation,
            self.test_congruence,
            self.test_regression,
            self.test_performance,
            self.test_ethics,
            self.test_epistemic_integrity,
            self.test_audit,
        ]

        for check in checks:
            try:
                report.results.append(check())
            except Exception as exc:  # assurance must expose, never hide, failure
                report.results.append(
                    AssuranceResult(
                        dimension=check.__name__.removeprefix("test_"),
                        disposition=Disposition.FAIL,
                        message="Unhandled assurance exception",
                        errors=[f"{type(exc).__name__}: {exc}"],
                    )
                )

        return report.finalize()

    @abstractmethod
    def test_contract(self) -> AssuranceResult:
        raise NotImplementedError

    @abstractmethod
    def test_validation(self) -> AssuranceResult:
        raise NotImplementedError

    @abstractmethod
    def test_congruence(self) -> AssuranceResult:
        raise NotImplementedError

    @abstractmethod
    def test_regression(self) -> AssuranceResult:
        raise NotImplementedError

    @abstractmethod
    def test_performance(self) -> AssuranceResult:
        raise NotImplementedError

    @abstractmethod
    def test_ethics(self) -> AssuranceResult:
        raise NotImplementedError

    @abstractmethod
    def test_epistemic_integrity(self) -> AssuranceResult:
        raise NotImplementedError

    def test_audit(self) -> AssuranceResult:
        return AssuranceResult(
            dimension="audit",
            disposition=Disposition.PASS,
            message="Assurance run will emit a versioned JSON audit report.",
        )
