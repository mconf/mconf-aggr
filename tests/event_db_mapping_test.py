import unittest
import unittest.mock as mock

from mconf_aggr.event_listener.db_mapping import map_message_to_db


class TestMapping(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_create_message(self):
        message = {
                      "data": {
                        "type": "event",
                        "id": "meeting-created",
                        "attributes": {
                          "meeting": {
                            "name": "mock_n",
                            "external-meeting-id": "mock_e",
                            "internal-meeting-id": "mock_i",
                            "is-breakout": False,
                            "duration": 0,
                            "create-time": 0000000,
                            "create-date": "Mock Date",
                            "moderator-pass": "mp",
                            "viewer-pass": "ap",
                            "record": False,
                            "voice-conf": 00000,
                            "dial-number": "000-000-0000",
                            "max-users": 0,
                            "metadata": {
                               "mock_data": "mock",
                               "another_mock": "mocked"
                            }
                          },
                          "event": {
                            "ts": 1502810164922
                          }
                        }
                      }
                  }
        expected = {
                        "external_meeting_id" : "mock_e",
                        "internal_meeting_id" : "mock_i",
                        "name" : "mock_n",
                        "create_time" : 0000000,
                        "create_date" : "Mock Date",
                        "voice_bridge" : 00000,
                        "dial_number" : "000-000-0000",
                        "attendee_pw" : "ap",
                        "moderator_pw" : "mp",
                        "duration" : 0,
                        "recording" : False,
                        "max_users" : 0,
                        "is_breakout" : False,
                        "meta_data" : {
                            "mock_data": "mock",
                            "another_mock": "mocked"
                        }
                   }

        mapping = map_message_to_db(message)

        self.assertEqual(mapping, expected)

    def test_end_message(self):
        message = {
                      "data": {
                        "type": "event",
                        "id": "meeting-ended",
                        "attributes": {
                          "meeting": {
                            "external-meeting-id": "mock_e",
                            "internal-meeting-id": "mock_i"
                          },
                          "event": {
                            "ts": 0
                          }
                        }
                      }
                  }
        expected = {
                        "external_meeting_id" : "mock_e",
                        "internal_meeting_id" : "mock_i",
                        "end_time": 0
                   }

        mapping = map_message_to_db(message)

        self.assertEqual(mapping, expected)

    def test_join_left_message(self):
        message = [{
                      "data": {
                        "type": "event",
                        "id": "user-joined",
                        "attributes": {
                          "meeting": {
                            "external-meeting-id": "mock_e",
                            "internal-meeting-id": "mock_i"
                          },
                          "user": {
                            "name": "mock_n",
                            "role": "MOCK",
                            "presenter": False,
                            "internal-user-id": "mock_ui",
                            "external-user-id": "mock_ue",
                            "sharing-mic": False,
                            "stream": False,
                            "listening-only": False
                          },
                          "event": {
                            "ts": 0
                          }
                        }
                      }
                    },
                    {
                      "data": {
                        "type": "event",
                        "id": "user-left",
                        "attributes": {
                          "meeting": {
                            "external-meeting-id": "mock_e",
                            "internal-meeting-id": "mock_i"
                          },
                          "user": {
                            "internal-user-id": "mock_ui",
                            "external-user-id": "mock_ue"
                          },
                          "event": {
                            "ts": 0
                          }
                        }
                      }
                    }]
        expected = [{
                        "name" : "mock_n",
                        "role" : "MOCK",
                        "internal_user_id" : "mock_ui",
                        "external_user_id" : "mock_ue",
                        "join_time" : 0
                    },
                    {
                        "internal_user_id" : "mock_ui",
                        "external_user_id" : "mock_ue",
                        "leave_time" : 0
                    }]

        for idx,message in enumerate(message):
            mapping = map_message_to_db(message)

            self.assertEqual(mapping, expected[idx])

    def test_user_message(self):

        message = {
                      "data": {
                        "type": "event",
                        "id": "event_name",
                        "attributes": {
                          "meeting": {
                            "external-meeting-id": "mock_e",
                            "internal-meeting-id": "mock_i"
                          },
                          "user": {
                            "internal-user-id": "mock_ui",
                            "external-user-id": "mock_ue"
                          },
                          "event": {
                            "ts": 0
                          }
                        }
                      }
                   }
        expected = {
                        "internal_user_id" : "mock_ui",
                        "external_user_id" : "mock_ue",
                        "external_meeting_id" : "mock_e",
                        "internal_meeting_id" : "mock_i",
                        "event_name" : "event_name"
                    }
        events = ["user-audio-voice-enabled","user-audio-voice-disabled",
                  "user-audio-listen-only-enabled","user-audio-listen-only-disabled",
                  "user-cam-broadcast-start","user-cam-broadcast-end"]

        for event in events:
            message["data"]["id"] = event
            expected["event_name"] = event

            mapping = map_message_to_db(message)

            self.assertEqual(mapping, expected)

    def test_rap_message(self):
        message = {
                      "data": {
                        "type": "event",
                        "id": "event_name",
                        "attributes": {
                          "meeting": {
                            "external-meeting-id": "mock_e",
                            "internal-meeting-id": "mock_i"
                          },
                          "event": {
                            "ts": 0
                          }
                        }
                      }
                  }
        expected = {
                        "external_meeting_id" : "mock_e",
                        "internal_meeting_id" : "mock_i",
                        "current_step" : "event_name"
                   }
        events = ["rap-archive-started","rap-archive-ended",
                    "rap-sanity-started","rap-sanity-ended",
                    "rap-post-archive-started","rap-post-archive-ended",
                    "rap-process-started","rap-process-ended",
                    "rap-post-process-started","rap-post-process-ended",
                    "rap-publish-started","rap-post-publish-started","rap-post-publish-ended"]

        for event in events:
            message["data"]["id"] = event
            expected["current_step"] = event

            mapping = map_message_to_db(message)

            self.assertEqual(mapping, expected)

        message = {
                        "data": {
                            "type": "event",
                            "id": "rap-publish-ended",
                            "attributes": {
                              "meeting": {
                                "external-meeting-id": "mock_e",
                                "internal-meeting-id": "mock_i"
                              },
                              "recording": {
                                "name": "mock_n",
                                "isBreakout": False,
                                "startTime": 0,
                                "endTime": 0,
                                "size": 0,
                                "rawSize": 0,
                                "metadata":{
                                	"mock_meta": "mocked_meta"
                                },
                                "playback":{
                                	"mock_playback": "mocked_playback"
                                },
                                "download":{
                                	"mock_download": "mocked_download"
                                }
                              },
                              "event": {
                                "ts": 0
                              }
                            }
                      }
                  }
        expected = {
                        "name" : "mock_n",
                        "is_breakout" : False,
                        "start_time" : 0,
                        "end_time" : 0,
                        "size" : 0,
                        "raw_size" : 0,
                        "meta_data" : {
                            "mock_meta": "mocked_meta"
                        },
                        "playback" : {
                            "mock_playback": "mocked_playback"
                        },
                        "download" : {
                            "mock_download": "mocked_download"
                        },
                        "external_meeting_id" : "mock_e",
                        "internal_meeting_id" : "mock_i",
                        "current_step" : "rap-publish-ended"
                   }

        mapping = map_message_to_db(message)

        self.assertEqual(mapping, expected)
