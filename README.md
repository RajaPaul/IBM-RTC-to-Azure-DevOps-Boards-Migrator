# IBM RTC to Azure DevOps (Boards) Migrator

## Introduction 

IBM RTC to Azure DevOps (Boards) Migrator is a collection of python scripts which helps in migrating work items from IBM RTC to Microsoft AZURE DEVOPS.
It uses [Azure DevOps Python API](https://github.com/Microsoft/azure-devops-python-api). and [RTCCLIENT](https://rtcclient.readthedocs.io/en/latest/quickstart.html#) libraries to perform operations via REST API.

## Installation and Dependencies

> **Python 3.8.1** was used during development
All dependencies are mentioned in the file scripts/requirements.txt. You can use the following commands to install the dependencies: 
``` pip install -r scripts/requirements.txt```


## Configuration

Config file is **scripts/CONFIG.py** 
 ```
RTC_USERNAME=""
RTC_PASSWORD=""
RTC_URL = "" # eg. https://ccm..../ccm
RTC_projectarea_name=""

project_name='' # AZURE PROJECT NAME : The project to migrate to
user_domain ='' # company domain. eg @google.com or @intel.com , ## only supports migration when all user email are of same domain

# Fill in with your personal access token and org URL for AZURE
personal_access_token = ''
organization_url = '' # eg.'https://dev.azure.com/sampleorg' 
 ```

 
## Migrating RTC Work Items

Config file is **scripts/CONFIG.py**

 ```
# Query Details : Enter the saved query urls as list items, eg. ["https://ccm-...../","https://ccm-...../"]

epic_query_urls=[]

userstory_query_urls=[]

task_query_urls =[]

  ```

## Migrating EPICS

### Migrate EPICS without EPIC Hierarchy

After configuring the setting run the file **scripts/AZURE_RTC_MIGRATE_EPICS.py**

### Migrate EPICS with EPIC Hierarchy

After configuring the setting run the file **scripts/AZURE_RTC_MIGRATE_EPIC_HIERARACHY.py**

## Migrating USER STORIES

After configuring the setting run the file **scripts/AZURE_RTC_MIGRATE_US.py**

## Migrating TASKS

After configuring the setting run the file **scripts/AZURE_RTC_MIGRATE_TASKS.py**





