PROCESS_INPUT ?= ./pdfs
PROCESS_OUT ?= informativos.html
PROCESS_DEST ?= assets/download/informativos
PROCESS_REPORT ?= relatorio_processamento.json

.PHONY: processar
processar:
	python -m app.processor.cli $(PROCESS_INPUT) --out $(PROCESS_OUT) --dest-root $(PROCESS_DEST) --report $(PROCESS_REPORT)
