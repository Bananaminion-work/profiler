from __future__ import annotations
from src.shared.data_models import BronzeData, Data
import pandas as pd
from pandas import DataFrame
from src.shared.upload_container import UploadContainer
from zipfile import ZipFile,is_zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from src.shared.exceptions import NoDataToWorkWithError, WrongInputError,SourceNotProvidedError


class BronzeCreator():
    
    upload : UploadContainer
    xmlContent: bytes | None = None
    csvContent: bytes | None = None
    bronzeObject : BronzeData
    
    xml_dict: dict[str,str] = {}
    csvData: DataFrame
    
    def create_bronze_object(self,uploadContainer: UploadContainer, source:str)->Data:
        
        # if else check for source is made here
        if source == "Rehm-recorder":
            self.extract_zip(uploadContainer) #get zip
            self.parse_xml() # read xml
            self.parse_csv() # read csv
            self.change_id_to_names() # create final dataframe
            self.csvData.set_index('ReadTime', inplace=True)
            
            #build Object
            self.bronzeObject = BronzeData(self.csvData)
            
        else:
            raise SourceNotProvidedError(f"The provided source '{source}' is not supported yet!")

        return self.bronzeObject
    
    
    
    def extract_zip(self,upload : UploadContainer):
        self.upload = upload
        
        zipBuffer = BytesIO(self.upload.content)
        
        if not is_zipfile(zipBuffer):
            raise WrongInputError("The uploaded file is not a valid zip file.")
        zipBuffer.seek(0)  # Reset buffer position to the beginning after checking

        with ZipFile(zipBuffer) as zipFile:
            for fileName in zipFile.namelist():
                
                if fileName.endswith('.xml'):
                    self.xmlContent = zipFile.read(fileName)
                    
                elif fileName.endswith('.csv'):
                    self.csvContent = zipFile.read(fileName)
    
    
    
    def parse_xml(self):
        
        # if no content to work with, raise error
        if self.xmlContent is None:
            raise NoDataToWorkWithError("No XML content found in the uploaded zip file.")
        
        else:
            #get selected datapoints from xml
            selectedDataPoints = ET.fromstring(self.xmlContent).find('SelectedDataPoints')
            
            #check if selectedDataPoints is None, if yes raise error, else continue
            if selectedDataPoints is None:
                raise NoDataToWorkWithError("No SelectedDataPoints found in the XML content.")
            
            else:
                # iterate through selectedDataPoints and save id-name-pairs in a dictionary
                for dataPoint in selectedDataPoints.findall('DataPointConfiguration'):
                    
                    element_id      = dataPoint.find('Id')
                    element_name    = dataPoint.find('Name')
                    
                    # check if both elements were found
                    if element_id is not None and element_name is not None:
                        text_id     = element_id.text
                        text_name   = element_name.text
                        
                        if text_id is not None and text_name is not None:
                            self.xml_dict[text_id] = text_name
                        
                        else:
                            raise NoDataToWorkWithError("Id and/or Name tag in the XML content does not contain text.")
                        
                    else:
                        raise NoDataToWorkWithError("Id and/or Name tag not found in the XML content.")
    
    
    
    
    def parse_csv(self):
        
        if self.csvContent is None:
            raise NoDataToWorkWithError("No CSV content found in the uploaded zip file.")
        else:
            csvBuffer = BytesIO(self.csvContent)
            csvBuffer.seek(0)  # Ensure buffer is at the beginning before reading
            
            try:
                self.csvData = pd.read_csv(csvBuffer,delimiter=';', encoding='utf-8')
                
            except Exception as e:
                raise WrongInputError(f"An error occurred while parsing the CSV content: {e}")
            
            
            
            
    def change_id_to_names(self):
        """replaces the arbitrary ids to talking names of xml"""
        self.csvData = self.csvData.rename(columns=self.xml_dict)