PROC=$(uname -p)

.PHONY: venv

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "Steps:"
	@echo "1. sudo make iperf"
	@echo "2. sudo make deps"
	@echo "3. make venv"
	@echo "4. sudo make install"

iperf: ## Install iperf3 command from source (scripts/make_iperf.sh), use host arch (no cross compile) 
	./scripts/make_iperf.sh

deps: ## Install dependencies via apt-get install
	apt-get -q -y install net-tools jq
	apt-get -q -y install traceroute
	apt-get -q -y install dnsutils
	apt-get -q -y install chromium-chromedriver nmap speedtest-cli

venv: ## Make virtual enviroment and activate it
	./scripts/make_venv.sh

install: ## Copy files to the device filesystem at /usr/local/src, /usr/local/bin, /etc/init.d/ and /etc/nm-exp-active-netrics
	./scripts/make_install.sh

cleanlogs: ## Remove nm-exp-active-netrics.log
	rm -f /tmp/nm/nm-exp-active-netrics/log/nm-exp-active-netrics.log
