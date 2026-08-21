from typing import Callable
from nicegui import ui
import pandas as pd
from pandas import DataFrame
from src.shared.channel_names import ChannelNames
from src.shared.violation import Violation
from src.shared.vvt_names import VvtNames


class ViolationDetector:
    
    _vvt : DataFrame
    conditionHandlers: dict[str, Callable]
    
    def __init__(self):
        self._vvt = pd.DataFrame()
        self.conditionHandlers = {
            "max": self.handle_max,
            "min": self.handle_min,
            "min_duration_above": self.handle_duration,
            "max_duration_above": self.handle_duration,
            "min_duration_below": self.handle_duration,
            "max_duration_below": self.handle_duration,
            "rate_in_range": self.rate_in_range,
            "main_vacuum_minimum": self.handle_main_vacuum_minimum
        }

    def set_vvt(self, vvt: DataFrame):
        """sets the vvt to be used for violation detection
        
        converst from string to float"""
        
        #set vvts in attribute
        self._vvt = vvt
        
        #convert to floats in case it is a string
        columnsToConvert = ['threshold', 'param1', 'param2', 'param3', 'param4']
        for column in columnsToConvert:
            if column in self._vvt.columns:
                self._vvt[column] = pd.to_numeric(self._vvt[column], errors='coerce')
    
    
    
    def detect_violations(self, df: DataFrame, vvt:str):
        """Detects violations in the given DataFrame based on the rules defined in the VVT for the selected VVT name.
        
        returns a list of Violation objects representing the detected violations."""
        
        # create empty list to store violations
        foundViolations = []
        
        # create base rules
        baseRules = self._vvt[self._vvt['vvt_name'] == VvtNames.VPS_MAIN]
        
        # if only baserules are selected, only load them
        if vvt == VvtNames.VPS_MAIN:
            rules = baseRules 
        
        # if any other vvt is selected, load these as well
        else:
            specificRules = self._vvt[self._vvt['vvt_name'] == vvt]
            
            # and merge them with base
            combined_rules = pd.concat([specificRules, baseRules])
            
            # drops dublicates, only uses the first so specific overrides base rules
            rules = combined_rules.drop_duplicates(subset=['rule_id'], keep ='first').copy() #type:ignore
            
            # change position for better ux
            rules['is_base'] = rules['vvt_name'] == VvtNames.VPS_MAIN
            rules = rules.sort_values(by='is_base', ascending=False).drop(columns='is_base')
        
        # iterate through rules and ignore index
        for _idx, rule in rules.iterrows():
            
            channel = rule['channel']
            condition = rule['condition']
            
            # save scope if set, otherwise default to 'all'
            scope = rule.get('scope', 'all')
            
            if channel not in df.columns:
                ui.notify(f"Channel with the name {channel} is not in the given Dataframe to analyze.")
                continue
            
            # get handler according to the condition to check
            currentHandler = self.conditionHandlers.get(condition)
            
            if currentHandler:
                
                df_to_check = df
                
                if scope == 'process':
                    df_to_check = self.crop_dataframe_while_process(df)
                    
                    if df_to_check.empty:
                        ui.notify(f"No process phases found in the measurement data, cannot apply rules with process scope for channel {channel}.")
                        continue
                    
                elif scope == 'outlet_bulkhead_open':
                    df_to_check = self.crop_dataframe_bulkhead_open(df)
                    
                    if df_to_check.empty:
                        ui.notify(f"No outlet_bulkhead_open phases found in the measurement data, cannot apply rules with outlet_bulkhead_open scope for channel {channel}.")
                        continue
                
                # analyze violations
                violations = currentHandler(df=df_to_check, **rule.to_dict())
                
                # append violations if any were found
                if violations:
                    foundViolations.extend(violations)
                    
        return foundViolations
    
    
        
    def handle_max(self,df: DataFrame, channel:str, threshold:float, **kwargs):
        """checks if given channel in given DataFrame is above given threshold
        
        returns Violation objects if any were found"""
        
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
        """checks if given channel in given DataFrame is below given threshold
        
        returns Violation objects if any were found"""
        
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
        """crops the given DataFrame between inlet-bulkhead open and outlet-bulkhead open
        
        scopes relatively on the main process"""
        
        #check if the channels are present in the dataframe
        if ChannelNames.INLET_BULKHEAD_OPEN not in df.columns or ChannelNames.OUTLET_BULKHEAD_OPEN not in df.columns:
            ui.notify(f"Columns of Bulheads not found in measurement data, cannot apply rules with process scope.")
            return DataFrame()
        
        # get index where PrcChbInletBulkheadOpen changes from 1 to zero
        chamberCloseIdx = df.index[df[ChannelNames.INLET_BULKHEAD_OPEN].diff() == -1]
        # get index where PrcChbOutletBulkheadOpen changes from 0 to 1
        chamberOpenIdx = df.index[df[ChannelNames.OUTLET_BULKHEAD_OPEN].diff() == 1]
        
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
    
    
    
    def crop_dataframe_bulkhead_open(self,df: DataFrame):
        """crops the given DataFrame to the data after outlet-bulkhead open to the end of the DataFrame"""
        
        # check if column exists
        if ChannelNames.OUTLET_BULKHEAD_OPEN not  in df.columns:
            ui.notify(f"Column '{ChannelNames.OUTLET_BULKHEAD_OPEN}' not found in measurement data, cannot apply rules with outlet_bulkhead_open scope.")
            return DataFrame()
        
        # find index where bulhead changes from 0 to 1
        bulkheadOpenIdx = df.index[df[ChannelNames.OUTLET_BULKHEAD_OPEN].diff() == 1]
        
        if len(bulkheadOpenIdx) > 0:
            
            first = bulkheadOpenIdx[0]
            return df.loc[[first]]
        
        else:
            return DataFrame()
        
        
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
    
    
    
    
    def handle_duration(self, df: DataFrame, vvt_name: str, rule_name:str, channel:str, threshold:float, param1:int, condition:str, **kwargs):
        """handles all duration conditions by checking the condition and calling the corresponding handler"""
        
        # create empty df
        relevantRows = DataFrame()
        
        # create boolean if violation occured
        violated = False
        
        # check if condition is above or below and filter df accordingly
        if "above" in condition:
            relevantRows = df[df[channel] > threshold]
        elif "below" in condition:
            relevantRows = df[df[channel] < threshold]
        
        # get duration of relevant rows
        duration = len(relevantRows)
        
        # check if condition is min or max and compare duration to param1
        if "min" in condition and duration < param1:
            violated = True
        elif "max" in condition and duration > param1:
            violated = True
            
        # create violation object if violated
        if violated:
            violation = Violation(
                        vvtName=vvt_name,
                        violatedRule=rule_name,
                        channel=channel,
                        actualValue=duration,
                        threshold=param1,
                        time=None
                    )
            return [violation]
            
        else:
            return []
        
        
    
    def handle_main_vacuum_minimum(self, df: DataFrame, vvt_name:str, rule_name:str, channel:str, threshold:float, **kwargs):
        """checks vacuum before outlet-bulkhead is opened
        
        checks if vacuum is below given threshold"""
        
        # check if positioning channel is in dataframe
        if ChannelNames.OUTLET_BULKHEAD_OPEN not in df.columns:
            ui.notify(f"Column '{ChannelNames.OUTLET_BULKHEAD_OPEN}' not found in measurement data, cannot apply main_vacuum_minimum condition.")
            return []
        
        # find index where bulkhead is 1 for the first time
        bulheadRows = df[df[ChannelNames.OUTLET_BULKHEAD_OPEN].diff() == 1]
        if bulheadRows.empty:
            ui.notify(f"No rows with '{ChannelNames.OUTLET_BULKHEAD_OPEN}' equal to 1 found in measurement data, cannot apply main_vacuum_minimum condition.")
            return []
        
        # get first index where bulkhead is open
        bulkheadIdx = bulheadRows.index[0]
        
        # only use data from 0 to index where bulkhead is first time 1
        dfSelection = df.loc[:bulkheadIdx].copy()
        
        # create gradient of vacuum channel
        dfSelection['gradient'] = dfSelection[channel].diff()
        
        # find index where gradient of vacuum is -20 or less
        gradientIdx = dfSelection.index[dfSelection['gradient'] <= -20]
        
        if gradientIdx.empty:
            ui.notify(f"No significant decrease in vacuum channel {channel} found before bulkhead opening, cannot apply main_vacuum_minimum condition.")
            return []
        
        # start from the last index to walk backwards
        startIdx = gradientIdx[-1]
        
        # check value of vacuum from above index on to be minimum the threshold
        dfSelection = dfSelection.loc[:startIdx]
        minVacuumMet = dfSelection[channel].min() <= threshold
        
        # create one violation object if there is no value <= threshold
        if not minVacuumMet:
            violation = Violation(
                        vvtName=vvt_name,
                        violatedRule=rule_name,
                        channel=channel,
                        actualValue=dfSelection[channel].min(),
                        threshold=threshold,
                        time=None
                    )
            return [violation]
        
        else:
            return []