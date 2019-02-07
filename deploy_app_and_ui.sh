#!/usr/bin/env bash
set -e

test -d venv || virtualenv -p python3 venv
venv/bin/pip install -Ur requirements.txt
venv/bin/pip install awscli

test "${TRAVIS_BRANCH}" = "master" && export ENV="prod" || export ENV="dev"

./venv/bin/chalice deploy --stage "${ENV}"
CHALICE_URL=$(./venv/bin/chalice url --stage "${ENV}")

# minify CSS
curl -X POST -s --data-urlencode 'input@./ui/css/style.css' https://cssminifier.com/raw > ./ui/css/style.min.css
sed -i "s|css/style.css|css/style.min.css|g" ./ui/index.html
rm -f ./ui/css/style.css

# minify JS
curl -X POST -s --data-urlencode 'input@./ui/js/main.js' https://javascript-minifier.com/raw > ./ui/js/main.min.js
sed -i "s|js/main.js|js/main.min.js|g" ./ui/index.html
rm -f ./ui/js/main.js

sed -i "s|http://localhost:8000/|$CHALICE_URL|g" ./ui/js/main.min.js

if [[ "${ENV}" = "dev" ]]; then
    ./venv/bin/aws s3 cp ./ui/. s3://dev.cronrange.info/ --recursive
else
    ./venv/bin/aws s3 cp ./ui/. s3://cronrange.info/ --recursive
fi
