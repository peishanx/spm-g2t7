from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account key file
SERVICE_ACCOUNT_FILE = './wfh-calendar-view-337bd913fcd5.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Initialize the Google Calendar API client
def get_calendar_service():
    return build('calendar', 'v3', credentials=credentials)

# Use your calendar ID here
calendar_id = 'd6c62e38d0acc337129c40e729e598c02515e1ea326722ca0b5ad5f2f2078214@group.calendar.google.com@group.calendar.google.com'
