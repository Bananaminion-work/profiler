from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class FilterComposition:
    """a class to represent the composition of filters for the measurement table"""
    
    ## MAKE SURE TO USE THE EXACT NAMES FROM METANAMES AS ATTRIBUTES TO AVOID TYPE ERRORS
    
    date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    oven_nr: int = 0
    product: str = ""
    oven_recipe: str = ""
    load_profile: str = ""
    comment: str = ""
    description: str = ""
    file_name: str = ""