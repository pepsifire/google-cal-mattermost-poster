from mattermostdriver import Driver
from config import Config
from getCalendarEvents import getEventsSoon, getTodaysEvents
from event import Event
from datetime import datetime, timedelta, timezone

def parseIsoTimeString(timestring: str):
    try:
        return datetime.fromisoformat(timestring).strftime("%d.%m.%Y %H.%M")
    except ValueError:
        return "N/A"


class MattermostHandler:
    driver: Driver
    globalConfig: Config
    
    def __init__(self, driver):
        self.driver = driver
        self.globalConfig = Config.from_file("config.json")
        try:
            driver.login()
            print("Connection established")
            
        except:
            print("Failed to login! Check your details")
    def __call__(self):
        return driver
        
    def getBotUser(self) -> dict:
        return self.driver.users.get_user(user_id="me")
    
    def getTeams(self) -> list:
        return self.driver.teams.get_teams()
    
    def getTeamByName(self, name: str) -> dict:
        return self.driver.teams.get_team_by_name(name)
    
    def getAllChannels(self) -> list:
        teamId = self.getTeamByName(self.globalConfig.mm_team_name)["id"]
        channels = self.driver.channels.get_channels_for_user(user_id="me", team_id=teamId)
        return channels
    
    def getChannelByName(self, name: str) -> dict:
        teamId = self.getTeamByName(self.globalConfig.mm_team_name)["id"]
        channel = self.driver.channels.get_channel_by_name(channel_name=name, team_id=teamId)
        return channel
    
    def postEventListToChannel(self, channelName: str, eventList: list[Event]):
        # https://developers.mattermost.com/integrate/reference/message-attachments/
        channelId = self.getChannelByName(channelName)["id"]

        fields = []
        currentTime = datetime.now(timezone.utc).astimezone()
        
        for event in eventList:
            eventStartParsed = parseIsoTimeString(event.start)
            eventEndParsed = parseIsoTimeString(event.end)
            fields.append(
                {
                    "title": event.name, 
                    "value": f"Starting time: {eventStartParsed}\nEnding time: {eventEndParsed}"
                }
            )
        postOptions = {
            "channel_id": channelId,
            "message": "",
            "props": {
                "attachments": [{
                    "fallback": "",
                    "text": f"Tapahtumia tälle päivälle ({currentTime.date()})",
                    "author_name": "Google Calendar Integration",
                    "title": "Tapahtumat",
                    "fields": fields
                }]
            }
        }
        
        self.driver.posts.create_post(postOptions)
    
    def postEventToChannel(self, channelName: str, event: Event):
        channelId = self.getChannelByName(channelName)["id"]
        eventStartParsed = parseIsoTimeString(event.start)
        eventEndParsed = parseIsoTimeString(event.end)
        postOptions = {
            "channel_id": channelId,
            "message": "",
            "props": {
                "attachments": [{
                    "fallback": f"{event.name} alkaa {eventStartParsed}",
                    "text": "Kohta ois tämmöstä tarjolla",
                    "author_name": "Google Calendar Integration",
                    "title": "Tapahtuma",
                    "fields": [{
                        "title": event.name,
                        "value": f"Starting time: {eventStartParsed}\nEnding time: {eventEndParsed}"
                    }]
                }]
            }
        }
        self.driver.posts.create_post(postOptions)


def initializeDriver():
    globalConfig = Config.from_file("config.json")

    mm = Driver({
        "url": globalConfig.mm_url,
        "token": globalConfig.mm_api_key,
        "scheme": "https",
        "port": 443
    })
    return MattermostHandler(mm)

driver = initializeDriver()
postingChannel = "bottitestikanava"
todaysEvents = getTodaysEvents()

eventsSoon = getEventsSoon(30)
currentTime = datetime.now(timezone.utc).astimezone()
print(eventsSoon)
print(currentTime)

if len(eventsSoon) != 0:
    # Check that the start date is in the future before sending
    if datetime.fromisoformat(eventsSoon[0].start) > (currentTime - timedelta(minutes = 5)):
        print("Sending message")    
        driver.postEventToChannel(postingChannel, eventsSoon[0])
