#!/bin/bash
set -e

# Read the arguments passed to the script
DOCKERFILE=$1

if [ -z "$DOCKERFILE" ]; then
    echo "Usage: $0 <Dockerfile>"
    exit 1
fi

# Ensure jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found, installing..."
    sudo apt-get install -y jq
fi

# Fetch the latest version number from GoogleChromeLabs
# LATEST_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json | jq -r '.milestones | to_entries | map(.value.version) | max')
LATEST_STABLE_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json" | jq -r '.channels.Stable.version')

# Update the Dockerfile with the latest version
sed -i '' -e "s/ENV ChromedriverVersion=\"[^\"]*\"/ENV ChromedriverVersion=\"$LATEST_STABLE_VERSION\"/" "$DOCKERFILE"

echo "Updated $DOCKERFILE with ChromeDriver version $LATEST_STABLE_VERSION"
