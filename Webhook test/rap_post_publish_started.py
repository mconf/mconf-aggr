from Utility.utils import internal_meeting_id, external_meeting_id, record_id, timestamp_now, post_event

rap_post_publish_started_2_json = {
    "data": {
        "type": "event",
        "id": "rap-post-publish-started",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "record-id": record_id,
            "workflow": "post_publish_recording_ready_callback"
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}

post_event(rap_post_publish_started_2_json)
