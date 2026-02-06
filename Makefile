# IRCTC Takedown Report – build from data/ → output/
# Run from project root. Ensure: export PYTHONPATH=src (or use make which sets it)

PY    := .venv/bin/python
ifneq ($(wildcard .venv),)
  PY := .venv/bin/python
else
  PY := python3
endif
DATA  := data
OUT   := output/IRCTC_Takedown_Report_generated.html
PDF   := output/IRCTC_Takedown_Report_generated.pdf
export PYTHONPATH := $(CURDIR)/src:$(PYTHONPATH)

.PHONY: report report-pdf open auto clean upload

report:
	$(PY) -m scripts.generate_report --data-dir $(DATA) --output $(OUT)
	@echo "HTML: $(OUT)"

report-pdf:
	$(PY) -m scripts.generate_report --data-dir $(DATA) --output $(OUT) --pdf
	@echo "PDF:  $(PDF)"

open: report-pdf
	@if command -v xdg-open >/dev/null 2>&1; then xdg-open $(PDF); \
	elif command -v open >/dev/null 2>&1; then open $(PDF); \
	else echo "Open $(PDF) manually"; fi

auto:
	$(PY) -m scripts.automate_report
	@echo "HTML + PDF generated with today's date."

upload:
	$(PY) -m scripts.app_upload

clean:
	rm -f $(OUT) $(PDF) output/main_logo.png
