from src.analyzer.zeropoint_calculator import ZeropointCalculator
from src.analyzer.violation_detector import ViolationDetector
from pandas import DataFrame


class Analyzer:
    
    _zero : ZeropointCalculator
    _violation : ViolationDetector
    
    def __init__(self):
        self._zero = ZeropointCalculator()
        self._violation = ViolationDetector()
    
    @property
    def vvt_set(self)->bool:
        return self._violation._vvt is not None and not self._violation._vvt.empty
    
    def set_vvt(self, vvt: DataFrame):
        self._violation.set_vvt(vvt)
    
    def analyze_zeropoints(self, gold: DataFrame):
        """analyzes the zeropoints of the given golddata
        
        returns results as ZeropointContainer"""
        
        zeropoints = self._zero.calculate_zeropoints(gold)
        return zeropoints
    
    def analyze_violations(self, gold: DataFrame, vvtName:str):
        """analyzes the violations of the given golddata against the specified vvt
        
        returns results as ViolationContainer"""
        
        violations = self._violation.detect_violations(gold, vvtName)
        return violations