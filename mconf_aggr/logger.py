import json
import os
import sys

from loguru import logger


def sink_serializer(message):
    record = message.record
    simplified = {
        "datetime": str(record["time"]),
        "level": record["level"].name,
        "name": record["name"],
        "thread": record["thread"].id,
        "line": record["line"],
        "message": record["message"],
    }
    serialized = json.dumps(simplified)
    print(serialized, file=sys.stderr)


def get_logger():
    LOG_LEVEL = str(os.environ.get("LOGURU_LOG_LEVEL"))
    LOG_SINK = os.environ.get("LOGURU_LOG_SINK")

    if LOG_SINK == "sys.stderr":
        SINK = sys.stderr
    elif LOG_SINK == "sink_serializer":
        SINK = sink_serializer
    else:
        logger.error("Failed to get SINK variable")

    logger.remove()

    logger.add(
        sink=SINK,
        level=LOG_LEVEL,
        format=(
            "<g>{time:YYYY-MM-DD HH:mm:ss.SSS ZZZ}</g> | <lvl>{level}</lvl> |"
            + " <b>{name}</b>:{line}:<c>[{thread}]</c> | {message}"
        ),
        colorize=True,
    )

    return logger
