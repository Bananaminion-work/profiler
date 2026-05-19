from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ui.appcontroller import AppController

from abc import ABC, abstractmethod
from ipywidgets import Widget,Button,VBox,HBox,Label,Layout,Text,RadioButtons,FileUpload,Output,Dropdown,Textarea,Accordion,DatePicker,GridspecLayout

import time


class BasePage (ABC):
    
    _layout : Widget
    _eventHandlersRegistered: bool
    controller: AppController
    
    def __init__(self,controller: AppController):
        self.controller = controller
        self._layout = self.build_layout()
        self.create_event_handlers()
        
    @property
    def layout(self) -> Widget:
        
        #if self.layout is None:
        #    self._layout = self.build_layout()
        #    
        #if not self._eventHandlersRegistered:
        #    self.create_event_handlers()
        #    self._eventHandlersRegistered=True
        
        return self._layout
    
    
    @abstractmethod
    def build_layout(self) -> Widget:
        pass
    
    @abstractmethod
    def create_event_handlers(self):
        pass
    
    def reset(self):
        pass
     
     
     
class SubPage(BasePage):
    
    # Elements
    btn_home:Button
        
    def build_layout(self)-> Widget:
        
        self.btn_home = Button(
            description ="Home",
            icon = 'home',
            layout = Layout(width='100px')
        )
        
        # defines the action of the home button
        def go_home(btn):
            self.controller.handle_navigation_request('landing')
            
        # sets the on_click method go_home for the btn_home object
        self.btn_home.on_click(go_home)
        
        pageContent = self.build_content()
        
        subLayoutWithBtn = VBox(
            [HBox([self.btn_home]),
             pageContent
             ]
        )
        
        return subLayoutWithBtn
    
    @abstractmethod
    def build_content(self) -> Widget:
        pass
        
    @abstractmethod
    def reset(self):
        pass    
    
        
        
class LandingPage(BasePage):
    
    # Attributes
    pageName = 'landing'
    
    # Elements
    lab_buttons: Label
    btn_createData: Button
    btn_showData: Button

    # Functions
    def build_layout(self):
        
        #-----elements-----#
        
        self.lab_buttons = Label(
            "Choose your action:"
        )
        
        self.btn_createData = Button(
            description ="Create measurement-data",
            icon = 'upload',
            layout = Layout(width='300px')
        )
    
        self.btn_showData = Button(
            description = "Show measurements from database",
            icon = "line-chart",
            layout = Layout(width="300px")
        )
        
        #-----boxing-----# 
        
        buttonBox = VBox(
            [self.lab_buttons,self.btn_createData,self.btn_showData],
            layout=Layout(
                align_items='center',
                margin = '20px auto',
            )
        )
        
        #-----return-----#
        return buttonBox
    
    def create_event_handlers(self):
        
        def on_import_click(btn):
            self.controller.handle_navigation_request('import-get')
        self.btn_createData.on_click(on_import_click)
        
        def on_show_click(btn):
            self.controller.handle_navigation_request('plot-select')
        self.btn_showData.on_click(on_show_click)
        


class ImportPage_getData(SubPage):

    # Attributes
    pageName='import-get'
    
    # Elements
    input_path: Text
    radio_source: RadioButtons
    upload: FileUpload
    label_input: Label
    btn_submit: Button
    label_source: Label
    label_upload: Label
    
    def build_content(self)-> Widget:
        
        #-----elements-----#
        
        self.label_input = Label(value="Please enter the path of the ZIP-file:")
        
        self.input_path = Text(
            placeholder='dbms\\ path\\ to\\ file...',
            layout = Layout(width='400px')
            )
        
        self.btn_submit = Button(
            description ="Submit",
            button_style = 'success',
            icon = 'success',
            layout = Layout(width='75px')
            )
        
        self.label_source = Label(value="Please select your source of Data:")
        
        self.radio_source = RadioButtons(
            options=['Solderstar','Rehm-recorder','Datapaq'],
            description="Source of the measurement-file",
            disabled=False,
            value="Solderstar"
        )
        
        self.label_upload = Label("Enter file instead of path:")
        
        self.upload = FileUpload(
            accept='.zip',
            multiple=False,
            description='Upload'
            )
                      
        #-----boxing-----# 
        
        inputBox = VBox(
            [self.label_input,HBox([self.input_path, self.btn_submit])]
        )
        
        sourceBox = VBox(
            [self.label_source, self.radio_source]
        )
                
        uploadBox = HBox(
            [self.label_upload,self.upload]
        )
                
                
        finalLayout = VBox(
            [inputBox,sourceBox,uploadBox]
        )
        #-----return-----#
        
        return finalLayout
    
    
    
    def create_event_handlers(self):
        
        def on_submit_click(btn):
            
            self.controller.log("send path..")
            self.controller.log(f"chosen source is {self.radio_source.value}")
            self.controller.log("calls handle_data_import_request")
            self.controller.handle_data_import_request()
            time.sleep(2)
            self.controller.handle_navigation_request('import-show')
            self.input_path.value = ""
            
        # btn gets the onclick method: on_submit_click
        self.btn_submit.on_click(on_submit_click)
    
    
    
    def reset(self):
        self.input_path.value=""
        
        
        
