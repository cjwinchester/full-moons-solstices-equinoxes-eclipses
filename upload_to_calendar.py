# https://developers.google.com/calendar/api/quickstart/python

import os.path
from os import environ
import time
import csv
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


almanac_cal_id = environ.get('ALMANAC_CAL_ID')

SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

with open('data/celestial-almanac.csv', 'r') as infile:
    reader = csv.DictReader(infile)
    data = list(reader)


try:
    service = build('calendar', 'v3', credentials=creds)

    '''
    page_token = None
    while True:
        events = service.events().list(calendarId=almanac_cal_id, pageToken=page_token).execute()
        for event in events['items']:
            print(event['summary'])
            service.events().delete(
                calendarId=almanac_cal_id,
                eventId=event['id']
            ).execute(num_retries=50)
            time.sleep(0.5)
        page_token = events.get('nextPageToken')
        if not page_token:
            break 

    '''

    for ev in data:
        title = ev.get('event_type')
        start_datetime = datetime.fromisoformat(ev.get('datetime'))
        all_day = ev.get('all_day')

        if all_day:
            start = {'date': start_datetime.date().isoformat()}
            end = start
        else:
            start = {'dateTime': start_datetime.isoformat(timespec='seconds')}

            # duration of lunar eclipse isn't available, so just add 60 mins
            if 'lunar eclipse' in title:
                end_dt = start_datetime + timedelta(minutes=60)

            # solar eclipse data has duration values
            if 'solar eclipse' in title:
                seconds = ev.get('duration_seconds') or 0
                minutes = ev.get('duration_minutes') or 0
                total_duration = int(seconds) + (int(minutes) * 60)

                # if no duration listed, make it 5 mins
                if total_duration == 0:
                    total_duration = 5 * 60

                end_dt = start_datetime + timedelta(seconds=total_duration)

            end = {'dateTime': end_dt.isoformat(timespec='seconds')}

        event = {
          'summary': ev.get('event_type'),
          'start': start,
          'end': end,
          'reminders': {
            'useDefault': False,
            'overrides': [
              {'method': 'email', 'minutes': 24 * 60}
            ],
          },
        }

        e = service.events().insert(
                calendarId=almanac_cal_id,
                body=event
            ).execute(num_retries=50)

        link = e.get('htmlLink')

        print(f'{ev.get("datetime")} - {ev.get("event_type")}')
        print(f'    Event created: {link}')

        time.sleep(0.5)

except HttpError as error:
    print(f'An error occurred: {error}')
