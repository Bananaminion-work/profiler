class Violation:
    
    _vvtName : str
    _violatedRule : str
    _actualValue : str
    _threshold : str
    
    def __init__(self, vvtName: str, violatedRule: str, actualValue: str, threshold: str):
        self._vvtName = vvtName
        self._violatedRule = violatedRule
        self._actualValue = actualValue
        self._threshold = threshold
    
    def get_vvt_name(self) -> str:
        return self._vvtName
    
    def get_violated_rule(self) -> str:
        return self._violatedRule
    
    def get_actual_value(self) -> str:
        return self._actualValue
    
    def get_threshold(self) -> str:
        return self._threshold