
from utils.logging_config import configure_logging
configure_logging()

import logging
logger = logging.getLogger(__name__)

from ui.main_window import run_app

if __name__ == "__main__":
    logger.info("Starting Image Upscale App")
    run_app()
