from Utility.utils import internal_meeting_id, internal_user_id, external_meeting_id, timestamp_now, post_event

userAudioVoiceEnabledJSON = {
    "data": {
        "type": "event",
        "id": "user-audio-voice-enabled",
        "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
            "user": {
                    "internal-user-id": internal_user_id,
                    "external-user-id": internal_user_id,
                    "sharing-mic": True,
                    "listening-only": False
            }
        },
        "event": {
            "ts": timestamp_now()
        }
    }
}

post_event(userAudioVoiceEnabledJSON)