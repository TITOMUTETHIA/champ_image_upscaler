import logging

def configure_logging(level=logging.INFO):
    fmt = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(handler)
