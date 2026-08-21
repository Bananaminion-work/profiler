import pandas as pd
from pandas import DataFrame
from src.shared.channel_names import ChannelNames
from src.shared.data_models import Data, BronzeData,  SilverData
from src.shared.exceptions import WrongInputError
from typing import Tuple
from datetime import datetime


class SilverCreator():
    
    silverDataFrame: DataFrame
    
    def create_silver_object(self, bronze: Data, source: str)->Tuple[SilverData,datetime]:
        """creates SilverData object from a BronzeData object and processes it according to the source of measurement"""
        
        # raise error if no BronzeData is provided
        if not isinstance(bronze, BronzeData):
            raise WrongInputError("Expected BronzeData as input for bronze parameter")
        
        else:
            self.silverDataFrame = bronze.get_dataframe().copy()
            
            self.silverDataFrame.reset_index(inplace=True) # ensure ReadTime is a column for processing
                            
            if source == "Rehm-recorder":
                # resample and save first entry for datetime
                dateTime = self.resample_dataframe()
                
                #make sure to only have numbers
                for col in self.silverDataFrame.columns:
                    if col != 'ReadTime':
                        self.silverDataFrame[col] = pd.to_numeric(self.silverDataFrame[col], errors='coerce')
                
                # rename attributes for better legend display
                self.rename_attributes_for_legend()
            
            else:
                raise WrongInputError("Source not supported for SilverData creation")
            
            # set ReadTime as index
            self.silverDataFrame.set_index('ReadTime', inplace=True)
            
            return SilverData(self.silverDataFrame),dateTime
    
    def rename_attributes_for_legend(self):
        """method to rename the attributes of the silver dataframe for better legend display in plots"""
        
        
        renameColumns = {
            
            # STANDARD MAPPING FROM REHM-RECORDER
            'ReadTime'                                  : ChannelNames.READ_TIME,
            'TempMeasureCh1SS'                          : ChannelNames.CH1,
            'TempMeasureCh2SS'                          : ChannelNames.CH2,
            'TempMeasureCh3SS'                          : ChannelNames.CH3,
            'TempMeasureCh4SS'                          : ChannelNames.CH4,
            'TempMeasureCh5SS'                          : ChannelNames.CH5,
            'TempMeasureCh6SS'                          : ChannelNames.CH6,
            'St_MediumPump'                             : ChannelNames.MEDIUM_PUMP,
            'VacuumActualV'                             : ChannelNames.VACUUM,
            'O2Analyse2|Actual'                         : ChannelNames.O2,
            'Heater_Bottom1|Actual Value'               : ChannelNames.HEATER_BOTTOM1_ACTUAL,
            'Heater_Bottom2|Actual Value'               : ChannelNames.HEATER_BOTTOM2_ACTUAL,
            'Heater_Bottom3|Actual Value'               : ChannelNames.HEATER_BOTTOM3_ACTUAL,
            'Heater_Bottom4|Actual Value'               : ChannelNames.HEATER_BOTTOM4_ACTUAL,
            'Heater_SideBack|Actual Value'              : ChannelNames.HEATER_SIDEBACK_ACTUAL,
            'Heater_SideFront|Actual Value'             : ChannelNames.HEATER_SIDEFRONT_ACTUAL,
            'Heater_SideLeft|Actual Value'              : ChannelNames.HEATER_SIDELEFT_ACTUAL,
            'Heater_SideRight|Actual Value'             : ChannelNames.HEATER_SIDERIGHT_ACTUAL,
            'Heater_Bottom1|Y'                          : ChannelNames.HEATER_BOTTOM1_Y,
            'Heater_Bottom2|Y'                          : ChannelNames.HEATER_BOTTOM2_Y,
            'Heater_Bottom3|Y'                          : ChannelNames.HEATER_BOTTOM3_Y,
            'Heater_Bottom4|Y'                          : ChannelNames.HEATER_BOTTOM4_Y,
            'Heater_SideBack|Y'                         : ChannelNames.HEATER_SIDEBACK_Y,
            'Heater_SideFront|Y'                        : ChannelNames.HEATER_SIDEFRONT_Y,
            'Heater_SideLeft|Y'                         : ChannelNames.HEATER_SIDELEFT_Y,
            'Heater_SideRight|Y'                        : ChannelNames.HEATER_SIDERIGHT_Y,
            'StDi_PrcChbInletBulkheadOpen'              : ChannelNames.INLET_BULKHEAD_OPEN,
            'StDi_PrcChbOutletBulkheadOpen'             : ChannelNames.OUTLET_BULKHEAD_OPEN,
            'Cooling|FanSpeedActual'                    : ChannelNames.COOLING_FAN_SPEED,
            'Heater_ChamberTop|Actual Value'            : ChannelNames.HEATER_CHAMBER_TOP,
            'LoadUnitSensor2'                           : ChannelNames.LOAD_UNIT_SENSOR2,
            'O2Analyse1|Actual'                         : ChannelNames.O2_ANALYSE1,
            'St_PrcChbInletBulkheadBreak'               : ChannelNames.INLET_BULKHEAD_BREAK,
            'St_PrcChbOutletBulkheadBreak'              : ChannelNames.OUTLET_BULKHEAD_BREAK,
            'UnLoadUnitSensor2'                         : ChannelNames.UNLOAD_UNIT_SENSOR2,
            'InletChamberSensor2'                       : ChannelNames.INLET_CHAMBER_SENSOR2,
            'InletChamberSensor1'                       : ChannelNames.INLET_CHAMBER_SENSOR1,
            
            # MAPPING FOR MOCK DATA GENERATION
            'InletBulkhead'                             : ChannelNames.INLET_BULKHEAD_OPEN,
            'OutletBulkhead'                            : ChannelNames.OUTLET_BULKHEAD_OPEN,
            'Vacuum'                                    : ChannelNames.VACUUM,
            'Oxygen'                                    : ChannelNames.O2,
        }
        
        self.silverDataFrame.rename(columns=renameColumns, inplace=True)
    
    def resample_dataframe(self):
        """Resample the DataFrame to have one entry per second."""
        
        # convert ReadTime to datetime (use the specified format) and set as index
        self.silverDataFrame['ReadTime'] = pd.to_datetime(
            self.silverDataFrame['ReadTime'],
            format='%d/%m/%y %H:%M:%S:%f'
        )
        
        # save the datetime of the first entry
        firstEntry = self.silverDataFrame['ReadTime'].iloc[0]
        #convert first entry to datetime object if it is not already
        if not isinstance(firstEntry, datetime):
            firstEntry = pd.to_datetime(firstEntry)
        
        # set the index to ReadTime for resampling
        self.silverDataFrame.set_index('ReadTime', inplace=True)
        
        # resample to 1 second intervals
        self.silverDataFrame = self.silverDataFrame.resample('1s').mean()
        
        # use fill method to fill missing values with last known value
        self.silverDataFrame = self.silverDataFrame.ffill()
        
        # reset index to ensure it is a column again
        self.silverDataFrame.reset_index(inplace=True)
        
        # replace ReadTime with a range of inkrementing integers
        self.silverDataFrame['ReadTime'] = range(len(self.silverDataFrame))
        
        return firstEntry
        