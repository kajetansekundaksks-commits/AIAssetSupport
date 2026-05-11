import subprocess
import sys
from logger_config import setup_logger


logger = setup_logger("daily_pipeline")

scripts = [
    "framework/load_news.py",
    "framework/load_market_data.py",
    "framework/analyze_sentiment.py",
    "framework/generate_brief_v3.py",
    "framework/send_briefs_v3.py"
]

for script in scripts:
    logger.info(f"Running {script}...")

    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True
    )

    logger.info(result.stdout)

    if result.stderr:
        logger.error(result.stderr)

    if result.returncode != 0:
        logger.error(f"Pipeline stopped at {script}")
        sys.exit(result.returncode)

logger.info("Daily pipeline completed successfully.")