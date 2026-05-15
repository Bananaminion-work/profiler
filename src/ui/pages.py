from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ui.appcontroller import AppController

from abc import ABC, abstractmethod
from ipywidgets import Widget,Button,VBox,HBox,Label,Layout,Text,RadioButtons,FileUpload,Output,Dropdown,Textarea,Accordion

import time


class BasePage (ABC):
    _layout : Widget
    controller: AppController
    
    def __init__(self,controller: AppController):
        self.controller = controller
        self._layout = self.build_layout()
        
    @property
    def layout(self) -> Widget:
        return self._layout
    
    
    @abstractmethod
    def build_layout(self) -> Widget:
        pass
     
     
     
class SubPage(BasePage):
        
    def build_layout(self)-> Widget:
        
        pageContent = self.build_content()
        
        btn_home = Button(
            description ="Home",
            icon = 'home',
            layout = Layout(width='100px')
        )
        
        # defines the action of the home button
        def go_home(btn):
            self.controller.handle_navigation_request('landing')
            
        # sets the on_click method go_home for the btn_home object
        btn_home.on_click(go_home)
        
        subLayoutWithBtn = VBox(
            [HBox([btn_home]),
             pageContent
             ]
        )
        
        return subLayoutWithBtn
    
    @abstractmethod
    def build_content(self) -> Widget:
        pass
        
        
        
class LandingPage(BasePage):

    def build_layout(self):
        
        #-----elements-----#
        
        lab_buttons = Label(
            "Choose your action:"
        )
        
        btn_createData = Button(
            description ="Create measurement-data",
            icon = 'upload',
            layout = Layout(width='300px')
        )
    
        btn_showData = Button(
            description = "Show measurements from database",
            icon = "line-chart",
            layout = Layout(width="300px")
        )
        
        
        #-----functions-----#
        
        def on_button_click(btn):
            self.controller.handle_navigation_request('import-get')
        btn_createData.on_click(on_button_click)
        
        #-----boxing-----# 
        
        buttonBox = VBox(
            [lab_buttons,btn_createData,btn_showData],
            layout=Layout(
                align_items='center',
                margin = '20px auto'
            )
        )
        
        #-----return-----#
        return buttonBox
        


class ImportPage_getData(SubPage):

    def build_content(self)-> Widget:
        
        #-----elements-----#
        
        label_input = Label(value="Please enter the path of the ZIP-file:")
        
        input_path = Text(
            placeholder='dbms\\ path\\ to\\ file...',
            layout = Layout(width='400px')
            )
        
        btn_submit = Button(
            description ="Submit",
            button_style = 'success',
            icon = 'success',
            layout = Layout(width='75px')
            )
        
        label_source = Label(value="Please select your source of Data:")
        
        radio_source = RadioButtons(
            options=['Solderstar','Rehm-recorder','Datapaq'],
            description="Source of the measurement-file",
            disabled=False,
            value="Solderstar"
        )
        
        label_upload = Label("Enter file instead of path:")
        
        upload = FileUpload(
            accept='.zip',
            multiple=False,
            description='Upload'
            )
        
        #-----functions-----#
        def on_submit_click(btn):
            
            self.controller.log("send path..")
            self.controller.log(f"chosen source is {radio_source.value}")
            self.controller.log("calls handle_data_import_request")
            self.controller.handle_data_import_request()
            time.sleep(2)
            self.controller.handle_navigation_request('import-show')
            input_path.value = ""
            
        # btn gets the onclick method: on_submit_click
        btn_submit.on_click(on_submit_click)
        
        
        #-----boxing-----# 
        
        inputBox = VBox(
            [label_input,HBox([input_path, btn_submit])]
        )
        
        sourceBox = VBox(
            [label_source, radio_source]
        )
                
        uploadBox = HBox(
            [label_upload,upload]
        )
                
                
        finalLayout = VBox(
            [inputBox,sourceBox,uploadBox]
        )
        #-----return-----#
        
        return finalLayout
        
        
        
