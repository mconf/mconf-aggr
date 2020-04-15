from Utility.utils import internal_meeting_id, external_meeting_id, record_id, timestamp_now, post_event

rap_publish_ended_pv_json = {
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

post_event(rap_publish_ended_pv_json)
