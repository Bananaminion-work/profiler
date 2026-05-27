from dataclasses import asdict, dataclass


# class for violation entrys
# dataclass decorator allows easy conversion to dictionary
@dataclass
class Violation:
    
    vvtName : str
    violatedRule : str
    actualValue : str
    threshold : str
    channel : str
    time : str
    
    def __init__(self, vvtName: str, violatedRule: str, channel:str, actualValue: str, threshold: str, time:str):
        self.vvtName = vvtName
        self.violatedRule = violatedRule
        self.channel = channel
        self.actualValue = actualValue
        self.threshold = threshold
        self.time = time
    
    def to_dict(self) -> dict:
        """returns a dictionary representation of the Violation object, useful for creating DataFrames"""
        
        # create mapping for column names
        keyMapping = {
            "vvtName": "VVT Name",
            "violatedRule": "Violated Rule",
            "channel": "Channel",
            "actualValue": "Actual Value",
            "threshold": "Threshold",
            "time": "Time of Occurance"
        }
        
        # std dict
        violationDict = asdict(self)
        
        # create empty dict
        returnDict ={}
        
        # map keys to new column names
        for key, value in violationDict.items():
            if key in keyMapping:
                returnDict[keyMapping[key]] = value
            else:
                returnDict[key] = value
        
        # return final dict
        return returnDict