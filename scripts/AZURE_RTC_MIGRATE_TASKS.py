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


FOLDER = CONFIG.TASK_FOLDER

UTILS.remove(FOLDER)
os.mkdir(FOLDER)
os.mkdir(FOLDER+'\items')

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
query_urls=CONFIG.userstory_query_urls

# column def
returned_properties = "rtc_cm:modifiedBy,dc:modified,rtc_cm:contextId,dc:subject,oslc_cm:priority,dc:creator,rtc_cm:due,rtc_cm:estimate,rtc_cm:correctedEstimate,rtc_cm:timeSpent,rtc_cm:startDate,dc:created,rtc_cm:resolvedBy,rtc_cm:plannedFor,rtc_cm:ownedBy,dc:description,dc:title,rtc_cm:state,rtc_cm:resolution,oslc_cm:severity,dc:type,dc:identifier,rtc_cm:comments,rtc_cm:com.ibm.team.apt.attribute.acceptance,rtc_cm:com.ibm.team.apt.attribute.complexity,calm:tracksRequirement"

default_field=None

RTC_AZURE_WORKITEM_MAP={}
WORKITEM_JSONFILE = CONFIG.TASK_JSON_FILE 
RTC_AZURE_PARENT_MAP ={}
PARENT_JSONFILE =  CONFIG.EPIC_JSON_FILE
WORKITEM_TYPE='Task'


if(os.path.isfile(PARENT_JSONFILE)):
    with open(PARENT_JSONFILE, "r") as read_file:
        RTC_AZURE_PARENT_MAP = json.load(read_file)

if(os.path.isfile(WORKITEM_JSONFILE)):
    with open(WORKITEM_JSONFILE, "r") as read_file:
        RTC_AZURE_WORKITEM_MAP = json.load(read_file)

queried_wis =[]

for query_url in query_urls:
    queried_wis.extend(queryclient.runSavedQueryByUrl(query_url, returned_properties=returned_properties))


