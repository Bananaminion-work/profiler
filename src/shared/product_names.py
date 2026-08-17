from enum import Enum

class ProductNames(str,Enum):
    
    VOLVO_ERAD =        "Volvo ERAD"
    VW_ECO_PMOC =       "VW Pmoc Eco"
    VOLVO_EFAD =        "Volvo EFAD"
    VW_BASE =           "VW MEB Base+"
    DAI_V2 =            "DAI V2"
    DAI_V4 =            "DAI V4"
    OTHER  =            "Other"
    
    
    @classmethod
    def to_list(cls):
        return [oven.value for oven in cls]