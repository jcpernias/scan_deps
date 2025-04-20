
all: test


.PHONY: test
test: test_scan_deps.py scan_deps.py
	pytest $<
