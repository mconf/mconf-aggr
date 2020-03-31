from kafka import KafkaProducer
import time
import json
from datetime import datetime

def timestamp_now():
    return int(datetime.timestamp(datetime.now()) * 1000)

kafka_topic = 'sample'

internal_meeting_id = "58ec2673ad6768c8f904c7e0d66307dbbf7a74f8-1571938092195"
record_id = internal_meeting_id
external_meeting_id = "random-4960974"
internal_user_id = "w_ygp0wa4hp9nx"

producer = KafkaProducer(bootstrap_servers='localhost:32769', value_serializer=lambda m: json.dumps(m).encode('ascii'))

rap_archive_started_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-archive-started",
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
]

producer.send(kafka_topic, key=b'rap-archive-started', value=rap_archive_started_json)
producer.flush()

rap_archive_ended_json = [
    {
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
]

producer.send(kafka_topic, key=b'rap-archive-ended', value=rap_archive_ended_json)
producer.flush()


rap_sanity_started_json = [
    {
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
]

producer.send(kafka_topic, key=b'rap-sanity-started', value=rap_sanity_started_json)
producer.flush()

rap_sanity_ended_json = [
    {
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
]

producer.send(kafka_topic, key=b'rap-sanity-ended', value=rap_sanity_ended_json)
producer.flush()


rap_process_started_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-process-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
                "record-id": record_id,
                "workflow": "presentation"
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=b'rap-process-started', value=rap_process_started_json)
producer.flush()

rap_process_ended_json = [
    {
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
]

producer.send(kafka_topic, key=b'rap-process-ended', value=rap_process_ended_json)
producer.flush()

rap_process_started_pv_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-process-started",
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
]

producer.send(kafka_topic, key=b'rap-process-started', value=rap_process_started_pv_json)
producer.flush()

rap_process_ended_pv_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-process-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
                "record-id": record_id,
                "success": False,
                "step-time": 167,
                "workflow": "presentation_video"
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=b'rap-process-ended', value=rap_process_ended_pv_json)
producer.flush()

rap_publish_started_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-publish-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
                "record-id": record_id,
                "workflow": "presentation"
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=b'rap-publish-started', value=rap_publish_started_json)
producer.flush()

rap_publish_ended_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-publish-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
                "record-id": record_id,
                "success": True,
                "step-time": 346,
                "workflow": "presentation",
                "recording": {
                    "name": external_meeting_id,
                    "is-breakout": "false",
                    "start-time": 1571938092195,
                    "end-time": 1571938108441,
                    "size": 1204266,
                    "raw-size": 4225033,
                    "metadata": {
                        "isBreakout": "false",
                        "meetingId": external_meeting_id,
                        "meetingName": external_meeting_id
                    },
                    "playback": {
                        "format": "presentation",
                        "link": "https://fake-live.mconf.com/playback/presentation/2.0/playback.html?meetingId=" + internal_meeting_id,
                        "processing_time": 2511,
                        "duration": 3655,
                        "extensions": {
                            "preview": {
                                "images": {
                                    "image": [
                                        {
                                            "attributes": {
                                                "width": 176,
                                                "height": 136,
                                                "alt": ""
                                            },
                                            "value": "https://fake-live.mconf.com/presentation/" + internal_meeting_id + "/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-1.png"
                                        },
                                        {
                                            "attributes": {
                                                "width": 176,
                                                "height": 136,
                                                "alt": ""
                                            },
                                            "value": "https://fake-live.mconf.com/presentation/"+internal_meeting_id+"/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-2.png"
                                        }
                                    ]
                                }
                            }
                        },
                        "size": 1204266
                    },
                    "download": {}
                }
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=b'rap-publish-ended', value=rap_publish_ended_json)
producer.flush()

