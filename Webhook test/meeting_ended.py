from Utility.utils import internal_meeting_id, internal_user_id, external_meeting_id, timestamp_now, post_event

meetingEndedJSON = {
    "data": {
        "type": "event",
        "id": "meeting-ended",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                }
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}

post_event(meetingEndedJSON)