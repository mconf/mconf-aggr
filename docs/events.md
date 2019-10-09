## meeting-created

```json
[
    {
        "data": {
            "type": "event",
            "id": "meeting-created",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952",
                    "name": "random-6794952",
                    "is-breakout": false,
                    "duration": 0,
                    "create-time": 1566579655837,
                    "create-date": "Fri Aug 23 17:00:55 UTC 2019",
                    "moderator-pass": "mp",
                    "viewer-pass": "ap",
                    "record": true,
                    "voice-conf": "78085",
                    "dial-number": "613-555-1234",
                    "max-users": 0,
                    "metadata": {}
                }
            },
            "event": {
                "ts": 1566579655893
            }
        }
    }
]
```

## user-joined

```json
[
    {
        "data": {
            "type": "event",
            "id": "user-joined",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "user": {
                    "internal-user-id": "w_psjtwgty7odj",
                    "external-user-id": "w_psjtwgty7odj",
                    "name": "User 291551",
                    "role": "MODERATOR",
                    "presenter": false
                }
            },
            "event": {
                "ts": 1566579661160
            }
        }
    }
]
```

## user-presenter-assigned

```json
[
    {
        "data": {
            "type": "event",
            "id": "user-presenter-assigned",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "user": {
                    "internal-user-id": "w_psjtwgty7odj",
                    "external-user-id": "w_psjtwgty7odj"
                }
            },
            "event": {
                "ts": 1566579661174
            }
        }
    }
]
```

## user-presenter-unassigned

```json
[
    {
        "data": {
            "type": "event",
            "id": "user-presenter-unassigned",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "user": {
                    "internal-user-id": "w_psjtwgty7odj",
                    "external-user-id": "w_psjtwgty7odj",
                    "name": "User 291551"
                }
            },
            "event": {
                "ts": 1566579661188
            }
        }
    }
]
```

## user-audio-voice-enabled

```json
[
    {
        "data": {
            "type": "event",
            "id": "user-audio-voice-enabled",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "user": {
                    "internal-user-id": "w_psjtwgty7odj",
                    "external-user-id": "w_psjtwgty7odj",
                    "sharing-mic": true,
                    "listening-only": true
                }
            },
            "event": {
                "ts": 1566579669252
            }
        }
    }
]
```

## meeting-recording-changed

```json
[
    {
        "data": {
            "type": "event",
            "id": "meeting-recording-changed",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                }
            },
            "event": {
                "ts": 1566579672061
            }
        }
    }
]
```

## meeting-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "meeting-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                }
            },
            "event": {
                "ts": 1566579685637
            }
        }
    }
]
```

## rap-archive-started

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-archive-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837"
            },
            "event": {
                "ts": 1566579711
            }
        }
    }
]
```

## rap-archive-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-archive-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "success": true,
                "step-time": 1117,
                "recorded": true,
                "duration": 7452
            },
            "event": {
                "ts": 1566579712
            }
        }
    }
]
```

## rap-sanity-started

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-sanity-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837"
            },
            "event": {
                "ts": 1566579742
            }
        }
    }
]
```

## rap-sanity-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-sanity-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "success": true,
                "step-time": 391
            },
            "event": {
                "ts": 1566579742
            }
        }
    }
]
```

## rap-process-started

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-process-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "workflow": "presentation"
            },
            "event": {
                "ts": 1566579773
            }
        }
    }
]
```

## rap-process-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-process-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "success": true,
                "step-time": 4605,
                "workflow": "presentation"
            },
            "event": {
                "ts": 1566579777
            }
        }
    }
]
```

## rap-process-started

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-process-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "workflow": "presentation_video"
            },
            "event": {
                "ts": 1566579777
            }
        }
    }
]
```

## rap-process-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-process-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "success": false,
                "step-time": 366,
                "workflow": "presentation_video"
            },
            "event": {
                "ts": 1566579778
            }
        }
    }
]
```

## rap-publish-started

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-publish-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "workflow": "presentation"
            },
            "event": {
                "ts": 1566579803
            }
        }
    }
]
```

