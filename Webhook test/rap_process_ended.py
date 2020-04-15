from Utility.utils import internal_meeting_id, external_meeting_id, record_id, timestamp_now, post_event

rap_process_ended_json = {
    "data": {
        "type": "event",
        "id": "rap-process-ended",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "record-id": record_id,
            "success": True,
            "step-time": 2511,
            "workflow": "presentation"
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}

post_event(rap_process_ended_json)