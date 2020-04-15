from Utility.utils import internal_meeting_id, internal_user_id, external_meeting_id, record_id, timestamp_now, post_event

rap_archive_ended_json = {
    "data": {
        "type": "event",
        "id": "rap-archive-ended",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "record-id": record_id,
            "success": True,
            "step-time": 843,
            "recorded": True,
            "duration": 3655
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}

post_event(rap_archive_ended_json)