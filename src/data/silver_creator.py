import pandas as pd
from pandas import DataFrame
from src.shared.data_models import Data, BronzeData,  SilverData
from src.shared.exceptions import WrongInputError


class SilverCreator():
    
    silverDataFrame: DataFrame
    
    def create_silver_object(self, bronze: Data, source: str)->SilverData:
        """creates SilverData object from a BronzeData object and processes it according to the source of measurement"""
        
        # raise error if no BronzeData is provided
        if not isinstance(bronze, BronzeData):
            raise WrongInputError("Expected BronzeData as input for bronze parameter")
        
        else:
            self.silverDataFrame = bronze.get_dataframe().copy()
                            
            if source == "Rehm-recorder":
                self.resample_dataframe()
                self.rename_attributes_for_legend()
            
            else:
                raise WrongInputError("Source not supported for SilverData creation")
            
            return SilverData(self.silverDataFrame)
    
    def rename_attributes_for_legend(self):
        
        renameColumns = {
            'TempMeasureCh1SS'                          : 'CH1',
            'TempMeasureCh2SS'                          : 'CH2',
            'TempMeasureCh3SS'                          : 'CH3',
            'TempMeasureCh4SS'                          : 'CH4',
            'TempMeasureCh5SS'                          : 'CH5',
            'TempMeasureCh6SS'                          : 'CH6',
            'St_MediumPump'                             : 'St_MediumPump',
            'VacuumActualV'                             : 'VacuumActualV in mBar',
            'O2Analyse2|Actual'                         : 'O2Analyse2|Actual',
            'Heater_Bottom1|Actual Value'               : 'Heater_Bottom1|Actual Value',
            'Heater_Bottom2|Actual Value'               : 'Heater_Bottom2|Actual Value',
            'Heater_Bottom3|Actual Value'               : 'Heater_Bottom3|Actual Value',
            'Heater_Bottom4|Actual Value'               : 'Heater_Bottom4|Actual Value',
            'Heater_SideBack|Actual Value'              : 'Heater_SideBack|Actual Value',
            'Heater_SideFront|Actual Value'             : 'Heater_SideFront|Actual Value',
            'Heater_SideLeft|Actual Value'              : 'Heater_SideLeft|Actual Value',
            'Heater_SideRight|Actual Value'             : 'Heater_SideRight|Actual Value',
            'Heater_Bottom1|Y'                          : 'Heater_Bottom1|Y',
            'Heater_Bottom2|Y'                          : 'Heater_Bottom2|Y',
            'Heater_Bottom3|Y'                          : 'Heater_Bottom3|Y',
            'Heater_Bottom4|Y'                          : 'Heater_Bottom4|Y',
            'Heater_SideBack|Y'                         : 'Heater_SideBack|Y',
            'Heater_SideFront|Y'                        : 'Heater_SideFront|Y',
            'Heater_SideLeft|Y'                         : 'Heater_SideLeft|Y',
            'Heater_SideRight|Y'                        : 'Heater_SideRight|Y',
            'StDi_PrcChbInletBulkheadOpen'              : 'PrcChbInletBulkheadOpen',
            'StDi_PrcChbOutletBulkheadOpen'             : 'PrcChbOutletBulkheadOpen',
            'Cooling|FanSpeedActual'                    : 'Cooling_FanSpeedActual',
            'Heater_ChamberTop|Actual Value'            : 'Heater_ChamberTop|Actual Value',
            'LoadUnitSensor2'                           : 'LoadUnitSensor2',
            'O2Analyse1|Actual'                         : 'O2Analyse1|Actual',
            'St_PrcChbInletBulkheadBreak'               : 'PrcChbInletBulkheadBreak',
            'St_PrcChbOutletBulkheadBreak'              : 'PrcChbOutletBulkheadBreak',
            'UnLoadUnitSensor2'                         : 'UnLoadUnitSensor2',
            'InletChamberSensor2'                       : 'InletChamberSensor2',
            'InletChamberSensor1'                       : 'InletChamberSensor1'
        }
        
        self.silverDataFrame.rename(columns=renameColumns, inplace=True)
    
    def resample_dataframe(self):
        """Resample the DataFrame to have one entry per second."""
        
        # convert ReadTime to datetime (use the specified format) and set as index
        self.silverDataFrame['ReadTime'] = pd.to_datetime(
            self.silverDataFrame['ReadTime'],
            format='%d/%m/%y %H:%M:%S:%f'
        )
        self.silverDataFrame.set_index('ReadTime', inplace=True)
        
        # resample to 1 second intervals
        self.silverDataFrame = self.silverDataFrame.resample('1s').mean()
        
        #optional: use fill method to fill missing values with last known value
        self.silverDataFrame = self.silverDataFrame.ffill()
        
        #reset index to ensure it as a column again
        #self.silverDataFrame.reset_index(inplace=True)