from enum import Enum

class VvtScopes(str, Enum):
    
    PROCESS = "process"
    BULKHEAD_OPEN = "outlet_bulkhead_open"
    
    @classmethod
    def get_options(cls):
        """Return a list of available preset names"""
        return list(cls)