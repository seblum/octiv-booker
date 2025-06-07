import re
import glob
import os


def update_docker_image_version(
    version: str, workflows_dir=".github/workflows", pattern="runner-*.yml"
):
    """
    Update DOCKER_IMAGE version string in matching YAML workflow files.

    Args:
        version: The version string to update to (e.g. "2.6.3").
        workflows_dir: Directory containing the workflow YAML files.
        pattern: Filename pattern to match workflow files.
    """
    print(f"Listing files in {workflows_dir}:")
    try:
        files_in_dir = os.listdir(workflows_dir)
        for f in files_in_dir:
            print(f" - {f}")
    except FileNotFoundError:
        print(f"Directory {workflows_dir} not found!")
        return

    file_pattern = os.path.join(workflows_dir, pattern)
    print(f"Using glob pattern: {file_pattern}")

    files = glob.glob(file_pattern)

    if not files:
        print(f"No files found matching {file_pattern}")
        return

    # Match any amount of whitespace before key, support single or double quotes for value
    docker_image_pattern = re.compile(
        r'^(\s*DOCKER_IMAGE:\s*)(["\'])octivbooker:[^"\']*(["\'])',
        re.MULTILINE,
    )

    for filepath in files:
        print(f"\nUpdating file: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace the DOCKER_IMAGE value but keep original quoting style and spacing
        def replacer(match):
            prefix = match.group(1)
            quote_start = match.group(2)
            quote_end = match.group(3)
            return f"{prefix}{quote_start}octivbooker:v{version}{quote_end}"

        new_content, count = docker_image_pattern.subn(replacer, content)

        if count == 0:
            print(f"Warning: No DOCKER_IMAGE line found in {filepath}")
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated DOCKER_IMAGE to octivbooker:v{version} in {filepath}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <TAG_VERSION>")
        sys.exit(1)

    tag_version = sys.argv[1]
    update_docker_image_version(tag_version)
