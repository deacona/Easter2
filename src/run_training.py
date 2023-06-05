from loguru import logger
import sys
import os

os.chdir("src")

logger.remove()
logger.add("../logs/run_training.log", rotation="1 day", level="DEBUG")
sys.stdout.write = logger.warning
sys.stderr.write = logger.warning

logger.info("TRAINING STARTED")

from easter_model import train

train()

logger.success("TRAINING COMPLETED")