from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone, time
from config import Config
from event import Event

def getEvents(start, end) -> list[Event]:
  globalConfig = Config.from_file("config.json")

  calendarId = globalConfig.calendar_id
  apikey = globalConfig.google_api_key

  service = build('calendar', 'v3', developerKey=apikey)

  events_list: list[Event] = []

  page_token = None
  while True:
    events = service.events().list(calendarId=calendarId, pageToken=page_token, timeMin=start, timeMax=end).execute()
    for e in events['items']:
      start_time = "Not specified"
      if "dateTime" in e['start'].keys():
        start_time = e['start']['dateTime']
      end_time = "Not specified"
      if "dateTime" in e['end']:
        end_time = e['end']['dateTime']
      _event = Event(name=e['summary'], start=start_time, end=end_time)
      events_list.append(_event)
    page_token = events.get('nextPageToken')
    if not page_token:
      break
  
  return events_list

def getTodaysEvents() -> list[Event]:
  currentTime = datetime.now(timezone.utc).astimezone()
  start = datetime.combine(currentTime, time.min).astimezone().isoformat()
  end = datetime.combine(currentTime, time.max).astimezone().isoformat()

  return getEvents(start, end)

def getEventsSoon(minutesRange: int) -> list[Event]:
  currentTime = datetime.now(timezone.utc).astimezone()
  searchRange = currentTime + timedelta(minutes = minutesRange)
  start = currentTime.isoformat()
  end = searchRange.isoformat()

  return getEvents(start, end)