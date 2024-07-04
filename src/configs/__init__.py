import logging
from typing import Any, Dict, Text


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

DEFAULT_LOGGING_CONFIG: Dict[Text, Any] = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "filename": "logs/api.log",
}
