from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.processor import cli, pdf_extract


@pytest.fixture(autouse=True)
def restore_pdf_reader(monkeypatch):
    # Ensure tests do not depend on real PDF parsing.
    original = pdf_extract._read_pdf_text

    yield

    monkeypatch.setattr(pdf_extract, "_read_pdf_text", original)


def write_fake_pdf(path: Path) -> None:
    path.write_text("fake", encoding="utf-8")


def test_process_directory_full_pdf(tmp_path, monkeypatch):
    pdf_path = tmp_path / "input"
    pdf_path.mkdir()
    file_path = pdf_path / "example.pdf"
    write_fake_pdf(file_path)

    text = """
FASM – Faculdade Santa Marcelina / 2026
1.º semestre
N.º 275
"""
    monkeypatch.setattr(pdf_extract, "_read_pdf_text", lambda _: text)

    dest_root = tmp_path / "assets" / "download" / "informativos"
    out_html = tmp_path / "informativos.html"
    report_path = tmp_path / "relatorio.json"

    report = cli.process_directory(pdf_path, out_html, report_path, dest_root)

    target = dest_root / "2026" / "275-FASM-2026.pdf"
    assert target.exists()
    html = out_html.read_text(encoding="utf-8")
    assert "275. FASM" in html
    assert "Veja o informativo da Faculdade Santa Marcelina (2026.1)" in html

    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["processed"][0]["metadata"]["number"] == "275"
    assert not data["pending"]


def test_fallback_number_from_filename(tmp_path, monkeypatch):
    pdf_dir = tmp_path / "input"
    pdf_dir.mkdir()
    file_path = pdf_dir / "UNISINOS.262.pdf"
    write_fake_pdf(file_path)

    text = """
UNISINOS – Universidade do Vale do Rio dos Sinos / 2026
2.º semestre
"""
    monkeypatch.setattr(pdf_extract, "_read_pdf_text", lambda _: text)

    dest_root = tmp_path / "dest"
    out_html = tmp_path / "out.html"
    report_path = tmp_path / "report.json"

    report = cli.process_directory(pdf_dir, out_html, report_path, dest_root)

    target = dest_root / "2026" / "262-UNISINOS-2026.pdf"
    assert target.exists()
    html = out_html.read_text(encoding="utf-8")
    assert "262. UNISINOS" in html
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["processed"][0]["number_source"] == "filename"
    assert report["processed"][0]["metadata"]["semester"] == "2"


def test_default_semester_when_missing(tmp_path, monkeypatch):
    pdf_dir = tmp_path / "input"
    pdf_dir.mkdir()
    file_path = pdf_dir / "foo.pdf"
    write_fake_pdf(file_path)

    text = """
ABC – Faculdade ABC / 2024
N.º 11
"""
    monkeypatch.setattr(pdf_extract, "_read_pdf_text", lambda _: text)

    dest_root = tmp_path / "dest"
    out_html = tmp_path / "out.html"
    report_path = tmp_path / "report.json"

    report = cli.process_directory(pdf_dir, out_html, report_path, dest_root)

    html = out_html.read_text(encoding="utf-8")
    assert "2024.1" in html
    assert report["processed"][0]["metadata"]["semester"] == "1"


def test_pending_when_no_text(tmp_path, monkeypatch):
    pdf_dir = tmp_path / "input"
    pdf_dir.mkdir()
    file_path = pdf_dir / "pending.pdf"
    write_fake_pdf(file_path)

    monkeypatch.setattr(pdf_extract, "_read_pdf_text", lambda _: "")

    dest_root = tmp_path / "dest"
    out_html = tmp_path / "out.html"
    report_path = tmp_path / "report.json"

    report = cli.process_directory(pdf_dir, out_html, report_path, dest_root)

    assert not report["processed"]
    assert report["pending"]
    assert "Não encontrou" in report["pending"][0]["reason"]


def test_collision_appends_suffix(tmp_path, monkeypatch):
    pdf_dir = tmp_path / "input"
    pdf_dir.mkdir()
    first = pdf_dir / "file1.pdf"
    second = pdf_dir / "file2.pdf"
    write_fake_pdf(first)
    write_fake_pdf(second)

    texts = {
        "file1.pdf": """
XYZ – Faculdade XYZ / 2025
N.º 12
""",
        "file2.pdf": """
XYZ – Faculdade XYZ / 2025
N.º 12
""",
    }

    monkeypatch.setattr(pdf_extract, "_read_pdf_text", lambda path: texts[path.name])

    dest_root = tmp_path / "dest"
    out_html = tmp_path / "out.html"
    report_path = tmp_path / "report.json"

    cli.process_directory(pdf_dir, out_html, report_path, dest_root)

    expected_a = dest_root / "2025" / "12-XYZ-2025.pdf"
    expected_b = dest_root / "2025" / "12-XYZ-2025-A.pdf"

    assert expected_a.exists()
    assert expected_b.exists()
