#!/usr/bin/env bash

test -d venv || virtualenv -p python3 venv
venv/bin/pip install -Ur requirements.txt
venv/bin/pip install awscli

test "$TRAVIS_BRANCH" = "master" && export ENV="prod" || export ENV="dev"

./venv/bin/chalice deploy --stage "$ENV"
CHALICE_URL=$(./venv/bin/chalice url)

sed -i "s|http://localhost:8000/|$CHALICE_URL/|g" ./ui/index.html

./venv/bin/aws s3 cp ./ui/. s3://cronrange-bucket-$ENV/ --recursive