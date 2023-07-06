from contextlib import contextmanager


@contextmanager
def override_log_level(logger, level):
    """Temporarily override the log level of a logger."""
    old_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)
