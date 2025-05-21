"""
GUI components package.
"""

from .method_table import MethodTable
from .calltree_table import CallTreeTable
from .recent_dirs import RecentDirectories
from .consumption_graph import ConsumptionGraphDialog
from .calltree_details import CallTreeDetailsDialog

__all__ = [
    'MethodTable',
    'CallTreeTable',
    'RecentDirectories',
    'ConsumptionGraphDialog',
    'CallTreeDetailsDialog',
] 