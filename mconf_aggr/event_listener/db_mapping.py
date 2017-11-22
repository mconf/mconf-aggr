# Receive parsed message from webhooks as dict
def map_message_to_db(message):
    #print(message)
    id = message["data"]["id"]
    if(id == "meeting-created"):
        msg = map_create_message(message)
    elif(id == "meeting-ended"):
        msg = map_end_message(message)
    elif(id == "user-joined" or id == "user-left"):
        msg = map_user_join_left(message, id)
    elif(id in ["user-audio-voice-enabled","user-audio-voice-disabled",
                "user-audio-listen-only-enabled","user-audio-listen-only-disabled",
                "user-cam-broadcast-start","user-cam-broadcast-end",
                "user-presenter-assigned", "user-presenter-unassigned"]):
        msg = map_user_events(message, id)
    elif(id in ["rap-archive-started","rap-archive-ended",
                "rap-sanity-started","rap-sanity-ended",
                "rap-post-archive-started","rap-post-archive-ended",
                "rap-process-started","rap-process-ended",
                "rap-post-process-started","rap-post-process-ended",
                "rap-publish-started","rap-publish-ended",
                "rap-post-publish-started","rap-post-publish-ended"]):
        msg = map_rap_events(message, id)
    return msg

def map_end_message(message):
    # Transform meeting-ended message to MeetingEventsObj
    return {
        "external_meeting_id" : message["data"]["attributes"]["meeting"]["external-meeting-id"],
        "internal_meeting_id" : message["data"]["attributes"]["meeting"]["internal-meeting-id"],
        "end_time": message["data"]["attributes"]["event"]["ts"]
    }

def map_create_message(message):
    # Transform meeting-created  message to MeetingEventsObj
    return {
        "external_meeting_id" : message["data"]["attributes"]["meeting"]["external-meeting-id"],
        "internal_meeting_id" : message["data"]["attributes"]["meeting"]["internal-meeting-id"],
        "name" :  message["data"]["attributes"]["meeting"]["name"],
        "create_time" :  message["data"]["attributes"]["meeting"]["create-time"],
        "create_date" : message["data"]["attributes"]["meeting"]["create-date"],
        "voice_bridge" : message["data"]["attributes"]["meeting"]["voice-conf"],
        "dial_number" : message["data"]["attributes"]["meeting"]["dial-number"],
        "attendee_pw" : message["data"]["attributes"]["meeting"]["viewer-pass"],
        "moderator_pw" : message["data"]["attributes"]["meeting"]["moderator-pass"],
        "duration" : message["data"]["attributes"]["meeting"]["duration"],
        "recording" : message["data"]["attributes"]["meeting"]["record"],
        # different event from webhooks? "hasBeenForciblyEnded" :
        # "startTime" :
        # "endTime" : need to define when to update start/end time and which timestamp
        "max_users" : message["data"]["attributes"]["meeting"]["max-users"],
        "is_breakout" : message["data"]["attributes"]["meeting"]["is-breakout"],
        "meta_data" : message["data"]["attributes"]["meeting"]["metadata"]
    }

def map_user_join_left(message, id):
    # Transform user-joined message to UsersEventsObj
    if(id == "user-joined"):
        return {
            "name" : message["data"]["attributes"]["user"]["name"],
            "role" : message["data"]["attributes"]["user"]["role"],
            "internal_user_id" : message["data"]["attributes"]["user"]["internal-user-id"],
            "external_user_id" : message["data"]["attributes"]["user"]["external-user-id"],
            "join_time" : message["data"]["attributes"]["event"]["ts"]
            # "meta_data" : message["data"]["attributes"]["user"]["metadata"]
        }
    elif(id == "user-left"):
        return {
            "internal_user_id" : message["data"]["attributes"]["user"]["internal-user-id"],
            "external_user_id" : message["data"]["attributes"]["user"]["external-user-id"],
            "leave_time" : message["data"]["attributes"]["event"]["ts"]
            # "meta_data" : message["data"]["attributes"]["user"]["metadata"]
        }

def map_user_events(message, id):
    # Transform general user events to UsersEventsObj
    return {
        "internal_user_id" : message["data"]["attributes"]["user"]["internal-user-id"],
        "external_user_id" : message["data"]["attributes"]["user"]["external-user-id"],
        "external_meeting_id" : message["data"]["attributes"]["meeting"]["external-meeting-id"],
        "internal_meeting_id" : message["data"]["attributes"]["meeting"]["internal-meeting-id"],
        "event_name" : id
    }

def map_rap_events(message, id):
    # Transform rap-messages to RecordingsObj
    if(id == "rap-publish-ended"):
        return {
            "name" : message["data"]["attributes"]["recording"]["name"],
            "is_breakout" : message["data"]["attributes"]["recording"]["isBreakout"],
            "start_time" : message["data"]["attributes"]["recording"]["startTime"],
            "end_time" : message["data"]["attributes"]["recording"]["endTime"],
            "size" : message["data"]["attributes"]["recording"]["size"],
            "raw_size" : message["data"]["attributes"]["recording"]["rawSize"],
            "meta_data" : message["data"]["attributes"]["recording"]["metadata"],
            "playback" : message["data"]["attributes"]["recording"]["playback"],
            "download" : message["data"]["attributes"]["recording"]["download"],
            "external_meeting_id" : message["data"]["attributes"]["meeting"]["external-meeting-id"],
            "internal_meeting_id" : message["data"]["attributes"]["meeting"]["internal-meeting-id"],
            "current_step" : id
        }
    else:
        return {
            "external_meeting_id" : message["data"]["attributes"]["meeting"]["external-meeting-id"],
            "internal_meeting_id" : message["data"]["attributes"]["meeting"]["internal-meeting-id"],
            "current_step" : id
        }
