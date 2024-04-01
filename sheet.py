import os
from google.auth.transport.requests import Request
#from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from dotenv import load_dotenv
import logging
import math
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
#command
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

load_dotenv()
staffsheet = os.getenv("STAFF")
datasheet = os.getenv("DATA")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
#credential = Credentials.from_authorized_user_file("token.json", SCOPES)
credential = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
credential = service_account.Credentials.from_service_account_file(
        "service_account.json", scopes=SCOPES)
logging.info("staffsheet: " + staffsheet)
logging.info("datasheet: " + datasheet)
logging.info("SPREADSHEET_ID: " + SPREADSHEET_ID)


async def channelid(channel, name):

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        sheets.values().append(spreadsheetId=staffsheet, insertDataOption="INSERT_ROWS", range=f"3:3",
                               valueInputOption="USER_ENTERED", body={'values': [
                [name, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", id]]}).execute()
    except HttpError as error:
        logging.error(error)


async def copy(name):
    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()

        # Get the spreadsheet
        spreadsheet = sheets.get(spreadsheetId=datasheet).execute()

        # Get the worksheet you want to copy
        template_sheet = [s for s in spreadsheet['sheets'] if s['properties']['title'] == 'template'][0]

        # Duplicate the worksheet
        request = {
            'requests': [
                {
                    'duplicateSheet': {
                        'sourceSheetId': template_sheet['properties']['sheetId'],
                        'newSheetName': name,
                    }
                }
            ]
        }
        sheets.batchUpdate(spreadsheetId=datasheet, body=request).execute()

        # Append values to the new sheet
        sheets.values().update(spreadsheetId=datasheet, range=f"{name}!A1:A1", valueInputOption="USER_ENTERED",
                               body={'values': [[name]]}).execute()
        # sheets.values().append(
        #    spreadsheetId=datasheet,
        #    insertDataOption="INSERT_ROWS",
        #    range=f"3:3",
        #    valueInputOption="USER_ENTERED",
        #    body={'values': [[name, "","","","","","","","","","","","","","","","","", "","", "", ids]]}
        # ).execute()
    except HttpError as error:
        logging.error(error)


async def findid(name, ids):
    #await checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        # if "<@" in ids:
        #    idd= ids[2:-1]
        # else:
        #    idd=ids
        # idd=ids
        # value= sheets.values().get(spreadsheetId=staffsheet, range=f"T:T").execute()
        sheets.values().append(spreadsheetId=staffsheet, insertDataOption="INSERT_ROWS", range=f"3:3",
                               valueInputOption="USER_ENTERED", body={'values': [
                [name, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ids]]}).execute()
        # sheets.values().append(spreadsheetId=staffsheet, insertDataOption="INSERT_ROWS" , range=f"T13:T13", valueInputOption="USER_ENTERED", body={'values': [[ids]]}).execute()

    except HttpError as error:
        logging.error(error)


async def getuser(name):
    sheet = "STAFF"
    #await checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        value = sheets.values().get(spreadsheetId=staffsheet, range=f"V:V").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and f"<@{row[0]}>" == f"{name}":
                name = i

        creditname = sheets.values().get(spreadsheetId=staffsheet, range=f"C{name}:C{name}").execute()
        return creditname["values"][0][0]
    except HttpError as error:
        logging.error(error)


async def getmessageid(id):
    name = None
    #await checkcred()
    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        value = sheets.values().get(spreadsheetId=datasheet, range=f"DATA!F:F").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and f"{row[0]}" == f"{id}":
                name = i
        if name is not None:
            data = sheets.values().get(spreadsheetId=datasheet, range=f"DATA!G{name}:K{name}").execute()
            return data["values"][0], name
    except HttpError as error:
        logging.error(error)


async def write(data, status):
    sheet_name = data[0]
    chapter = data[1]
    chapter_index = None
    chapter_found = False
    first = data[2]
    second = data[3]
    user = data[4]
    #await checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        value = sheets.values().get(spreadsheetId=datasheet, range=f"{sheet_name}!A:A").execute()

        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == chapter:
                chapter_index = i
                chapter_found = True
        if not chapter_found:
            # Check if the previous chapter rounded equals the current chapter
            # and if the previous chapter plus one equals the current chapter
            prev_chapter = float(value['values'][len(value['values']) - 1][0]) if value['values'] else 0  # Ensure prev_chapter is an integer
            math.floor(prev_chapter)
            if math.ceil(float(prev_chapter)) ==  math.floor(float(chapter)) or math.floor(float(prev_chapter)) == math.floor(float(chapter)) or int(prev_chapter)+1 == int(chapter):
                chapter_index = len(value['values']) + 1
                sheets.values().append(spreadsheetId=datasheet, range=f"{sheet_name}!A{chapter_index}:A{chapter_index}",
                                       insertDataOption="INSERT_ROWS", valueInputOption="USER_ENTERED",
                                       body={'values': [[chapter]]}).execute()
        if chapter_index is not None:
            value = sheets.values().get(spreadsheetId=datasheet,
                                        range=f"{sheet_name}!{first}{chapter_index}:{second}{chapter_index}").execute()
            sheets.values().update(spreadsheetId=datasheet,
                                   range=f"{sheet_name}!{first}{chapter_index}:{second}{chapter_index}",
                                   valueInputOption="USER_ENTERED",
                                   body={'values': [[await getuser(user), status]]}).execute()



    except HttpError as error:
        logging.error(f"An error occurred: {error}")


async def store(message_id, sheet, ch, user, f, se):
    #await checkcred()
    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        sheets.values().append(spreadsheetId=datasheet, range=f"DATA!F2:K2", insertDataOption="INSERT_ROWS",
                               valueInputOption="USER_ENTERED",
                               body={'values': [[str(message_id), sheet, ch, f, se, str(user)]]}).execute()
    except HttpError as error:
        logging.error(error)


async def writechannel(channel_id, sheet):
    #await checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()

        sheets.values().append(spreadsheetId=datasheet, insertDataOption="INSERT_ROWS", range=f"CHANNELS!3:3",
                               valueInputOption="USER_ENTERED", body={'values': [[channel_id, sheet]]}).execute()
    except HttpError as error:
        logging.error(error)


async def updatesheet(channel_id, sheet):
    #await checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()

        value = sheets.values().get(spreadsheetId=datasheet, range=f"CHANNELS!A:A").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == f"{channel_id}":
                row = i

        sheets.values().update(spreadsheetId=datasheet, range=f"CHANNELS!{row}:{row}", valueInputOption="USER_ENTERED",
                               body={'values': [[channel_id, sheet]]}).execute()
    except HttpError as error:
        logging.error(error)


async def updatechannel_id(channel_id, sheet):
    #await checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()

        value = sheets.values().get(spreadsheetId=datasheet, range=f"CHANNELS!B:B").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == f"{sheet}":
                row = i

        sheets.values().update(spreadsheetId=datasheet, range=f"CHANNELS!{row}:{row}", valueInputOption="USER_ENTERED",
                               body={'values': [[channel_id, sheet]]}).execute()
    except HttpError as error:
        logging.error(error)


async def getsheetname(channel_id):
    #await checkcred()
    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        rowd = None
        value = sheets.values().get(spreadsheetId=datasheet, range=f"CHANNELS!A:A").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == channel_id:
                rowd = i
        name = sheets.values().get(spreadsheetId=datasheet, range=f"CHANNELS!B{rowd}:B{rowd}").execute()
        return name["values"][0][0]
    except HttpError as error:
        logging.error(error)


async def getchannelid(sheet):
    #await checkcred()
    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        rowd = None
        value = sheets.values().get(spreadsheetId=datasheet, range=f"CHANNELS!B:B").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == sheet:
                rowd = i
        name = sheets.values().get(spreadsheetId=datasheet, range=f"CHANNELS!A{rowd}:A{rowd}").execute()
        return name["values"][0][0]
    except HttpError as error:
        logging.error(error)


async def delete_row(row_index):
    #await checkcred()
    service = build("sheets", "v4", credentials=credential)
    sheets = service.spreadsheets()
    sheets.values().update(spreadsheetId=datasheet, range=f"DATA!{row_index}:{row_index}",
                           valueInputOption="USER_ENTERED", body={'values': [
            ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]]}).execute()


async def get_sheet_id_by_name(spreadsheet_id, sheet_name):
    service = build('sheets', 'v4', credentials=credential)
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in spreadsheet['sheets']:
        if sheet['properties']['title'] == sheet_name:
            print(sheet['properties']['sheetId'])


# get_sheet_id_by_name(datasheet, "DATA")

