from pandas import DataFrame
from src.shared.violation import Violation


class ViolationDetector:
    def __init__(self, vvt: dict[str, dict[str, str]]):
        self._vvt = vvt
    
    def detect_violations(self, df: DataFrame) -> dict[str, Violation]:
        
        
        
        return dict[str, Violation]()