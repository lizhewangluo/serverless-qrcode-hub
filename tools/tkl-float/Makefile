# Makefile for Taokouling Float Tool

.PHONY: help test clean install run build

help:
	@echo "Available targets:"
	@echo "  install - Install Python dependencies"
	@echo "  test    - Run unit tests"
	@echo "  run     - Run the application in development mode"
	@echo "  build   - Build executable with PyInstaller"
	@echo "  clean   - Clean build artifacts"

install:
	pip install -r requirements.txt

test:
	python test_runner.py

run:
	python quick_start.py

build:
	./build.bat

clean:
	rm -rf build/ dist/ __pycache__/ app/__pycache__/ tests/__pycache__/ app/providers/__pycache__/