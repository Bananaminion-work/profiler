from nicegui import ui
from pandas import DataFrame
from src.shared.violation import Violation


class ViolationDetector:
    
    _vvt : DataFrame
    
    def __init__(self, vvt: DataFrame):
        self._vvt = vvt
    
    def detect_violations(self, df: DataFrame, vvt:str):
        
        """Detects violations in the given DataFrame based on the rules defined in the VVT for the selected VVT name.
        
        returns a list of Violation objects representing the detected violations."""
        
        # create empty list to store violations
        foundViolations = []
        
        # filter for rules of the selected vvt
        rulesOfSelectedVvt = self._vvt[self._vvt['vvt_name'] == vvt]
        
        
        for index, rule in rulesOfSelectedVvt.iterrows():
            name = rule['rule_name']
            channel = rule['channel']
            condition = rule['condition']
            threshold = rule['threshold']
            param1 = rule['param1']
            param2 = rule['param2']
            
            # check if channel exists in the measurement data
            if channel not in df.columns:
                ui.notify(f"Channel {channel} not found in measurement data, skipping rule {name}.")
                continue

            violatedRows = DataFrame()
            
            # check conditions
            if condition == "max":
                violatedRows = df[df[channel] > threshold]
                
            elif condition == "min":
                violatedRows = df[df[channel] < threshold]
                
            elif condition == "duration_above_while_process":
                # select rows after PrcChbInletBulkheadOpen changes from 1 to zero
                chamberCloseIdx = df.index[df['PrcChbInletBulkheadOpen'].diff() == -1]
                # delet rows after PrcChbOutletBulkheadOpen changes from 0 to 1
                chamberOpenIdx = df.index[df['PrcChbOutletBulkheadOpen'].diff() == 1]
                
                # check if more than one index was found and only choose one
                if len(chamberCloseIdx) > 0 and len(chamberOpenIdx) > 0:
                    start = chamberCloseIdx[0]
                    # Erstes Outlet-Öffnen NACH dem Start
                    after_start = chamberOpenIdx[chamberOpenIdx > start]
                    end = after_start[0] if len(after_start) > 0 else df.index[-1]
                    dfSelection = df.loc[start:end]
                
                else:
                    dfSelection = DataFrame()
                    
                if not dfSelection.empty:
                    
                    entrysAboveThreshold = len(dfSelection[dfSelection[channel] > threshold])

                    if entrysAboveThreshold < param1:
                        violation = Violation(
                            vvtName=vvt,
                            violatedRule=name,
                            channel=channel,
                            actualValue=entrysAboveThreshold,
                            threshold=param1,
                            time=None
                        )
                        foundViolations.append(violation)
                
            elif condition == "min_duration_above":
                entrysAboveParam1 = df[df[channel] > threshold]
                
                duration = len(entrysAboveParam1)
                
                if duration > param1:
                    violation = Violation(
                        vvtName=vvt,
                        violatedRule=name,
                        channel=channel,
                        actualValue=duration,
                        threshold=param1,
                        time=None
                    )
                    foundViolations.append(violation)
                    
                continue
            
            elif condition == "min_duration_below":
                entrysBelowParam1 = df[df[channel] < threshold]
                
                duration = len(entrysBelowParam1)
                
                if duration < param1:
                    violation = Violation(
                        vvtName=vvt,
                        violatedRule=name,
                        channel=channel,
                        actualValue=duration,
                        threshold=param1,
                        time=None
                    )
                    foundViolations.append(violation)
                    
                continue
            
                
            elif condition == "rate_in_range":
                
                # find base of gradient
                baseChannel = channel.removesuffix('_gradient')
                # select rows where base channel is between param1 and param2
                dfSelection = df[(df[baseChannel] <= param1) & (df[baseChannel] >= param2)]
                
                # check if rows were found
                if not dfSelection.empty:
                    
                    # negative threshold needs min-condition
                    if threshold < 0:
                        violatedRows = dfSelection[dfSelection[channel] < threshold]
                    
                    # positive threshold needs max-condition
                    elif threshold >= 0:
                        violatedRows = dfSelection[dfSelection[channel] > threshold]
                        
            # create new violation object for each violated row
            if not violatedRows.empty:
                
                for index, row in violatedRows.iterrows():
                    actualValue = row[channel]
                    violation = Violation(
                        vvtName=vvt,
                        violatedRule=name,
                        channel=channel,
                        actualValue=actualValue,
                        threshold=threshold,
                        time=int(str(index))
                    )
                    foundViolations.append(violation)
        
        # return the list of violation-objects          
        return foundViolations
        
        