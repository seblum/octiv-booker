#!/bin/bash
set -e

# Ensure jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found, installing..."
    sudo apt-get install -y jq
fi

# Fetch the latest version number from GoogleChromeLabs
LATEST_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json | jq -r '.milestones | to_entries | map(.value.version) | max')

# Update the Dockerfile with the latest version
sed -i "s/ENV ChromedriverVersion=\"[^\"]*\"/ENV ChromedriverVersion=\"$LATEST_VERSION\"/" Dockerfile

echo "Updated Dockerfile with ChromeDriver version $LATEST_VERSION"
