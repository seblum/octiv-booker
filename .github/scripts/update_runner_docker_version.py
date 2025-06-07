import re
import os


def update_docker_image_version(version: str, workflow_dirs=None):
    """
    Update docker_image version in all workflow files starting with 'runner-'.

    Args:
        version: The version string to update to (e.g. "2.6.3").
        workflow_dirs: List of directories containing workflow YAML files.
    """
    if workflow_dirs is None:
        workflow_dirs = [".github/workflows", ".github/hooks"]

    for workflows_dir in workflow_dirs:
        print(f"\nLooking in: {workflows_dir}")
        try:
            files_in_dir = os.listdir(workflows_dir)
            for f in files_in_dir:
                print(f" - {f}")
        except FileNotFoundError:
            print(f"Directory {workflows_dir} not found!")
            continue

        runner_files = [
            f for f in files_in_dir if f.startswith("runner-") and f.endswith(".yaml")
        ]

        if not runner_files:
            print(f"No files starting with 'runner-' found in {workflows_dir}")
            continue

        # Regex to find docker_image: octivbooker:v<version>
        docker_image_pattern = re.compile(
            r"^(\s*docker_image:\s*octivbooker:)v[\d\.]+",
            re.MULTILINE,
        )

        for filename in runner_files:
            filepath = os.path.join(workflows_dir, filename)
            print(f"\nUpdating file: {filepath}")
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            new_content, count = docker_image_pattern.subn(
                rf"\1v{version}",
                content,
            )

            if count == 0:
                print(f"Warning: No docker_image line found in {filepath}")
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated docker_image to octivbooker:v{version} in {filepath}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <TAG_VERSION>")
        sys.exit(1)

    tag_version = sys.argv[1]
    update_docker_image_version(tag_version)
