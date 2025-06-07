from pathlib import Path
from datetime import datetime, timedelta

TEMPLATE_PATH = Path("./hooks/runner-template.yaml")
TIME_FOLDER = Path("src/slotbooker/data/")
WORKFLOW_DIR = Path(".github/workflows")


def parse_time_folder(name):
    try:
        return datetime.strptime(name, "%H%M")
    except ValueError:
        return None


def generate_cron(dt):
    adjusted = (dt - timedelta(minutes=5)).time()
    return f"{adjusted.minute} {adjusted.hour} * * *", adjusted.hour, adjusted.minute


def main():
    if not TEMPLATE_PATH.exists():
        print(f"Template file not found: {TEMPLATE_PATH}")
        return

    template = TEMPLATE_PATH.read_text()

    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)

    for entry in sorted(TIME_FOLDER.iterdir()):
        if entry.is_dir():
            dt = parse_time_folder(entry.name)
            if not dt:
                continue  # Skip invalid names

            time_str = dt.strftime("%H%M")
            cron, hour, minute = generate_cron(dt)

            yaml_content = template.format(
                time=time_str, cron=cron, cron_hour=hour, cron_minute=minute
            )

            output_file = WORKFLOW_DIR / f"runner-{time_str}.yaml"
            output_file.write_text(yaml_content)
            print(f"Generated {output_file}")


if __name__ == "__main__":
    main()
