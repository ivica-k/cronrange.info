venv: requirements.txt
	test -d venv || virtualenv -p python3 venv
	venv/bin/pip install -Ur test_requirements.txt
	venv/bin/pip install -Ur infra/requirements.txt

local: venv
	venv/bin/chalice local --no-autoreload

test: venv
	venv/bin/python -m unittest discover