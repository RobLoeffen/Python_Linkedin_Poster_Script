import logging
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("linkedin_poster")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

# File logging
file_handler = logging.FileHandler(
    LOG_DIR / "linkedin.log",
    encoding="utf-8"
)
file_handler.setFormatter(formatter)

# Console logging (GitHub Actions)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)