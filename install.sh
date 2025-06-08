#!/usr/bin/env bash
# Simple setup script for RealEstateScraper
set -e
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
if [[ "$(uname -s)" == *NT* || "$(uname -s)" == *MINGW* || "$(uname -s)" == *MSYS* ]]; then
  pip install -r RealEstateScraper/requirements.txt
else
  grep -v '^win10toast' RealEstateScraper/requirements.txt | pip install -r /dev/stdin
fi
echo "Environment setup complete. Activate with 'source venv/bin/activate'"
