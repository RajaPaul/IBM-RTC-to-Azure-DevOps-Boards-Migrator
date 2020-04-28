import CONFIG
import RTC
import AZURE
from  azure.devops.v5_0.work_item_tracking.models import JsonPatchOperation
from azure.devops.v5_1.work_item_tracking.models import Comment
from azure.devops.v5_1.work_item_tracking.models import CommentCreate
from datetime import datetime
import json
import os
import UTILS
import glob
import mmap


US_FOLDER = CONFIG.US_FOLDER

UTILS.remove(US_FOLDER)
os.mkdir(US_FOLDER)
os.mkdir(US_FOLDER+'\items')

# Clients
validate_only=CONFIG.validate_only
bypass_rules=CONFIG.bypass_rules
suppress_notifications=CONFIG.suppress_notifications
rtcclient = RTC.rtcclient
queryclient = rtcclient.query
core_client = AZURE.core_client

wit_client = AZURE.wit_client
wit_5_1_client = AZURE.wit_5_1_client

# Project

project_name = CONFIG.project_name
project = core_client.get_project(project_name)
projectarea_name = RTC.ISD_Project_Area.title

# Query URL
userstory_query_urls=CONFIG.userstory_query_urls

# column def
returned_properties = "rtc_cm:modifiedBy,dc:modified,rtc_cm:contextId,dc:subject,oslc_cm:priority,dc:creator,rtc_cm:due,rtc_cm:estimate,rtc_cm:correctedEstimate,rtc_cm:timeSpent,rtc_cm:startDate,dc:created,rtc_cm:resolvedBy,rtc_cm:plannedFor,rtc_cm:ownedBy,dc:description,dc:title,rtc_cm:state,rtc_cm:resolution,oslc_cm:severity,dc:type,dc:identifier,rtc_cm:comments,rtc_cm:com.ibm.team.apt.attribute.acceptance,rtc_cm:com.ibm.team.apt.attribute.complexity,calm:tracksRequirement"

default_field=None

RTC_AZURE_US_MAP={}
RTC_AZURE_EPIC_MAP ={}


if(os.path.isfile(CONFIG.EPIC_JSON_FILE)):
    with open(CONFIG.EPIC_JSON_FILE, "r") as read_file:
        RTC_AZURE_EPIC_MAP = json.load(read_file)

if(os.path.isfile(CONFIG.US_JSON_FILE)):
    with open(CONFIG.US_JSON_FILE, "r") as read_file:
        RTC_AZURE_US_MAP = json.load(read_file)

queried_wis =[]

for userstory_query_url in userstory_query_urls:
    queried_wis.extend(queryclient.runSavedQueryByUrl(userstory_query_url, returned_properties=returned_properties))



