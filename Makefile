.PHONY: test install

install: venv
	. venv/bin/activate; python setup.py develop

venv:
	virtualenv venv

test:
	. venv/bin/activate; python setup.py nosetests

release: test
	$(shell python scripts/release.py $(shell python setup.py -V))
