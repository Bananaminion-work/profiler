from src.shared.bulk_import_information import BulkImportInformation
from src.shared.upload_container import UploadContainer
from io import BytesIO
from zipfile import ZipFile
from pandas import DataFrame
import pandas as pd

class BulkImportReader():
    
    imported_information: list[BulkImportInformation] = []
    
    tempInformation = BulkImportInformation()
    
    def read_input_files(self, content: list[UploadContainer]):
        """reads the input files from the upload container and returns a DataFrame with the data
        
        returns a list of BulkImportInformation objects with the information of the imported measurements"""
        
        self.content = content
        
        # iterate through the list of UploadContainers and unpack the zip files
        for upload in self.content:
            
            zipBuffer = BytesIO(upload.content)
            with ZipFile(zipBuffer) as zip_file:
                
                # create empty BulkImportInformation object to store the information of the current file
                self.tempInformation = BulkImportInformation()
                # save the filename of the current file
                self.tempInformation.filename = upload.fileName
                
                # read all filenames in the zip
                for fileName in zip_file.namelist():

                    # save content of xml
                    if fileName.endswith('.xml'):
                        self.xmlContent = zip_file.read(fileName)
                        self.extract_xml_information()
                        
                    # save content of csv
                    elif fileName.endswith('.csv'):
                        self.csvContent = zip_file.read(fileName)
                        self.extract_csv_information()
                            

                    
                self.imported_information.append(self.tempInformation)
                    
        return self.imported_information
    
    
    
    def extract_xml_information(self):
        """reads descripton and configname from the xml content and saves it in the BulkImportInformation object"""

        if self.xmlContent is None:
            raise ValueError("No XML content found in the uploaded zip file.")
        
        else:
            # parse the xml content
            import xml.etree.ElementTree as ET
            root = ET.fromstring(self.xmlContent)
            
            # extract description and configname from the xml
            description_element = root.find('Description')
            config_name_element = root.find('ConfigName')
            
            if description_element is not None:
                self.tempInformation.description = description_element.text #type:ignore
            else:
                self.tempInformation.description = ""
                
            if config_name_element is not None:
                self.tempInformation.config_name = config_name_element.text #type:ignore
            else:
                self.tempInformation.config_name = ""
    
    
    def extract_csv_information(self):
        """reads the first entry of ReadTime, saves it as date and starttime in the BulkImportInformation object"""
        
        if self.csvContent is None:
            raise ValueError("No CSV content found in the uploaded zip file.")
        
        else:
            # read the csv content into a DataFrame
            df = DataFrame(pd.read_csv(BytesIO(self.csvContent)))
            
            # check if 'ReadTime' column exists
            if 'ReadTime' in df.columns:
                first_read_time = df['ReadTime'].iloc[0]
                
                # cast as a datetime object
                first_read_time = pd.to_datetime(first_read_time)
                
                # save as date and starttime
                self.tempInformation.date = first_read_time.strftime("%Y-%m-%d")
                self.tempInformation.starttime = first_read_time.strftime("%H:%M:%S")