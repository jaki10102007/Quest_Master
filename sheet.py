import os
import logging
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from dotenv import load_dotenv
import math
from google.oauth2 import service_account
from config import role_dict_reaction
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
load_dotenv()
staffsheet = os.getenv("STAFF") # Where staff info is tracked
progresssheet = os.getenv("DATA") # Progess tracker
ID= os.getenv("ID") # Used for deleting rows
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
credential = service_account.Credentials.from_service_account_file(
    "service_account.json", scopes=SCOPES)
service = build("sheets", "v4", credentials=credential)
sheets = service.spreadsheets()

async def retriev_assignments(user):
    """
        This function retrieves assignments for a specific user from a Google Sheets spreadsheet.

        It first fetches all values in column K of the DATA sheet, where user assignments are stored in the format "<@user_id>".
        It then iterates over these values, and for each row where the value matches the provided user ID, it appends the row index to a list.
        For each row index in this list, it creates a range string representing columns F to K of that row in the DATA sheet.
        If there are any ranges to request, it performs a batchGet request to fetch these ranges from the spreadsheet.
        The values from each fetched range are then appended to a list, which is returned.

        If an HttpError occurs during any of these operations, it is caught and logged, and the function returns None.

        Args:
            user (str): The ID of the user to retrieve assignments for.

        Returns:
            list: A list of lists, where each inner list represents the values in columns F to K of a row in the DATA sheet where the user ID in column K matches the provided user ID. If an error occurs, returns None.
        """
    try:
        matching_row = []
        value = sheets.values().get(spreadsheetId=progresssheet, range=f"DATA!K:K").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and f"{row[0]}" == f"<@{user}>":
                matching_row.append(i)
        ranges = [f"DATA!F{rowd}:L{rowd}" for rowd in matching_row]  # Create a list of ranges
        data = []
        if ranges:  # Check if there are any ranges to request
            batch_request = sheets.values().batchGet(spreadsheetId=progresssheet, ranges=ranges).execute()
            for response in batch_request['valueRanges']:
                data.append(response['values'])
        logging.info(f"data is {data}")
        return data
    except HttpError as error:
        logging.error(error)

async def copy(name):
    '''This will copy the template sheet and append the name to the new sheet'''
    try:

        # Get the spreadsheet
        spreadsheet = sheets.get(spreadsheetId=progresssheet).execute()

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
        sheets.batchUpdate(spreadsheetId=progresssheet, body=request).execute()

        # Append values to the new sheet
        sheets.values().update(spreadsheetId=progresssheet, range=f"{name}!A1:A1", valueInputOption="USER_ENTERED",
                               body={'values': [[name]]}).execute()
    except HttpError as error:
        logging.error(error)


async def findid(name, ids):
    """
        This function adds a Discord user's name and ID to the staff sheet in Google Sheets.

        Args:
            name (str): The Discord username.
            ids (str): The Discord user's ID.

        Raises:
            HttpError: If an error occurs while trying to append the values to the Google Sheets spreadsheet. The error is logged using the `logging` module.
    """
    try:
        sheets.values().append(spreadsheetId=staffsheet, insertDataOption="INSERT_ROWS", range=f"3:3",
                               valueInputOption="USER_ENTERED", body={'values': [
                [name, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ids]]}).execute()

    except HttpError as error:
        logging.error(error)


async def getuser(name):
    try:
        value = sheets.values().get(spreadsheetId=staffsheet, range=f"V:V").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and f"<@{row[0]}>" == f"{name}":
                name = i

        creditname = sheets.values().get(spreadsheetId=staffsheet, range=f"C{name}:C{name}").execute()
        return creditname["values"][0][0]
    except HttpError as error:
        logging.error(error)


