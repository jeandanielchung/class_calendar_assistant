# class_calendar_assistant
Short Python script to read in class assignment data from Google Sheets and create/update Google Calendar events for lazy people like me

## Instructions for use
1. You will need to create a GCP project to use the Google Calendar and Sheets APIs
1. Authorize your project to use these 2 APIs
1. Download the client configuration and save the file as credentials.json in the root directory
1. You might need to install the Google Python API client library: https://github.com/googleapis/google-api-python-client
1. Create a config.json file with the following
    1. CALENDAR_ID: <id of whatever calendar you want to use> (note: I'd suggest creating a calendar specifically for your class assignments)
    1. SPREADSHEET_ID: <id of the Google Sheet you want to use> (note: the sheet has to be in the column format <classname, date, name, weight> with an assignment on every row)
    1. RANGE_NAME: <name of the page and cell range for your assignment data>
1. simply use `python create_class_assignment_events.py` and check your Google Calendar for your newly scheduled events!
    1. Note: the first time you run this script you will have to authorize your app to access your data

## Notes
- The script will check your existing calendar and update assignments already scheduled. If an assignment hasn't already been scheduled a new event will be created for it
