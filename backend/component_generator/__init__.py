"""
Component Generator Module for Jinie Backend.
Generates reusable UI components (e.g. React Native components) from layout structures.
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from generator import ComponentGenerator

__all__ = [
    "ComponentGenerator",
]
