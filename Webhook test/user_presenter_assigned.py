from Utility.utils import internal_meeting_id, internal_user_id, external_meeting_id, timestamp_now, post_event

presenterAssignedJSON = {
    "data": {
        "type": "event",
        "id": "user-presenter-assigned",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "user": {
                    "internal-user-id": internal_user_id,
                    "external-user-id": internal_user_id
            }
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}


post_event(presenterAssignedJSON)
