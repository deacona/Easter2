from loguru import logger
import sys
import os

os.chdir("src")

logger.remove()
logger.add("../logs/run_evaluation.log", rotation="1 day", level="DEBUG")
sys.stdout.write = logger.warning
sys.stderr.write = logger.warning

logger.info("EVALUATION STARTED")

from predict import test_on_iam
checkpoint_path = "Empty"

test_on_iam(show=False, partition="validation", checkpoint=checkpoint_path, uncased=True)

test_on_iam(show=False, partition="test", checkpoint=checkpoint_path, uncased=True)

logger.success("EVALUATION COMPLETED")