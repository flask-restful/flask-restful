.PHONY: test install

install: venv
	. venv/bin/activate; python setup.py develop

venv:
	virtualenv venv

test:
	. venv/bin/activate; python setup.py nosetests

analysis:
	. venv/bin/activate; flake8 --select=E112,E113,E901,E902,W601,W602,W603,W604,W402,W403,W404,W801,W802,W803,W804,W805,W806 flask_restful tests

release: test
	$(shell python scripts/release.py $(shell python setup.py -V))
