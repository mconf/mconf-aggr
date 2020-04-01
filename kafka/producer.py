from kafka import KafkaProducer
import time
import json
from datetime import datetime

def timestamp_now():
    return int(datetime.timestamp(datetime.now()) * 1000)

kafka_topic = 'sample'

internal_meeting_id = "58ec2673ad6768c8f904c7e0d66307dbbf7a74f8-1571938092195"
internal_meeting_id_bytes = b"58ec2673ad6768c8f904c7e0d66307dbbf7a74f8-1571938092195"
external_meeting_id = "random-4960974"
internal_user_id = "w_ygp0wa4hp9nx"

producer = KafkaProducer(bootstrap_servers='localhost:32768', value_serializer=lambda m: json.dumps(m).encode('ascii'))

a = input(">")

createJSON = [
    {
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
                    "metadata": {"foo":"bar"}
                }
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=internal_meeting_id_bytes, value=createJSON)
producer.flush()

a = input(">")

presenterAssignedJSON = [
    {
        "data": {
            "type": "event",
            "id": "user-presenter-assigned",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
                "user": {
                    "internal-user-id": internal_user_id,
                    "external-user-id": internal_user_id
                }
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=internal_meeting_id_bytes, value=presenterAssignedJSON)
producer.flush()

a = input(">")

userJoinedJSON = [
    {
        "data": {
            "type": "event",
            "id": "user-joined",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
                "user": {
                    "internal-user-id": internal_user_id,
                    "external-user-id": internal_user_id,
                    "name": "User 780365",
                    "role": "MODERATOR",
                    "presenter": False
                }
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=internal_meeting_id_bytes, value=userJoinedJSON)
producer.flush()

a = input(">")

userPresenterUnassignedJSON = [
    {
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
]

producer.send(kafka_topic, key=internal_meeting_id_bytes, value=userPresenterUnassignedJSON)
producer.flush()

a = input(">")

userAudioVoiceEnabledJSON = [
    {
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
]

producer.send(kafka_topic, key=internal_meeting_id_bytes, value=userAudioVoiceEnabledJSON)
producer.flush()

a = input(">")

meetingRecordingChangedJSON = [
    {
        "data": {
            "type": "event",
            "id": "meeting-recording-changed",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                }
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=internal_meeting_id_bytes, value=meetingRecordingChangedJSON)
producer.flush()

a = input(">")

meetingEndedJSON = [
    {
        "data": {
            "type": "event",
            "id": "meeting-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                }
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=internal_meeting_id_bytes, value=meetingEndedJSON)
producer.flush()