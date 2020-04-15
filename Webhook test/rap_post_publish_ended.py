from Utility.utils import internal_meeting_id, external_meeting_id, record_id, timestamp_now, post_event

rap_post_publish_ended_2_json = {
    "data": {
        "type": "event",
        "id": "rap-post-publish-ended",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "record-id": record_id,
            "success": True,
            "step-time": 182,
            "workflow": "post_publish_recording_ready_callback"
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}

post_event(rap_post_publish_ended_2_json)
