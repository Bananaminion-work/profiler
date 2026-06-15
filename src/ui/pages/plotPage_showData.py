from src.ui.pages.base_pages import SubPage
from nicegui import ui


class PlotPage_showData(SubPage):
    pageName = "plot-show"
    config: str = "standard"
    chosenZeropoint_show: str = "none"

    def build_content(self) -> None:
        with ui.column().classes("w-full gap-4"):
            
            # section 1: plot modification options
            with ui.row().classes("items-center"):
                ui.label("Modify plots:")
                
                ui.select(
                    ["standard", "standard2", "3", "4", "5", "6", "7", "8"],
                    value="standard",
                    label="choose config for plot",
                    on_change = self.update_plot
                ).bind_value(self,"config").classes("w-100")
                
                
                
                # load options
                zeropointOptions = self.controller.load_zeropoint_options()
                # add "none" as option on the first postion
                if "none" not in zeropointOptions:
                    zeropointOptions.insert(0, "none")
                
                ui.select(
                    options=zeropointOptions,
                    value=zeropointOptions[0],
                    label="choose zeropoint for plot",
                    on_change=self.update_plot_and_vvt
                ).bind_value(self,"chosenZeropoint_show").classes("w-100")
            
            
            
            
            # section 2: plot area
            with ui.card().classes("w-full h-[65vh] relative") as plotCard:

                    # fullscreen button for plot area
                    ui.button(
                                    icon='fullscreen',
                                    on_click=lambda: ui.run_javascript(
                                            f'document.fullscreenElement ? document.exitFullscreen() : getElement({plotCard.id}).$el.requestFullscreen()'
                                        )
                                ).props('flat round').classes('absolute bottom-2 right-2 z-10') #orientation of the button
                    
                    # create container for specialist to draw in
                    self.plotContainer = ui.column().classes("w-full h-full")
                    # call function to draw plot (init)
                    self.update_plot()           
                
                
                
            # section 3: violation table
            with ui.card().classes("w-full"):
                
                # create dropdown to select vvt use on change event
                with ui.row().classes("w-full"):
                    
                    ui.label("Choose VVT and Measurement to be checked")
                    
                    # load options
                    vvtOptions = self.controller.load_vvt_options()
                    #set first option as value
                    self.selectedVVT = vvtOptions[0] if vvtOptions else ""
                    
                    measurements = self.controller.load_measurement_options()
                    self.selectedMeasurementId = measurements[0] if measurements else ""
                    
                    ui.select(
                        vvtOptions,
                        label="Select VVT",
                        on_change=self.update_vvt_table
                        ).bind_value(self, "selectedVVT").classes("w-100")
                    
                    
                    ui.select(
                        measurements,
                        label="Select Measurement",
                        on_change=self.update_vvt_table
                        ).bind_value(self, "selectedMeasurementId").classes("w-100"
                    )
                    
                # create table container with label
                ui.label("VVT - Violations").classes('text-lg')
                self.tableContainer = ui.row().classes("w-full h-60 overflow-auto")
                
                
        # init table and plot
        self.update_vvt_table()
        self.update_plot()
                
                
                
    def update_plot(self):
        """callback to let specialist draw the plot into the container"""
        
        if not hasattr(self, 'plotContainer'):
            return  # controller is not set yet, do nothing
        
        # clear container for fresh plot
        self.plotContainer.clear()
        
        # call controller to get plotcontent
        plotContent = self.controller.handle_plot_measurements_request(
                self.config,
                self.chosenZeropoint_show
            )
        
        # draw go.figure objekt in container
        if plotContent is not None:
            # with function enables the call of handle-method on the container object
            with self.plotContainer:
                ui.plotly(plotContent).classes("w-full h-full")
                
                
                
                
    def update_vvt_table(self):
        
        # check if table already exists
        if not hasattr(self, 'tableContainer'):
            return  # controller is not set yet, do nothing
        
        self.tableContainer.clear()
        
        # call controller on the container to get table content
        with self.tableContainer:
            self.controller.handle_violation_table_update_request_by_id(
                self.selectedVVT,
                self.chosenZeropoint_show,
                self.selectedMeasurementId
            )
                
                
                
    def update_plot_and_vvt(self):
        """calls the update functions for plot and vvt-table, to update both at the same time when zeropoint selection is changed"""
        self.update_plot()
        self.update_vvt_table()
                
                
                
    def reset(self):
        """resets the page to default state, e.g. after loading new data"""
        self.config = "standard"
        self.chosenZeropoint_show = "none"
        self.update_plot()