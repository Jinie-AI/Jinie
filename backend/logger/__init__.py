"""
backend/srs/logger/__init__.py

Public interface for the logger/ package. Lets other modules do:

    from logger import Logger

instead of reaching into logger.logger directly.
"""

from logger.logger import Logger

__all__ = ["Logger"]