async def check_old_entries(bot):
    result = sheets.values().get(spreadsheetId=progresssheet, range="DATA!L:L").execute()
    result2 = sheets.values().get(spreadsheetId=progresssheet, range="DATA!M:M").execute()
    values = result.get('values', [])
    values2 = result2.get('values', [])
    # Get the current date and time
    now = datetime.now()
    channel_id = 1224453260543266907  # Replace with your channel ID
    channel = bot.get_channel(channel_id)
    # Loop through the values
    for i, value in enumerate(values, start=1):
        if value:
            try:
                # Parse the date and time from the value
                date_time = datetime.strptime(value[0], "%Y-%m-%d")
                date_only = date_time.strftime("%Y-%m-%d")
                # Check if the date and time is older than 5 days
                if now - date_time > timedelta(days=4):
                    if values2[i - 1] and values2[i - 1][0] is not None:
                        pass
                    else:
                        data = sheets.values().get(spreadsheetId=progresssheet, range=f"DATA!F{i}:K{i}").execute()
                        series = data["values"][0][1]
                        chapter = data["values"][0][2]
                        user = data["values"][0][5]
                        role = data["values"][0][3]
                        if role in role_dict_reaction:
                            role = role_dict_reaction[role]
                        message = await channel.send(
                            f"Hey, {user}! You accepted an assignment on {date_only} for {series} CH {chapter} ({role}). The deadline for this is tomorrow. Will you be able to finish it by then?")
                        sheets.values().update(spreadsheetId=progresssheet, range=f"DATA!M{i}:M{i}",
                                               valueInputOption="USER_ENTERED",
                                               body={'values': [[str(message.id)]]}).execute()
                        await message.add_reaction("✅")
                        await message.add_reaction("<:no:1225574648088105040>")
                        await message.add_reaction("❌")

            except ValueError:
                # The value is not a date and time
                pass


async def storetime(row, time):
    sheets.values().update(spreadsheetId=progresssheet, range=f"DATA!L{row}:L{row}",
                           valueInputOption="USER_ENTERED", body={'values': [[str(time)]]}).execute()


async def getmessageid(id):
    """
        This asynchronous function retrieves Data by using a message ID from a Google Sheets spreadsheet.

        Args:
            id (str): The ID of the message to retrieve.

        Returns:
            tuple: A tuple containing the fetched values and the row index if the ID is found, None otherwise.

        Raises:
            HttpError: If an error occurs while trying to fetch the values from the Google Sheets spreadsheet. The error is logged using the `logging` module.
    """
    name = None
    # await checkcred()
    try:
        value = sheets.values().get(spreadsheetId=progresssheet, range=f"DATA!F:F").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and f"{row[0]}" == f"{id}":
                name = i
        if name is not None:
            data = sheets.values().get(spreadsheetId=progresssheet, range=f"DATA!G{name}:K{name}").execute()
            return data["values"][0], name
    except HttpError as error:
        logging.error(error)


async def remove_due_date(row):
    sheets.values().update(spreadsheetId=progresssheet, range=f"DATA!M{row}:M{row}",
                           valueInputOption="USER_ENTERED", body={'values': [[""]]}).execute()


async def getmessageid_due_date(id):
    name = None
    try:
        value = sheets.values().get(spreadsheetId=progresssheet, range=f"DATA!M:M").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and f"{row[0]}" == f"{id}":
                name = i
        if name is not None:
            data = sheets.values().get(spreadsheetId=progresssheet, range=f"DATA!F{name}:L{name}").execute()
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

    try:
        value = sheets.values().get(spreadsheetId=progresssheet, range=f"{sheet_name}!A:A").execute()

        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == chapter:
                chapter_index = i
                chapter_found = True
        if not chapter_found:
            # Check if the previous chapter rounded equals the current chapter
            # and if the previous chapter plus one equals the current chapter
            prev_chapter = float(value['values'][len(value['values']) - 1][0]) if value[
                'values'] else 0  # Ensure prev_chapter is an integer
            math.floor(prev_chapter)
            if math.ceil(float(prev_chapter)) == math.floor(float(chapter)) or math.floor(
                    float(prev_chapter)) == math.floor(float(chapter)) or int(prev_chapter) + 1 == int(chapter):
                chapter_index = len(value['values']) + 1
                sheets.values().append(spreadsheetId=progresssheet, range=f"{sheet_name}!A{chapter_index}:A{chapter_index}",
                                       insertDataOption="INSERT_ROWS", valueInputOption="USER_ENTERED",
                                       body={'values': [[chapter]]}).execute()
        if chapter_index is not None:
            value = sheets.values().get(spreadsheetId=progresssheet,
                                        range=f"{sheet_name}!{first}{chapter_index}:{second}{chapter_index}").execute()
            if first == "N":
                if status == "Done":
                    sheets.values().update(spreadsheetId=progresssheet,
                                           range=f"{sheet_name}!{first}{chapter_index}:{second}{chapter_index}",
                                           valueInputOption="USER_ENTERED",
                                           body={'values': [[True, ""]]}).execute()
            else:

                if status == "":
                    sheets.values().update(spreadsheetId=progresssheet,
                                           range=f"{sheet_name}!{first}{chapter_index}:{second}{chapter_index}",
                                           valueInputOption="USER_ENTERED",
                                           body={'values': [["", status]]}).execute()
                else:
                    sheets.values().update(spreadsheetId=progresssheet,
                                           range=f"{sheet_name}!{first}{chapter_index}:{second}{chapter_index}",
                                           valueInputOption="USER_ENTERED",
                                           body={'values': [[await getuser(user), status]]}).execute()
    except HttpError as error:
        logging.error(f"An error occurred: {error}")


