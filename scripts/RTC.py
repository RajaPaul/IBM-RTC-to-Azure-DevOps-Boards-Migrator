from rtcclient.utils import setup_basic_logging
from rtcclient import RTCClient
import CONFIG


url = CONFIG.RTC_URL
username = CONFIG.RTC_USERNAME
password = CONFIG.RTC_PASSWORD


rtcclient = RTCClient(url, username, password, ends_with_jazz=CONFIG.ends_with_jazz)

projectAreas = rtcclient.getProjectAreas()
ISD_Project_Area = projectAreas[0]

