"""Command line interface for processing informativo PDFs."""
from __future__ import annotations

import argparse
import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .html_builder import build_li
from .normalizer import (
    build_target_name,
    ensure_destination,
    ensure_unique_filename,
    sanitize_metadata,
)
from .pdf_extract import extract_metadata

LOGGER = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    original_path: Path
    final_path: Optional[Path]
    metadata: Dict[str, str]
    number_source: str
    pending_reason: Optional[str] = None

    @property
    def is_pending(self) -> bool:
        return self.pending_reason is not None


def process_pdf(
    pdf_path: Path,
    dest_root: Path,
    force_filename: bool = False,
) -> ProcessResult:
    metadata = extract_metadata(pdf_path)
    sanitized = sanitize_metadata(metadata)
    metadata.update(sanitized)

    missing = []
    if not metadata.get("acronym"):
        missing.append("SIGLA")
    if not metadata.get("fullname"):
        missing.append("Title")
    if not metadata.get("year"):
        missing.append("ANO")

    number = metadata.get("number")
    number_source = metadata.get("number_source", "missing")
    if not number:
        missing.append("número")
    elif number_source == "filename" and not force_filename:
        LOGGER.info(
            "Número derivado do nome do arquivo para %s", pdf_path.name
        )

    if missing:
        reason = "Não encontrou " + ", ".join(missing) + " no PDF"
        if "número" in missing and number_source == "missing":
            reason = "Não encontrou número no PDF nem no nome do arquivo"
        return ProcessResult(
            original_path=pdf_path,
            final_path=None,
            metadata=metadata,
            number_source=number_source,
            pending_reason=reason,
        )

    destination_folder = ensure_destination(metadata["year"], dest_root)
    target_name = build_target_name(metadata)
    final_path = ensure_unique_filename(destination_folder, target_name)

    shutil.move(str(pdf_path), final_path)

    return ProcessResult(
        original_path=pdf_path,
        final_path=final_path,
        metadata=metadata,
        number_source=number_source,
    )


def process_directory(
    input_dir: Path,
    out_html: Path,
    report_path: Path,
    dest_root: Path,
    force_filename: bool = False,
) -> Dict[str, List[Dict[str, str]]]:
    pdf_files = sorted(
        [p for p in input_dir.iterdir() if p.suffix.lower() == ".pdf"],
        key=lambda p: p.name,
    )

    processed: List[ProcessResult] = []

    for pdf in pdf_files:
        try:
            result = process_pdf(pdf, dest_root, force_filename=force_filename)
            processed.append(result)
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Falha ao processar %s", pdf)
            processed.append(
                ProcessResult(
                    original_path=pdf,
                    final_path=None,
                    metadata={},
                    number_source="missing",
                    pending_reason=f"Erro inesperado: {exc}",
                )
            )

    successes = [r for r in processed if not r.is_pending]
    pendings = [r for r in processed if r.is_pending]

    html_entries = []
    sortable_entries = []
    for index, result in enumerate(successes):
        metadata = result.metadata.copy()
        # Guarantee values for HTML
        display_meta = {
            "number": metadata["number"],
            "acronym": metadata["acronym"],
            "fullname": metadata["fullname"],
            "year": metadata["year"],
            "semester": metadata.get("semester", "1"),
        }
        html_entries.append((index, display_meta, result.final_path.name))
        try:
            sort_number = int(display_meta["number"])
        except (TypeError, ValueError):
            sort_number = float("inf")
        sortable_entries.append((sort_number, index))

    sortable_entries.sort()
    ordered_html = []
    for _, idx in sortable_entries:
        meta = html_entries[idx][1]
        filename = html_entries[idx][2]
        ordered_html.append(build_li(meta, filename))

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text("\n".join(ordered_html), encoding="utf-8")

    report = {
        "processed": [
            {
                "original": str(r.original_path),
                "final": str(r.final_path) if r.final_path else None,
                "metadata": r.metadata,
                "number_source": r.number_source,
            }
            for r in successes
        ],
        "pending": [
            {
                "original": str(r.original_path),
                "reason": r.pending_reason,
                "metadata": r.metadata,
            }
            for r in pendings
        ],
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    total = len(processed)
    LOGGER.info(
        "Processados: %s | Sucesso: %s | Pendências: %s",
        total,
        len(successes),
        len(pendings),
    )

    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Processa PDFs de informativos")
    parser.add_argument("input_dir", type=Path, help="Pasta com os PDFs")
    parser.add_argument("--out", dest="out_html", type=Path, default=Path("informativos.html"))
    parser.add_argument(
        "--dest-root",
        dest="dest_root",
        type=Path,
        default=Path("assets/download/informativos"),
        help="Pasta raiz para salvar os PDFs normalizados",
    )
    parser.add_argument(
        "--report",
        dest="report_path",
        type=Path,
        default=Path("relatorio_processamento.json"),
        help="Arquivo JSON de relatório",
    )
    parser.add_argument(
        "--force-filename",
        action="store_true",
        help="Permite usar número extraído do nome do arquivo quando ausente no PDF",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    report = process_directory(
        input_dir=args.input_dir,
        out_html=args.out_html,
        report_path=args.report_path,
        dest_root=args.dest_root,
        force_filename=args.force_filename,
    )

    print(
        f"Processados: {len(report['processed']) + len(report['pending'])} | "
        f"Sucesso: {len(report['processed'])} | Pendências: {len(report['pending'])}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