count=0
# FIELD MAPPING
for user_story_item in queried_wis:
    count=count+1
    if(RTC_AZURE_US_MAP.get(user_story_item.identifier) is not None): continue
    
    comments = user_story_item.getComments()
    attachments = user_story_item.getAttachments()
    parent = user_story_item.getParent(returned_properties=returned_properties)


    jpos = []
    description = ""
    if description is not None:
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add" 
        jpo.path = "/fields/System.Title"
        jpo.value = user_story_item.title[:255]
        description+='<b> RTC ' + user_story_item.type + ' '+ user_story_item.identifier + ' : </b>' + user_story_item.title + ' <br/> <br/>'

        jpos.append(jpo)

    if description != "":
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.Description"
        jpo.value = description

        jpos.append(jpo)

    if (user_story_item.ownedBy is not None and user_story_item.ownedBy!='unassigned'):
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.AssignedTo"
        jpo.value = user_story_item.ownedBy + CONFIG.user_domain

        jpos.append(jpo)

        
        
    if (user_story_item.modifiedBy is not None and user_story_item.modifiedBy !='unassigned'):
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.ChangedBy"
        jpo.value =user_story_item.modifiedBy + CONFIG.user_domain

        jpos.append(jpo)
    
        
        
    if (user_story_item.creator is not None and user_story_item.creator != 'unassigned' ):
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.CreatedBy"
        jpo.value =user_story_item.creator + CONFIG.user_domain

        jpos.append(jpo)
    
        
    jpo = JsonPatchOperation()
    jpo.from_ = None
    jpo.op = "add"
    jpo.path = "/fields/System.Tags"
    jpo.value = 'RTC-Migration;'+'RTC-ID:'+user_story_item.identifier
    if user_story_item.subject is not None:
        rtc_tags = ";"+ user_story_item.subject.replace( ',',';')
        jpo.value +=rtc_tags
    if user_story_item.plannedFor is not None:
        rtc_tags =  ";RTC-PlannedFor:"+ user_story_item.plannedFor
        jpo.value +=rtc_tags

    jpos.append(jpo)

    
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.TCM.ReproSteps"
        jpo.value = default_field

        jpos.append(jpo)
    
        
    if user_story_item.raw_data.get('rtc_cm:com.ibm.team.apt.attribute.complexity') is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Scheduling.StoryPoints"
        full_string = user_story_item.raw_data['rtc_cm:com.ibm.team.apt.attribute.complexity']['@rdf:resource']
        split_data = full_string.split("complexity/")
        jpo.value = split_data[1]

        jpos.append(jpo)
    
        
    if user_story_item.raw_data.get('oslc_cm:priority') is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.Priority"
        full_string = user_story_item.raw_data['oslc_cm:priority']['@rdf:resource']
        split_data = full_string.split("priority.literal.l")
        if(split_data[1]==7 or split_data[1]=="7"):
            jpo.value = 3
        elif(split_data[1]==11 or split_data[1]=="11"):
            jpo.value = 4
        else:
            jpo.value = split_data[1]

        jpos.append(jpo)
    
        
    if user_story_item.severity is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.Severity"
        jpo.value = user_story_item.severity

        jpos.append(jpo)
    
        
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.Activity"
        jpo.value = default_field

        jpos.append(jpo)
    
        
    if user_story_item.state is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.State"
        jpo.value = user_story_item.state

        jpos.append(jpo)
    
        
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.BacklogPriority"
        jpo.value = default_field 

        jpos.append(jpo)
    
        
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Scheduling.Effort"
        jpo.value = default_field

        jpos.append(jpo)
    
        
    if user_story_item.raw_data.get('rtc_cm:com.ibm.team.apt.attribute.acceptance') is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.AcceptanceCriteria"
        jpo.value = user_story_item.raw_data['rtc_cm:com.ibm.team.apt.attribute.acceptance']

        jpos.append(jpo)
    
        
    if user_story_item.resolution is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.Resolution"
        jpo.value = user_story_item.resolution

        jpos.append(jpo)
    
        
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.BusinessValue"
        jpo.value = default_field

        jpos.append(jpo)
    
        
    if user_story_item.due is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Scheduling.TargetDate"  #############maybe mapped to due date
        jpo.value = datetime.strptime(user_story_item.due[:19], '%Y-%m-%dT%H:%M:%S')

        jpos.append(jpo)
    
        
    if user_story_item.startDate is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Scheduling.StartDate"
        jpo.value = datetime.strptime(user_story_item.startDate[:19], '%Y-%m-%dT%H:%M:%S')

        jpos.append(jpo)
    
        
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Scheduling.FinishDate"
        jpo.value = default_field

        jpos.append(jpo)

    if parent is not None:
        if RTC_AZURE_EPIC_MAP.get(parent.identifier) is not None:
            jpos.append(RTC_AZURE_EPIC_MAP.get(parent.identifier))


    
    
    createdWorkItem = wit_client.create_work_item(document=jpos,project=project.id,type="User Story",validate_only=validate_only,bypass_rules=bypass_rules,suppress_notifications=suppress_notifications)
    attachment_html="<b>RTC-ATTACHMENTS : </b> <br/>"
    if attachments is not None:
        for attachment in attachments:
            attachment_html += '<a href="'+attachment.url+'" >'+attachment.label+' </a>  by '+attachment.creator +' on '+attachment.created+'<br/>'

        wit_5_1_client.add_comment(project=project.id,work_item_id=createdWorkItem.id,request=CommentCreate(text=attachment_html))
        
        UTILS.remove(US_FOLDER +'\\'+ user_story_item.identifier)
        os.mkdir(US_FOLDER +'\\'+ user_story_item.identifier)
        for i in attachments:
            print(i)
            UTILS.download_rtc_attachment(url=i.url,rtcclient=rtcclient,relativefilepathandname=US_FOLDER +'\\'+ user_story_item.identifier+'\\'+i.description)
                
        files = glob.glob(os.getcwd() + '\\' +US_FOLDER +'\\'+ user_story_item.identifier+"\\*")
        for doc_path in files:
            print(doc_path)
            with open(doc_path, 'r+b') as file:
                # use mmap, so we don't load entire file in memory at the same time, and so we can start
                # streaming before we are done reading the file.
                mm = mmap.mmap(file.fileno(), 0)
                basename = os.path.basename(doc_path)
                attachment = wit_client.create_attachment(mm, file_name=basename)
                                
                # Link Work Item to attachment
                patch_document = [
                    JsonPatchOperation(
                        op="add",
                        path="/relations/-",
                        value={
                            "rel": "AttachedFile",
                            "url": attachment.url
                        }
                    )
                ]
                wit_client.update_work_item(document=patch_document, id=createdWorkItem.id,project=project.id,validate_only=validate_only,bypass_rules=bypass_rules,suppress_notifications=suppress_notifications)


    if comments is not None:
        for comment in comments:
            if comment.description is not None:
                comment_html="<b>RTC Comment By :</b> " + comment.creator + "<b> RTC-TIMESTAMP : </b>" +comment.created +'<br>'+ comment.description
                wit_5_1_client.add_comment(project=project.id,work_item_id=createdWorkItem.id,request=CommentCreate(text=comment_html))
    
    
    userstory_details = {"self":{"op": "add","path": "/relations/-","value": {
      "rel": "System.LinkTypes.Hierarchy-Reverse",
      "name": "Parent",
      "url": createdWorkItem.url
    }},"parent":  RTC_AZURE_EPIC_MAP.get(parent.identifier) if parent is not None else None}

    RTC_AZURE_US_MAP[user_story_item.identifier]=userstory_details
    print(createdWorkItem)
    # Creates a new file 
    with open('./'+US_FOLDER+'/items/'+user_story_item.identifier, 'w') as fp: 
        json.dump(userstory_details,fp)
        
    with open(CONFIG.US_JSON_FILE, 'w') as f:
        json.dump(RTC_AZURE_US_MAP, f)

    print(str(count) + ' of ' + str(len(queried_wis)) + ' User Stories migrated ')


print('USER STORY MIGRATION COMPLETE')
