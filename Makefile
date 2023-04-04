PROC=$(uname -p)

.PHONY: venv

####### RUN make help <---------

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "Steps:"
	@echo "1. sudo make user"
	@echo "2. make ndt"
	@echo "3. make oplat"
	@echo "4. sudo make iperf"
	@echo "5. make speedtest"
	@echo "6. sudo make deps"
	@echo "7. sudo make venv"
	@echo "8. sudo make install"
	@echo "9. make build"

iperf: ## Install iperf3 command from source, use host arch (no cross compile) 
	./scripts/make_iperf.sh

ndt: ## Install ndt command for host arch
	./scripts/make_ndt.sh

oplat: ## Install oplat command for host arch
	./scripts/make_oplat.sh

speedtest: ## Install speedtest command for host arch
	./scripts/make_speedtest.sh

deps: ## Install dependencies via apt-get install
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	python3 get-pip.py
	apt -q -y --fix-broken install
	apt-get -q -y install net-tools jq
	apt-get -q -y install traceroute
	apt-get -q -y install dnsutils
	apt-get -q -y install nmap
	apt-get -q -y install build-essential
	apt-get -q -y install python3-venv
	apt-get -q -y install tshark
	#apt-get -q -y install chromium-chromedriver #(disabled)

venv: ## Make virtual enviroment and activate it
	./scripts/make_venv.sh
	ln -s /usr/local/src/nm-exp-active-netrics/venv ./venv

vca: ## Make vca 
	./scripts/make_vca.sh

build: ## Build .deb package for the current arch
	cd package/deb/; ./build.sh; cp nm-exp-active-netrics*.deb ~/

install: ## Copy files to the device filesystem at /usr/local/src, /usr/local/bin, /etc/init.d/ and /etc/nm-exp-active-netrics
	./scripts/make_install.sh

user: ## Make system user group netrics:netrics
	./scripts/make_netrics_user_group.sh

plugin-vca:
	git submodule init
	git submodule update --remote
	sudo apt -y install xvfb python3-tk python3-dev scrot xdg-utils 
	sudo snap install chromium
	source ./venv/bin/activate; pip install -r src/netrics/plugin/netrics-vca-test/requirements.txt 

clearlogs: ## Remove nm-exp-active-netrics.log
	rm -f /tmp/nm/nm-exp-active-netrics/log/nm-exp-active-netrics.log

clearpending: ## Remove /tmp/nm/nm-exp-active-netrics/upload/pending
	rm -Rf /tmp/nm/nm-exp-active-netrics/upload/pending

cleararchive: ## Remove /tmp/nm/nm-exp-active-netrics/upload/archive
	rm -Rf /tmp/nm/nm-exp-active-netrics/upload/archive

cleantmp: ## Remove /tmp/nm/
	rm -Rf /tmp/nm/nm-exp-active-netrics/

clean: ## Clean all /tmp/nm/nm-exp-active-netrics/*
	rm -Rf /tmp/nm/nm-exp-active-netrics/
	rm -Rf /usr/local/src/nm-exp-active-netrics/
