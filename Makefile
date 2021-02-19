PROC=$(uname -p)

.PHONY: venv

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "See the README.md for additional usage and customization options"

iperf: ## Make iperf3 command from source (scripts/make_iperf.sh), use host arch (no cross compile) 
	./scripts/make_iperf.sh

venv: ## make virtual enviroment and activate
	./scripts/make_venv.sh
