from src.analyzer.zeropoint_calculator import ZeropointCalculator
from src.analyzer.violation_detector import ViolationDetector
from pandas import DataFrame

from src.shared.warning_collector import WarningCollector


class Analyzer:
    
    _zero : ZeropointCalculator
    _violation : ViolationDetector
    
    def __init__(self):
        self._warnings = WarningCollector()
        self._zero = ZeropointCalculator(self._warnings)
        self._violation = ViolationDetector(self._warnings)
    
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
    
    
    def flush_warnings(self):
        """flushes the warnings to the UI"""
        self._warnings.flush()