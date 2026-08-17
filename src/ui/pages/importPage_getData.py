from typing import Optional # to allow None as a value for uploaded_content


from nicegui import ui
from nicegui.events import UploadEventArguments
from src.shared.upload_container import UploadContainer


from src.ui.pages.base_pages import SubPage


class ImportPage_getData(SubPage):
    pageName = "import-get"
    path: str = ""
    source: str = ""
    uploadWidget: ui.upload
    uploaded_file_name: str = ""
    uploaded_content: Optional[bytes] = None

    def build_content(self) -> None:
          
        with ui.column().classes("gap-4 w-96 mx-auto my-8 items-center"):
                ui.label("Please use the upload-button to upload the zip-file of your measurement:").classes("text-lg")
                ui.separator()
                ui.label("Please select your source of Data:")
                
                # create options and set the default
                sourceOptions = ["Rehm-recorder", "Solderstar (direct copy, withour Rehm-recorder)",  "Datapaq"]
                self.source = sourceOptions[0]
                
                ui.radio(
                    options=sourceOptions
                ).bind_value(self, "source")

                self.uploadWidget = ui.upload(
                    on_upload=self.on_upload, 
                    multiple=False,
                    auto_upload=True
                ).props("accept=.zip").classes("w-full")

                ui.separator()

                ui.button(
                    "Submit",
                    icon="check",
                    on_click=self.on_submit_click
                    ).classes("w-full")
        
    async def on_upload(self, e: UploadEventArguments) -> None:
        """handles the upload-event of the upload-widget, 
        saves the file name and content in the page-attributes.
        needs to be async because of the await for reading the file content"""
        self.uploaded_file_name = e.file.name
        self.uploaded_content = await e.file.read()
    
    def on_submit_click(self) -> None:
        
        if self.uploaded_content is None:
            ui.notify("Please upload a file before submitting.", color="negative")
            return
        
        
        uploadContainer = UploadContainer(self.uploaded_file_name, self.uploaded_content)
        
        # check if file was uploaded
        if isinstance(uploadContainer.content, bytes):
            self.controller.handle_data_import_request(uploadContainer, self.source)
            
            self.controller.handle_navigation_request("import-show")


    def reset(self) -> None:
        self.source = "Solderstar"
        self.uploaded_file_name = ""
        self.uploaded_content = b""