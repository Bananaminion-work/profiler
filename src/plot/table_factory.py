from nicegui import ui

from src.shared.violation import Violation
import pandas as pd
from pandas import DataFrame


class TableFactory:
        
    def update_violation_table(self, violations: list[Violation], offset: int):
        """draws a table with a given list of violation-objects and applys the given offset to the 'Time of Occurance' column of the table"""
        
        
        # check if content is not empty and create df out of the violation-objects
        if violations is not None and len(violations) > 0:
            tableContent = DataFrame([violation.to_dict() for violation in violations])
            
            # apply the offset to the time column of the tableContent df
            tableContent = self.apply_offset(tableContent, offset)
        
        else:
            tableContent = DataFrame()
            
        # draw the table with nicegui
        ui.table.from_pandas(tableContent).classes("w-full h-full")
    
    
    
    def apply_offset(self, df: DataFrame, offset: int) -> DataFrame:
        """applies the given offset to the 'Time of Occurance' column of the given DataFrame and returns the updated DataFrame"""
        
        if "Time of Occurance" in df.columns:
            
            # makes ints out of the strings, if there is an error it converts to NaN
            numericTimeDf = pd.to_numeric(df['Time of Occurance'], errors='coerce')
            
            df['Time of Occurance'] = numericTimeDf + offset
        
        return df