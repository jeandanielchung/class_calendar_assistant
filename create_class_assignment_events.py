from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

CLIENT_SECRETS_FILENAME = 'credentials.json'
CALENDAR_ID, SPREADSHEET_ID, RANGE_NAME = '', '', ''  # NOTE: specify specific values here or in config.json

if not (CALENDAR_ID and SPREADSHEET_ID and RANGE_NAME):
    with open('config.json', 'r') as f:
        config = json.load(f)
        CALENDAR_ID = config['CALENDAR_ID']
        SPREADSHEET_ID = config['SPREADSHEET_ID']
        RANGE_NAME = config['RANGE_NAME']

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILENAME, SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

calendar_service = build('calendar', 'v3', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)


def read_assignment_sheet():
    # Call the Sheets API
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Class,Date,Name,Weight:')
        for row in values:
            classname, date, name, weight = row
            print(f"{classname}, {date}, {name}, {weight}")

    return values


def get_current_events():
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = calendar_service.events().list(calendarId=CALENDAR_ID, timeMin=now).execute()
    events = events_result.get('items', [])

    return {event['summary']: event['id'] for event in events}


def get_identifier(summary):
    # TODO: find better delimiter to get just class and name
    return tuple(summary.split(' ')[:-1])


def event_exists(summary, current_events):
    return get_identifier(summary) in list(map(lambda x: get_identifier(x), current_events))


def create_event(event, current_events):
    if event['summary'] in current_events:
        # First retrieve the event from the API.
        event_id = current_events[event['summary']]
        current_event = calendar_service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        current_event.update(event)
        updated_event = calendar_service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=current_event).execute()
        event_link = updated_event.get('htmlLink')
        print(f"Event updated: {event_link}")
    else:
        new_event = calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        event_link = new_event.get('htmlLink')
        print(f"Event created: {event_link}")


def create_events():
    assignments = read_assignment_sheet()
    current_events = get_current_events()

    for assignment in assignments:
        classname, date, name, weight = assignment
        date = datetime.datetime.strptime(date, '%m/%d/%Y').date()
        if date > datetime.date.today():
            date = date.isoformat()
            event = {
                'summary': f"[{classname}] {name} ({weight}%)",
                'start': {
                    'date': date,
                    },
                'end': {
                    'date': date,
                },
            }
            create_event(event, current_events)


def main():
    create_events()


if __name__ == '__main__':
    main()
