from enum import Enum


class ConditionNames(str,Enum):
    """names of the conditions that can be used to check data"""
    
    MAX = "max"
    MIN = "min"
    MAX_DURATION_ABOVE = "max_duration_above"
    MIN_DURATION_ABOVE = "min_duration_above"
    RATE_IN_RANGE = "rate_in_range"
    MAIN_VACUUM_MINIMUM = "main_vacuum_minimum"
    
    @classmethod
    def get_options(cls):
        """Return a list of available preset names"""
        return list(cls)
