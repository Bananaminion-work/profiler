from src.ui.pages.base_pages import SubPage
from nicegui import ui
from nicegui.events import UploadEventArguments

from src.shared.upload_container import UploadContainer


class BulkImportPage(SubPage):
    pageName = "bulkImportPage"
    
    def __init__(self, controller):
        super().__init__(controller)
        self.uploadedFiles: list[UploadContainer] = []
    
    def build_content(self)->None:
        
        ui.label("Bulk upload of measurement data").classes("text-2xl font-bold")
        
        with ui.card().classes("w-[50vh] items-center"):
            
            with ui.column().classes("gap-4 w-96 mx-auto my-8 items-center"):
                ui.label("Use the Upload-Button to upload all your ZIP-files:").classes("text-lg")
                ui.separator()
                
                self.uploadWidget = ui.upload(
                    on_upload=self.on_upload, 
                    multiple=True,
                    auto_upload=True
                ).props("accept=.zip").classes("w-full")
                
                ui.separator()
                
                self.filesCount = ui.label(f"Uploaded files: 0").classes("text-lg")
                
                ui.separator()
                
                ui.button(
                    "Submit",
                    icon="check",
                    on_click=self.on_submit_click
                    ).classes("w-full")
                
    async def on_upload(self, e: UploadEventArguments) -> None:
        """handles the upload of the files and stores them in the uploadedFiles list"""
        # gather data in UploadContainer
        container = UploadContainer(
            fileName=e.file.name,
            content=await e.file.read()
        )
        
        # append file to list
        self.uploadedFiles.append(container)
        
        # change text of amount of uploaded files
        self.filesCount.set_text(f"Uploaded files: {len(self.uploadedFiles)}")
        
        
    def on_submit_click(self) -> None:
        
        self.controller.handle_bulk_import_request(self.uploadedFiles)
        