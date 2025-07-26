"""
Local Constraint Manager
=========================
This module provides a local constraint manager for Maya tools.
Local constraints are the constraints used in the current scene, contrary to the referenced ones.

Normally, the local constraints belong to the animator. Therefore, this is a tool principally for animators. 
Sometimes it gets confusing to manage constraints, especially when there are many of them.
"""

import logging

__version__ = "1.0.0"
__author__ = "LFR"
__all__ = [
    # Modules
    "constraint_toolkit", 
    "constraint_toolkit_gui",
    # Main classes
    "ConstraintToolkitGUI",
    # Key functions
    "get_all_constraints",
    "get_constraint_connections"
]

logging.basicConfig(
    level=logging.NOTSET, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
