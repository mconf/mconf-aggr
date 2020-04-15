from Utility.utils import internal_meeting_id, external_meeting_id, record_id, timestamp_now, post_event

rap_sanity_ended_json = {
    "data": {
        "type": "event",
        "id": "rap-sanity-ended",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "record-id": record_id,
            "success": True,
            "step-time": 183
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}

post_event(rap_sanity_ended_json)