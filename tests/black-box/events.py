from Utility.utils import timestamp_now, post_event

def post_meeting_created(internal_meeting_id, external_meeting_id):
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

def post_meeting_ended(internal_meeting_id, external_meeting_id):
    meetingEndedJSON = {
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

    post_event(meetingEndedJSON)

def post_meeting_recording_changed(internal_meeting_id, external_meeting_id):
    meetingRecordingChangedJSON = {
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

    post_event(meetingRecordingChangedJSON)

def post_rap_archive_ended(internal_meeting_id, external_meeting_id, record_id):
    rap_archive_ended_json = {
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

    post_event(rap_archive_ended_json)

def post_rap_archive_started(internal_meeting_id, external_meeting_id, record_id):
    rap_archive_started_json = {
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

    post_event(rap_archive_started_json)

def post_rap_post_publish_ended(internal_meeting_id, external_meeting_id, record_id):
    rap_post_publish_ended_json = {
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

    post_event(rap_post_publish_ended_json)

def post_rap_post_publish_started(internal_meeting_id, external_meeting_id, record_id):
    rap_post_publish_started_json = {
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

    post_event(rap_post_publish_started_json)

def post_rap_process_ended_pv(internal_meeting_id, external_meeting_id, record_id):
    rap_process_ended_pv_json = {
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

    post_event(rap_process_ended_pv_json)

def post_rap_process_ended(internal_meeting_id, external_meeting_id, record_id):
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

def post_rap_process_started_pv(internal_meeting_id, external_meeting_id, record_id):
    rap_process_started_pv_json = {
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

    post_event(rap_process_started_pv_json)

def post_rap_process_started(internal_meeting_id, external_meeting_id, record_id):
    rap_process_started_json = {
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

    post_event(rap_process_started_json)

def post_rap_publish_ended_pv(internal_meeting_id, external_meeting_id, record_id):
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

def post_rap_publish_ended_rec_pv(internal_meeting_id, external_meeting_id, record_id):
    rap_publish_ended_rec_pv_json = {
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
                                            "https://fake-rec.mconf.com/presentation/"+record_id +
                                            "/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-1.png",
                                            "https://fake-rec.mconf.com/presentation/"+record_id +
                                            "/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-2.png"
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

    post_event(rap_publish_ended_rec_pv_json)

def post_rap_publish_ended_rec(internal_meeting_id, external_meeting_id, record_id):
    rap_publish_ended_rec_json = {
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
                                            "https://fake-rec.mconf.com/presentation/"+record_id +
                                            "/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-1.png",
                                            "https://fake-rec.mconf.com/presentation/"+record_id +
                                            "/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1571938092218/thumbnails/thumb-2.png"
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

    post_event(rap_publish_ended_rec_json)

def post_rap_publish_ended(internal_meeting_id, external_meeting_id, record_id):
    rap_publish_ended_json = {
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

    post_event(rap_publish_ended_json)

def post_rap_publish_started_pv(internal_meeting_id, external_meeting_id, record_id):
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

def post_rap_publish_started(internal_meeting_id, external_meeting_id, record_id):
    rap_publish_started_json = {
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

    post_event(rap_publish_started_json)

def post_rap_sanity_ended(internal_meeting_id, external_meeting_id, record_id):
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

def post_rap_sanity_started(internal_meeting_id, external_meeting_id, record_id):
    rap_sanity_started_json = {
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

    post_event(rap_sanity_started_json)

def post_user_audio_voice_enabled(internal_meeting_id, external_meeting_id, internal_user_id):
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

def post_user_joined(internal_meeting_id, external_meeting_id, internal_user_id):
    userJoinedJSON = {
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

    post_event(userJoinedJSON)

def post_user_presenter_assigned(internal_meeting_id, external_meeting_id, internal_user_id):
    presenterAssignedJSON = {
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


    post_event(presenterAssignedJSON)

def post_user_presenter_unassigned(internal_meeting_id, external_meeting_id, internal_user_id):
    userPresenterUnassignedJSON = {
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

    post_event(userPresenterUnassignedJSON)