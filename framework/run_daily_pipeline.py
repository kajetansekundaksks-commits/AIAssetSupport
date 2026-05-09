import subprocess
import sys

scripts = [
    "framework/load_news.py",
    "framework/analyze_sentiment.py",
    "framework/generate_brief_v3.py",
    "framework/send_briefs_v3.py"
]

for script in scripts:
    print(f"Running {script}...")

    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print(f"Pipeline stopped at {script}")
        sys.exit(result.returncode)

print("Daily pipeline completed successfully.")