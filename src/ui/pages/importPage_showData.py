from nicegui import ui
from src.ui.pages.base_pages import SubPage
from src.shared.meta_names import MetaNames


class ImportPage_showData(SubPage):
    
    pageName = "import-show"
    oven_Recipe: str = ""
    oven_Nr: str = "1234"
    product: str = "PM6"
    load: str = "8"
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
    config: str = "standard"
    bulkheadZeropoint: str = ""
    firstInjectionZeropoint: str = ""
    above235Zeropoint: str = ""
    ventilate2Zeropoint: str = ""
    chosenZeropoint_show: str = "none"
    activeZeropoint: str = ""
    selectedVVT: str = ""

    def _create_accordion(self) -> None:
        groups = [
            ("Injections",        "Injection",         ["injection_1",    "injection_2",    "injection_3",    "injection_4"]),
            ("Waiting-time",      "Waiting-time",      ["waiting_1",      "waiting_2",      "waiting_3",      "waiting_4"]),
            ("Cooling-frequency", "Cooling-frequency", ["cooling_freq_1", "cooling_freq_2", "cooling_freq_3", "cooling_freq_4"]),
            ("Cooling-time",      "Cooling-time",      ["cooling_time_1", "cooling_time_2", "cooling_time_3", "cooling_time_4"]),
        ]
        for title, prefix, attrs in groups:
            with ui.expansion(title, icon="expand_more"):
                for i, attr in enumerate(attrs, 1):
                    ui.input(f"{prefix} {i}:", placeholder="enter value...").classes("w-full").bind_value(self, attr)

    def build_content(self) -> None:
        
        
        with ui.column().classes("w-full gap-4"):
            
            
            # section 1: Config
            with ui.card().classes("w-full"):
                ui.label("Choose config and zeropoint").classes('text-lg')
                with ui.row().classes("w-full"):
                    ui.select(
                        ["standard", "standard2", "3", "4", "5", "6", "7", "8"],
                        value="standard",
                        label="choose config for plot",
                        on_change=self.update_plot_config
                    ).bind_value(self,"config").classes("w-100")
                    
                    ui.select(
                        options=["none", "bulkhead", "first injection", "above 235", "ventilate 2"],
                        value="none",
                        label="choose zeropoint for plot",
                        on_change=self.update_vvt_selection
                    ).bind_value(self,"chosenZeropoint_show").classes("w-100")
                    
                    
                    
            # section 2: Plot
            with ui.card().classes("w-full h-[65vh] relative") as plotCard:
                    #fullscreen button 
                    ui.button(
                                    icon='fullscreen',
                                    on_click=lambda: ui.run_javascript(
                                            f'document.fullscreenElement ? document.exitFullscreen() : getElement({plotCard.id}).$el.requestFullscreen()'
                                        )
                                ).props('flat round').classes('absolute bottom-2 right-2 z-10') #orientation of the button
                    
                    # create container for specialist to draw in
                    self.plotContainer = ui.column().classes("w-full h-full")
                    # call function to draw plot (init)
                    self.update_plot_preview()
                    
                    
                    
            # section 3: vvt dropdown and table
            with ui.card().classes("w-full"):
                
                # create table container with label
                ui.label("VVT - Violations").classes('text-lg')
                self.tableContainer = ui.row().classes("w-full h-60 overflow-auto")
                
                # create dropdown to select vvt use on change event
                with ui.row().classes("w-full"):
                    
                    ui.label("Choose VVT to be checked")
                    vvtOptions = self.controller.load_vvt_options()
                    vvtOptions.insert(0,"None")
                    
                    ui.select(
                        vvtOptions,
                        value=vvtOptions[0],
                        label="Select VVT",
                        on_change=self.update_vvt_table
                        ).bind_value(self, "selectedVVT").classes("w-100")
                    
                    
            
            # section 4: Metadata and details
            with ui.card().classes("w-full"):
                ui.label("input Metadata to be saved to database").classes('text-lg')
            
                with ui.grid(columns=2).classes("w-full gap-3"):
                    ui.select(["1234", "2345", "3456", "4567"], value="1234", label="Select the oven-number").bind_value(self, "oven_Nr")
                    ui.select(["VW-ECO", "VOLVO-ERAD", "BASE", "PM6"], value="PM6", label="Select the product").bind_value(self, "product")
                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Load of the profile type").bind_value(self, "load")
                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Position of measurement cooler").bind_value(self, "pos")
                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Amount of coolers").bind_value(self, "count")
                    ui.radio(["Production", "Test"], value="Test").props("inline").bind_value(self, "prod_test")

                ui.separator()
                with ui.row().classes("w-full"):
                    ui.input("Nozzlefield", placeholder="Dreifachdüsenfeld").bind_value(self, "nozzlefield").classes("w-200")
                    ui.input("Profilename", placeholder="used profilename").bind_value(self, "profile_name").classes("w-200")
                    ui.input("Oven recipe", placeholder="oven recipe").bind_value(self, "oven_Recipe").classes("w-200")
                self._create_accordion()
                ui.textarea("Comment", placeholder="enter your comment..").bind_value(self, "comment").classes("w-full") 
                    
                    
                    
                # separator and buttons
                ui.separator().classes("my-4")
                
                with ui.row().classes("justify-end w-full"):
                    ui.button("Save", on_click=self.on_save_click)
                    ui.button("Discard", color="negative", on_click=self.on_discard_click)
                    
        self.update_plot_preview
        
    def update_plot_preview(self):
        """clears plot container and redraws with fresh plot"""
        self.plotContainer.clear()
        
        plotContent = self.controller.handle_plot_request_single(self.config,self.chosenZeropoint_show)
        
        if plotContent is not None:
            # with function enables the call of handle-method on the container object
            with self.plotContainer:
                ui.plotly(plotContent).classes("w-full h-full")

                
                
    def update_vvt_table(self):
        """clears the vvt table container and redraws the table with the violations for the selected vvt"""
        self.tableContainer.clear()
        
        with self.tableContainer:
            self.controller.handle_violation_table_update_request(self.selectedVVT, self.chosenZeropoint_show)
    
    
    def update_vvt_selection(self):
        self.update_plot_preview()
        self.update_vvt_table()
        
        
    def update_plot_config(self):
        self.chosenZeropoint_show = "none"
        self.update_plot_preview()
        self.update_vvt_table()
    

    def on_save_click(self) -> None:
        # fields that must have a value
        requiredFields = [
            "oven_Recipe",
            "oven_Nr",
            "product",
            "load",
            "pos",
            "count",
            "prod_test",
            "nozzlefield",
            "profile_name",
            "injection_1",
            "injection_2",
            "injection_3",
            "injection_4",
            "waiting_1",
            "waiting_2",
            "waiting_3",
            "waiting_4",
            "cooling_freq_1",
            "cooling_freq_2",
            "cooling_freq_3",
            "cooling_freq_4",
            "cooling_time_1",
            "cooling_time_2",
            "cooling_time_3",
            "cooling_time_4"
        ]
        
        for field in requiredFields:
            value = getattr(self, field)
            
            # cancel if field value is missing
            if not value:
                ui.notify(f"Please fill in the required field: {field}", color="negative")
                return
        
        
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
        
        saved_directly = self.controller.handle_save_request(metadata)
        
        if not saved_directly:
            self._show_duplicate_dialog()
      
    
    
    
    def _show_duplicate_dialog(self):
        """Zeichnet das Warn-Popup"""
        with ui.dialog() as dialog, ui.card():
            ui.label("A measurement with similar metadata (±1 hour) already exists.")
            ui.label("Do you really want to save it anyway?")
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button("Cancel", on_click=dialog.close).props('flat')
                ui.button("Yes, save it", on_click=lambda: [self.controller._save_measurement_to_database(), dialog.close()]).props('color=negative')
                
        dialog.open()
    
    

    def on_discard_click(self) -> None:
        self.controller.handle_popup("confirm", "Are you sure to discard and return to home?", self.pageName)

    def reset(self) -> None:
        self.oven_Nr = "1234"
        self.oven_Recipe = ""
        self.product = "PM6"
        self.load = "8"
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
        self.config = "standard"