## rap-publish-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-publish-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "success": true,
                "step-time": 559,
                "workflow": "presentation",
                "recording": {
                    "name": "random-6794952",
                    "is-breakout": "false",
                    "size": 1217895,
                    "metadata": {
                        "isBreakout": "false",
                        "meetingId": "random-6794952",
                        "meetingName": "random-6794952"
                    },
                    "playback": {
                        "format": "presentation",
                        "link": "https://test-live220.dev.mconf.com/playback/presentation/2.0/playback.html?meetingId=708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                        "processing_time": 4605,
                        "duration": 7452,
                        "extensions": {
                            "preview": {
                                "images": {
                                    "image": [
                                        "https://test-live220.dev.mconf.com/presentation/708a8390eb8db424411bc602400a683b4a28562f-1566579655837/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1566579655878/thumbnails/thumb-1.png",
                                        "https://test-live220.dev.mconf.com/presentation/708a8390eb8db424411bc602400a683b4a28562f-1566579655837/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1566579655878/thumbnails/thumb-2.png"
                                    ]
                                }
                            }
                        },
                        "size": 1217895
                    },
                    "download": {}
                }
            },
            "event": {
                "ts": 1566579804
            }
        }
    }
]
```

## rap-post-publish-started

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-post-publish-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "workflow": "post_publish_recording_ready_callback"
            },
            "event": {
                "ts": 1566579804
            }
        }
    }
]
```

## rap-post-publish-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-post-publish-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "success": true,
                "step-time": 261,
                "workflow": "post_publish_recording_ready_callback"
            },
            "event": {
                "ts": 1566579804
            }
        }
    }
]
```

## rap-process-started

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-process-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "workflow": "presentation_video"
            },
            "event": {
                "ts": 1566579986
            }
        }
    }
]
```

## rap-process-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-process-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "success": true,
                "step-time": 248,
                "workflow": "presentation_video"
            },
            "event": {
                "ts": 1566579987
            }
        }
    }
]
```

## rap-publish-started

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-publish-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "workflow": "presentation_video"
            },
            "event": {
                "ts": 1566580017
            }
        }
    }
]
```

## rap-publish-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-publish-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "success": true,
                "step-time": 324,
                "workflow": "presentation_video",
                "recording": {
                    "name": "random-6794952",
                    "is-breakout": "false",
                    "size": 270755,
                    "metadata": {
                        "isBreakout": "false",
                        "meetingId": "random-6794952",
                        "meetingName": "random-6794952"
                    },
                    "playback": {
                        "format": "presentation_video",
                        "link": "https://test-live220.dev.mconf.com/presentation_video/708a8390eb8db424411bc602400a683b4a28562f-1566579655837/video.mp4",
                        "processing_time": 4605,
                        "duration": 7452,
                        "extensions": {
                            "preview": {
                                "images": {
                                    "image": [
                                        "https://test-live220.dev.mconf.com/presentation/708a8390eb8db424411bc602400a683b4a28562f-1566579655837/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1566579655878/thumbnails/thumb-1.png",
                                        "https://test-live220.dev.mconf.com/presentation/708a8390eb8db424411bc602400a683b4a28562f-1566579655837/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1566579655878/thumbnails/thumb-2.png"
                                    ]
                                }
                            }
                        },
                        "size": 270755
                    },
                    "download": {}
                }
            },
            "event": {
                "ts": 1566580017
            }
        }
    }
]
```

## rap-post-publish-started

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-post-publish-started",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "workflow": "post_publish_recording_ready_callback"
            },
            "event": {
                "ts": 1566580017
            }
        }
    }
]
```

## rap-post-publish-ended

```json
[
    {
        "data": {
            "type": "event",
            "id": "rap-post-publish-ended",
            "attributes": {
                "meeting": {
                    "internal-meeting-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                    "external-meeting-id": "random-6794952"
                },
                "record-id": "708a8390eb8db424411bc602400a683b4a28562f-1566579655837",
                "success": true,
                "step-time": 377,
                "workflow": "post_publish_recording_ready_callback"
            },
            "event": {
                "ts": 1566580018
            }
        }
    }
]
```