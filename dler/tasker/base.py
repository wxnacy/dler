import os

from dler.constants import DOWNLOAD_DIR, ENV_DOWNLOAD_DIR

class BaseConfig:
    task_type: str
    download_dir: str = ENV_DOWNLOAD_DIR or DOWNLOAD_DIR
