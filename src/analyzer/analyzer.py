from src.analyzer.zeropoint_calculator import ZeropointCalculator
from src.analyzer.violation_detecter import ViolationDetector
from pandas import DataFrame


class Analyzer:
    
    _zero : ZeropointCalculator
    _violation : ViolationDetector
    
    def __init__(self, vvt: dict[str, dict[str, str]]):
        self._zero = ZeropointCalculator()
        self._violation = ViolationDetector(vvt)
        
    def analyze_measurement(self,df: DataFrame):
        zeropoints = self._zero.calculate_zeropoints(df)
        violations = self._violation.detect_violations(df)
        return zeropoints, violations