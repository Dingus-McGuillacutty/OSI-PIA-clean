#!/usr/bin/env python3
"""Bounded, non-executing document extraction for protected PIA intake.

The extractor produces faithful, review-pending evidence candidates. It does
not identify capabilities, score a participant, resolve credentials, or write
to a graph.

artifact_id: component-pia-evidence-extraction-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree

from software.intake.local_private_intake import IntakePreflightError


PARSER_VERSION = "pia-safe-evidence-extractor/0.1.0"
MAX_EXTRACTED_CHARACTERS = 500_000
MAX_CANDIDATES = 500
MAX_CANDIDATE_CHARACTERS = 2_000
MAX_PDF_PAGES = 250
MAX_PDF_DECOMPRESSED_STREAM_BYTES = 2_000_000
MAX_CSV_ROWS = 5_000
MAX_CSV_COLUMNS = 100
MAX_DOCX_MEMBERS = 2_000
MAX_DOCX_UNCOMPRESSED_BYTES = 25 * 1024 * 1024
MAX_DOCX_COMPRESSION_RATIO = 200

SUPPORTED_EXTENSIONS = {".txt", ".csv", ".rtf", ".docx", ".pdf"}
MANUAL_REVIEW_EXTENSIONS = {".doc", ".zip"}

CONTROL_WORD = re.compile(
    r"""
    \\(?:
        (?P<hex>'[0-9a-fA-F]{2}) |
        (?P<word>[a-zA-Z]+)(?P<arg>-?\d+)?[ ]? |
        (?P<symbol>[^a-zA-Z0-9])
    )
    """,
    re.VERBOSE,
)
RTF_DESTINATIONS = {
    "aftncn",
    "aftnsep",
    "aftnsepc",
    "annotation",
    "atnauthor",
    "atndate",
    "atnicn",
    "atnid",
    "atnparent",
    "atnref",
    "atntime",
    "atrfend",
    "atrfstart",
    "author",
    "background",
    "bkmkend",
    "bkmkstart",
    "blipuid",
    "buptim",
    "category",
    "colorschememapping",
    "colortbl",
    "comment",
    "company",
    "creatim",
    "datafield",
    "datastore",
    "defchp",
    "defpap",
    "do",
    "doccomm",
    "docvar",
    "dptxbxtext",
    "ebcend",
    "ebcstart",
    "factoidname",
    "falt",
    "fchars",
    "ffdeftext",
    "ffentrymcr",
    "ffexitmcr",
    "ffformat",
    "ffhelptext",
    "ffl",
    "ffname",
    "ffstattext",
    "field",
    "file",
    "filetbl",
    "fldinst",
    "fldrslt",
    "fldtype",
    "fname",
    "fontemb",
    "fontfile",
    "fonttbl",
    "footer",
    "footerf",
    "footerl",
    "footerr",
    "footnote",
    "formfield",
    "ftncn",
    "ftnsep",
    "ftnsepc",
    "g",
    "generator",
    "gridtbl",
    "header",
    "headerf",
    "headerl",
    "headerr",
    "hl",
    "hlfr",
    "hlinkbase",
    "hlloc",
    "hlsrc",
    "hsv",
    "htmltag",
    "info",
    "keycode",
    "keywords",
    "latentstyles",
    "lchars",
    "levelnumbers",
    "leveltext",
    "lfolevel",
    "linkval",
    "list",
    "listlevel",
    "listname",
    "listoverride",
    "listoverridetable",
    "listpicture",
    "liststylename",
    "listtable",
    "listtext",
    "lsdlockedexcept",
    "macc",
    "maccPr",
    "mailmerge",
    "maln",
    "malnScr",
    "manager",
    "margPr",
    "mbar",
    "mbarPr",
    "mbaseJc",
    "mbegChr",
    "mborderBox",
    "mborderBoxPr",
    "mbox",
    "mboxPr",
    "mchr",
    "mcount",
    "mctrlPr",
    "md",
    "mdeg",
    "mdegHide",
    "mden",
    "mdiff",
    "mdPr",
    "me",
    "mendChr",
    "meqArr",
    "meqArrPr",
    "mf",
    "mfName",
    "mfPr",
    "mfunc",
    "mfuncPr",
    "mgroupChr",
    "mgroupChrPr",
    "mgrow",
    "mhideBot",
    "mhideLeft",
    "mhideRight",
    "mhideTop",
    "mhtmltag",
    "mlim",
    "mlimloc",
    "mlimlow",
    "mlimlowPr",
    "mlimupp",
    "mlimuppPr",
    "mm",
    "mmaddfieldname",
    "mmath",
    "mmathPict",
    "mmathPr",
    "mmaxdist",
    "mmc",
    "mmcJc",
    "mmconnectstr",
    "mmconnectstrdata",
    "mmcPr",
    "mmcs",
    "mmdatasource",
    "mmheadersource",
    "mmmailsubject",
    "mmodso",
    "mmodsofilter",
    "mmodsofldmpdata",
    "mmodsomappedname",
    "mmodsoname",
    "mmodsorecipdata",
    "mmodsosort",
    "mmodsosrc",
    "mmodsotable",
    "mmodsoudl",
    "mmodsoudldata",
    "mmodsouniquetag",
    "mmPr",
    "mmquery",
    "mmr",
    "mnary",
    "mnaryPr",
    "mnoBreak",
    "mnum",
    "mobjDist",
    "moMath",
    "moMathPara",
    "moMathParaPr",
    "mopEmu",
    "mphant",
    "mphantPr",
    "mplcHide",
    "mpos",
    "mr",
    "mrad",
    "mradPr",
    "mrPr",
    "msepChr",
    "mshow",
    "mshp",
    "msPre",
    "msPrePr",
    "msSub",
    "msSubPr",
    "msSubSup",
    "msSubSupPr",
    "msSup",
    "msSupPr",
    "mstrikeBLTR",
    "mstrikeH",
    "mstrikeTLBR",
    "mstrikeV",
    "msub",
    "msubHide",
    "msup",
    "msupHide",
    "mtransp",
    "mtype",
    "mvertJc",
    "mvfmf",
    "mvfml",
    "mvtof",
    "mvtol",
    "mzeroAsc",
    "mzeroDesc",
    "mzeroWid",
    "nesttableprops",
    "nextfile",
    "nonesttables",
    "objalias",
    "objclass",
    "objdata",
    "object",
    "objname",
    "objsect",
    "objtime",
    "oldcprops",
    "oldpprops",
    "oldsprops",
    "oldtprops",
    "oleclsid",
    "operator",
    "panose",
    "password",
    "passwordhash",
    "pgp",
    "pgptbl",
    "picprop",
    "pict",
    "pn",
    "pnseclvl",
    "pntext",
    "pntxta",
    "pntxtb",
    "printim",
    "private",
    "propname",
    "protend",
    "protstart",
    "protusertbl",
    "pxe",
    "result",
    "revtbl",
    "revtim",
    "rsidtbl",
    "rxe",
    "shp",
    "shpgrp",
    "shpinst",
    "shppict",
    "shprslt",
    "shptxt",
    "sn",
    "sp",
    "staticval",
    "stylesheet",
    "subject",
    "sv",
    "svb",
    "tc",
    "template",
    "themedata",
    "title",
    "txe",
    "ud",
    "upr",
    "userprops",
    "wgrffmtfilter",
    "windowcaption",
    "writereservation",
    "writereservhash",
    "xe",
    "xform",
    "xmlattrname",
    "xmlattrvalue",
    "xmlclose",
    "xmlname",
    "xmlnstbl",
    "xmlopen",
}
SECTION_LABELS = {
    "experience": "statement",
    "professional experience": "statement",
    "work experience": "statement",
    "employment": "statement",
    "education": "event",
    "certifications": "event",
    "certification": "event",
    "credentials": "event",
    "licenses": "event",
    "training": "event",
    "courses": "event",
    "projects": "output",
    "selected projects": "output",
    "accomplishments": "achievement",
    "achievements": "achievement",
    "awards": "achievement",
    "skills": "statement",
    "technical skills": "statement",
    "service": "activity",
    "volunteer experience": "activity",
    "publications": "output",
    "summary": "statement",
    "professional summary": "statement",
}


class EvidenceExtractionError(IntakePreflightError):
    """Raised when an artifact cannot cross the safe extraction boundary."""


@dataclass(frozen=True)
class SourceBlock:
    source_locator: str
    text: str


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bounded_text(value: str) -> str:
    value = value.replace("\x00", "")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    if len(value) > MAX_EXTRACTED_CHARACTERS:
        raise EvidenceExtractionError(
            "Extracted text exceeds the 500,000-character safety limit."
        )
    return value


def _decode_text(content: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return _bounded_text(content.decode(encoding)), encoding
        except UnicodeDecodeError:
            continue
    raise EvidenceExtractionError(
        "The text encoding could not be decoded safely."
    )


def _text_blocks(text: str, *, locator_prefix: str = "paragraph") -> list[SourceBlock]:
    blocks: list[SourceBlock] = []
    pending: list[str] = []

    def flush() -> None:
        if not pending:
            return
        normalized = " ".join(part.strip() for part in pending if part.strip())
        pending.clear()
        if normalized:
            blocks.append(
                SourceBlock(
                    source_locator=f"{locator_prefix} {len(blocks) + 1}",
                    text=normalized,
                )
            )

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if re.match(r"^(?:[-*•▪◦]|\d+[.)])\s+", line):
            flush()
            blocks.append(
                SourceBlock(
                    source_locator=f"{locator_prefix} {len(blocks) + 1}",
                    text=re.sub(r"^(?:[-*•▪◦]|\d+[.)])\s+", "", line).strip(),
                )
            )
            continue
        pending.append(line)
    flush()
    return blocks


def _extract_txt(content: bytes) -> tuple[list[SourceBlock], list[str], str]:
    text, encoding = _decode_text(content)
    return _text_blocks(text), [], f"text/{encoding}"


def _extract_csv(content: bytes) -> tuple[list[SourceBlock], list[str], str]:
    text, encoding = _decode_text(content)
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(text[:8_192], delimiters=",;\t|")
        has_header = sniffer.has_header(text[:8_192])
    except csv.Error:
        dialect = csv.excel
        has_header = False
    parsed_rows: list[tuple[int, list[str]]] = []
    reader = csv.reader(io.StringIO(text, newline=""), dialect)
    for number, row in enumerate(reader, start=1):
        if number > MAX_CSV_ROWS:
            raise EvidenceExtractionError(
                "The CSV exceeds the 5,000-row safety limit."
            )
        if len(row) > MAX_CSV_COLUMNS:
            raise EvidenceExtractionError(
                f"CSV row {number} exceeds the 100-column safety limit."
            )
        values = [
            re.sub(r"\s+", " ", cell.replace("\x00", "")).strip()
            for cell in row
        ]
        if any(values):
            parsed_rows.append((number, values))
    headers: list[str] = []
    lexical_header = (
        len(parsed_rows) > 1
        and all(
            re.fullmatch(r"[A-Za-z][A-Za-z0-9 _./()-]{0,79}", value)
            for value in parsed_rows[0][1]
            if value
        )
        and any(parsed_rows[0][1])
    )
    if (has_header or lexical_header) and parsed_rows:
        headers = parsed_rows.pop(0)[1]
    rows: list[SourceBlock] = []
    for number, values in parsed_rows:
        # Values remain inert text. Formula prefixes are never evaluated.
        rendered = " | ".join(
            (
                f"{headers[index - 1]}: {value}"
                if index <= len(headers) and headers[index - 1]
                else f"column {index}: {value}"
            )
            for index, value in enumerate(values, start=1)
            if value
        )
        rows.append(SourceBlock(f"row {number}", rendered))
    return rows, [], f"csv/{encoding}"


def _strip_rtf(content: bytes) -> str:
    text = content.decode("latin-1")
    if not text.lstrip().startswith("{\\rtf"):
        raise EvidenceExtractionError("The document is not recognizable RTF.")
    output: list[str] = []
    stack: list[tuple[int, bool]] = []
    ignorable = False
    unicode_skip = 1
    index = 0
    while index < len(text):
        char = text[index]
        if char == "{":
            stack.append((unicode_skip, ignorable))
            index += 1
            continue
        if char == "}":
            if stack:
                unicode_skip, ignorable = stack.pop()
            index += 1
            continue
        if char != "\\":
            if not ignorable:
                output.append(char)
            index += 1
            continue
        match = CONTROL_WORD.match(text, index)
        if not match:
            index += 1
            continue
        index = match.end()
        if match.group("hex"):
            if not ignorable:
                output.append(bytes.fromhex(match.group("hex")[1:]).decode("cp1252"))
            continue
        word = match.group("word")
        argument = match.group("arg")
        symbol = match.group("symbol")
        if symbol == "*":
            ignorable = True
        elif symbol in {"\\", "{", "}"} and not ignorable:
            output.append(symbol)
        elif symbol == "~" and not ignorable:
            output.append(" ")
        elif word in RTF_DESTINATIONS:
            ignorable = True
        elif word == "uc" and argument is not None:
            unicode_skip = max(0, min(int(argument), 10))
        elif word == "u" and argument is not None:
            if not ignorable:
                value = int(argument)
                if value < 0:
                    value += 65_536
                output.append(chr(value))
            index = min(len(text), index + unicode_skip)
        elif word in {"par", "line"} and not ignorable:
            output.append("\n")
        elif word == "tab" and not ignorable:
            output.append("\t")
    return _bounded_text("".join(output))


def _extract_rtf(content: bytes) -> tuple[list[SourceBlock], list[str], str]:
    return _text_blocks(_strip_rtf(content)), [], "rtf/plain-text"


def _safe_docx_archive(content: bytes) -> zipfile.ZipFile:
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise EvidenceExtractionError("The DOCX container is invalid.") from exc
    infos = archive.infolist()
    if len(infos) > MAX_DOCX_MEMBERS:
        archive.close()
        raise EvidenceExtractionError(
            "The DOCX contains too many embedded members."
        )
    total = sum(info.file_size for info in infos)
    if total > MAX_DOCX_UNCOMPRESSED_BYTES:
        archive.close()
        raise EvidenceExtractionError(
            "The DOCX expanded content exceeds the 25 MB safety limit."
        )
    for info in infos:
        if info.file_size and info.compress_size == 0:
            archive.close()
            raise EvidenceExtractionError("The DOCX compression metadata is invalid.")
        if (
            info.compress_size
            and info.file_size / info.compress_size > MAX_DOCX_COMPRESSION_RATIO
        ):
            archive.close()
            raise EvidenceExtractionError(
                "The DOCX compression ratio exceeds the safety limit."
            )
    if "word/document.xml" not in archive.namelist():
        archive.close()
        raise EvidenceExtractionError("The DOCX has no main document body.")
    return archive


def _extract_docx(content: bytes) -> tuple[list[SourceBlock], list[str], str]:
    with _safe_docx_archive(content) as archive:
        xml = archive.read("word/document.xml")
    if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
        raise EvidenceExtractionError("Unsafe XML declarations are not permitted.")
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise EvidenceExtractionError("The DOCX document XML is invalid.") from exc
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    blocks: list[SourceBlock] = []
    for paragraph in root.iter(f"{namespace}p"):
        parts: list[str] = []
        for node in paragraph.iter():
            if node.tag == f"{namespace}t" and node.text:
                parts.append(node.text)
            elif node.tag == f"{namespace}tab":
                parts.append("\t")
            elif node.tag in {f"{namespace}br", f"{namespace}cr"}:
                parts.append("\n")
        text = re.sub(r"[ \t]+", " ", "".join(parts)).strip()
        if text:
            blocks.append(SourceBlock(f"paragraph {len(blocks) + 1}", text))
    return blocks, [], "docx/word-document-xml"


def _extract_pdf(content: bytes) -> tuple[list[SourceBlock], list[str], str]:
    try:
        from pypdf import PdfReader
        from pypdf import filters as pdf_filters
        from pypdf.errors import PyPdfError
    except ImportError as exc:
        raise EvidenceExtractionError(
            "PDF extraction requires the optional pypdf dependency."
        ) from exc
    pdf_filters.ZLIB_MAX_OUTPUT_LENGTH = MAX_PDF_DECOMPRESSED_STREAM_BYTES
    pdf_filters.LZW_MAX_OUTPUT_LENGTH = MAX_PDF_DECOMPRESSED_STREAM_BYTES
    pdf_filters.RUN_LENGTH_MAX_OUTPUT_LENGTH = (
        MAX_PDF_DECOMPRESSED_STREAM_BYTES
    )
    try:
        reader = PdfReader(io.BytesIO(content), strict=True)
        if reader.is_encrypted:
            raise EvidenceExtractionError(
                "Password-protected PDFs require a participant-provided text copy."
            )
        if len(reader.pages) > MAX_PDF_PAGES:
            raise EvidenceExtractionError(
                "The PDF exceeds the 250-page extraction limit."
            )
        blocks: list[SourceBlock] = []
        warnings: list[str] = []
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            page_blocks = _text_blocks(
                _bounded_text(page_text),
                locator_prefix=f"page {page_number}, paragraph",
            )
            blocks.extend(page_blocks)
            if not page_text.strip():
                warnings.append(
                    f"Page {page_number} produced no selectable text; OCR was not attempted."
                )
        if not blocks:
            raise EvidenceExtractionError(
                "The PDF produced no selectable text. Provide a text-readable copy "
                "or route it to an approved OCR process."
            )
        return blocks, warnings, "pdf/pypdf-selectable-text"
    except EvidenceExtractionError:
        raise
    except (PyPdfError, ValueError, TypeError, KeyError) as exc:
        raise EvidenceExtractionError(
            "The PDF could not be parsed safely."
        ) from exc


def _heading_key(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", text.lower()).strip()


def _looks_like_heading(text: str) -> bool:
    key = _heading_key(text)
    if key in SECTION_LABELS:
        return True
    return (
        len(text) <= 70
        and len(text.split()) <= 8
        and text.rstrip().endswith(":")
    )


def _classify_evidence(text: str, section_type: str) -> tuple[str, str]:
    lowered = text.lower()
    if re.search(
        r"\b(achieved|awarded|improved|increased|reduced|saved|exceeded|"
        r"completed ahead|recognized)\b",
        lowered,
    ):
        return "achievement", "bounded lexical indicator"
    if re.search(
        r"\b(responsible for|managed|oversaw|supervised|administered|maintained)\b",
        lowered,
    ):
        return "responsibility", "bounded lexical indicator"
    if re.search(
        r"\b(created|developed|produced|delivered|implemented|authored|designed)\b",
        lowered,
    ):
        return "output", "bounded lexical indicator"
    if re.search(
        r"\b(completed|graduated|certified|earned|received)\b",
        lowered,
    ):
        return "event", "bounded lexical indicator"
    if section_type in {
        "activity",
        "achievement",
        "event",
        "output",
        "responsibility",
    }:
        return section_type, "source section label"
    return "statement", "neutral default"


def _candidate_chunks(text: str) -> Iterable[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return
    while len(normalized) > MAX_CANDIDATE_CHARACTERS:
        split_at = normalized.rfind(". ", 0, MAX_CANDIDATE_CHARACTERS)
        if split_at < 200:
            split_at = normalized.rfind(" ", 0, MAX_CANDIDATE_CHARACTERS)
        if split_at < 1:
            split_at = MAX_CANDIDATE_CHARACTERS
        yield normalized[: split_at + 1].strip()
        normalized = normalized[split_at + 1 :].strip()
    if normalized:
        yield normalized


def normalize_candidates(blocks: list[SourceBlock]) -> list[dict[str, str]]:
    """Turn source blocks into conservative, review-pending Evidence fields."""

    candidates: list[dict[str, str]] = []
    section_label = ""
    section_type = "statement"
    for block in blocks:
        if _looks_like_heading(block.text):
            section_label = block.text.rstrip(":").strip()
            section_type = SECTION_LABELS.get(
                _heading_key(block.text),
                "statement",
            )
            continue
        for chunk in _candidate_chunks(block.text):
            if len(candidates) >= MAX_CANDIDATES:
                raise EvidenceExtractionError(
                    "The document exceeds the 500-candidate review limit."
                )
            evidence_type, basis = _classify_evidence(chunk, section_type)
            candidates.append(
                {
                    "evidence_text": chunk,
                    "evidence_type": evidence_type,
                    "source_locator": block.source_locator,
                    "source_section": section_label,
                    "extraction_method": "automated",
                    "fidelity_status": "normalized",
                    "review_status": "unreviewed",
                    "classification_basis": basis,
                    "capability_assertions_created": "none",
                }
            )
    return candidates


class SafeEvidenceExtractor:
    """Extract supported content without executing document or archive content."""

    def extract(self, *, filename: str, content: bytes) -> dict[str, Any]:
        extension = Path(filename).suffix.lower()
        if extension in MANUAL_REVIEW_EXTENSIONS:
            return {
                "extraction_status": "review_required",
                "parser_id": PARSER_VERSION,
                "parser_profile": "manual-preparation-required",
                "source_extension": extension,
                "extracted_text": "",
                "extracted_text_checksum": "",
                "candidates": [],
                "warnings": [
                    (
                        "Legacy .doc files require conversion to DOCX, PDF, RTF, or "
                        "plain text before extraction."
                        if extension == ".doc"
                        else "General ZIP archives are retained but not expanded by "
                        "the evidence extractor."
                    )
                ],
                "capability_assertions_created": [],
            }
        if extension not in SUPPORTED_EXTENSIONS:
            raise EvidenceExtractionError(
                "This document type has no approved extraction parser."
            )
        if extension == ".txt":
            blocks, warnings, parser_profile = _extract_txt(content)
        elif extension == ".csv":
            blocks, warnings, parser_profile = _extract_csv(content)
        elif extension == ".rtf":
            blocks, warnings, parser_profile = _extract_rtf(content)
        elif extension == ".docx":
            blocks, warnings, parser_profile = _extract_docx(content)
        else:
            blocks, warnings, parser_profile = _extract_pdf(content)
        extracted_text = _bounded_text(
            "\n\n".join(block.text for block in blocks)
        )
        candidates = normalize_candidates(blocks)
        status = "complete" if candidates else "review_required"
        if not candidates:
            warnings.append(
                "No reviewable evidence candidates were produced."
            )
        return {
            "extraction_status": status,
            "parser_id": PARSER_VERSION,
            "parser_profile": parser_profile,
            "source_extension": extension,
            "extracted_text": extracted_text,
            "extracted_text_checksum": (
                _sha256_text(extracted_text) if extracted_text else ""
            ),
            "candidates": candidates,
            "warnings": warnings,
            "capability_assertions_created": [],
        }
