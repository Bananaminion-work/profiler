from nicegui import ui

from src.shared.violation import Violation
from src.shared.filter_composition import FilterComposition
from src.shared.meta_names import MetaNames
import pandas as pd
from pandas import DataFrame
from typing import cast



class TableFactory:
    
    def __init__(self):
        self.vvt_df = DataFrame()
        
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
        
    
    def text_filter(self, mask: pd.Series, content:DataFrame, col_name:str, filter_value:str) -> pd.Series:
        """applies a text filter to the given mask and returns the updated mask"""
        
        if filter_value and col_name in content.columns:
            return mask & content[col_name].astype(str).str.contains(str(filter_value), case=False, na=False, regex=False)
        
        return mask
        
        
    def apply_filter(self, content: DataFrame, filter: FilterComposition, selected_ids: set) -> DataFrame:
        """applys filters with the given values of the FilterComposition-object to the given Dataframe
        
        returns the filtered DataFrame"""
        
        # return the df if filter is empty
        if content.empty:
            return content
            
        # create mask without filtering
        mask = pd.Series(True, index=content.index)

        # TEXT-FILTERS
        
        # ovennr
        mask = self.text_filter(mask, content, MetaNames.OVEN_NR, getattr(filter, MetaNames.OVEN_NR, ""))
        # product
        mask = self.text_filter(mask, content, MetaNames.PRODUCT, getattr(filter, MetaNames.PRODUCT, ""))
        # recipe
        mask = self.text_filter(mask, content, MetaNames.OVEN_RECIPE, getattr(filter, MetaNames.OVEN_RECIPE, ""))
        # load profile
        mask = self.text_filter(mask, content, MetaNames.LOAD_PROFILE, getattr(filter, MetaNames.LOAD_PROFILE, ""))
        # comment
        mask = self.text_filter(mask, content, MetaNames.COMMENT, getattr(filter, MetaNames.COMMENT, ""))
        # description
        mask = self.text_filter(mask, content, MetaNames.DESCRIPTION, getattr(filter, MetaNames.DESCRIPTION, ""))
        # file name
        mask = self.text_filter(mask, content, MetaNames.FILENAME, getattr(filter, MetaNames.FILENAME, ""))
        # config name
        mask = self.text_filter(mask, content, MetaNames.CONFIG_NAME, getattr(filter, MetaNames.CONFIG_NAME, ""))


        # date
        filter_date = getattr(filter, MetaNames.DATE, None)
        if filter_date and MetaNames.DATE in content.columns:
            
            # check if it is a range or just one date
            if isinstance(filter_date, str):
                date_from = filter_date.replace("/", "-")
                date_to = date_from
                
            else:
                # define range limits
                date_from = filter_date.get("from", "").replace("/", "-")
                date_to = filter_date.get("to", "").replace("/", "-")
            
            # convert to datetime
            content_dates = pd.to_datetime(content[MetaNames.DATE], errors='coerce').dt.date #type:ignore
            
            # apply the date filter to the mask
            if date_from:
                date_from = pd.to_datetime(date_from, format="%Y-%m-%d").date()
                mask &= (content_dates >= date_from)
            if date_to:
                date_to = pd.to_datetime(date_to, format="%Y-%m-%d").date()
                mask &= (content_dates <= date_to)
            
        # time
        filter_time = getattr(filter, MetaNames.START_TIME, None)
        if filter_time and MetaNames.START_TIME in content.columns:
            # convert string to datetime.time
            targetTime = pd.to_datetime(filter_time, format="%H:%M").strftime("%H:%M")
            mask &= (content[MetaNames.START_TIME].astype(str).str[:5] >= targetTime)
        
        # always show selected ids
        selectionMask = content[MetaNames.MEASUREMENT_ID].isin(selected_ids)
        
        # use filtermask and selection mask
        mask = mask | selectionMask

        # return the df with only the rows that passed all tests
        return cast(DataFrame, content.loc[mask])


    def build_admin_vvt_table(self, df: DataFrame, registry: dict, container)->None:
        """builds a table for the admin view of the vvt table with the given dataframe and registry of columns and their definitions"""
        # copy input df for safety
        self.vvt_df = df.copy()
        
        with container:
            
            with ui.column().classes("w-full overflow-x-auto gap-0"):
                
                # display headers
                with ui.row().classes("min-w-max flex-nowrap gap-1 bg-gray-200 p-2 sticky top-0"):
                    for col, col_def in registry.items():
                        ui.label(col_def.label).classes("w-60 font-bold text-sm shrink-0")
                
                
                # create data-rows
                for row_idx, row in self.vvt_df.iterrows():
                    with ui.row().classes("min-w-max flex-nowrap gap-1 p-1 border-b"):
                
                        # iterate over the columns in the registry to create the widgets for each column
                        for col, col_def in registry.items():
                        
                            # get actual value
                            value = row.get(col, "")
                            
                            # bugfix: if value is nan, set it to empty string
                            if pd.isna(value):
                                value = ""
                            
                            # if option is dropdown ui select will be created
                            if col_def.widget == "dropdown":
                                options = col_def.option_source.get_options()
                                ui.select(
                                    options,
                                    value=value if value in options else None,
                                    label=col_def.label,
                                    # on_change will be called when the value of the select changes, it will call the _on_edit method with the row index, column name and new value
                                    on_change=lambda e, r=row_idx, c=col: self._on_edit(r, c, e.value)
                                ).classes("w-60 shrink-0").props("dense borderless")
                                
                            elif col_def.widget == "text":                                
                                ui.input(
                                    value=str(value),
                                    label=col_def.label,
                                    on_change=lambda e, r=row_idx, c=col: self._on_edit(r, c, e.value)
                                ).classes("w-60 shrink-0").props("dense borderless")
                            
                            
                            
                            
    def _on_edit(self, row_idx, col_name, new_value):
        """updates the value of the cell in the dataframe when a widget is changed"""
        self.vvt_df.at[row_idx, col_name] = new_value
        
    def get_vvt_df(self) -> DataFrame:
        """returns the current state of the vvt dataframe"""
        return self.vvt_df.copy()
    
    def reset_vvt_df(self):
        """resets the vvt dataframe to the given dataframe"""
        self.vvt_df = DataFrame()
        
    