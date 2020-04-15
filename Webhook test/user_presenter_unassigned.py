from Utility.utils import internal_meeting_id, internal_user_id, external_meeting_id, timestamp_now, post_event

userPresenterUnassignedJSON = {
    "data": {
        "type": "event",
        "id": "user-presenter-unassigned",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "user": {
                    "internal-user-id": internal_user_id,
                    "external-user-id": internal_user_id,
                    "name": "User 780365"
            }
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}

post_event(userPresenterUnassignedJSON)
