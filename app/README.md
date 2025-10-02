# Informativos Builder (.exe leve)

Este app gera automaticamente os `<li>` dos Informativos (Curso Objetivo) a partir de uma pasta com PDFs.

## Requisitos
- Windows 10/11
- Python 3.10 ou superior (https://www.python.org/downloads/)
- (Opcional) Para gerar o `.exe`: PyInstaller

## Como usar sem compilar (modo rápido)
1. Instale o Python e o pip.
2. No Prompt de Comando (ou PowerShell), dentro da pasta `app/`:
   ```bash
   python -m pip install -r requirements.txt
   python main.py
   ```
3. Na janela:
   - Clique em **Selecionar...** e escolha a pasta com os PDFs.
   - Clique em **Salvar como...** e escolha o arquivo `informativos.html`.
   - Clique em **Gerar HTML**.

## Como gerar o `.exe`
1. Abra o Prompt de Comando (ou PowerShell) na pasta `app/`.
2. Rode:
   ```bash
   build.bat
   ```
3. O executável ficará em: `dist/InformativosBuilder.exe`.

## Padrões esperados
- PDFs nomeados como: `NUM-SIGLA-ANO.pdf` (ex.: `275-FASM-2026.pdf`).
- O app tenta extrair do conteúdo do PDF: número, sigla, nome completo, ano e semestre (`1.º` ou `2.º`).
  Caso não encontre, usa o **fallback** baseado no nome do arquivo.
- Quando os dados obrigatórios são encontrados, o PDF é automaticamente renomeado para o padrão `NUM-SIGLA-ANO.pdf`
  (acréscimos numéricos são incluídos se já existir um arquivo com o mesmo nome).
- O HTML gerado segue o padrão:
  ```html
  <li class="informativo list-group-item col-12 col-md-6 border-end">
    <a class="page-pdf" href="assets/download/informativos/ANO/NUM-SIGLA-ANO.pdf" title="Veja o informativo da NOME COMPLETO (ANO.SEM)">
      NUM. SIGLA
      <span class="badge bg-primary rounded-pill float-end">PDF
        <!-- SVG -->
      </span>
    </a>
  </li>
  ```

## Dicas
- Você pode ampliar o dicionário `KNOWN_FULLNAMES` no código para mapear sigla → nome completo.
- Se quiser um ícone no `.exe`, adicione um `.ico` e use a flag `--icon seuicone.ico` no comando do PyInstaller.
