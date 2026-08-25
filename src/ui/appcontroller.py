from datetime import datetime
from typing import Any, cast
from nicegui import ui
from nicegui import run

# import components
from src.plot.plot_factory import PlotFactory
from src.shared.filter_composition import FilterComposition
from src.shared.meta_names import MetaNames
from src.shared.oven_numbers import OvenNumbers
from src.shared.product_names import ProductNames
from src.ui.ui_view import UiView
from src.data.data_manager import DataManager
from src.database.database_manager import DatabaseManager
from src.analyzer.analyzer import Analyzer
from src.plot.table_factory import TableFactory
from src.shared.product_vvt_mapping import ProductVvtMapping
from src.plot.vvt_table_registry import COLUMN_REGISTRY

# import helping classes and containers
from src.shared.metadata import Metadata
from src.shared.upload_container import UploadContainer
from src.shared.data_models import Data
from src.shared.data_composition import DataComposition
from src.shared.zeropoint_container import ZeropointContainer
from src.shared.plot_presets import PlotPresets

# import pages
from src.ui.pages.popup_pages import Popup_confirm, Popup_warning

# import exceptions
from src.shared.exceptions import WrongInputError



class AppController:
    
    # Modules:
    
    data : DataManager
    database : DatabaseManager
    plot : PlotFactory
    ui : UiView
    table : TableFactory
    analyzer : Analyzer
    
    user : str
    isAdmin : bool = False
    
    # Attributes:
    
    #current_session_measurement : DataComposition
    terminalContent : Any
    terminalContainer : Any
    pageContainer : Any
    _layout : Any
    pages={}
    
    # Functions:
    
    def __init__(self, pageContainer, terminalContainer, user):
        """
        creates all Pages in a dictionary
        creates the UiView
        creates framework for visual output
        """
        
        # assign containers to instance of AppController -> multiple users get their own instance of AppController
        self.pageContainer = pageContainer
        self.terminalContainer = terminalContainer
        self.terminalContent = terminalContainer
        self._layout = pageContainer.parent_slot.parent
        
        self.user = str(user)
            
        # create UiView
        self.ui = UiView(self.pageContainer,self)
        
        # create pages dictionary
        self.pages = self.ui.get_pages()
        
        # create DataManager
        self.data = DataManager()
        
        # create PlotFactory
        self.plot = PlotFactory()
        
        # create Analyzer
        self.analyzer = Analyzer()
        
        # create TableFactory
        self.table = TableFactory()
        
        # instanciate current session measurement with empty data
        self.data.current_import_measurement = DataComposition()
        
        # show initial page
        self.handle_navigation_request('landing')
    
    
    
    def log(self, text: str):
        """prints given text into the terminal container"""
        
        with self.terminalContent:
            ui.label(text)
        self.terminalContent.update()
        
        
    
    @property
    def layout(self)->Any:
        return self._layout
    
    
    
    @property    
    def goldDataframe(self):
        """returns the DataFrame of the current import-session's gold data
        
        does type-cheking for you"""
        
        goldData = self.data.current_import_measurement.get_medallion_data().get("gold")
        if isinstance(goldData, Data):
            return goldData.get_dataframe()
        else:
            raise WrongInputError(f"(@property: goldDataframe): Expected a Data object for gold data, got {type(goldData)} instead.")

    
    
    def init_database(self, db_type:str):
        """initializes the database with the given type once and if type changes"""
        self.database = DatabaseManager(db_type.lower())



    def handle_navigation_request(self, pageName: str, **kwargs):
        """calls UiView to switch the page\n
        resets user input of the pages
        """
        if pageName == 'landing':
            # reset pages
            self.reset_all_pages()
            
            # reset terminal
            self.terminalContent.clear()
            
            # clear ids, golddata and zeropoints
            self.data.current_gold_data_for_plot  = {}
            self.data.current_gold_zeropoints = {}
            self.data.measurement_name_mapping = {}
            self.data.measurement_ids.clear()
            
            # clear current session
            self.data.current_import_measurement = DataComposition()

        # if callback was used with kwargs, use intel
        if kwargs:
            self.pages[pageName].configure(**kwargs)
        
        self.ui.switch_page(pageName)
        
        
        
    def reset_all_pages(self):
        """calls the reset method of all pages to reset user input and state"""
        for pageObject in self.pages.values():
            pageObject.reset()
        
        
        
    def create_data_composition(self, uploadContainer: UploadContainer, source:str):
        """creates the medallion objects from the uploaded data and saves them in the current session measurement"""
        
        # attributes
        medallionObjects: dict[str,Data]
        dateTime: datetime
        description: str
        
        # get metadata
        meta = self.data.current_import_measurement.get_metadata()
        
        # saves medallionobjects in current session, as well as the datetime of the measurement (from silver data)
        medallionObjects, dateTime, description, config_name = self.data.create_data_from_measurement(uploadContainer, source)
        
        
        if isinstance(medallionObjects, dict):
            # save medallion data
            self.data.current_import_measurement.set_medallion_data(medallionObjects)
            # save datetime in metadata
            meta.set_datetime(dateTime)
            # save description in metadata
            meta.set_description(description)
            # save config_name in metadata
            meta.set_config_name(config_name)
            # save filename in metadata
            meta.set_file_name(uploadContainer.fileName)
                        
        else:
            raise WrongInputError(f"Expected a dict of Data objects, got {type(medallionObjects)} instead.")
        
        
        
    def handle_data_import_request(self, uploadContainer: UploadContainer, source:str):
        """creates the medallion objects from input data"""
        
        # save the name 
        self.data.fileName = uploadContainer.fileName
        
        #create medallion data
        self.create_data_composition(uploadContainer, source)
        
        # get gold data
        goldData = self.goldDataframe  
        
        #analyze data and save results in current session measurement
        zeropointList = self.analyzer.analyze_zeropoints(goldData)
        
        # show warnings if there are any
        self.analyzer.flush_warnings()
        
        #save zeropoints in current session
        self.data.current_import_measurement.set_zeropoint_container(zeropointList)
        
        # store the source in metadata
        self.data.current_import_measurement.get_metadata().set_source(source)
        
    
    
    def handle_popup(self, type:str, message:str,returnPage:str):
        
        """use type:['confirm','warning']
        enter message to be displayed in popup
        """
        
        if type == 'confirm':
            pageObject=self.ui.get_page('Popup_confirm')
            popupObject=cast(Popup_confirm,pageObject)
            popupObject.set_message(message)
            popupObject.set_returnPage(returnPage)
            self.handle_navigation_request('Popup_confirm')
            
            
        elif type == 'warning':
            pageObject=self.ui.get_page('Popup_warning')
            popupObject=cast(Popup_warning,pageObject)
            popupObject.set_message(message)
            popupObject.set_returnPage(returnPage)
            self.handle_navigation_request('Popup_warning')
        
        
        
    def handle_plot_request_single(self, config:str, zeropoint:str, scope:str):
        """takes in plot-config, the chosen zeropoint, and the chosen scope and creates the plot in the calling ui-space"""
        
        # get offset for the chosen zeropoint from current session measurement
        offsetList = self.data.current_import_measurement.get_zeropoint_container().get_zeropoints()
        
        # fallback to 0 if the chosen zeropoint is not in the list
        if zeropoint not in offsetList or zeropoint is None:
            offset = 0
        else:
            offset = offsetList[zeropoint]
        
        # apply scope to the gold-dataframe for the plot based on the chosen scope
        df_for_plot = self.data.scope_data_single(scope)
        
        # copy gold-data and apply offset, create plot with offset
        return self.plot.create_plot_single(df_for_plot, config, offset)
        
       
        
    # asynchronous method to save in separate thread, so the ui does not freeze while saving
    async def handle_save_request(self, metadata: dict[str,str]):
        """takes in metadata from the user input
        
        saves the current session measurement to the database, and checks if there is a duplicate
        
        method is async to avoid freezing the ui while saving to the database
        
        calls _save_measurement_to_database() to do the actual saving in a separate thread"""
        
        # set metadata for current session measurement
        self.data.current_import_measurement.get_metadata().set_user_input(metadata)
        
        # get meta-object from current session measurement for easier handling
        metaObject = self.data.current_import_measurement.get_metadata()
        
        # triggers popup in the page if duplicate
        try:
            if self.database.is_duplicate(metaObject.get_metadata_dict()):
                return False
            
        except Exception as e:
            print(f"APPCONTROLLER: Error while checking for duplicate: {e}")
            return False
        
        # show notification that saving is in progress
        ui.notify("Saving measurement to database...", color="info")
        
        try:
            # run the saving in a separate thread
            await run.io_bound(self._save_measurement_to_database)
        
            # if saving is successful, show notification
            ui.notify("Measurement saved successfully!", color="positive")
            self.handle_navigation_request('landing')
            return True
        
        except Exception as e:
            # if failiure in db happens
            print(f"APPCONTROLLER: Error while saving measurement to database: {e}")
            ui.notify(f"Error while saving measurement to database: {e}", color="negative")
            return False

        
        
        
    def _save_measurement_to_database(self):
        """saves the current session measurement to the database
        
        resets the current session after saving to avoid artefacts in the next measurement"""
        
        # check if current session objects are valid
        for data in self.data.current_import_measurement.get_medallion_data().values():
            if not isinstance(data, Data):
                raise WrongInputError(f"Expected a Data object in medallion array, got {type(data)} instead.")
            
        if not isinstance(self.data.current_import_measurement.get_metadata(), Metadata):
            raise WrongInputError(f"Expected a Metadata-object in current session, got {type(self.data.current_import_measurement.get_metadata())} instead.")        
        
        # save measurement to database
        self.database.save_measurement(self.data.current_import_measurement)
        
        # reset current session after saving
        self.data.reset()
    
    
    
    async def handle_force_save_request(self):
        """saves the measurement to the database, even if it is a duplicate"""
        
        ui.notify("Force-saving measurement to database...", color="info")
        
        try:
            await run.io_bound(self._save_measurement_to_database)
            ui.notify("Measurement force-saved successfully!", color="positive")
            self.handle_navigation_request('landing')
        
        except Exception as e:
            ui.notify(f"Error while force-saving measurement to database: {e}", color="negative")
    
    
    def load_vvt_options(self)-> list[str]:
        """returns a list of all vvts in the database"""
        return self.database.load_vvt()["vvt_name"].unique().tolist()
    
    
    
    def load_zeropoint_options(self)-> list[str]:
        """returns a list with the keys of possible zeropoints"""
        return list(ZeropointContainer().get_zeropoints().keys())
    
    
    
    def load_oven_options(self):
        """returns a list of the possible oven numbers from shared-dataclass"""
        return OvenNumbers.to_list()
    
    
    
    def load_product_options(self):
        """returns a list of the possible products from shared-dataclass"""
        return ProductNames.to_list()
    
    
    
    def load_scope_options(self):
        """returns a list of the available presets from the plot-factory"""
        return PlotPresets.get_options()
    
    
    
    
    def load_measurement_options(self) -> dict[str,str]:
        """returns a list of the current measurements being displayed in the multiple-plot"""
        return self.data.measurement_name_mapping
        
        
        
    def load_plot_configs(self)-> list[str]:
        """returns a list of the available plot-configs from the plot-factory"""
        return self.plot.get_available_configs()
    
    
    
    def load_date_and_starttime(self) -> dict[str,str]:
        """returns the date and starttime of the current measurement when measurement is imported
        
        returns empty string as fallback"""
        
        metadata = self.data.current_import_measurement.get_metadata().get_metadata_dict()
        
        return {MetaNames.DATE: metadata.get(MetaNames.DATE,""), MetaNames.START_TIME: metadata.get(MetaNames.START_TIME,"")}
    
    
    
    def load_product_vvt_mapping(self)-> dict[str,str]:
        """returns a dict with product as key and vvt as value from the database"""
        return {k.value: v for k, v in ProductVvtMapping.asdict().items()}
    
    
    
    def load_file_name(self) -> str:
        """returns the file name of the current session measurement"""
        return self.data.current_import_measurement.get_metadata().get_metadata_dict().get(MetaNames.FILENAME,"")



    def load_description(self) -> str:
        """returns the description of the current session measurement"""
        return self.data.current_import_measurement.get_metadata().get_metadata_dict().get(MetaNames.DESCRIPTION,"")
    
    
    
    def load_config_name(self) -> str:
        """returns the config name of the current session measurement"""
        return self.data.current_import_measurement.get_metadata().get_metadata_dict().get(MetaNames.CONFIG_NAME,"")
        
        
    
    def load_product_of_measurement(self, measurement_id:str) -> str:
        """returns the product of the given measurement id from the database"""
        return str(self.database.get_measurement_metadata(measurement_id)[MetaNames.PRODUCT])
    
    
    
    def handle_violation_table_update_request(self, vvtName:str, zeropoint:str):
        """calls the analyzer and tablefactory to create a tale for the found violations"""
        
        #load vvts for Analyzer once
        if not self.analyzer.vvt_set:
            self.analyzer.set_vvt(self.database.load_vvt())
    
        # get gold dataframe and violations from analyzer
        gold = self.goldDataframe
        violations = self.analyzer.analyze_violations(gold,vvtName)
        
        # get value of zeropoint from current session measurement
        if not zeropoint == "none":
            currentOffset = self.data.current_import_measurement.get_zeropoint_container().get_zeropoints()[zeropoint]
        
        else:
            currentOffset = 0
        
        # let specialist create table with violation-list and zeropoint-logic
        self.table.update_violation_table(violations, currentOffset)
        
        
    
    def handle_violation_table_update_request_by_id(self, vvtName:str, zeropoint:str, selectedMeasurement:str):
        """calls analyzer and table factory to create table of violations by selected id"""
        
        #load vvts for Analyzer once
        if not self.analyzer.vvt_set:
            self.analyzer.set_vvt(self.database.load_vvt())
        
        # check if selected id is in current gold data
        if not self.data.current_gold_data_for_plot or not selectedMeasurement:
            return
        
        if selectedMeasurement not in self.data.current_gold_data_for_plot:
            print(f"Suche nach ID: {selectedMeasurement}")
            print(f"vorhandene IDS: {list(self.data.current_gold_data_for_plot.keys())}")
            ui.notify(f"Selected measurement id '{selectedMeasurement}' not found in current gold data.", color="negative")
            return
        
        # get gold dataframe and violations from analyzer
        gold = self.data.current_gold_data_for_plot[selectedMeasurement]
        violations = self.analyzer.analyze_violations(gold,vvtName)
        
        # if none is selected set offset to 0
        if zeropoint == "none":
            currentOffset = 0
        
        # get value of zeropoint from current session measurement
        else:
            zeroContainer = self.data.current_gold_zeropoints[selectedMeasurement]
            currentOffset = zeroContainer.get_zeropoints()[zeropoint]
            
            
        # call specialist to update table with violation-list and zeropoint-logic
        self.table.update_violation_table(violations, currentOffset)
    
    
    def handle_measurement_table_request(self, filter: FilterComposition):
        """reads the metadata source and coordinates the display of the measurement table"""
        
        # get the metadata from the source
        metaDf = self.database.list_saved_measurements()
        
        if metaDf is None:
            ui.notify("No measurements found.", color="negative")
            
        else:
            # call factory to draw the table with the content
            self.table.update_measurement_table(
                metaDf,
                filter,
                selected_ids = self.data.measurement_ids,
                set_selected_ids_callback = self.set_selected_measurements
                )
            
    
    
    def set_selected_measurements(self, selected_ids: set):
        """updates the set of selected measurement ids based on user selection in the measurement table"""
        
        # uses python.set as datatype for easy addition and removal of ids, also ensures uniqueness
        self.data.measurement_ids = selected_ids
        
        
    # async method to make sure the UI does not freeze while the data is being fetched from the database
    async def handle_show_selected_request(self):
        """handles the plotting of the selected measurements
        
        is async to avoid freezing the UI while fetching data from the database"""
        
        if not self.data.measurement_ids:
            ui.notify("No measurements selected. Please select measurements from the table to show them in the plot.", color="negative")
            return
        
        try:
            # fetch the data in a separate thread to avoid blocking the UI
            await run.io_bound(self.fetch_plot_data)
            
            # show warnings if there are any
            self.analyzer.flush_warnings()
            
            # navigate to plot page
            self.handle_navigation_request('plot-show')
            
        except Exception as e:
            ui.notify(f"Error while fetching data for selected measurements: {e}", color="negative")
            print(f"Error while fetching data for selected measurements: {e}")
        
        
    def fetch_plot_data(self):
        """fetches the plot data for the selected measurements"""
        
        # get gold-data with the selected ids from the database
        self.data.current_gold_data_for_plot  = self.database.get_gold_data_by_id(self.data.measurement_ids)
        
        # calculate zeropoints for the selected measurements and save them in dict
        for id, df in self.data.current_gold_data_for_plot.items():
            
            # calculate zeropoints with analyzer
            zeropointList = self.analyzer.analyze_zeropoints(df)
            
            #set zeropoints for the measurement in dict with measurement_id as key
            self.data.current_gold_zeropoints[id] = zeropointList
        
        # create dict for base-mapping
        baseMapping = {}
            
        # build name mapping for display
        for id in self.data.measurement_ids:
            # get metadata for the id
            metaDf = self.database.get_measurement_metadata(id)
            
            # if there is metadata, build a new name
            if not metaDf.empty:
                oven = metaDf[MetaNames.OVEN_NR].values[0]
                date = metaDf[MetaNames.DATE].values[0]
                product = metaDf[MetaNames.PRODUCT].values[0]
                
                displayName = f"{oven} | {date} | {product}"
                
            # in case there is no metadata:    
            else:
                displayName = f"Messung: {id[:4]}"
            
            # save the base-mapping
            baseMapping[id] = displayName
            
        # count measurements with the same name
        name_count = {}
        for name in baseMapping.values():
            name_count[name] = name_count.get(name, 0) + 1
        
        # create final mapping and save to data
        self.data.measurement_name_mapping = {}
        current_counts = {}
        
        # assemble names
        for id, name in baseMapping.items():
            if name_count[name] > 1:
                current_counts[name] = current_counts.get(name, 0) + 1
                self.data.measurement_name_mapping[str(id)] = f"({current_counts[name]}) {name}"
            else:
                self.data.measurement_name_mapping[str(id)] = name
        
        
        
    def handle_plot_measurements_request(self, config:str, zeropoint:str, preset:str):
        """handles the request to draw the plot of the before selected measurements based on config and zeropoint"""
        
        #check if there is data
        if not self.data.current_gold_data_for_plot:
            return None
        
        #create dict with zeropoints for the plot based on the selected zeropoint
        zeropointsDict = {}
        for m_id, zeropointContainer in self.data.current_gold_zeropoints.items():
            
            # set offset as 0 if chosen none
            if zeropoint == "none":
                zeropointsDict[m_id] = 0
            
            # set zeropoint from calculation
            else:
                zeropointsDict[m_id] = zeropointContainer.get_zeropoints()[zeropoint]
        
        # apply scope to the dataframes for the plot based on the chosen config
        df_for_plot = {}
        
        # apply scope to each dataframe 
        df_for_plot = self.data.scope_data_multiple(preset)
        
        # create display-names
        mapping = self.data.measurement_name_mapping    
        
        # create new dicts
        displayDfDict = {mapping.get(str(m_id),str(m_id)): df for m_id, df in df_for_plot.items()}
        
        displayZeroDict = {
            str(mapping.get(str(m_id),str(m_id))): int(offset)
            for m_id, offset in zeropointsDict.items()
            }
        
        # call plot factory to draw plot
        return self.plot.create_plot_multiple(
            displayDfDict,
            displayZeroDict,
            config
        )
        
    
    # async for spinner
    async def handle_admin_check(self):
        """checks if the user has admin rights and navigates to the admin landing page if true, otherwise shows a notification
        
        async if the check might take too long"""        
        
        spinner = ui.notification("Checking admin rights...", type="ongoing", spinner=True, color="info")
        
        # only use admin if the database source is databricks
        if self.database.source != "databricks":
            ui.notify("Admin check is only available for Databricks source.", color="negative")
            return
        
        # check if user has admin rights
        self.isAdmin = await run.io_bound(self.database.check_admin, self.user)
        
        spinner.dismiss()#type: ignore
        
        if self.isAdmin:
            self.handle_navigation_request('admin_landing')
            
        else:
            ui.notify("You do not have admin rights.", color="negative")
            
            
        
    def load_user(self):
        """returns the user of the current session"""
        return str(self.user)
    
    
    
    async def handle_delete_measurements(self):
        """deletes the selected measurements from the database"""
        
        # load ids
        selected_ids = self.data.measurement_ids

        # delete asynchronous with spinner
        async def _delete():
            notification = ui.notification(
                "Deleting measurements...",
                type="ongoing",
                spinner=True,
            )

            # run the deletion in a separate thread to avoid blocking the UI
            await run.io_bound(self.database.delete_measurements, selected_ids)

            # dismiss the notification and close the dialog
            notification.dismiss()
            dialog.close()
            
            # notify how many measurements were deleted and return to admin landing
            ui.notify(f"{len(selected_ids)} measurements deleted.", type="positive")
            self.handle_navigation_request("admin_landing")



        # Confirmation-Dialog
        with ui.dialog() as dialog, ui.card().classes("p-6"):
            ui.label("Confirm Deletion").classes("text-lg font-bold")
            ui.label(
                f"Are you sure you want to delete {len(selected_ids)} "
                f"selected measurements? This action cannot be undone."
            )
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("Cancel", on_click=dialog.close)
                ui.button("Delete", color="red", on_click=_delete)

        dialog.open()
        
        
        
    def handle_admin_vvt_table(self, tableContainer):
        """handles the request to display the vvt table in the admin page
        
        takes in the container for the table to be displayed in"""
        
        # get the current vvt
        vvt_df = self.database.load_vvt()
        
        # create registry once for the session
        if not hasattr(self, 'registry') or self.registry is None:
            self.registry = COLUMN_REGISTRY
        
        self.table.build_admin_vvt_table(
            vvt_df,
            self.registry,
            tableContainer
        )
        
        
        
    def handle_admin_rewrite_vvts(self):
        """handles the request to rewrite the vvts in the database with the new vvt df from the table"""
        
        # get the df from the table
        vvt_df = self.table.get_vvt_df()
        
        # rewrite the vvts in the database
        self.database.admin_rewrite_vvt(vvt_df)
        
        ui.notify("VVTs rewritten successfully.", color="positive")
        
        self.handle_navigation_request('admin_landing')
        
        
        
    def handle_bulk_import_request(self, content: list[UploadContainer]):
        """handles the bulk import of measurements from a list of UploadContainers"""
        
        # read data from uploaded files
        information = self.data.get_information_bulk_import(content)
        
        print(f"Bulk import information: {information}")
        
        self.handle_navigation_request('bulkImportPage')