#!/usr/bin/env bash
set -e

ENV="${ENV:=dev}"

test -d venv || virtualenv -p python3 venv
venv/bin/pip install -Ur requirements.txt
venv/bin/pip install awscli

# SSM param created with CDK
API_URL=$(aws ssm get-parameter --name "/${ENV}/cronrange/api_url" | jq -r '.Parameter.Value')

# minify CSS
curl -X POST -s --data-urlencode input@ui/css/style.css https://www.toptal.com/developers/cssminifier/api/raw > ./ui/css/style.min.css
sed -i "s|css/style.css|css/style.min.css|g" ./ui/index.html

# minify JS
curl -X POST -s --data-urlencode "input@./ui/js/main.js" https://www.toptal.com/developers/javascript-minifier/api/raw > ./ui/js/main.min.js
sed -i "s|js/main.js|js/main.min.js|g" ./ui/index.html

sed -i "s|http://localhost:8000/|$API_URL|g" ./ui/js/main.min.js

if [[ "${ENV}" = "dev" ]]; then
    sed -i "s|HOSTNAME_HERE|http://dev.cronrange.info|g" ./ui/index.html
    ./venv/bin/aws s3 sync ./ui/. s3://dev.cronrange.info/ --exclude "css/style.css" --exclude "js/main.js"
else
    sed -i "s|HOSTNAME_HERE|https://cronrange.info|g" ./ui/index.html
    ./venv/bin/aws s3 sync ./ui/. s3://cronrange.info/ --exclude "css/style.css" --exclude "js/main.js"
fi
