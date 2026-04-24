.PHONY: help

SHELL := /bin/bash

help: ## Display this help page
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Cleanup artifacts
	@rm -rf dist/

ci: ## Generate ci pipeline
	./ch template ci --provider github --output .github/workflows/main.yml
