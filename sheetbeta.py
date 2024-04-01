import asyncio
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from dotenv import load_dotenv
import logging
import math
import datetime
import gspread

# command
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
load_dotenv()
staffsheet = "Bourbon (Staff info)"
datasheet = "Bourbon (Work Progress Tracker)"
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
#credential = Credentials.from_authorized_user_file("token.json", SCOPES)
#credential = Credentials.from_service_account("token.json", SCOPES)
#client = gspread.authorize(credential)
client = gspread.service_account(filename='service_account.json')
logging.info("staffsheet: " + staffsheet)
logging.info("datasheet: " + datasheet)
logging.info("SPREADSHEET_ID: " + SPREADSHEET_ID)
#try:
#    service = build("sheets", "v4", credentials=credential)
#    sheets = service.spreadsheets()
#except:
#    logging.error("An error occurred: {error}")


async def copy(name):
    try:
        # Open the Google Sheets document
        spreadsheet = client.open(datasheet)
        # Get the worksheet you want to copy
        template_sheet = spreadsheet.worksheet('template')
        # Duplicate the worksheet
        new_sheet = spreadsheet.duplicate_sheet(template_sheet.id, new_sheet_name=name)
        # Append values to the new sheet
        new_sheet.update('A1', name)
    except gspread.exceptions.APIError as error:
        logging.error(error)


async def findid(name, ids):
    # Open the Google Sheets document and get the worksheet
    sheet = client.open(staffsheet).worksheet("STAFF")
    # Append a new row with the name and ids
    row_data= [name, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ids]
    sheet.append_row( [name], insert_data_option="INSERT_ROWS", table_range="A1:V22")


async def getuser(name):
    # Open the Google Sheets document and get the worksheet
    sheet = client.open(staffsheet).worksheet("STAFF")
    # Get all records in the sheet
    records = sheet.get_all_records()
    # Find the record with the matching name
    for i, record in enumerate(records, start=1):
        if record['V'] == name:
            # Return the corresponding credit name
            return record['C']
    # If no matching record is found, return None
    return None


async def getmessageid(id):
    name = None
    try:
        # Open the Google Sheets document and get the worksheet
        sheet = client.open(datasheet).worksheet("DATA")
        # Get all records in the sheet
        records = sheet.get_all_records()
        # Find the record with the matching id
        for i, record in enumerate(records, start=1):
            if record['F'] == id:
                name = i
        if name is not None:
            # Get the data in the range from column G to column K at the `name` row
            data = sheet.range(f"G{name}:K{name}")
            # Return the data and name
            return [cell.value for cell in data], name
    except gspread.exceptions.APIError as error:
        logging.error(error)


async def write(data, status):
    sheet_name = data[0]
    chapter = data[1]
    first = data[2]
    second = data[3]
    user = data[4]
    # Open the Google Sheets document and get the worksheet
    sheet = client.open(datasheet).worksheet(sheet_name)
    # Get all records in the sheet
    records = sheet.get_all_records()
    # Find the record with the matching chapter
    for i, record in enumerate(records, start=1):
        if record['A'] == chapter:
            # Update the corresponding user and status
            sheet.update_cell(i, ord(first.upper()) - 64, await getuser(user))
            sheet.update_cell(i, ord(second.upper()) - 64, status)
            break
    else:
        # If the chapter was not found, check the conditions
        prev_chapter = float(records[-1]['A']) if records else 0
        if math.ceil(prev_chapter) == math.floor(float(chapter)) or math.floor(prev_chapter) == math.floor(
                float(chapter)) or int(prev_chapter) + 1 == int(chapter):
            # Append a new row with the chapter, user, and status
            sheet.append_row([chapter, await getuser(user), status])


async def store(message_id, sheet, ch, user, f, se):  ##### stop changing role to f , se and then changing back #####
    # Open the Google Sheets document and get the worksheet
    data_sheet = client.open(datasheet).worksheet("DATA")
    # Append a new row with the message_id, sheet, ch, f, se, and user
    data_sheet.append_row([str(message_id), sheet, ch, f, se, str(user)])

########## WORKS ##########
async def writechannel(channel_id, sheet_name):
    # Open the Google Sheets document and get the worksheet
    sheet = client.open(datasheet).worksheet("CHANNELS")
    # Append a new row with the channel ID and sheet name
    sheet.append_row([channel_id, sheet_name])

########## WORKS ##########
async def updatesheet(channel_id, sheet_name):
    # Open the Google Sheets document and get the worksheet
    sheet = client.open(datasheet).worksheet("CHANNELS")
    # Get all records in the sheet
    records = sheet.get_all_records()
    # Find the record with the matching channel ID
    for i, record in enumerate(records, start=1):
        if record['channel id'] == channel_id:
            # Update the corresponding sheet name
            sheet.update_cell(i+1, 2, sheet_name)
            break

########## WORKS ##########
async def updatechannel_id(channel_id, sheet_name):
    # Open the Google Sheets document and get the worksheet
    sheet = client.open(datasheet).worksheet("CHANNELS")
    # Get all records in the sheet
    records = sheet.get_all_records()
    # Find the record with the matching sheet name
    for i, record in enumerate(records, start=1):
        if record['sheet name'] == sheet_name:
            # Update the corresponding channel ID
            sheet.update_cell(i+1, 1, channel_id)
            break


async def getsheetname(channel_id):
    # Open the Google Sheets document and get the worksheet
    sheet = client.open(datasheet).worksheet("CHANNELS")
    # Get all records in the sheet
    records = sheet.get_all_records()
    # Find the record with the matching channel ID
    for i, record in enumerate(records, start=1):
        if record['A'] == channel_id:
            # Return the corresponding sheet name
            return record['B']
    # If no matching record is found, return None
    return None


##### the reverse of the above function #####
async def getchannelid(sheet_name):
    print("getchannelid function called")
    # Open the Google Sheets document and get the worksheet
    sheet = client.open(datasheet).worksheet("CHANNELS")
    # Get all records in the sheet

    records = sheet.get_all_records()
    print(f"Number of records: {len(records)}")
    # Print the keys from the first record (which are the column names)
    if records:
        logging.info("Column names:", records[0].keys())
        print("Column names:", records[0].keys())
    else:
        logging.error("No records found")
    for i, record in enumerate(records, start=1):
        print(record)
        if record['B'] == sheet_name:
            # Return the corresponding channel ID
            return record['A']
    # If no matching record is found, return None
    return None


async def delete_row(row_index):
    # Open the Google Sheets document and get the worksheet
    sheet = client.open(datasheet).worksheet("DATA")
    # Delete the row
    sheet.delete_row(row_index)


async def get_sheet_id_by_name(spreadsheet_id, sheet_name):
    service = build('sheets', 'v4', credentials=credential)
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in spreadsheet['sheets']:
        if sheet['properties']['title'] == sheet_name:
            print(sheet['properties']['sheetId'])


# get_sheet_id_by_name(datasheet, "DATA")

#async def checkcred():
#    if os.path.exists("token.json"):
#        credential = Credentials.from_authorized_user_file("token.json", SCOPES)
#    if not credential or not credential.valid:
#        if credential and credential.expired and credential.refresh_token:
#            credential.refresh(Request())
#        else:
#            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
 #           credential = flow.run_local_server(port=0)
#            with open("token.json", "w") as token:
#                token.write(credential.to_json())

