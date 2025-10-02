# Informativos Builder

Ferramentas para extrair metadados dos PDFs de informativos, normalizar os arquivos e gerar a listagem em HTML.

## Requisitos
- Python 3.10 ou superior
- Dependências do projeto: `pip install -r requirements.txt`

## Processamento via CLI
1. Organize os PDFs que deseja processar em uma pasta (ex.: `./pdfs`).
2. Execute o comando abaixo a partir da raiz do repositório:
   ```bash
   python -m app.processor.cli ./pdfs --out informativos.html
   ```
   Opções úteis:
   - `--dest-root`: raiz onde os PDFs serão salvos. Padrão: `assets/download/informativos`.
   - `--report`: caminho do relatório JSON com sucessos e pendências. Padrão: `relatorio_processamento.json`.
   - `--force-filename`: permite usar o número extraído do nome do arquivo quando ausente no PDF.
3. O script gera:
   - PDFs renomeados para `NUM-SIGLA-ANO.pdf` (ex.: `275-FASM-2026.pdf`) dentro de `assets/download/informativos/ANO/`.
   - `informativos.html` com um `<li>` por PDF seguindo o padrão do site.
   - `relatorio_processamento.json` com o resumo de processamento.

### Makefile
Há um atalho para processamento:
```bash
make processar PROCESS_INPUT=./pdfs PROCESS_OUT=informativos.html
```
As variáveis `PROCESS_DEST` e `PROCESS_REPORT` podem ser personalizadas se necessário.

## Heurísticas de extração
- Cabeçalho (`SIGLA – NOME COMPLETO / 2026`) → extrai sigla, nome completo e ano.
- Linha `N.º 275` (variações `Nº`, `N.`, `N:`) → extrai o número.
- `1.º semestre` ou `2.º semestre` → extrai o semestre (padrão `1` quando ausente).
- Caso o número não seja encontrado no PDF, é buscado no final do nome original (`UNISINOS.262.pdf → 262`).
- Se sigla, nome completo ou ano não forem encontrados no PDF, o arquivo permanece como pendência.

## Saída HTML
Cada PDF válido gera um `<li>` exatamente como abaixo:
```html
<li class="informativo list-group-item col-12 col-md-6 border-end">
  <a class="page-pdf" href="assets/download/informativos/ANO/NUM-SIGLA-ANO.pdf" title="Veja o informativo da NOME COMPLETO (ANO.SEM)">
    NUM. SIGLA
    <span class="badge bg-primary rounded-pill float-end">PDF
      <svg aria-labelledby="icon-download-solid" role="img" enable-background="new 0 0 24 24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="svg-8 svg-fill-white mb-1">
        <path d="m12 16c-.205 0-.401-.084-.543-.232l-5.25-5.5c-.455-.477-.114-1.268.543-1.268h2.75v-1.25c0-4.273 3.477-7.75 7.75-7.75.414 0 .75.336.75.75s-.336.75-.75.75c-1.517 0-2.75 1.233-2.75 2.75v4.75h2.75c.657 0 .998.791.543 1.268l-5.25 5.5c-.142.148-.338.232-.543.232z"></path>
        <path d="m21 18h-18c-1.654 0-3 1.346-3 3s1.346 3 3 3h18c1.654 0 3-1.346 3-3s-1.346-3-3-3z"></path>
      </svg>
    </span>
  </a>
</li>
```

## Interface gráfica (legado)
O arquivo `app/main.py` mantém a interface gráfica original para uso manual. Ele utiliza as mesmas heurísticas e continua funcionando para cenários simples.
