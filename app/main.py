#!/usr/bin/env python3
"""
Informativos Builder - GUI
- Seleciona a pasta com PDFs (padrão: NUM-SIGLA-ANO.pdf)
- Extrai infos do PDF (número, sigla, nome completo, ano e semestre)
- Gera as <li> no padrão do Curso Objetivo e salva em um HTML

Requisitos: PyPDF2
"""
import re
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import PyPDF2
except Exception:
    PyPDF2 = None

SVG = '''<svg aria-labelledby="icon-download-solid" role="img" enable-background="new 0 0 24 24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="svg-8 svg-fill-white mb-1">
  <path d="m12 16c-.205 0-.401-.084-.543-.232l-5.25-5.5c-.455-.477-.114-1.268.543-1.268h2.75v-1.25c0-4.273 3.477-7.75 7.75-7.75.414 0 .75.336.75.75s-.336.75-.75.75c-1.517 0-2.75 1.233-2.75 2.75v4.75h2.75c.657 0 .998.791.543 1.268l-5.25 5.5c-.142.148-.338.232-.543.232z"></path>
  <path d="m21 18h-18c-1.654 0-3 1.346-3 3s1.346 3 3 3h18c1.654 0 3-1.346 3-3s-1.346-3-3-3z"></path>
</svg>'''

KNOWN_FULLNAMES = {
    "FASM": "Faculdade Santa Marcelina",
    # Adicione mapeamentos conforme necessário
}

def read_text(pdf_path: Path) -> str:
    if PyPDF2 is None:
        return ""
    try:
        reader = PyPDF2.PdfReader(str(pdf_path))
        parts = []
        for p in reader.pages:
            parts.append(p.extract_text() or "")
        return "\n".join(parts)
    except Exception:
        return ""

def parse_fields(text: str, filename: str):
    # Número no rodapé: "N.º 275"
    m = re.search(r"N[\.ºo]?\s*[:.]?\s*(\d{1,4})\s*$", text, re.IGNORECASE | re.MULTILINE)
    number = m.group(1) if m else None

    # Cabeçalho: "FASM – FACULDADE SANTA MARCELINA / 2026"
    m = re.search(r"^\s*([A-Z0-9]{2,})\s*[–-]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s\.\-/'&]+?)\s*/\s*(\d{4})\s*$", text, re.MULTILINE)
    acronym = m.group(1).strip() if m else None
    fullname = " ".join(m.group(2).split()) if m else None
    year = m.group(3) if m else None

    # Semestre: "1.º semestre" ou "2.º semestre"
    m = re.search(r"(\d)\.\s*º\s*semestre", text, re.IGNORECASE)
    sem = m.group(1) if m else None

    # Fallback para nome do arquivo: 275-FASM-2026.pdf
    m = re.search(r"(\d+)-([A-Za-z0-9]+)-(\d{4})\.pdf$", filename, re.IGNORECASE)
    if m:
        number = number or m.group(1)
        acronym = acronym or m.group(2).upper()
        year = year or m.group(3)

    if not fullname and acronym:
        fullname = KNOWN_FULLNAMES.get(acronym, acronym)

    sem = sem or "1"
    return number, acronym, fullname, year, sem

def build_li(number, acronym, fullname, year, sem, filename):
    href = f"assets/download/informativos/{year}/{filename}"
    title = f"Veja o informativo da {fullname} ({year}.{sem})"
    return (
        '<li class="informativo list-group-item col-12 col-md-6 border-end">\n'
        f'  <a class="page-pdf" href="{href}" title="{title}">\n'
        f'    {number}. {acronym}\n'
        '    <span class="badge bg-primary rounded-pill float-end">PDF\n'
        f'      {SVG}\n'
        '    </span>\n'
        '  </a>\n'
        '</li>'
    )

def sanitize_part(value: str, pattern: str) -> str:
    cleaned = re.sub(pattern, "", value or "")
    return cleaned

def build_filename(number: str, acronym: str, year: str) -> str:
    number_clean = sanitize_part(number, r"[^0-9]")
    acronym_clean = sanitize_part(acronym.upper(), r"[^A-Z0-9]")
    year_clean = sanitize_part(year, r"[^0-9]")
    if not (number_clean and acronym_clean and year_clean):
        return ""
    return f"{number_clean}-{acronym_clean}-{year_clean}.pdf"

