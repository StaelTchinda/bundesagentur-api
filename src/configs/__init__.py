import logging
from typing import Any, Dict, Text


DEFAULT_LOGGING_CONFIG: Dict[Text, Any] = {
    "level": logging.DEBUG,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "filemode": "a",
    "filename": "logs/api.log",
}

