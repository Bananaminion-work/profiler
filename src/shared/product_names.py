from enum import Enum

class ProductNames(str,Enum):
    
    PM5_ECO     = "PM5: VW-ECO"
    PM6_ERAD    = "PM6: VOLVO-ERAD"
    PM6_BASE    = "PM6: BASE"
    
    
    @classmethod
    def to_list(cls):
        return [oven.value for oven in cls]