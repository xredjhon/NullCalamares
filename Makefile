PYTHON := python3

.PHONY: build validate verify-packages ascii-check clean

build:
	$(PYTHON) scripts/build.py

validate:
	$(PYTHON) scripts/build.py

verify-packages:
	$(PYTHON) scripts/verify_repo_packages.py

ascii-check:
	$(PYTHON) scripts/check_ascii.py

clean:
	rm -rf dist
