from enum import Enum

class OvenNumbers(str,Enum):
    
    RTP2_1  = "Rtp2 PM5 - 5418"
    RTP2_2  = "Rtp2 PM6 Oven 1 - 5937"
    RTP2_3  = "Rtp2 PM6 Oven 2 - 6156"
    
    MUB_1   = "MuB 5962"
    
    HTVP_1  = "HtvP L1 Oven 1 - 6150"
    HTVP_2  = "HtvP L1 Oven 2 - 6153"
    HTVP_3  = "HtvP L1 Oven 3 - 6151"
    HTVP_4  = "HtvP L1 Oven 4 - 6152"
    HTVP_5  = "HtvP L2 Oven 5 - 6154"
    HTVP_6  = "HtvP L2 Oven 6 - 6155"
    
    OTHER   = "Other"
    
    @classmethod
    def to_list(cls):
        return [oven.value for oven in cls]