class ImportPage_showData(SubPage):

    # Attributes
    pageName='import-show'
    accordionNames:list[Text]
    
    # Elements
    plotArea: Output
    drd_ovenNr: Dropdown
    drd_product: Dropdown
    drd_loadOfProfileType: Dropdown
    drd_posOfMeasurementCooler: Dropdown
    drd_coolerCountOnTray: Dropdown
    radio_productionOrTest: RadioButtons
    input_nozzlefield: Text
    accordion: Accordion
    input_profileName: Text
    input_comment: Textarea
    btn_save: Button
    btn_discard: Button
    drd_zeropointPlot: Dropdown
    drd_zeropoint_bulkhead: Dropdown
    drd_zeropoint_firstInjection: Dropdown
    drd_zeropoint_above_235: Dropdown
    drd_zeropoint_ventilate_2: Dropdown
    
    
    # helping function for widget-element
    def create_accordion(self)-> Accordion:
            
            def create_labeledTextfield(labelName:str):
                label = Label(value=labelName, layout=Layout(width='80px'))
                text_field = Text(placeholder='enter value...', layout=Layout(width='300px'))
                self.accordionNames.append(text_field)
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
    
    def useFormulaLayout(self,flag:bool)->Layout:
        if flag==True:
            return Layout(
                width='600px',
                height='40px',
                overflow='auto'
            )
        else:
            return Layout()
        
    def useShortLayout(self,flag:bool)->Layout:
        if flag==True:
            return Layout(
                width='300px',
                height='40px',
                overflow='auto'
            )
        else:
            return Layout()
        
    
    def build_content(self)-> Widget:
        

        #-----elements-----#
        self.plotArea_layout=Layout(
            min_width='400px',
            max_height='300px',
            border='1px solid grey'
        )
        self.plotArea = Output(layout=self.plotArea_layout)
        
        self.label_ovenNr = Label(
            value="Select the oven-number:",
            layout=self.useFormulaLayout(True)
        )
        
        self.drd_ovenNr = Dropdown(
            options=['1234','2345','3456','4567'],
            value='1234',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        self.label_product = Label(
            value="Select the product:",
            layout=self.useFormulaLayout(True)
        )
        
        self.drd_product = Dropdown(
            options=['VW-ECO','VOLVO-ERAD','BASE','PM6'],
            value='PM6',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        self.label_loadOfProfileType = Label(
            value="Select the load of the profile type:",
            layout=self.useFormulaLayout(True)
        )
        
        self.drd_loadOfProfileType = Dropdown(
            options=['1','2','3','4','5','6','7','8'],
            value='8',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        self.label_posOfMeasurementCooler = Label(
            value="Select the position of the measurement cooler:",
            layout=self.useFormulaLayout(True)
        )
        
        self.drd_posOfMeasurementCooler = Dropdown(
            options=['1','2','3','4','5','6','7','8'],
            value='8',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        self.label_coolerCountOnTray = Label(
            value="Select the amount of coolers\n in the process-chamber:",
            layout=self.useFormulaLayout(True)
        )
        
        self.drd_coolerCountOnTray = Dropdown(
            options=['1','2','3','4','5','6','7','8'],
            value='8',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        self.label_productionOrTest = Label(
            value="Select whether measurement\n was a test or in\n serial production:",
            layout=self.useFormulaLayout(True)
        )
        
        self.radio_productionOrTest = RadioButtons(
            options=['Serialproduction','Test'],
            value='Test',
            disabled=False,
            layout=Layout(width='200px')
        )
        
        self.label_nozzlefield = Label(
            value="Enter Name of the nozzlefield\n used for measurement:",
            layout=self.useFormulaLayout(True)
        )
        
        self.input_nozzlefield = Text(
            placeholder="Dreifachdüsenfeld"
        )
        
        self.accordionNames=[]
        self.accordion = self.create_accordion()
        
        self.label_profileName = Label(
            value="Enter the profilename:",
            layout=self.useFormulaLayout(True)
        )
        
        self.input_profileName = Text(
            placeholder="used profilename"
        )
        
        self.label_comment = Label(
            value="Enter your personal comment:",
            layout=self.useFormulaLayout(True)
        )
        
        self.input_comment = Textarea(
            placeholder="enter your comment.."
        )
        
        self.btn_save = Button(
            description ="Save",
            button_style = 'success',
            layout = Layout(width='75px')
        )
        
        self.btn_discard = Button(
            description ="Discard",
            button_style = 'danger',
            layout = Layout(width='75px')
        )
        
        ######### ZEROPOINT-ELEMENTS

        self.label_zeroPointPlot = Label(
            value="Choose zeropoint for plot:",
            layout=self.useShortLayout(True)
        )
        
        self.drd_zeropointPlot = Dropdown(
            # options muss vom appcontroler geholt werden, der bekommts von data
            options=['muss übergeben werden','2','3','4','5','6','7','8'],
            value='muss übergeben werden',
            disabled= False,
            layout=Layout(width='200px')
        )
        
        self.label_zeroPointDb = Label(
            value="Choose zeropoints for Database:",
            layout=self.useShortLayout(True)
        )
        
        self.label_zeropoint_bulkhead = Label(
            value='Bulhead closed-zeropoint',
            layout=self.useShortLayout(True)
        )
        
        self.drd_zeropoint_bulkhead = Dropdown(
            options=['muss übergeben werden','2','3','4','5','6','7','8'],
            value='muss übergeben werden',
            disabled= False,
            layout=Layout(width='200px')
        )
        
        self.label_zeropoint_firstInjection = Label(
            value='First injection-zeropoint',
            layout=self.useShortLayout(True)
        )
        
        self.drd_zeropoint_firstInjection = Dropdown(
            options=['muss übergeben werden','2','3','4','5','6','7','8'],
            value='muss übergeben werden',
            disabled= False,
            layout=Layout(width='200px')
        )
        
        self.label_zeropoint_above_235 = Label(
            value='Above 235-zeropoint',
            layout=self.useShortLayout(True)
        )
        
        self.drd_zeropoint_above_235 = Dropdown(
            options=['muss übergeben werden','2','3','4','5','6','7','8'],
            value='muss übergeben werden',
            disabled= False,
            layout=Layout(width='200px')
        )
        
        self.label_zeropoint_ventilate_2 = Label(
            value='Ventilate 2-zeropoint',
            layout=self.useShortLayout(True)
        )
        
        self.drd_zeropoint_ventilate_2 = Dropdown(
            options=['muss übergeben werden','2','3','4','5','6','7','8'],
            value='muss übergeben werden',
            disabled= False,
            layout=Layout(width='200px')
        )
        
        #-----boxing-----# 
        
        nozzleFieldBox = VBox([self.label_nozzlefield,self.input_nozzlefield])
        profileNameBox = VBox([self.label_profileName,self.input_profileName])
        commentBox = VBox([self.label_comment,self.input_comment])
        buttonBox = HBox([self.btn_save,self.btn_discard],layout=Layout(justify_content='flex-end'))
        
        drdBox = VBox([
            VBox([self.label_ovenNr,self.drd_ovenNr]),
            VBox([self.label_product,self.drd_product]),
            VBox([self.label_loadOfProfileType,self.drd_loadOfProfileType]),
            VBox([self.label_posOfMeasurementCooler ,self.drd_posOfMeasurementCooler]),
            VBox([self.label_coolerCountOnTray ,self.drd_coolerCountOnTray]),
            VBox([self.label_productionOrTest, self.radio_productionOrTest])
        ])
        
        metaBox = VBox([
            drdBox,nozzleFieldBox,profileNameBox,self.accordion,commentBox,buttonBox
        ])
        
        zeroV1 = VBox([self.label_zeroPointPlot,self.drd_zeropointPlot])
        zeroV2 = VBox([self.label_zeropoint_bulkhead,self.drd_zeropoint_bulkhead])
        zeroV3 = VBox([self.label_zeropoint_firstInjection,self.drd_zeropoint_firstInjection])
        zeroV4 = VBox([self.label_zeropoint_above_235,self.drd_zeropoint_above_235])
        zeroV5 = VBox([self.label_zeropoint_ventilate_2,self.drd_zeropoint_ventilate_2])
        
        zeroGrid = GridspecLayout(2,4)
        zeroGrid[0,0] = zeroV1
        zeroGrid[0,1] = self.label_zeroPointDb
        zeroGrid[1,0] = zeroV2
        zeroGrid[1,1] = zeroV3
        zeroGrid[1,2] = zeroV4
        zeroGrid[1,3] = zeroV5
        
        #-----return-----#
        return VBox([HBox([self.plotArea,metaBox]), zeroGrid])
    
    
    
    def create_event_handlers(self):
        
        def on_save_click(btn):
            self.controller.log("Data gets written to the database...")
            self.controller.log("this is to be implemented soon...")
            time.sleep(1.5)
            self.controller.handle_popup('warning','Data has been saved to the database','landing')
        self.btn_save.on_click(on_save_click)
        
        def on_discard_click(btn):
            self.controller.handle_popup('confirm','Are you sure to discard and return to home?',self.pageName)
        self.btn_discard.on_click(on_discard_click)
    
    
    
    def reset(self):
        """resets content of user input"""
        self.input_nozzlefield.value=""
        self.input_profileName.value=""
        for text_field in self.accordionNames:
            text_field.value=""
        self.input_comment.value=""
        
    
        

class PlotPage_selectData(SubPage):
    
    # Attributes
    pageName='plot-select'
    
    # Elements
    tableContainer: Output
    label_datePicker: Label
    datePicker: DatePicker
    label_ovenNr: Label
    drd_ovenNr: Dropdown
    label_product: Label
    input_product: Text
    label_nozzlefield: Label
    input_nozzlefield: Text
    label_profileName: Label
    input_profileName: Text
    btn_show: Button
    btn_discard: Button
    
    
    
    def useFormulaLayout(self,flag:bool):
        if flag==True:
            return Layout(
                width='300px',
                height='35px',
                #overflow='auto'
            )
        else:
            return Layout()

    def build_content(self)-> Widget:
        #-----elements-----#
        
        self.tableContainer_layout=Layout(
            max_width='400px',
            min_height='400px',
            border='1px solid grey'
        )
        self.tableContainer = Output(layout=self.tableContainer_layout)
        
        self.label_datePicker = Label(
            value="Pick the date:",
            layout=self.useFormulaLayout(True)
        )
        
        self.datePicker = DatePicker()
        
        self.label_ovenNr = Label(
            value="Select the oven-number:",
            layout=self.useFormulaLayout(True)
        )
        
        self.drd_ovenNr = Dropdown(
            options=['1234','2345','3456','4567'],
            value='1234',
            disabled= False,
            layout=Layout(width='75px')
        )
        
        self.label_product = Label(
            value="Enter the product name",
            layout=self.useFormulaLayout(True)
        )
        
        self.input_product = Text(
            placeholder="Product name:"
        )
        
        self.label_nozzlefield = Label(
            value="Nozzlefield:",
            layout=self.useFormulaLayout(True)
        )
        
        self.input_nozzlefield = Text(
            placeholder="Nozzlefield"
        )
        
        self.label_profileName = Label(
            value="Profilename:",
            layout=self.useFormulaLayout(True)
        )
        
        self.input_profileName = Text(
            placeholder="Profilename"
        )
        
        self.btn_show = Button(
            description ="Show selected",
            button_style = 'success',
            layout = Layout(width='75px')
        )
        
        self.btn_discard = Button(
            description ="Discard",
            button_style = 'danger',
            layout = Layout(width='75px')
        )
        
        #-----boxing-----# 
        
        filterBox = VBox([
            HBox([
                VBox([self.label_datePicker, self.datePicker]),
                VBox([self.label_ovenNr, self.drd_ovenNr]),
                VBox([self.label_product, self.input_product])
            ]),
            HBox([
                VBox([self.label_nozzlefield,self.input_nozzlefield]),
                VBox([self.label_profileName,self.input_profileName])
            ])
        ])
        
        btnBox= HBox([
            self.btn_show,self.btn_discard
        ],layout=Layout(justify_content='flex-end')
               )
        
        #-----return-----#
        
        return VBox([
            filterBox,self.tableContainer,btnBox
        ])
        
        
        
    def create_event_handlers(self):
        
        def on_show_click(btn):
            self.controller.handle_navigation_request('plot-show')
        self.btn_show.on_click(on_show_click)
        
        def on_discard_click(btn):
            self.controller.handle_popup('confirm','Are you sure to discard and return to home?',self.pageName)
        self.btn_discard.on_click(on_discard_click)
        
        
        
    def reset(self):
        self.input_nozzlefield.value=""
        self.input_product.value=""
        self.input_profileName.value=""
        self.datePicker.value=None
                
        

class PlotPage_showData(SubPage):
    
    # Attributes
    pageName='plot-show'
    
    # Elements
    plotArea: Output
    label_zeropoint: Label
    drd_zeropoint: Dropdown

    def build_content(self)-> Widget:
      
    
        #-----elements-----#
        
        self.plotArea = Output()
        self.plotArea.layout = Layout(
            min_width='1200px',
            max_with='1920px',
            min_height='500px',
            max_height='720px',
            border='1px solid grey'
        )
        
        self.label_zeropoint = Label(
            value='Choose zeropoint:',
            layout=Layout(
                width='400px',
                height='40px',
                overflow='auto'
            )
        )
        
        self.drd_zeropoint = Dropdown(
            options=['bulkhead','ventilate 2','first injection','above 235°C'],
            value='bulkhead',
            disabled= False,
            layout=Layout(width='400px')
        )
        
        #-----functions-----#
        
        
        
        #-----boxing-----# 
        
        zeroBox = HBox([
            self.label_zeropoint,self.drd_zeropoint
        ])
        
        #-----return-----#
        
        return VBox([self.plotArea,zeroBox])
    
    
    
    def create_event_handlers(self):
        pass
    
    
    
    def reset(self):
        pass
    
class Popup_confirm(BasePage):
    
    # Attributes
    label_message:Label
    returnPage:str
    
    # Elements
    label_message:Label
    btn_yes:Button
    btn_no:Button
    
    def build_layout(self) -> Widget:
        
        #-----elements-----#
        
        self.label_message=Label(
            layout=Layout(
                overflow_y='auto',
                border='1px solid grey',
                justify_content='center',
                align_items='center'
            )
        )
        
        self.btn_yes = Button(
            description ="YES",
            button_style = 'success',
            layout = Layout(width='200px')
        )
        
        self.btn_no = Button(
            description ="NO",
            button_style = 'danger',
            layout = Layout(width='200px')
        )
        
        #-----boxing-----#
        
        buttonBox = HBox([
            self.btn_yes,self.btn_no
        ],layout=Layout(
            justify_content='center',
            align_items='center'
        ))
        
        popupBox = VBox([self.label_message,buttonBox])
        
        outputBox = VBox(
            children=[popupBox],
            layout=Layout(
                justify_content='center',
                align_items='center'
            )
        )
        
        #-----return-----#
        
        return outputBox
    
    
    
    def create_event_handlers(self):

        def on_yes_click(btn):
            self.controller.handle_navigation_request('landing')
        self.btn_yes.on_click(on_yes_click)
        
        def on_no_click(btn):
            self.controller.handle_navigation_request(self.returnPage)
        self.btn_no.on_click(on_no_click)  
    
    
    
    def set_message(self,message:str):
        self.label_message.value = message
        
    def set_returnPage(self,pageName:str):
        self.returnPage = pageName
        
class Popup_warning(BasePage):
    
    # Attributes
    label_message:Label
    returnPage:str
    
    # Elements
    label_message:Label
    btn_ok:Button
    
    def build_layout(self) -> Widget:
        
        #-----elements-----#
        
        self.label_message=Label(
            layout=Layout(
                overflow_y='auto',
                border='1px solid grey',
                justify_content='center',
                align_items='center'
            )
        )
        
        self.btn_ok = Button(
            description ="OK",
            button_style = 'success',
            layout = Layout(width='200px')
        )
        
        #-----boxing-----#
        outputBox = VBox(
            children=[self.label_message,self.btn_ok],
            layout=Layout(
                justify_content='center',
                align_items='center'
            )
        )
        #-----return-----#
        
        return outputBox
    
    
    
    def create_event_handlers(self):
        def on_ok_click(btn):
            self.controller.handle_navigation_request(self.returnPage)
        self.btn_ok.on_click(on_ok_click)
    
    
    
    def set_message(self,message:str):
        self.label_message.value = message
    
    def set_returnPage(self,pageName:str):
        self.returnPage = pageName