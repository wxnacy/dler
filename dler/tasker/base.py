import os

from dler.constants import DOWNLOAD_DIR

class BaseConfig:
    task_type: str
    download_dir: str = os.getenv("DLER_DOWNLOAD_DIR") or DOWNLOAD_DIR

