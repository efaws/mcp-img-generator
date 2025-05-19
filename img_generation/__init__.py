import platform
import subprocess
from .logger import logger
from .server import mcp
from .server import main

def img_generation():
    main()


__all__ = ["img_generation","server"]