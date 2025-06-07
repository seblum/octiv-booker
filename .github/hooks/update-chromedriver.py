import sys
import subprocess
import requests
import re
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python update_chromedriver_version.py <Dockerfile>")
        sys.exit(1)

    dockerfile_path = Path(sys.argv[1])

    if not dockerfile_path.exists():
        print(f"Error: File not found: {dockerfile_path}")
        sys.exit(1)

    # Ensure jq is installed (optional in Python, but you can check subprocess call here if needed)
    try:
        subprocess.run(["jq", "--version"], check=True, stdout=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: jq not found. Not required for Python version.")

    # Get the latest stable ChromeDriver version
    try:
        resp = requests.get(
            "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
        )
        resp.raise_for_status()
        latest_stable = resp.json()["channels"]["Stable"]["version"]
    except Exception as e:
        print(f"Failed to fetch latest ChromeDriver version: {e}")
        sys.exit(1)

    # Read and update Dockerfile
    original_content = dockerfile_path.read_text()
    updated_content, count = re.subn(
        r'ENV\s+ChromedriverVersion="[^"]+"',
        f'ENV ChromedriverVersion="{latest_stable}"',
        original_content,
    )

    if count == 0:
        print("No ChromedriverVersion line found to update.")
        sys.exit(1)

    dockerfile_path.write_text(updated_content)
    print(f"Updated {dockerfile_path} with ChromeDriver version {latest_stable}")


if __name__ == "__main__":
    main()
