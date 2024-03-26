import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from dotenv import load_dotenv
import logging

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
load_dotenv()
staffsheet = os.getenv("STAFF")
datasheet = os.getenv("DATA")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
credential = Credentials.from_authorized_user_file("token.json", SCOPES)
logging.info("staffsheet: " + staffsheet)
logging.info("datasheet: " + datasheet)
logging.info("SPREADSHEET_ID: " + SPREADSHEET_ID)


def channelid(channel, name):
    credential = Credentials.from_authorized_user_file("token.json", SCOPES)

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        sheets.values().append(spreadsheetId=staffsheet, insertDataOption="INSERT_ROWS", range=f"3:3",
                               valueInputOption="USER_ENTERED", body={'values': [
                [name, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", id]]}).execute()
    except HttpError as error:
        print(error)


def copy(name):
    checkcred()
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
        print(error)


def findid(name, ids):
    checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        # if "<@" in ids:
        #    idd= ids[2:-1]
        # else:
        #    idd=ids
        # idd=ids
        # print(idd)üß
        print(type(ids))
        # value= sheets.values().get(spreadsheetId=staffsheet, range=f"T:T").execute()
        sheets.values().append(spreadsheetId=staffsheet, insertDataOption="INSERT_ROWS", range=f"3:3",
                               valueInputOption="USER_ENTERED", body={'values': [
                [name, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ids]]}).execute()
        # sheets.values().append(spreadsheetId=staffsheet, insertDataOption="INSERT_ROWS" , range=f"T13:T13", valueInputOption="USER_ENTERED", body={'values': [[ids]]}).execute()

    except HttpError as error:
        print(error)


def getuser(name):
    sheet = "STAFF"
    checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        value = sheets.values().get(spreadsheetId=staffsheet, range=f"V:V").execute()
        print(value)
        print(name)
        for i, row in enumerate(value['values'], start=1):
            if row and f"<@{row[0]}>" == f"{name}":
                name = i

        creditname = sheets.values().get(spreadsheetId=staffsheet, range=f"C{name}:C{name}").execute()
        print(creditname)
        return creditname["values"][0][0]
    except HttpError as error:
        print(error)


def getmessageid(id):
    name = None
    checkcred()
    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        value = sheets.values().get(spreadsheetId=datasheet, range=f"DATA!F:F").execute()
        # print(value)
        for i, row in enumerate(value['values'], start=1):
            if row and f"{row[0]}" == f"{id}":
                name = i
                print(i)
        if name is not None:
            data = sheets.values().get(spreadsheetId=datasheet, range=f"DATA!G{name}:K{name}").execute()
            print(data)
            return data["values"][0], name
    except HttpError as error:
        print(error)


def write(data, status):
    sheet2 = data[0]
    ch = data[1]
    chnew = None
    f = data[2]
    se = data[3]
    user = data[4]
    checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()

        value = sheets.values().get(spreadsheetId=datasheet, range=f"{sheet2}!A:A").execute()

        for i, row in enumerate(value['values'], start=0):
            if row and row[0] == ch:
                chnew = i
            if chnew is None:
                chnew = i+1
                sheets.values.append(spreadsheetId=datasheet, range=f"{sheet2}!{f}1:{se}1", insertDataOption="INSERT_ROWS",
                                valueInputOption="USER_ENTERED",
                                body={'values': [[]]}).execute()
        value = sheets.values().get(spreadsheetId=datasheet, range=f"{sheet2}!{f}{ch}:{se}{ch}").execute()
        sheets.values().update(spreadsheetId=datasheet, range=f"{sheet2}!{f}{ch}:{se}{ch}",
                               valueInputOption="USER_ENTERED", body={'values': [[getuser(user), status]]}).execute()
    except HttpError as error:
        logging.error(error)


def store(message_id, sheet, ch, user, f, se):
    checkcred()
    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()
        sheets.values().append(spreadsheetId=datasheet, range=f"DATA!F2:K2", insertDataOption="INSERT_ROWS",
                               valueInputOption="USER_ENTERED",
                               body={'values': [[str(message_id), sheet, ch, f, se, str(user)]]}).execute()
    except HttpError as error:
        logging.error(error)


def writechannel(channel_id, sheet):
    checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()

        sheets.values().append(spreadsheetId=datasheet, insertDataOption="INSERT_ROWS", range=f"CHANNELS!3:3",
                               valueInputOption="USER_ENTERED", body={'values': [[channel_id, sheet]]}).execute()
    except HttpError as error:
        print(error)


def updatesheet(channel_id, sheet):
    checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()

        value = sheets.values().get(spreadsheetId=datasheet, range=f"CHANNELS!A:A").execute()
        print(value)
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == f"{channel_id}":
                row = i

        sheets.values().update(spreadsheetId=datasheet, range=f"CHANNELS!{row}:{row}", valueInputOption="USER_ENTERED",
                               body={'values': [[channel_id, sheet]]}).execute()
    except HttpError as error:
        print(error)


def updatechannel_id(channel_id, sheet):
    checkcred()

    try:
        service = build("sheets", "v4", credentials=credential)
        sheets = service.spreadsheets()

        value = sheets.values().get(spreadsheetId=datasheet, range=f"CHANNELS!B:B").execute()
        print(value)
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == f"{sheet}":
                row = i

        sheets.values().update(spreadsheetId=datasheet, range=f"CHANNELS!{row}:{row}", valueInputOption="USER_ENTERED",
                               body={'values': [[channel_id, sheet]]}).execute()
    except HttpError as error:
        print(error)


def getsheetname(channel_id):
    checkcred()
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
        print(error)


def getchannelid(sheet):
    checkcred()
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
        print(error)


def delete_row(row_index):
    checkcred()
    service = build("sheets", "v4", credentials=credential)
    sheets = service.spreadsheets()
    sheets.values().update(spreadsheetId=datasheet, range=f"DATA!{row_index}:{row_index}",
                           valueInputOption="USER_ENTERED", body={'values': [
            ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]]}).execute()


def get_sheet_id_by_name(spreadsheet_id, sheet_name):
    service = build('sheets', 'v4', credentials=credential)
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in spreadsheet['sheets']:
        if sheet['properties']['title'] == sheet_name:
            print(sheet['properties']['sheetId'])


# get_sheet_id_by_name(datasheet, "DATA")

def checkcred():
    if os.path.exists("token.json"):
        credential = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not credential or not credential.valid:
        if credential and credential.expired and credential.refresh_token:
            credential.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credential = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(credential.to_json())



checkcred()