rap_post_publish_started_json = [
    {
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
]

producer.send(kafka_topic, key=b'rap-post-publish-started', value=rap_post_publish_started_json)
producer.flush()

rap_post_publish_ended_json = [
    {
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
                "step-time": 186,
                "workflow": "post_publish_recording_ready_callback"
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=b'rap-post-publish-started', value=rap_post_publish_started_json)
producer.flush()

rap_process_started_pv_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-process-started",
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
]

producer.send(kafka_topic, key=b'rap-process-started', value=rap_process_started_pv_json)
producer.flush()

rap_process_ended_pv_json = [
    {
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
                "step-time": 167,
                "workflow": "presentation_video"
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=b'rap-process-ended', value=rap_process_ended_pv_json)
producer.flush()

rap_publish_started_pv_json = [
    {
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
]

producer.send(kafka_topic, key=b'rap-publish-started', value=rap_publish_started_pv_json)
producer.flush()

rap_publish_ended_pv_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-publish-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
                "record-id": record_id,
                "success": True,
                "step-time": 193,
                "workflow": "presentation_video",
                "recording": {
                    "name": external_meeting_id,
                    "is-breakout": "false",
                    "start-time": 1571938092195,
                    "end-time": 1571938108441,
                    "size": 18683,
                    "raw-size": 4225033,
                    "metadata": {
                        "isBreakout": "false",
                        "meetingId": external_meeting_id,
                        "meetingName": external_meeting_id
                    },
                    "playback": {
                        "format": "presentation_video",
                        "link": "https://fake-live.mconf.com/presentation_video/"+record_id+"/video.mp4",
                        "processing_time": 2511,
                        "duration": 3655,
                        "extensions": {
                            "preview": {
                                "images": {
                                    "image": [
                                        {
                                            "attributes": {
                                                "width": 176,
                                                "height": 136,
                                                "alt": ""
                                            },
                                            "value": "https://fake-live.mconf.com/presentation/"+record_id+"/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-1.png"
                                        },
                                        {
                                            "attributes": {
                                                "width": 176,
                                                "height": 136,
                                                "alt": ""
                                            },
                                            "value": "https://fake-live.mconf.com/presentation/"+record_id+"/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-2.png"
                                        }
                                    ]
                                }
                            }
                        },
                        "size": 18683
                    },
                    "download": {}
                }
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=b'rap-publish-ended', value=rap_publish_ended_pv_json)
producer.flush()

rap_post_publish_started_2_json = [
    {
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
]

producer.send(kafka_topic, key=b'rap-post-publish-started', value=rap_post_publish_started_2_json)
producer.flush()

rap_post_publish_ended_2_json = [
    {
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
]

producer.send(kafka_topic, key=b'rap-post-publish-ended', value=rap_post_publish_ended_2_json)
producer.flush()

rap_publish_ended_rec_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-publish-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
                "record-id": record_id,
                "success": True,
                "step-time": 346,
                "workflow": "presentation",
                "recording": {
                    "name": external_meeting_id,
                    "is-breakout": "false",
                    "start-time": 1571938092195,
                    "end-time": 1571938108441,
                    "size": 1204266,
                    "raw-size": 4225033,
                    "metadata": {
                        "isBreakout": "false",
                        "meetingId": external_meeting_id,
                        "meetingName": external_meeting_id,
                        "bbb-aws-published-time": 1571938385358,
                        "bbb-aws-original-link-presentation": "https://fake-live.mconf.com/playback/presentation/2.0/playback.html?meetingId="+record_id
                    },
                    "playback": {
                        "format": "presentation",
                        "link": "https://fake-rec.mconf.com/playback/presentation/2.0/playback.html?meetingId="+record_id,
                        "processing_time": 2511,
                        "duration": 3655,
                        "extensions": {
                            "preview": {
                                "images": {
                                    "image": [
                                        "https://fake-rec.mconf.com/presentation/"+record_id+"/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-1.png",
                                        "https://fake-rec.mconf.com/presentation/"+record_id+"/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-2.png"
                                    ]
                                }
                            }
                        },
                        "size": 1204266
                    },
                    "download": {}
                }
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=b'rap-publish-ended', value=rap_publish_ended_rec_json)
producer.flush()

rap_publish_ended_rec_pv_json = [
    {
        "data": {
            "type": "event",
            "id": "rap-publish-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": internal_meeting_id,
                    "external-meeting-id": external_meeting_id
                },
                "record-id": record_id,
                "success": True,
                "step-time": 193,
                "workflow": "presentation_video",
                "recording": {
                    "name": external_meeting_id,
                    "is-breakout": "false",
                    "start-time": 1571938092195,
                    "end-time": 1571938108441,
                    "size": 18683,
                    "raw-size": 4225033,
                    "metadata": {
                        "isBreakout": "false",
                        "meetingId": external_meeting_id,
                        "meetingName": external_meeting_id,
                        "bbb-aws-published-time": 1571938392493,
                        "bbb-aws-original-link-presentation-video": "https://fake-live.mconf.com/presentation_video/"+record_id+"/video.mp4"
                    },
                    "playback": {
                        "format": "presentation_video",
                        "link": "https://fake-rec.mconf.com/presentation_video/"+record_id+"/video.mp4",
                        "processing_time": 2511,
                        "duration": 3655,
                        "extensions": {
                            "preview": {
                                "images": {
                                    "image": [
                                        "https://fake-rec.mconf.com/presentation/"+record_id+"/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-1.png",
                                        "https://fake-rec.mconf.com/presentation/"+record_id+"/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-2.png"
                                    ]
                                }
                            }
                        },
                        "size": 18683
                    },
                    "download": {}
                }
            },
            "event": {
                "ts": timestamp_now()
            }
        }
    }
]

producer.send(kafka_topic, key=b'rap-publish-ended', value=rap_publish_ended_rec_pv_json)
producer.flush()