import re

from nicegui import ui
from src.shared.config_names import ConfigNames
from src.ui.pages.base_pages import SubPage
from src.shared.meta_names import MetaNames
from src.shared.vvt_names import VvtNames
from src.shared.zeropoint_names import ZeropointNames
from src.shared.plot_presets import PlotPresets

class ImportPage_showData(SubPage):
    
    pageName = "import-show"
    oven_Recipe: str = ""
    oven_Nr: str = "1234"
    product: str = "PM6"
    load: str = "25%"
    pos: str = "8"
    count: str = "8"
    prod_test: str = "Test"
    nozzlefield: str = ""
    profile_name: str = ""
    comment: str = ""
    injection_1: str = ""
    injection_2: str = ""
    injection_3: str = ""
    injection_4: str = ""
    waiting_1: str = ""
    waiting_2: str = ""
    waiting_3: str = ""
    waiting_4: str = ""
    cooling_freq_1: str = ""
    cooling_freq_2: str = ""
    cooling_freq_3: str = ""
    cooling_freq_4: str = ""
    cooling_time_1: str = ""
    cooling_time_2: str = ""
    cooling_time_3: str = ""
    cooling_time_4: str = ""
    config: str = ConfigNames.STANDARD_BOTTOM
    bulkheadZeropoint: str = ""
    firstInjectionZeropoint: str = ""
    above235Zeropoint: str = ""
    ventilate2Zeropoint: str = ""
    chosenZeropoint_show: str = ZeropointNames.NONE
    chosenScope: str = PlotPresets.DEFAULT
    activeZeropoint: str = ""
    selectedVVT: str = ""

    def _create_accordion(self) -> None:
        
        # create first accordion
        with ui.expansion("Injections & Holding Times (1-4)", icon="colorize").classes("w-full"):
            
            # create 4 rows for the 4 phases
            with ui.row().classes("w-full no-wrap gap-4 p-2"):
                for i in range(1,5):
                    with ui.card().classes("p-3 gap-2 bg-slate-50"):
                        ui.label(f"Phase {i}").classes("text-weight-bold text-primary")
                        # volume
                        ui.input(f"Volume of injection {i}:").classes("w-full").bind_value(self, f"injection_{i}")
                        # holdingTime
                        ui.input(f"Holding Time {i}:").classes("w-full").bind_value(self, f"waiting_{i}")
                    
        # create second accordion
        with ui.expansion("Coolingprocess (1-4)", icon="ac_unit").classes("w-full"):
            
            # create 4 rows for the 4 phases
            with ui.row().classes("w-full no-wrap gap-4 p-2"):
                for i in range(1,5):
                    with ui.card().classes("p-3 gap-2 bg-slate-50"):
                        ui.label(f"Phase {i}").classes("text-weight-bold text-primary")
                        # volume
                        ui.input(f"Cooling Frequency {i}:").classes("w-full").bind_value(self, f"cooling_freq_{i}")
                        # holdingTime
                        ui.input(f"Cooling Time {i}:").classes("w-full").bind_value(self, f"cooling_time_{i}")



    def build_content(self) -> None:
        
        
        with ui.column().classes("w-full gap-4"):
            
            # section 1: analysis area
            with ui.card().classes("w-full h-[85vh] relative flex flex-col p-0") as plotCard:
                
                # section 1: Config
                with ui.row().classes("w-full p-4 items-center gap-4 bg-gray-50 shrink-0"):
                    ui.label("Choose config, zeropoint and scope").classes('text-lg')
                    
                    # get options
                    configs = self.controller.load_plot_configs()
                    # add Standard config to the first position if not already present
                    if ConfigNames.STANDARD_BOTTOM not in configs:
                        configs.insert(0, ConfigNames.STANDARD_BOTTOM)
                    
                    ui.select(
                        configs,
                        value=configs[0],
                        label="choose config for plot",
                        on_change=self.update_plot_config
                    ).bind_value(self,"config").classes("w-100")
                    
                    # load options
                    zeropointOptions = self.controller.load_zeropoint_options()
                    
                    ui.select(
                        options=zeropointOptions,
                        value=zeropointOptions[0],
                        label="choose zeropoint for plot",
                        on_change=self.update_vvt_selection
                    ).bind_value(self,"chosenZeropoint_show").classes("w-100")
                    
                    
                    # load options
                    scopeOptions = self.controller.load_scope_options()
                    
                    ui.select(
                        options=scopeOptions,
                        value=scopeOptions[0],
                        label="choose data preset for plot",
                        on_change=self.update_plot_config
                    ).bind_value(self,"chosenScope").classes("w-100")
                        
                #fullscreen button 
                ui.button(
                                icon='fullscreen',
                                on_click=lambda: ui.run_javascript(
                                        f'document.fullscreenElement ? document.exitFullscreen() : getElement({plotCard.id}).$el.requestFullscreen()'
                                    )
                            ).props('flat round').classes('absolute bottom-2 right-2 z-10') #orientation of the button
                    
                # create container for specialist to draw in
                self.plotContainer = ui.column().classes("w-full flex-1 p-0 m-0 min-h-0 minw-0")
                # call function to draw plot (init)
                self.update_plot_preview()
                        
                    
                    
            # section 3: vvt dropdown and table
            with ui.card().classes("w-full"):
                
                # create dropdown to select vvt use on change event
                with ui.row().classes("w-full"):
                    
                    ui.label("Choose VVT to be checked")
                    
                    # load options
                    self.vvtOptions = self.controller.load_vvt_options()
                    #set first option as value
                    self.selectedVVT = VvtNames.VPS_MAIN if self.vvtOptions else ""
                    
                    ui.select(
                        self.vvtOptions,
                        label="Select VVT",
                        on_change=self.update_vvt_table
                        ).bind_value(self, "selectedVVT").classes("w-100")
                    
                # create table container with label
                ui.label("VVT - Violations").classes('text-lg')
                self.tableContainer = ui.row().classes("w-full h-60 overflow-auto")
                    
                    
            
            # section 4: Metadata and details
            with ui.card().classes("w-full"):
                ui.label("Input Metadata to be saved to database").classes('text-xl')
                
                # get intel
                dateAndStart = self.controller.load_date_and_starttime()
                fileName = self.controller.load_file_name()
                description = self.controller.load_description()
                self.configName = self.controller.load_config_name()
                
                with ui.card().classes("w-full p-3 gap-2 bg-slate-50"):
                    
                    ui.label(f"Date of measurement: {dateAndStart[MetaNames.DATE]}").classes("text-lg")
                    ui.label(f"Start time of measurement: {dateAndStart[MetaNames.START_TIME]}").classes("text-lg")

                    ui.label(f"File name: {fileName}").classes("text-lg")
                    ui.label(f"Measurenemt description from XML-file: {description}").classes("text-lg")
                    ui.label(f"Config name from XML-file: {self.configName}").classes("text-lg")
            
                with ui.grid(columns=2).classes("w-full gap-3"):
                    
                    
                    # get options for dropdowns from controller
                    self.ovenOptions = self.controller.load_oven_options()
                    
                    self.productOptions = self.controller.load_product_options()
                    self.product = self.productOptions[0] if self.productOptions else "" # set first option as default value
                    
                    ui.select(self.ovenOptions, label="Select the oven-number").bind_value(self, "oven_Nr")
                    ui.select(self.productOptions, label="Select the product", on_change=self.change_vvt_preset).bind_value(self, "product")
                    carrierloadOptions = ["25%", "50%", "75%", "100%"]
                    ui.select(carrierloadOptions, value=carrierloadOptions[0], label="Loading-condition").bind_value(self, "load")
                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Position of measurement cooler").bind_value(self, "pos")
                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Amount of coolers").bind_value(self, "count")
                    ui.radio(["Production", "Test"], value="Test").props("inline").bind_value(self, "prod_test")

                ui.separator()
                with ui.row().classes("w-full"):
                    ui.input(MetaNames.NOZZLEFIELD, placeholder="Dreifachdüsenfeld").bind_value(self, "nozzlefield").classes("w-200")
                    ui.input(MetaNames.PROFILE_NAME, placeholder="used profilename").bind_value(self, "profile_name").classes("w-200")
                    ui.input(MetaNames.OVEN_RECIPE, placeholder="oven recipe").bind_value(self, "oven_Recipe").classes("w-200")
                self._create_accordion()
                ui.textarea(MetaNames.COMMENT, placeholder="enter your comment..").bind_value(self, "comment").classes("w-full")
                    
                    
                    
                # separator and buttons
                ui.separator().classes("my-4")
                
                with ui.row().classes("justify-end w-full"):
                    ui.button("Save", on_click=self.on_save_click)
                    ui.button("Return to Home", color="negative", on_click=self.on_discard_click)
                    
        # init plot and table
        self.change_oven_preset()
        self.update_plot_preview()
        self.update_vvt_table()
        
    def update_plot_preview(self):
        """clears plot container and redraws with fresh plot"""
        
        if not hasattr(self, 'plotContainer') or self.plotContainer.is_deleted:
            return  # container is not set yet, do nothing
        
        self.plotContainer.clear()
        
        plotContent = self.controller.handle_plot_request_single(
            self.config,
            self.chosenZeropoint_show,
            self.chosenScope
            )
        
        if plotContent is not None:
            # with function enables the call of handle-method on the container object
            with self.plotContainer:
                ui.plotly(plotContent).classes("w-full h-full").props("responsive=True")

                
                
    def update_vvt_table(self):
        """clears the vvt table container and redraws the table with the violations for the selected vvt"""
        
        if not hasattr(self, "tableContainer") or self.tableContainer.is_deleted:
            return
        
        self.tableContainer.clear()
        
        with self.tableContainer:
            self.controller.handle_violation_table_update_request(self.selectedVVT, self.chosenZeropoint_show)
    
    
    def update_vvt_selection(self):
        self.update_plot_preview()
        self.update_vvt_table()
        
        
    def update_plot_config(self):
        if self.config == None:
            return  # do nothing if config is not set
        
        self.chosenZeropoint_show = ZeropointNames.NONE
        self.update_plot_preview()
        self.update_vvt_table()
    

    async def on_save_click(self, saveButton) -> None:
        
        
        # fields that must have a value
        requiredFields = {
            "nozzlefield"           : MetaNames.NOZZLEFIELD,
            "profile_name"          : MetaNames.PROFILE_NAME,
            "oven_Recipe"           : MetaNames.OVEN_RECIPE,
            "oven_Nr"               : MetaNames.OVEN_NR,
            "product"               : MetaNames.PRODUCT,
            "load"                  : MetaNames.LOAD_PROFILE,
            "pos"                   : MetaNames.POSITION_MEASUREMENT_COOLER,
            "count"                 : MetaNames.COOLER_COUNT_ON_TRAY,
            "injection_1"           : MetaNames.INJECTION_1,
            "waiting_1"             : MetaNames.WAITING_1,
            "cooling_freq_1"        : MetaNames.COOLING_FREQ_1,
            "cooling_time_1"        : MetaNames.COOLING_TIME_1,
        }
        
        for field in requiredFields.keys():
            value = getattr(self, field)
            
            # cancel if field value is missing
            if not value:
                ui.notify(f"Please fill in the required field: {requiredFields[field]}", color="negative")
                return
        
        
        # turn off the button to prevent multiple clicks
        saveButton.sender.disable()
        
        
        # create a metadta dict with static names from shared/meta_names.py
        metadata = {
            MetaNames.OVEN_RECIPE                   : self.oven_Recipe,
            MetaNames.OVEN_NR                       : self.oven_Nr,
            MetaNames.PRODUCT                       : self.product,
            MetaNames.LOAD_PROFILE                  : self.load,
            MetaNames.POSITION_MEASUREMENT_COOLER   : self.pos,
            MetaNames.COOLER_COUNT_ON_TRAY          : self.count,
            MetaNames.TEST_COOLER_FLAG              : self.prod_test,
            MetaNames.NOZZLEFIELD                   : self.nozzlefield,
            MetaNames.PROFILE_NAME                  : self.profile_name,
            MetaNames.COMMENT                       : self.comment,
            MetaNames.INJECTION_1                   : self.injection_1,
            MetaNames.INJECTION_2                   : self.injection_2,
            MetaNames.INJECTION_3                   : self.injection_3,
            MetaNames.INJECTION_4                   : self.injection_4,
            MetaNames.WAITING_1                     : self.waiting_1,
            MetaNames.WAITING_2                     : self.waiting_2,
            MetaNames.WAITING_3                     : self.waiting_3,
            MetaNames.WAITING_4                     : self.waiting_4,
            MetaNames.COOLING_FREQ_1                : self.cooling_freq_1,
            MetaNames.COOLING_FREQ_2                : self.cooling_freq_2,
            MetaNames.COOLING_FREQ_3                : self.cooling_freq_3,
            MetaNames.COOLING_FREQ_4                : self.cooling_freq_4,
            MetaNames.COOLING_TIME_1                : self.cooling_time_1,
            MetaNames.COOLING_TIME_2                : self.cooling_time_2,
            MetaNames.COOLING_TIME_3                : self.cooling_time_3,
            MetaNames.COOLING_TIME_4                : self.cooling_time_4
        }
        
        saved_directly = await self.controller.handle_save_request(metadata)

        if not saved_directly:
            self._show_duplicate_dialog()
      
    
    
    
    def _show_duplicate_dialog(self):
        """Zeichnet das Warn-Popup"""
        with ui.dialog() as dialog, ui.card():
            ui.label("A measurement with similar metadata (±1 hour) already exists.")
            ui.label("Do you really want to save it anyway?")
            
            async def on_confirm():
                dialog.close()
                await self.controller.handle_force_save_request()
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button("Cancel", on_click=dialog.close).props('flat')
                ui.button("Yes, save it", on_click=on_confirm).props('color=negative')
                
        dialog.open()
    
    

    def on_discard_click(self) -> None:
        self.controller.handle_popup("confirm", "Are you sure to discard and return to home?", self.pageName)

    def reset(self) -> None:
        self.oven_Nr = "1234"
        self.oven_Recipe = ""
        self.product = "PM6"
        self.load = "25%"
        self.pos = "8"
        self.count = "8"
        self.prod_test = "Test"
        self.nozzlefield = ""
        self.profile_name = ""
        self.comment = ""
        self.injection_1 = ""
        self.injection_2 = ""
        self.injection_3 = ""
        self.injection_4 = ""
        self.waiting_1 = ""
        self.waiting_2 = ""
        self.waiting_3 = ""
        self.waiting_4 = ""
        self.cooling_freq_1 = ""
        self.cooling_freq_2 = ""
        self.cooling_freq_3 = ""
        self.cooling_freq_4 = ""
        self.cooling_time_1 = ""
        self.cooling_time_2 = ""
        self.cooling_time_3 = ""
        self.cooling_time_4 = ""
        self.config = ConfigNames.STANDARD_BOTTOM
        
    def change_vvt_preset(self):
               
        product_vvt_mapping = self.controller.load_product_vvt_mapping()
        
        if self.product in product_vvt_mapping:
            # set vvt selection to the mapped value for the selected product
            self.selectedVVT = product_vvt_mapping[self.product]
            
        else:
            self.selectedVVT = VvtNames.VPS_MAIN  # default value if product not found in mapping
            
            
    def change_oven_preset(self):
        """selects the oven number depending on the config name"""
        
        if not self. configName:
            return  # do nothing if configName is not set
        
        numberInConfig = re.findall(r"\d+", self.configName)
        
        if not numberInConfig:
            return  # do nothing if no number is found in configName
        
        if self.ovenOptions is not None:
            
            # search for the number of the configname
            for number in numberInConfig:
                for option in self.ovenOptions:
                    if number in option:
                        self.oven_Nr = option
                        return  # exit the function after setting the oven number
        
        return  # do nothing if no matching oven number is found in ovenOptions