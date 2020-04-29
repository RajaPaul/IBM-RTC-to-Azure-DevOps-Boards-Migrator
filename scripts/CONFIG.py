RTC_USERNAME=""
RTC_PASSWORD=""
RTC_URL = "" # eg. https://ccm..../ccm
RTC_projectarea_name = ""

project_name='' # AZURE PROJECT NAME : The project to migrate to
user_domain ='' # company domain. eg @google.com or @intel.com


# Fill in with your personal access token and org URL for AZURE
personal_access_token = ''
organization_url = '' # eg.'https://dev.azure.com/sampleorg' 


# Query Details : Enter the saved query urls as list items, eg. ["https://ccm-...../","https://ccm-...../"]
epic_query_urls=[]

userstory_query_urls=[]

task_query_urls =[]


EPIC_FOLDER = 'EPICs'
EPIC_JSON_FILE = 'rtc-azure-epicmap.json'

US_FOLDER = 'UserStories'
US_JSON_FILE = 'rtc-azure-userstorymap.json'


TASK_FOLDER = 'TASKS'
TASK_JSON_FILE = 'rtc-azure-taskmap.json'


validate_only=False
bypass_rules=True
suppress_notifications=True
ends_with_jazz=False


