from src.ui.pages.base_pages import SubPage
from nicegui import ui


class PlotPage_showData(SubPage):
    pageName = "plot-show"
    config: str = "standard"
    chosenZeropoint_show: str = "none"

    def build_content(self) -> None:
        with ui.column().classes("w-full gap-4"):
            
            # section 1: plot area
            with ui.card().classes("w-full min-h-[500px]") as plotCard:

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
                
            # section 2: plot modification
            with ui.row().classes("items-center"):
                ui.label("Modify plots:")
                
                ui.select(
                    ["standard", "standard2", "3", "4", "5", "6", "7", "8"],
                    value="standard",
                    label="choose config for plot",
                    on_change = self.update_plot
                ).bind_value(self,"config").classes("w-100")
                
                ui.select(
                    options = ["none", "bulkhead", "first injection", "above 235", "ventilate 2"],
                    value = "none",
                    label = 'choose zeropoint for all plots',
                    on_change = self.update_plot
                ).bind_value(self,"chosenZeropoint_show").classes("w-100")
                
                
                
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