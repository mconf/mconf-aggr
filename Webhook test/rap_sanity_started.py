from Utility.utils import internal_meeting_id, internal_user_id, external_meeting_id, record_id, timestamp_now, post_event

rap_sanity_started_json = {
    "data": {
        "type": "event",
        "id": "rap-sanity-started",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "record-id": record_id
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}

post_event(rap_sanity_started_json)