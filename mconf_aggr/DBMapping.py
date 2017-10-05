
def mapMessageToDB(message):
    #print(message)
    id = message["data"]["id"]
    if(id == 'meeting-created'):
        msg = mapCreateMessage(message)
    elif(id == 'meeting-ended'):
        msg = mapEndMessage(message)
    elif(id == 'user-joined' or id == 'user-left'):
        msg = mapUserJoinLeft(message, id)
    elif(id in ['user-audio-voice-enabled','user-audio-voice-disabled','user-audio-listen-only-enabled'
       ,'user-audio-listen-only-disabled','user-cam-broadcast-start','user-cam-broadcast-end']):
        msg = mapUserEvents(message, id)
    return msg

def mapEndMessage(message):
    # Transform meeting-ended message to MeetingEventsObj
    return {
        "externalMeetingId" : message["data"]["attributes"]["meeting"]["external-meeting-id"],
        "internalMeetingId" : message["data"]["attributes"]["meeting"]["internal-meeting-id"],
        "endTime": message["data"]["attributes"]["event"]["ts"]
    }

def mapCreateMessage(message):
    # Transform meeting-created  message to MeetingEventsObj
    return {
        # "createdAt" :
        # "updatedAt" : check if both are created/updated by sqlalchemy
        "externalMeetingId" : message["data"]["attributes"]["meeting"]["external-meeting-id"],
        "internalMeetingId" : message["data"]["attributes"]["meeting"]["internal-meeting-id"],
        "name" :  message["data"]["attributes"]["meeting"]["name"],
        "createTime" :  message["data"]["attributes"]["meeting"]["create-time"],
        "createDate" : message["data"]["attributes"]["meeting"]["create-date"],
        "voiceBridge" : message["data"]["attributes"]["meeting"]["voice-conf"],
        "dialNumber" : message["data"]["attributes"]["meeting"]["dial-number"],
        "attendeePW" : message["data"]["attributes"]["meeting"]["viewer-pass"],
        "moderatorPW" : message["data"]["attributes"]["meeting"]["moderator-pass"],
        "duration" : message["data"]["attributes"]["meeting"]["duration"],
        "recording" : message["data"]["attributes"]["meeting"]["record"], #or recorded? or recording?
        # different event from webhooks? "hasBeenForciblyEnded" :
        # "startTime" :
        # "endTime" : need to define when to update start/end time and which timestamp
        "maxUsers" : message["data"]["attributes"]["meeting"]["max-users"],
        "isBreakout" : message["data"]["attributes"]["meeting"]["is-breakout"],
        # user events will increment this :: "uniqueUsers" :
        "meta_data" : message["data"]["attributes"]["meeting"]["metadata"]
    }

def mapUserJoinLeft(message, id):
    # Transform user-joined message to UsersEventsObj
    if(id == "user-joined"):
        return {
            "name" : message["data"]["attributes"]["user"]["name"],
            "role" : message["data"]["attributes"]["user"]["role"],
            "internalUserId" : message["data"]["attributes"]["user"]["internal-user-id"],
            "externalUserId" : message["data"]["attributes"]["user"]["external-user-id"],
            "joinTime" : message["data"]["attributes"]["event"]["ts"]
            # "meta_data" : message["data"]["attributes"]["user"]["metadata"]
        }
    elif(id == "user-left"):
        return {
            "internalUserId" : message["data"]["attributes"]["user"]["internal-user-id"],
            "externalUserId" : message["data"]["attributes"]["user"]["external-user-id"],
            "leaveTime" : message["data"]["attributes"]["event"]["ts"]
            # "meta_data" : message["data"]["attributes"]["user"]["metadata"]
        }

def mapUserEvents(message, id):
    return {
        "internalUserId" : message["data"]["attributes"]["user"]["internal-user-id"],
        "externalUserId" : message["data"]["attributes"]["user"]["external-user-id"],
        "externalMeetingId" : message["data"]["attributes"]["meeting"]["external-meeting-id"],
        "internalMeetingId" : message["data"]["attributes"]["meeting"]["internal-meeting-id"],
        "eventName" : id
    }
