import json 

import logging
import uuid


def get_logger():
    logger = logging.getlogger()
    logger.setLevel(logging.INFO)
    def log(level ,payload):
        payload["correlation_id"] = str(uuid.uuid4())
        logger.log(level,json.dumps(payload))
    return log
