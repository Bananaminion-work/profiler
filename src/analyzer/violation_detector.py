from typing import Callable
from nicegui import ui
import pandas as pd
from pandas import DataFrame
from src.shared.violation import Violation


class ViolationDetector:
    
    _vvt : DataFrame
    _dfToAnalyze : DataFrame
    conditionHandlers: dict[str, Callable]
    
    def __init__(self, vvt: DataFrame):
        self._vvt = vvt
        
        #convert to floats in case it is a string
        columnsToConvert = ['threshold', 'param1', 'param2']
        for column in columnsToConvert:
            if column in self._vvt.columns:
                self._vvt[column] = pd.to_numeric(self._vvt[column], errors='coerce')
        
        self.conditionHandlers = {
            "max": self.handle_max,
            "min": self.handle_min,
            "duration_above_while_process": self.handle_min_duration_above,
            "min_duration_above": self.handle_min_duration_above,
            "max_duration_above": self.handle_max_duration_above,
            "min_duration_below": self.handle_min_duration_below,
            "max_duration_below": self.handle_max_duration_below,
            "rate_in_range": self.rate_in_range
        }
    
    def detect_violations(self, df: DataFrame, vvt:str):
        
        """Detects violations in the given DataFrame based on the rules defined in the VVT for the selected VVT name.
        
        returns a list of Violation objects representing the detected violations."""
        
        # create empty list to store violations
        foundViolations = []
        
        # filter for rules of the selected vvt
        rules = self._vvt[self._vvt['vvt_name'] == vvt]
        
        # iterate through rules and ignore index
        for _idx, rule in rules.iterrows():
            
            channel = rule['channel']
            condition = rule['condition']
            
            if channel not in df.columns:
                ui.notify(f"Channel with the name {channel} is not in the given Dataframe to analyze.")
                continue

            currentHandler = self.conditionHandlers.get(condition)
            
            if currentHandler:
                violations = currentHandler(df=df, **rule.to_dict())
                if violations:
                    foundViolations.extend(violations)
                    
        return foundViolations
    
    
        
    def handle_max(self,df: DataFrame, channel:str, threshold:float, **kwargs):
        # check for rows where channel value is above threshold and return these rows
        violatedRows = df[df[channel] > threshold]
        
        if isinstance(violatedRows, DataFrame):
        
            violations = self.create_violations_from_dataframe(
                violatedRows,
                vvt_name=kwargs['vvt_name'],
                rule_name=kwargs['rule_name'],
                channel=channel,
                threshold=threshold
                )
            
            return violations
        
    
    
    def handle_min(self,df: DataFrame, channel:str, threshold:float, **kwargs):
        # check for rows where channel value is below threshold and return these rows
        violatedRows = df[df[channel] < threshold]
        
        if isinstance(violatedRows, DataFrame):
        
            violations = self.create_violations_from_dataframe(
                violatedRows,
                vvt_name=kwargs['vvt_name'],
                rule_name=kwargs['rule_name'],
                channel=channel,
                threshold=threshold
                )
            
            return violations
    
    def handle_min_duration_above(self,df: DataFrame,vvt_name: str, rule_name:str, channel:str, threshold:float, param1:int, **kwargs):
        """checks if the channel is above the threshold for at least the duration in param1
        
        returns a violation object if rule is not met"""
        
        # get rows where channel is above threshold
        entrysAbove = df[df[channel] > threshold]

        duration = len(entrysAbove)
        
        # if duration is below minimum duration defined in param1
        if duration < param1:
            violation = Violation(
                        vvtName=vvt_name,
                        violatedRule=rule_name,
                        channel=channel,
                        actualValue=duration,
                        threshold=threshold,
                        time=None
                    )
            return [violation]
            
        else:
            return []
        
        
    def handle_max_duration_above(self,df: DataFrame,vvt_name: str, rule_name:str, channel:str, threshold:float, param1:int, **kwargs):
        """checks if the channel is above the threshold for max of the duration in param1
        
        returns a violation object if rule is not met"""
        
        # get rows where channel is above threshold
        entrysAbove = df[df[channel] > threshold]
        
        duration = len(entrysAbove)
        
        # if duration is above maximum duration defined in param1
        if duration > param1:
            violation = Violation(
                        vvtName=vvt_name,
                        violatedRule=rule_name,
                        channel=channel,
                        actualValue=duration,
                        threshold=threshold,
                        time=None
                    )
            return [violation]
            
        else:
            return []
        
        
    def handle_min_duration_below(self,df: DataFrame,vvt_name: str, rule_name:str, channel:str, threshold:float, param1:int, **kwargs):
        """checks if the channel is below the threshold for at least the duration in param1
        
        returns a violation object if rule is not met"""
        
        # get rows where channel is below threshold
        entrysBelow = df[df[channel] < threshold]
        
        duration = len(entrysBelow)
        
        # if duration is below minimum duration defined in param1
        if duration < param1:
            violation = Violation(
                        vvtName=vvt_name,
                        violatedRule=rule_name,
                        channel=channel,
                        actualValue=duration,
                        threshold=threshold,
                        time=None
                    )
            return [violation]
            
        else:
            return []
        
                
    def handle_max_duration_below(self,df: DataFrame,vvt_name: str, rule_name:str, channel:str, threshold:float, param1:int, **kwargs):
        """checks if the channel is below the threshold for max of the duration in param1
        
        returns a violation object if rule is not met"""
        
        # get rows where channel is below threshold
        entrysBelow = df[df[channel] < threshold]
        
        duration = len(entrysBelow)
        
        # if duration is above maximum duration defined in param1
        if duration > param1:
            violation =  Violation(
                        vvtName=vvt_name,
                        violatedRule=rule_name,
                        channel=channel,
                        actualValue=duration,
                        threshold=threshold,
                        time=None
                    )
            return [violation]
            
        else:
            return []
        
        
    
    def duration_above_while_process(self,df: DataFrame,vvt_name: str, rule_name:str, channel:str, threshold:float, param1:int, **kwargs):
        
        dfSelection = self.crop_dataframe_while_process(df)
        
        if isinstance(dfSelection, DataFrame) and not dfSelection.empty:
            return self.handle_min_duration_above(dfSelection,vvt_name, rule_name, channel, threshold, param1)
        else:
            return []
    
            
    
    def rate_in_range(self,df: DataFrame, channel:str, threshold:float, param1:float, param2:float, **kwargs):
        
        """checks if the channel (must be gradient) is above or below the threshold while the base channel is between certain values param1 and param2"""
        
        # find base of gradient
        baseChannel = channel.removesuffix('_gradient')
        if baseChannel not in df.columns:
            ui.notify(f"Base channel {baseChannel} not found in measurement data, cannot apply rate_in_range condition for channel {channel}.")
            return DataFrame()
        # select rows where base channel is between param1 and param2
        dfSelection = df[(df[baseChannel] <= param1) & (df[baseChannel] >= param2)]
        
        # check if rows were found
        if not dfSelection.empty:
            
            violatedRows = DataFrame()
            
            # negative threshold needs min-condition
            if threshold < 0:
                violatedRows = dfSelection[dfSelection[channel] < threshold]
            
            # positive threshold needs max-condition
            elif threshold >= 0:
                violatedRows = dfSelection[dfSelection[channel] > threshold]
                
            violations = self.create_violations_from_dataframe(
                violatedRows,
                vvt_name=kwargs['vvt_name'],
                rule_name=kwargs['rule_name'],
                channel=channel,
                threshold=threshold
                )
            
            return violations
                                                               
            
        else:
            return []
        
        
    def crop_dataframe_while_process(self,df: DataFrame):
        
        # get index where PrcChbInletBulkheadOpen changes from 1 to zero
        chamberCloseIdx = df.index[df['PrcChbInletBulkheadOpen'].diff() == -1]
        # get index where PrcChbOutletBulkheadOpen changes from 0 to 1
        chamberOpenIdx = df.index[df['PrcChbOutletBulkheadOpen'].diff() == 1]
        
        # check if more than one index was found and only choose one
        if len(chamberCloseIdx) > 0 and len(chamberOpenIdx) > 0:
            start = chamberCloseIdx[0]
            # first outlet opening AFTER the start
            after_start = chamberOpenIdx[chamberOpenIdx > start]
            end = after_start[0] if len(after_start) > 0 else df.index[-1]
            
            # create dataframe with rows between start and end index
            dfSelection = df.loc[start:end]
        
        else:
            dfSelection = DataFrame()
            
        return dfSelection
        
        
    def create_violations_from_dataframe(self, df: DataFrame,vvt_name:str, rule_name:str, channel:str, threshold:float):
        """creates violation objects from the given dataframe and returns a list of these violations"""
        
        violations = []
        
        if not df.empty:
              
            for index, row in df.iterrows():
                actualValue = row[channel]
                violation = Violation(
                    vvtName=vvt_name,
                    violatedRule=rule_name,
                    channel=channel,
                    actualValue=actualValue,
                    threshold=threshold,
                    time=int(str(index))
                )
                violations.append(violation)
        
                continue
        
        return violations