venv: requirements.txt
	test -d venv || virtualenv -p python3 venv
	venv/bin/pip install -Ur requirements_test.txt

local: venv
	venv/bin/chalice local

test: venv
	venv/bin/python -m unittest discover