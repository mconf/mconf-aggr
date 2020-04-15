from Utility.utils import internal_meeting_id, external_meeting_id, timestamp_now, post_event

createJSON = {
    "data": {
        "type": "event",
                "id": "meeting-created",
                "attributes": {
                    "meeting": {
                        "internal-meeting-id": internal_meeting_id,
                        "external-meeting-id": external_meeting_id,
                        "name": external_meeting_id,
                        "is-breakout": False,
                        "duration": 0,
                        "create-time": timestamp_now(),
                        "create-date": "Thu Oct 24 13:28:12 EDT 2019",
                        "moderator-pass": "mp",
                        "viewer-pass": "ap",
                        "record": True,
                        "voice-conf": "75393",
                        "dial-number": "613-555-1234",
                        "max-users": 0,
                        "metadata": {"foo": "bar"}
                    }
                },
        "event": {"ts": timestamp_now()}
    }
}

post_event(createJSON)
