from nicegui import ui

from src.shared.violation import Violation
from src.shared.filter_composition import FilterComposition
from src.shared.meta_names import MetaNames
import pandas as pd
from pandas import DataFrame
from typing import cast



class TableFactory:
        
    def update_violation_table(self, violations: list[Violation], offset: int):
        """draws a table with a given list of violation-objects and applys the given offset to the 'Time of Occurance' column of the table"""
        
        
        # check if content is not empty and create df out of the violation-objects
        if violations is not None and len(violations) > 0:
            tableContent = DataFrame([violation.to_dict() for violation in violations])
            
            # round the numbers to be displayed
            tableContent[Violation.ACTUAL_VALUE] = tableContent[Violation.ACTUAL_VALUE].round(2)
            
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
    
    
    
    def update_measurement_table(self, content:DataFrame, filter: FilterComposition,selected_ids: set, set_selected_ids_callback):
        """creates a table with the content to display the saved measurements"""
        
        # filter the content before table is created
        filteredDf = self.apply_filter(content,filter, selected_ids)
        
        filteredDf = filteredDf.fillna("")
        
        # create a dict for each column and make it sortable
        columns = [
            {
                'name': col,
                'label': col.replace('_',' ').title(),
                'field': col,
                'sortable': True,
                'align': 'left'
            }
            for col in filteredDf.columns
            # dont show the measurement_id column in the table
            if col != "measurement_id"
        ]
        
        # create rows
        rows = filteredDf.to_dict(orient='records')
        
        # create table 
        table = ui.table(
            columns=columns,
            rows=rows,
            selection = 'multiple',
            row_key = MetaNames.MEASUREMENT_ID
            ).classes("w-full h-full")
        
        # set checkboxes if id is selected
        if selected_ids:
            table.selected = [
                row for row in rows
                if row[MetaNames.MEASUREMENT_ID] in selected_ids
            ]
            
        def handle_click():
            # get the ids from the selected rows
            current_ids = {row[MetaNames.MEASUREMENT_ID] for row in table.selected}
            # use callback method from controller to update the selected ids
            set_selected_ids_callback(current_ids)
            
        table.on('selection', handle_click)
        
        
        
    def apply_filter(self, content: DataFrame, filter: FilterComposition, selected_ids: set) -> DataFrame:
        """applys filters with the given values of the FilterComposition-object to the given Dataframe
        
        returns the filtered DataFrame"""
        
        # return the df if filter is empty
        if content.empty:
            return content
            
        # create mask without filtering
        mask = pd.Series(True, index=content.index)

        # filter df for each attribute
        
        # ovennr
        filter_oven_nr = getattr(filter, MetaNames.OVEN_NR, 0) 
        if filter_oven_nr > 0:
            
            mask &= (content[MetaNames.OVEN_NR] == filter_oven_nr)

        # product
        filter_product = getattr(filter, MetaNames.PRODUCT, "")
        if filter_product:
            mask &= content[MetaNames.PRODUCT].astype(str).str.contains(filter_product, case=False, na=False)

        # recipe
        filter_recipe = getattr(filter, MetaNames.OVEN_RECIPE, "")
        if filter_recipe:
            mask &= content[MetaNames.OVEN_RECIPE].astype(str).str.contains(filter_recipe, case=False, na=False)
        
        # load profile
        filter_profile = getattr(filter, MetaNames.LOAD_PROFILE, "")
        if filter_profile:
            mask &= content[MetaNames.LOAD_PROFILE].astype(str).str.contains(filter_profile, case=False, na=False)

        # comment
        filter_comment = getattr(filter, MetaNames.COMMENT, "")
        if filter_comment:
            mask &= content[MetaNames.COMMENT].astype(str).str.contains(filter_comment, case=False, na=False)
            
        # date
        filter_date = getattr(filter, MetaNames.DATE, None)
        if filter_date:
            # convert string to datetime
            targetDate = pd.to_datetime(filter_date, format="%Y-%m-%d").date()
            mask &= (content[MetaNames.DATE] == targetDate)
            
        # time
        filter_time = getattr(filter, MetaNames.START_TIME, None)
        if filter_time:
            # convert string to datetime.time
            targetTime = pd.to_datetime(filter_time, format="%H:%M").time()
            mask &= (content[MetaNames.START_TIME] >= targetTime)
        
        # always show selected ids
        selectionMask = content[MetaNames.MEASUREMENT_ID].isin(selected_ids)
        
        # use filtermask and selection mask
        mask = mask | selectionMask

        # return the df with only the rows that passed all tests
        return cast(DataFrame, content.loc[mask])