count=0
# FIELD MAPPING
for work_item in queried_wis:
    count=count+1
    if(RTC_AZURE_WORKITEM_MAP.get(work_item.identifier) is not None): continue
    
    comments = work_item.getComments()
    attachments = work_item.getAttachments()
    parent = work_item.getParent(returned_properties=returned_properties)


    jpos = []
    description = ""
    if description is not None:
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add" 
        jpo.path = "/fields/System.Title"
        jpo.value = work_item.title[:255]
        description+='<b> RTC ' + work_item.type + ' '+ work_item.identifier + ' : </b>' + work_item.title + ' <br/> <br/>'

        jpos.append(jpo)

    if description != "":
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.Description"
        jpo.value = description

        jpos.append(jpo)

    if (work_item.ownedBy is not None and work_item.ownedBy!='unassigned'):
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.AssignedTo"
        jpo.value = work_item.ownedBy + CONFIG.user_domain

        jpos.append(jpo)

        
        
    if (work_item.modifiedBy is not None and work_item.modifiedBy !='unassigned'):
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.ChangedBy"
        jpo.value =work_item.modifiedBy + CONFIG.user_domain

        jpos.append(jpo)
    
        
        
    if (work_item.creator is not None and work_item.creator != 'unassigned' ):
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.CreatedBy"
        jpo.value =work_item.creator + CONFIG.user_domain

        jpos.append(jpo)
    
        
    jpo = JsonPatchOperation()
    jpo.from_ = None
    jpo.op = "add"
    jpo.path = "/fields/System.Tags"
    jpo.value = 'RTC-Migration;'+'RTC-ID:'+work_item.identifier
    if work_item.subject is not None:
        rtc_tags = ";"+ work_item.subject.replace( ',',';')
        jpo.value +=rtc_tags
    if work_item.plannedFor is not None:
        rtc_tags =  ";RTC-PlannedFor:"+ work_item.plannedFor
        jpo.value +=rtc_tags

    jpos.append(jpo)

    
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.TCM.ReproSteps"
        jpo.value = default_field

        jpos.append(jpo)
    
        
    if work_item.raw_data.get('rtc_cm:com.ibm.team.apt.attribute.complexity') is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Scheduling.StoryPoints"
        full_string = work_item.raw_data['rtc_cm:com.ibm.team.apt.attribute.complexity']['@rdf:resource']
        split_data = full_string.split("complexity/")
        jpo.value = split_data[1]

        jpos.append(jpo)
    
        
    if work_item.raw_data.get('oslc_cm:priority') is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.Priority"
        full_string = work_item.raw_data['oslc_cm:priority']['@rdf:resource']
        split_data = full_string.split("priority.literal.l")
        if(split_data[1]==7 or split_data[1]=="7"):
            jpo.value = 3
        elif(split_data[1]==11 or split_data[1]=="11"):
            jpo.value = 4
        else:
            jpo.value = split_data[1]

        jpos.append(jpo)
    
        
    if work_item.severity is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.Severity"
        jpo.value = work_item.severity

        jpos.append(jpo)
    
        
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.Activity"
        jpo.value = default_field

        jpos.append(jpo)
    
        
    if work_item.state is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/System.State"
        jpo.value = work_item.state

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
    
        
    if work_item.raw_data.get('rtc_cm:com.ibm.team.apt.attribute.acceptance') is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.AcceptanceCriteria"
        jpo.value = work_item.raw_data['rtc_cm:com.ibm.team.apt.attribute.acceptance']

        jpos.append(jpo)
    
        
    if work_item.resolution is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.Resolution"
        jpo.value = work_item.resolution

        jpos.append(jpo)
    
        
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Common.BusinessValue"
        jpo.value = default_field

        jpos.append(jpo)
    
        
    if work_item.due is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Scheduling.TargetDate"  #############maybe mapped to due date
        jpo.value = datetime.strptime(work_item.due[:19], '%Y-%m-%dT%H:%M:%S')

        jpos.append(jpo)
    
        
    if work_item.startDate is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Scheduling.StartDate"
        jpo.value = datetime.strptime(work_item.startDate[:19], '%Y-%m-%dT%H:%M:%S')

        jpos.append(jpo)
    
        
    if default_field is not None:
            
        jpo = JsonPatchOperation()
        jpo.from_ = None
        jpo.op = "add"
        jpo.path = "/fields/Microsoft.VSTS.Scheduling.FinishDate"
        jpo.value = default_field

        jpos.append(jpo)

    if parent is not None:
        if RTC_AZURE_PARENT_MAP.get(parent.identifier) is not None:
            jpos.append(RTC_AZURE_PARENT_MAP.get(parent.identifier))


    
    
    createdWorkItem = wit_client.create_work_item(document=jpos,project=project.id,type=WORKITEM_TYPE,validate_only=validate_only,bypass_rules=bypass_rules,suppress_notifications=suppress_notifications)
    attachment_html="<b>RTC-ATTACHMENTS : </b> <br/>"
    if attachments is not None:
        for attachment in attachments:
            attachment_html += '<a href="'+attachment.url+'" >'+attachment.label+' </a>  by '+attachment.creator +' on '+attachment.created+'<br/>'

        wit_5_1_client.add_comment(project=project.id,work_item_id=createdWorkItem.id,request=CommentCreate(text=attachment_html))
        
        UTILS.remove(FOLDER +'\\'+ work_item.identifier)
        os.mkdir(FOLDER +'\\'+ work_item.identifier)
        for i in attachments:
            print(i)
            UTILS.download_rtc_attachment(url=i.url,rtcclient=rtcclient,relativefilepathandname=FOLDER +'\\'+ work_item.identifier+'\\'+i.description)
                
        files = glob.glob(os.getcwd() + '\\' +FOLDER +'\\'+ work_item.identifier+"\\*")
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
    }},"parent":  RTC_AZURE_PARENT_MAP.get(parent.identifier) if parent is not None else None}

    RTC_AZURE_WORKITEM_MAP[work_item.identifier]=userstory_details
    print(createdWorkItem)
    # Creates a new file 
    with open('./'+FOLDER+'/items/'+work_item.identifier, 'w') as fp: 
        json.dump(userstory_details,fp)
        
    with open(WORKITEM_JSONFILE, 'w') as f:
        json.dump(RTC_AZURE_WORKITEM_MAP, f)

    print(str(count) + ' of ' + str(len(queried_wis)) + WORKITEM_TYPE + 's migrated ')


print('USER STORY MIGRATION COMPLETE')