def ensure_unique_name(folder: Path, filename: str) -> Path:
    target = folder / filename
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    counter = 1
    while True:
        candidate = folder / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1

def maybe_rename_pdf(pdf: Path, number: str, acronym: str, year: str) -> Path:
    desired_name = build_filename(number, acronym, year)
    if not desired_name:
        return pdf
    if pdf.name == desired_name:
        return pdf
    target = ensure_unique_name(pdf.parent, desired_name)
    try:
        pdf = pdf.rename(target)
    except Exception:
        return pdf
    return pdf

def generate_from_folder(folder: Path) -> str:
    pdfs = sorted(p for p in folder.iterdir() if p.suffix.lower()==".pdf")
    items = []
    for pdf in pdfs:
        text = read_text(pdf)
        number, acronym, fullname, year, sem = parse_fields(text, pdf.name)
        # Guard-rails
        if not (number and acronym and year):
            m = re.search(r"(\d+)-([A-Za-z0-9]+)-(\d{4})\.pdf$", pdf.name, re.IGNORECASE)
            if m:
                number = number or m.group(1)
                acronym = acronym or m.group(2).upper()
                year = year or m.group(3)
                if not fullname:
                    fullname = acronym
                if not sem:
                    sem = "1"
            else:
                continue
        pdf = maybe_rename_pdf(pdf, number, acronym, year)
        items.append(build_li(number, acronym, fullname, year, sem, pdf.name))
    return "\n".join(items)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Informativos Builder")
        self.geometry("640x360")
        self.resizable(False, False)

        self.folder_var = tk.StringVar()
        self.output_var = tk.StringVar()

        frm = ttk.Frame(self, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Pasta com PDFs:").grid(row=0, column=0, sticky="w")
        row1 = ttk.Frame(frm)
        row1.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0,8))
        entry1 = ttk.Entry(row1, textvariable=self.folder_var, width=60)
        entry1.pack(side="left", fill="x", expand=True)
        ttk.Button(row1, text="Selecionar...", command=self.choose_folder).pack(side="left", padx=(8,0))

        ttk.Label(frm, text="Arquivo de saída (.html):").grid(row=2, column=0, sticky="w")
        row2 = ttk.Frame(frm)
        row2.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0,8))
        entry2 = ttk.Entry(row2, textvariable=self.output_var, width=60)
        entry2.pack(side="left", fill="x", expand=True)
        ttk.Button(row2, text="Salvar como...", command=self.choose_output).pack(side="left", padx=(8,0))

        self.progress = ttk.Progressbar(frm, mode="determinate", maximum=100)
        self.progress.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8,8))

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=3, sticky="e")
        ttk.Button(btns, text="Gerar HTML", command=self.run).pack(side="left")
        ttk.Button(btns, text="Sair", command=self.destroy).pack(side="left", padx=(8,0))

        for i in range(3):
            frm.columnconfigure(i, weight=1)

        if PyPDF2 is None:
            messagebox.showwarning("Aviso", "A biblioteca PyPDF2 não está instalada. Instale para extrair texto dos PDFs. O app ainda consegue usar o nome do arquivo como fallback.")

    def choose_folder(self):
        p = filedialog.askdirectory()
        if p:
            self.folder_var.set(p)

    def choose_output(self):
        f = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML","*.html")], initialfile="informativos.html")
        if f:
            self.output_var.set(f)

    def run(self):
        folder = Path(self.folder_var.get().strip() or ".")
        if not folder.exists():
            messagebox.showerror("Erro", "Selecione uma pasta válida com PDFs.")
            return
        out = self.output_var.get().strip()
        if not out:
            messagebox.showerror("Erro", "Escolha o arquivo de saída (.html).")
            return

        try:
            self.progress["value"] = 10
            self.update_idletasks()
            html = generate_from_folder(folder)
            self.progress["value"] = 80
            self.update_idletasks()
            Path(out).write_text(html, encoding="utf-8")
            self.progress["value"] = 100
            messagebox.showinfo("Concluído", f"Arquivo gerado:\n{out}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar HTML:\n{e}")
        finally:
            self.progress["value"] = 0

if __name__ == "__main__":
    app = App()
    app.mainloop()