async def store(message_id, sheet, ch, user, f, se):
    try:
        sheets.values().append(spreadsheetId=progresssheet, range=f"DATA!F2:K2", insertDataOption="INSERT_ROWS",
                               valueInputOption="USER_ENTERED",
                               body={'values': [[str(message_id), sheet, ch, f, se, str(user)]]}).execute()
    except HttpError as error:
        logging.error(error)


async def writechannel(channel_id, sheet):
    try:
        sheets.values().append(spreadsheetId=progresssheet, insertDataOption="INSERT_ROWS", range=f"CHANNELS!3:3",
                               valueInputOption="USER_ENTERED", body={'values': [[channel_id, sheet]]}).execute()
    except HttpError as error:
        logging.error(error)


async def updatesheet(channel_id, sheet):
    try:
        value = sheets.values().get(spreadsheetId=progresssheet, range=f"CHANNELS!A:A").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == f"{channel_id}":
                row = i

        sheets.values().update(spreadsheetId=progresssheet, range=f"CHANNELS!{row}:{row}", valueInputOption="USER_ENTERED",
                               body={'values': [[channel_id, sheet]]}).execute()
    except HttpError as error:
        logging.error(error)


async def updatechannel_id(channel_id, sheet):
    try:
        value = sheets.values().get(spreadsheetId=progresssheet, range=f"CHANNELS!B:B").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == f"{sheet}":
                row = i

        sheets.values().update(spreadsheetId=progresssheet, range=f"CHANNELS!{row}:{row}", valueInputOption="USER_ENTERED",
                               body={'values': [[channel_id, sheet]]}).execute()
    except HttpError as error:
        logging.error(error)


async def getsheetname(channel_id):
    try:
        rowd = None
        value = sheets.values().get(spreadsheetId=progresssheet, range=f"CHANNELS!A:A").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == channel_id:
                rowd = i
        name = sheets.values().get(spreadsheetId=progresssheet, range=f"CHANNELS!B{rowd}:B{rowd}").execute()
        return name["values"][0][0]
    except HttpError as error:
        logging.error(error)


async def getchannelid(sheet):
    try:
        rowd = None
        value = sheets.values().get(spreadsheetId=progresssheet, range=f"CHANNELS!B:B").execute()
        for i, row in enumerate(value['values'], start=1):
            if row and row[0] == sheet:
                rowd = i
        name = sheets.values().get(spreadsheetId=progresssheet, range=f"CHANNELS!A{rowd}:A{rowd}").execute()
        return name["values"][0][0]
    except HttpError as error:
        logging.error(error)


async def delete_row(row_index):  # delets the row in the sheet "Data" ...
    # await checkcred()

    request = sheets.batchUpdate(
        spreadsheetId=progresssheet,
        body={
            'requests': [
                {
                    'deleteDimension': {
                        'range': {
                            'sheetId': ID,  # Replace with your sheet ID
                            'dimension': 'ROWS',
                            'startIndex': row_index - 1,
                            'endIndex': row_index
                        }
                    }
                }
            ]
        }
    )
    response = request.execute()


async def get_sheet_id_by_name(spreadsheet_id, sheet_name):
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in spreadsheet['sheets']:
        if sheet['properties']['title'] == sheet_name:
            print(sheet['properties']['sheetId'])


#async def main():
#    await get_sheet_id_by_name(progresssheet, "DATA")