class ImportPage_showData(SubPage):
    
    plotArea : Output
    
    # helping function for widget-element
    def create_accordion(self)-> Accordion:
            
            def create_labeledTextfield(label:str):
                label = Label(value=label, layout=Layout(width='80px'))
                text_field = Text(placeholder='enter value...', layout=Layout(width='300px'))
                return HBox([label, text_field])
            
            pane_injectionAmount = VBox([
                create_labeledTextfield("Injection 1:"),
                create_labeledTextfield("Injection 2:"),
                create_labeledTextfield("Injection 3:"),
                create_labeledTextfield("Injection 4:")
            ])
            
            pane_waitingTime = VBox([
                create_labeledTextfield("Waiting-time 1:"),
                create_labeledTextfield("Waiting-time 2:"),
                create_labeledTextfield("Waiting-time 3:"),
                create_labeledTextfield("Waiting-time 4:")
            ])
            
            pane_coolingFrequency = VBox([
                create_labeledTextfield("Cooling-frequency 1:"),
                create_labeledTextfield("Cooling-frequency 2:"),
                create_labeledTextfield("Cooling-frequency 3:"),
                create_labeledTextfield("Cooling-frequency 4:")
            ])
            
            pane_coolingTime = VBox([
                create_labeledTextfield("Cooling-time 1:"),
                create_labeledTextfield("Cooling-time 2:"),
                create_labeledTextfield("Cooling-time 3:"),
                create_labeledTextfield("Cooling-time 4:")
            ])
            
            accordion = Accordion([
                pane_injectionAmount,
                pane_waitingTime,
                pane_coolingFrequency,
                pane_coolingTime
            ])
            
            accordion.set_title(0,"Injections")
            accordion.set_title(1,"Waiting-time")
            accordion.set_title(2,"Cooling-frequency")
            accordion.set_title(3,"Cooling-time")
            
            return accordion
    
    
    def build_content(self)-> Widget:
        

        #-----elements-----#
        self.plotArea = Output(
            hight='400px',
            width='50%'
        )
        
        label_ovenNr = Label(
            value="Select the oven-number:",
            layout=Layout(width='250px')
        )
        
        drd_ovenNr = Dropdown(
            options=['1234','2345','3456','4567'],
            value='1234',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        label_product = Label(
            value="Select the product:",
            layout=Layout(width='250px')
        )
        
        drd_product = Dropdown(
            options=['VW-ECO','VOLVO-ERAD','BASE','PM6'],
            value='PM6',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        label_loadOfProfileType = Label(
            value="Select the load of the profile type:",
            layout=Layout(width='400px')
        )
        
        drd_loadOfProfileType = Dropdown(
            options=['1','2','3','4','5','6','7','8'],
            value='8',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        label_posOfMeasurementCooler = Label(
            value="Select the position of the measurement cooler:",
            layout=Layout(width='400px')
        )
        
        drd_posOfMeasurementCooler = Dropdown(
            options=['1','2','3','4','5','6','7','8'],
            value='8',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        label_coolerCountOnTray = Label(
            value="Select the amount of coolers\n in the process-chamber:",
            layout=Layout(width='400px')
        )
        
        drd_coolerCountOnTray = Dropdown(
            options=['1','2','3','4','5','6','7','8'],
            value='8',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        label_productionOrTest = Label(
            value="Select whether measurement\n was a test or in\n serial production:",
            layout=Layout(width='400px')
        )
        
        radio_productionOrTest = RadioButtons(
            options=['Serialproduction','Test'],
            value='Test',
            disabled=False,
            layout=Layout(width='75px')
        )
        
        label_nozzlefield = Label(
            value="Enter Name of the nozzlefield\n used for measurement:",
            layout=Layout(width='400px')
        )
        
        input_nozzlefield = Text(
            placeholder="Dreifachdüsenfeld"
        )
        
        accordion = self.create_accordion()
        
        label_profileName = Label(
            value="Enter the profilename:",
            layout=Layout(width='400px')
        )
        
        input_profileName = Text(
            placeholder="used profilename"
        )
        
        label_comment = Label(
            value="Enter your personal comment:",
            layout=Layout(width='400px')
        )
        
        input_comment = Textarea(
            placeholder="enter your comment.."
        )
        
        btn_save = Button(
            description ="Save",
            button_style = 'success',
            layout = Layout(width='75px')
        )
        
        btn_discard = Button(
            description ="Discard",
            button_style = 'danger',
            layout = Layout(width='75px')
        )

        
        #-----functions-----#
        
        
        
        #-----boxing-----# 
        
        nozzleFieldBox = HBox([label_nozzlefield,input_nozzlefield])
        profileNameBox = HBox([label_profileName,input_profileName])
        commentBox = HBox([label_comment,input_comment])
        buttonBox = HBox([btn_save,btn_discard],layout=Layout(justify_content='flex-end'))
        drdBox = VBox([
            HBox([label_ovenNr,drd_ovenNr]),
            HBox([label_product,drd_product]),
            HBox([label_loadOfProfileType,drd_loadOfProfileType]),
            HBox([label_posOfMeasurementCooler ,drd_posOfMeasurementCooler]),
            HBox([label_coolerCountOnTray ,drd_coolerCountOnTray]),
            HBox([label_productionOrTest, radio_productionOrTest])
        ])
        
        metaBox = VBox([
            drdBox,nozzleFieldBox,profileNameBox,accordion,commentBox,buttonBox
        ],layout=Layout(width='50%')
                       )       
        
        #-----return-----#
        return HBox([self.plotArea,metaBox])
        
    
        

class PlotPage_selectData(SubPage):

    def build_content(self)-> Widget:
        # THIS IS A PLACEHOLDER
        return Widget()
        #-----elements-----#
        
        
        
        #-----functions-----#
        
        
        
        #-----boxing-----# 
        
        
        
        #-----return-----#
    
                
        

class PlotPage_showData(SubPage):

    def build_content(self)-> Widget:
        # THIS IS A PLACEHOLDER
        return Widget()
        #-----elements-----#
        
        
        
        #-----functions-----#
        
        
        
        #-----boxing-----# 
        
        
        
        #-----return-----#
    