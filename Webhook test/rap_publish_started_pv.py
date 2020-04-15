from Utility.utils import internal_meeting_id, external_meeting_id, record_id, timestamp_now, post_event

rap_publish_started_pv_json = {
    "data": {
        "type": "event",
        "id": "rap-publish-started",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "record-id": record_id,
            "workflow": "presentation_video"
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}


post_event(rap_publish_started_pv_json)
