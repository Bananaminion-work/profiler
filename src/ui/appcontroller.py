from typing import Any, cast

from nicegui import ui
from pandas import DataFrame

# import components
from src.plot.plot_factory import PlotFactory
from src.shared.filter_composition import FilterComposition
from src.shared.violation import Violation
from src.ui.ui_view import UiView
from src.data.data_manager import DataManager
from src.database.database_manager import DatabaseManager
from src.analyzer.analyzer import Analyzer
from src.plot.table_factory import TableFactory

# import helping classes and containers
from src.shared.metadata import Metadata
from src.shared.upload_container import UploadContainer
from src.shared.data_models import Data
from src.shared.data_composition import DataComposition
from src.shared.zeropoint_container import ZeropointContainer

# import pages
from src.ui.pages.importPage_getData import ImportPage_getData
from src.ui.pages.importPage_showData import ImportPage_showData
from src.ui.pages.landing import LandingPage
from src.ui.pages.plotPage_selectData import PlotPage_selectData
from src.ui.pages.plotPage_showData import PlotPage_showData
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
    
    # Attributes:
    
    current_session_measurement : DataComposition
    terminalContent : Any
    terminalContainer : Any
    pageContainer : Any
    _layout : Any
    pages={}
    selected_measurement_ids: set
    current_gold_dataframe_for_plot: dict[str,DataFrame]
    current_gold_zeropoints: dict[str,ZeropointContainer]
    
    # Functions:
    
    def __init__(self, pageContainer, terminalContainer):
        """
        creates all Pages in a dictionary
        creates the UiView
        creates framework for visual output
        """
        #with ui.column().classes("w-full max-w-[1920px] mx-auto") as root:
        #    self.pageContainer = ui.column().classes("w-full min-h-[720px]")
        #    ui.separator()
        #    self.terminalContainer = ui.column().classes("w-full h-24 border p-2 overflow-auto")
        #    
        #self.terminalContent = self.terminalContainer
        #self._layout = root
        
        # assign containers to instance of AppController -> multiple users get their own instance of AppController
        self.pageContainer = pageContainer
        self.terminalContainer = terminalContainer
        self.terminalContent = terminalContainer
        self._layout = pageContainer.parent_slot.parent
        self.selected_measurement_ids = set()
        self.current_gold_dataframe_for_plot = {}
            
        # create pages dictionary
        self.create_pages()
        
        # create UiView
        self.ui = UiView(self.pages,self.pageContainer)
        
        # create DataManager
        self.data = DataManager()
        
        # create PlotFactory
        self.plot = PlotFactory()
        
        #create DatabaseManager
        self.database = DatabaseManager("csv")
        
        # create Analyzer
        self.analyzer = Analyzer(self.database.load_vvt())
        
        # create TableFactory
        self.table = TableFactory()
        
        # instanciate current session measurement with empty data
        self.current_session_measurement = DataComposition()
        
        # show initial page
        self.handle_navigation_request('landing')
    
        
    
    
    def log(self, text: str):
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
        
        goldData = self.current_session_measurement.get_medallion_data().get("gold")
        if isinstance(goldData, Data):
            return goldData.get_dataframe()
        else:
            raise WrongInputError(f"(@property: goldDataframe): Expected a Data object for gold data, got {type(goldData)} instead.")
    
    
    
    def reset_measuremen_ids(self):
        """clears the set of selected measurement ids, used when navigating back to home to ensure clean state for next selection"""
        self.selected_measurement_ids.clear()
    
    
    
    def create_pages(self):
        """initiates all pages, also used to clear input-cells after home-navigation
        """
    
        self.pages['landing'] = LandingPage(self)
        self.pages['import-get'] = ImportPage_getData(self)
        self.pages['import-show'] = ImportPage_showData(self)
        self.pages['plot-select'] = PlotPage_selectData(self)
        self.pages['plot-show'] = PlotPage_showData(self)
        self.pages['popup-confirm'] = Popup_confirm(self)
        self.pages['popup-warning'] = Popup_warning(self)



    def handle_navigation_request(self, pageName: str):
        """calls UiView to switch the page\n
        resets user input of the pages
        """
        if pageName == 'landing':
            # reset pages
            self.reset_all_pages()
            # reset terminal
            self.terminalContent.clear()
            # clear ids, golddata and zeropoints
            self.reset_measuremen_ids()
            self.current_gold_dataframe_for_plot = {}
            self.current_gold_zeropoints = {}
            # clear current session
            self.current_session_measurement = DataComposition()

        self.ui.switch_page(pageName)
        
        
        
    def reset_all_pages(self):
        for pageObject in self.pages.values():
            pageObject.reset()
        
        
        
    def create_data_composition(self, uploadContainer: UploadContainer, source:str):
        # saves medallionobjects in current session, as well as the datetime of the measurement (from silver data)
        medallionObjects, dateTime = self.data.create_data_from_measurement(uploadContainer, source)
        
        if isinstance(medallionObjects, dict):
            self.current_session_measurement.set_medallion_data(medallionObjects)
            
            self.current_session_measurement.get_metadata().set_datetime(dateTime)
        else:
            raise WrongInputError(f"Expected a dict of Data objects, got {type(medallionObjects)} instead.")
        
        
        
    def handle_data_import_request(self, uploadContainer: UploadContainer, source:str):
        """creates the medallion objects from input data"""
        
        #create medallion data
        self.create_data_composition(uploadContainer, source)
        
        # get gold data
        goldData = self.goldDataframe  
        
        #analyze data and save results in current session measurement
        zeropointList = self.analyzer.analyze_zeropoints(goldData)
        
        #save zeropoints in current session
        self.current_session_measurement.set_zeropoint_container(zeropointList)
        
        # store the source in metadata
        self.current_session_measurement.get_metadata().set_source(source)
        
    
    
    def handle_popup(self, type:str, message:str,returnPage:str):
        
        """use type:['confirm','warning']
        enter message to be displayed in popup
        """
        
        if type == 'confirm':
            pageObject=self.ui.get_page('popup-confirm')
            popupObject=cast(Popup_confirm,pageObject)
            popupObject.set_message(message)
            popupObject.set_returnPage(returnPage)
            self.handle_navigation_request('popup-confirm')
            
            
        elif type == 'warning':
            pageObject=self.ui.get_page('popup-warning')
            popupObject=cast(Popup_warning,pageObject)
            popupObject.set_message(message)
            popupObject.set_returnPage(returnPage)
            self.handle_navigation_request('popup-warning')
        
        
        
    def handle_plot_request_single(self, config:str, zeropoint:str):
        """takes in plot-config and the chosen zeropoint and creates the plot in the calling ui-space"""
        
        # get offset for the chosen zeropoint from current session measurement
        offsetList = self.current_session_measurement.get_zeropoint_container().get_zeropoints()
        offset = offsetList[zeropoint]
        
        # copy gold-data and apply offset, create plot with offset
        goldData = self.goldDataframe.copy()
        return self.plot.create_plot_single(goldData, config, offset)
        
        
        
    def handle_save_request(self, metadata: dict[str,str]):
                
        # set metadata for current session measurement
        self.current_session_measurement.get_metadata().set_user_input(metadata)
        
        # check if current session objects are valid
        for data in self.current_session_measurement.get_medallion_data().values():
            if not isinstance(data, Data):
                raise WrongInputError(f"Expected a Data object in medallion array, got {type(data)} instead.")
            
        if not isinstance(self.current_session_measurement.get_metadata(), Metadata):
            raise WrongInputError(f"Expected a Metadata-object in current session, got {type(self.current_session_measurement.get_metadata())} instead.")
        
        # TODO: check if there is another measurement already saved with same or similar metadata
        # ask user for confirmation if they want to overwrite the existing measurement or not (popup)
        
        
        # save measurement to database
        self.database.save_measurement(self.current_session_measurement)
        ui.notify("Measurement saved successfully!", color="green")
        
        # reset current session after saving
        self.current_session_measurement = DataComposition()
        self.handle_navigation_request('landing')
    
    
    
    def load_vvt_options(self)-> list[str]:
        """returns a list of all vvts in the database"""
        return self.database.load_vvt()["vvt_name"].unique().tolist()
    
    
    
    def handle_violation_table_update_request(self, vvtName:str, zeropoint:str):
    
        # get gold dataframe and violations from analyzer
        gold = self.goldDataframe
        violations = self.analyzer.analyze_violations(gold,vvtName)
        
        # get value of zeropoint from current session measurement
        if not zeropoint == "none":
            currentOffset = self.current_session_measurement.get_zeropoint_container().get_zeropoints()[zeropoint]
        
        else:
            currentOffset = 0
        
        # let specialist create table with violation-list and zeropoint-logic
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
                selected_ids = self.selected_measurement_ids,
                set_selected_ids_callback = self.set_selected_measurements
                )
            
    
    
    def set_selected_measurements(self, selected_ids: set):
        """updates the set of selected measurement ids based on user selection in the measurement table"""
        
        # uses python.set as datatype for easy addition and removal of ids, also ensures uniqueness
        self.selected_measurement_ids = selected_ids
        
        
        
    def handle_show_selected_request(self):
        
        if not self.selected_measurement_ids:
            ui.notify("No measurements selected. Please select measurements from the table to show them in the plot.", color="negative")
            return
        
        # get gold-data with the selected ids from the database
        self.current_gold_dataframe_for_plot = self.database.get_gold_data_by_id(self.selected_measurement_ids)
        
        # calculate zeropoints for the selected measurements and save them in dict
        for id, df in self.current_gold_dataframe_for_plot.items():
            
            # calculate zeropoints with analyzer
            zeropointList = self.analyzer.analyze_zeropoints(df)
            
            #set zeropoints for the measurement in dict with measurement_id as key
            self.current_gold_zeropoints[id] = zeropointList
        
        # navigate to plot page
        self.handle_navigation_request('plot-show')
        
        
        
    def handle_plot_measurements_request(self, config:str, zeropoint:str):
        """handles the request to draw the plot of the before selected measurements based on config and zeropoint"""
        
        #check if there is data
        if not hasattr(self, 'current_gold_dataframe_for_plot') or not self.current_gold_dataframe_for_plot:
            ui.notify("There is no data to be displayed.", color="negative")
            return None
        
        #create dict with zeropoints for the plot based on the selected zeropoint
        zeropointsDict = {}
        for id, zeropointContainer in self.current_gold_zeropoints.items():
            
            # set offset as 0 if chosen none
            if zeropoint == "none":
                zeropointsDict[id] = 0
            
            # set zeropoint from calculation
            else:
                zeropointsDict[id] = zeropointContainer.get_zeropoints()[zeropoint]
        
        # call plot factory to draw plot
        return self.plot.create_plot_multiple(
            self.current_gold_dataframe_for_plot,
            zeropointsDict,
            config
        )