import os
from apiclient import discovery
from apiclient.http import MediaFileUpload
import datetime
from google.oauth2 import service_account


def uploadFile(filename, filepath, mimetype, folder_id):
    """
        uploads a file to a google drive
        parameters: -filename (string): what you want the file to be named
                    -filepath (string): where the file is in the current directory
                    -mimetype (string): the metadata type of the file (pdf, csv, xlsx)
                    -folder_id (string): the folder that the file will be put in
    """
    file_metadata = {'name': filename,
                     'parents':[folder_id]}
    media = MediaFileUpload(filepath, mimetype=mimetype)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    
def createFolder(name,parents):
    """
        creates a folder in a google drive
        parameters: -name: a string name that the folder will inherit
                    -parents: a string id of the folder above this one. if none, folder will
                              be created in 'my drive'
        returns: String, the id of the google folder.
    """
    if parents:
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parents]}
        file = drive_service.files().create(body = file_metadata,
                                            fields = 'id').execute()
    else:
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            }
        file = drive_service.files().create(body = file_metadata,
                                            fields = 'id').execute()
    folder_id = file.get('id')
    return folder_id

def search(query):
    """
        searches a google drive for a specific file
        parameters: -query: a string that specifies search criteria
        returns: List of items that match for the query string
    """
    results = drive_service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)",q = query).execute()
    items = results.get('files', [])

    return items



def updateFile(fileName,fileId):
    """
        overwrites a file in a google drive
        parameters: -filename (string): name of the file
                    -file_id (string): id of the file
                    
    """
    file_metadata = {'name': fileName,
                     'mimetype':'application/octet-stream'}
    media_body = MediaFileUpload(fileName,mimetype = 'application/octet-stream')
    result = drive_service.files().update(body=file_metadata,
                                          fileId = fileId,
                                          media_body=media_body).execute()

def executePush():
    """
        Method that executes the upload of a qvw file to a google drive. Uses a Json file generated from a service account
        to send an authentication request to the same google service account. If a file with the same name is already present
        in the google drive, the program will overwrite the existing google file. Be sure to share the highest folder in the
        hierarchy with the service account name so that the queries will work correctly.
        
        When using this script in a new folder...
            1. change the fileName variable
            2. change the UPLOAD_FOLDER variable
    """
        
    QAfolder = search("name = 'QA'")
    id_QA = QAfolder[0].get('id')
    ProdFolder = search("name = 'PROD'")
    id_Prod = ProdFolder[0].get('id')

    
    ### ENTER THE NAME OF THE QVW FILE WITH FILE EXTENSION
    fileName = '.qvw'

    ### ENTER 'id_QA' if uploading to QA. ENTER 'id_Prod' if uploading to Prod.
    UPLOAD_FOLDER = id_QA
    ###
    
    mimetype = 'application/octet-stream'
    files = search("name contains "+"'"+fileName+"'"+ " and "+"'"+UPLOAD_FOLDER+"'"+" in parents")
    
    if len(files) > 0:
        id_ = files[0].get('id')
        updateFile(fileName,id_)
    else:
        uploadFile(fileName,fileName,mimetype,UPLOAD_FOLDER)

"""
Place the secret file in one secure directory. This way, we change directory to grab it from python executions instead of
copying the file all over a drive.
"""

os.chdir("path_to_your_secret_file")
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account_file.json'
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = discovery.build('drive', 'v3', credentials = credentials)

# change back to the cwd to upload/update the qvw file
os.chdir(os.path.dirname(os.path.realpath(__file__)))

executePush()
