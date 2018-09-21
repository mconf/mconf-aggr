import copy
import unittest

from tests.integration import IntegrationEngine


class UseCaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = IntegrationEngine(
            token="my-authorization-token",
            database_uri="postgresql://mconf:postgres@192.168.122.1/mconf",
            delay=1
        )

    def test_01_create_meeting(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "meeting-created",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036",
                            "name": "random-8730036",
                            "is-breakout": False,
                            "duration": 0,
                            "create-time": 1535121789863,
                            "create-date": "Fri Aug 24 14:43:09 UTC 2018",
                            "moderator-pass": "mp",
                            "viewer-pass": "ap",
                            "record": False,
                            "voice-conf": "71096",
                            "dial-number": "613-555-1234",
                            "max-users": 0,
                            "metadata": {}
                        }
                    },
                    "event": {
                        "ts": 1535121789919
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']

            meetings, meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            self.assertEqual(meetings.running, False)
            self.assertEqual(meetings.has_user_joined, False)
            self.assertEqual(meetings.participant_count, 0)
            self.assertEqual(meetings.listener_count, 0)
            self.assertEqual(meetings.voice_participant_count, 0)
            self.assertEqual(meetings.video_count, 0)
            self.assertEqual(meetings.moderator_count, 0)
            self.assertEqual(meetings.attendees, [])

            self.assertEqual(meetings_events.server_url, "https://localhost")
            self.assertEqual(meetings_events.create_time, event[0]['data']['attributes']['meeting']['create-time'])
            self.assertEqual(meetings_events.create_date, event[0]['data']['attributes']['meeting']['create-date'])
            self.assertEqual(meetings_events.start_time, None)
            self.assertEqual(meetings_events.end_time, None)
            self.assertEqual(meetings_events.internal_meeting_id, event[0]['data']['attributes']['meeting']['internal-meeting-id'])
            self.assertEqual(meetings_events.external_meeting_id, event[0]['data']['attributes']['meeting']['external-meeting-id'])
            self.assertEqual(meetings_events.name, event[0]['data']['attributes']['meeting']['name'])
            self.assertEqual(meetings_events.dial_number, event[0]['data']['attributes']['meeting']['dial-number'])
            self.assertEqual(meetings_events.moderator_pw, event[0]['data']['attributes']['meeting']['moderator-pass'])
            self.assertEqual(meetings_events.attendee_pw, event[0]['data']['attributes']['meeting']['viewer-pass'])
            self.assertEqual(meetings_events.recording, event[0]['data']['attributes']['meeting']['record'])
            self.assertEqual(meetings_events.has_forcibly_ended, False)
            self.assertEqual(meetings_events.max_users, 0)
            self.assertEqual(meetings_events.is_breakout, False)
            self.assertEqual(meetings_events.unique_users, 0)

            self.__class__.meetings_events = copy.deepcopy(meetings_events)

    def test_02_first_user_joined(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "user-joined",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        },
                        "user": {
                            "internal-user-id": "w_lf51uvwvgqya",
                            "external-user-id": "w_lf51uvwvgqya",
                            "name": "User 4650358",
                            "role": "MODERATOR",
                            "presenter": False
                        }
                    },
                    "event": {
                        "ts": 1535121816114
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']
            internal_user_id = event[0]['data']['attributes']['user']['internal-user-id']

            users_events, users_meetings_events = self.engine.users_meetings_events_by_user_id(internal_user_id)
            meetings, meetings_meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            self.assertEqual(users_meetings_events, meetings_meetings_events)

            self.assertEqual(users_events.name, event[0]['data']['attributes']['user']['name'])
            self.assertEqual(users_events.internal_user_id, event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(users_events.external_user_id, event[0]['data']['attributes']['user']['external-user-id'])
            self.assertEqual(users_events.role, event[0]['data']['attributes']['user']['role'])
            self.assertEqual(users_events.join_time, event[0]['data']['event']['ts'])
            self.assertEqual(users_events.leave_time, None)
            self.assertEqual(users_events.meta_data, None)

            self.assertEqual(meetings.running, True)
            self.assertEqual(meetings.has_user_joined, True)
            self.assertEqual(meetings.participant_count, 1)
            self.assertEqual(meetings.listener_count, 0)
            self.assertEqual(meetings.voice_participant_count, 0)
            self.assertEqual(meetings.video_count, 0)
            self.assertEqual(meetings.moderator_count, 1)

            attendees = meetings.attendees

            self.assertEqual(len(attendees), 1)
            self.assertEqual(attendees[0]['internal_user_id'], event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(attendees[0]['external_user_id'], event[0]['data']['attributes']['user']['external-user-id'])
            self.assertEqual(attendees[0]['full_name'], event[0]['data']['attributes']['user']['name'])
            self.assertEqual(attendees[0]['role'], event[0]['data']['attributes']['user']['role'])
            self.assertEqual(attendees[0]['is_presenter'], event[0]['data']['attributes']['user']['presenter'])
            self.assertEqual(attendees[0]['is_listening_only'], False)
            self.assertEqual(attendees[0]['has_joined_voice'], False)
            self.assertEqual(attendees[0]['has_video'], False)

            self.assertEqual(users_meetings_events.unique_users, 1)
            self.assertEqual(users_meetings_events.start_time, event[0]['data']['event']['ts'])

    def test_03_second_user_joined(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "user-joined",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        },
                        "user": {
                            "internal-user-id": "w_lf51uvwvgqya2",
                            "external-user-id": "w_lf51uvwvgqya2",
                            "name": "User 46503582",
                            "role": "MODERATOR",
                            "presenter": True
                        }
                    },
                    "event": {
                        "ts": 1535121816117
                    }
                }
            }
        ]


        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']
            internal_user_id = event[0]['data']['attributes']['user']['internal-user-id']

            users_events, users_meetings_events = self.engine.users_meetings_events_by_user_id(internal_user_id)
            meetings, meetings_meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            self.assertEqual(users_meetings_events, meetings_meetings_events)

            self.assertEqual(users_events.name, event[0]['data']['attributes']['user']['name'])
            self.assertEqual(users_events.internal_user_id, event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(users_events.external_user_id, event[0]['data']['attributes']['user']['external-user-id'])
            self.assertEqual(users_events.role, event[0]['data']['attributes']['user']['role'])
            self.assertEqual(users_events.join_time, event[0]['data']['event']['ts'])
            self.assertEqual(users_events.leave_time, None)
            self.assertEqual(users_events.meta_data, None)

            self.assertEqual(meetings.running, True)
            self.assertEqual(meetings.has_user_joined, True)
            self.assertEqual(meetings.participant_count, 2)
            self.assertEqual(meetings.listener_count, 0)
            self.assertEqual(meetings.voice_participant_count, 0)
            self.assertEqual(meetings.video_count, 0)
            self.assertEqual(meetings.moderator_count, 2)

            attendees = meetings.attendees

            self.assertEqual(len(attendees), 2)
            self.assertEqual(attendees[1]['internal_user_id'], event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(attendees[1]['external_user_id'], event[0]['data']['attributes']['user']['external-user-id'])
            self.assertEqual(attendees[1]['full_name'], event[0]['data']['attributes']['user']['name'])
            self.assertEqual(attendees[1]['role'], event[0]['data']['attributes']['user']['role'])
            self.assertEqual(attendees[1]['is_presenter'], event[0]['data']['attributes']['user']['presenter'])
            self.assertEqual(attendees[1]['is_listening_only'], False)
            self.assertEqual(attendees[1]['has_joined_voice'], False)
            self.assertEqual(attendees[1]['has_video'], False)

            self.assertEqual(users_meetings_events.unique_users, 2)

    def test_04_first_user_audio_enabled(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "user-audio-voice-enabled",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        },
                        "user": {
                            "internal-user-id": "w_lf51uvwvgqya",
                            "external-user-id": "w_lf51uvwvgqya",
                            "sharing-mic": False,
                            "listening-only": True
                        }
                    },
                    "event": {
                        "ts": 1535043770795
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']
            internal_user_id = event[0]['data']['attributes']['user']['internal-user-id']

            users_events, users_meetings_events = self.engine.users_meetings_events_by_user_id(internal_user_id)
            meetings, meetings_meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            attendees = meetings.attendees

            self.assertEqual(users_meetings_events, meetings_meetings_events)

            self.assertEqual(users_events.internal_user_id, event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(users_events.external_user_id, event[0]['data']['attributes']['user']['external-user-id'])

            self.assertEqual(meetings.running, True)
            self.assertEqual(meetings.has_user_joined, True)
            self.assertEqual(meetings.participant_count, 2)
            self.assertEqual(meetings.listener_count, 1)
            self.assertEqual(meetings.voice_participant_count, 0)
            self.assertEqual(meetings.video_count, 0)
            self.assertEqual(meetings.moderator_count, 2)

            self.assertEqual(attendees[0]["is_presenter"], False)
            self.assertEqual(attendees[0]["is_listening_only"], True)
            self.assertEqual(attendees[0]["has_joined_voice"], False)
            self.assertEqual(attendees[0]["has_video"], False)

    def test_05_second_user_audio_enabled(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "user-audio-voice-enabled",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        },
                        "user": {
                            "internal-user-id": "w_lf51uvwvgqya2",
                            "external-user-id": "w_lf51uvwvgqya2",
                            "sharing-mic": True,
                            "listening-only": True
                        }
                    },
                    "event": {
                        "ts": 1535043770798
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']
            internal_user_id = event[0]['data']['attributes']['user']['internal-user-id']

            users_events, users_meetings_events = self.engine.users_meetings_events_by_user_id(internal_user_id)
            meetings, meetings_meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            attendees = meetings.attendees

            self.assertEqual(users_meetings_events, meetings_meetings_events)

            self.assertEqual(users_events.internal_user_id, event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(users_events.external_user_id, event[0]['data']['attributes']['user']['external-user-id'])

            self.assertEqual(meetings.running, True)
            self.assertEqual(meetings.has_user_joined, True)
            self.assertEqual(meetings.participant_count, 2)
            self.assertEqual(meetings.listener_count, 2)
            self.assertEqual(meetings.voice_participant_count, 1)
            self.assertEqual(meetings.video_count, 0)
            self.assertEqual(meetings.moderator_count, 2)

            self.assertEqual(attendees[1]["is_presenter"], True)
            self.assertEqual(attendees[1]["is_listening_only"], True)
            self.assertEqual(attendees[1]["has_joined_voice"], True)
            self.assertEqual(attendees[1]["has_video"], False)

    def test_06_first_user_presenter_assigned(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "user-presenter-assigned",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        },
                        "user": {
                            "internal-user-id": "w_lf51uvwvgqya",
                            "external-user-id": "w_lf51uvwvgqya"
                        }
                    },
                    "event": {
                        "ts": 1535043770803
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']
            internal_user_id = event[0]['data']['attributes']['user']['internal-user-id']

            users_events, users_meetings_events = self.engine.users_meetings_events_by_user_id(internal_user_id)
            meetings, meetings_meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            attendees = meetings.attendees

            self.assertEqual(users_meetings_events, meetings_meetings_events)

            self.assertEqual(users_events.internal_user_id, event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(users_events.external_user_id, event[0]['data']['attributes']['user']['external-user-id'])

            self.assertEqual(attendees[1]["is_presenter"], True)

    def test_07_first_user_presenter_unassigned(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "user-presenter-unassigned",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        },
                        "user": {
                            "internal-user-id": "w_lf51uvwvgqya",
                            "external-user-id": "w_lf51uvwvgqya"
                        }
                    },
                    "event": {
                        "ts": 1535043770806
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']
            internal_user_id = event[0]['data']['attributes']['user']['internal-user-id']

            users_events, users_meetings_events = self.engine.users_meetings_events_by_user_id(internal_user_id)
            meetings, meetings_meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            attendees = meetings.attendees

            self.assertEqual(users_meetings_events, meetings_meetings_events)

            self.assertEqual(users_events.internal_user_id, event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(users_events.external_user_id, event[0]['data']['attributes']['user']['external-user-id'])

            self.assertEqual(attendees[0]["is_presenter"], False)

    def test_08_first_user_left(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "user-left",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        },
                        "user": {
                            "internal-user-id": "w_lf51uvwvgqya",
                            "external-user-id": "w_lf51uvwvgqya"
                        }
                    },
                    "event": {
                        "ts": 1535122111181
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']
            internal_user_id = event[0]['data']['attributes']['user']['internal-user-id']

            users_events, users_meetings_events = self.engine.users_meetings_events_by_user_id(internal_user_id)
            meetings, meetings_meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            self.assertEqual(users_meetings_events, meetings_meetings_events)

            self.assertEqual(users_events.internal_user_id, event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(users_events.external_user_id, event[0]['data']['attributes']['user']['external-user-id'])
            self.assertEqual(users_events.leave_time, event[0]['data']['event']['ts'])
            self.assertEqual(users_events.meta_data, None)

            self.assertEqual(meetings.running, True)
            self.assertEqual(meetings.has_user_joined, True)
            self.assertEqual(meetings.participant_count, 1)
            self.assertEqual(meetings.listener_count, 1)
            self.assertEqual(meetings.voice_participant_count, 1)
            self.assertEqual(meetings.video_count, 0)
            self.assertEqual(meetings.moderator_count, 1)

            attendees = meetings.attendees

            self.assertEqual(len(attendees), 1)

    def test_09_second_user_presenter_unassigned(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "user-presenter-unassigned",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        },
                        "user": {
                            "internal-user-id": "w_lf51uvwvgqya2",
                            "external-user-id": "w_lf51uvwvgqya2"
                        }
                    },
                    "event": {
                        "ts": 1535122111184
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']
            internal_user_id = event[0]['data']['attributes']['user']['internal-user-id']

            users_events, users_meetings_events = self.engine.users_meetings_events_by_user_id(internal_user_id)
            meetings, meetings_meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            attendees = meetings.attendees

            self.assertEqual(users_meetings_events, meetings_meetings_events)

            self.assertEqual(users_events.internal_user_id, event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(users_events.external_user_id, event[0]['data']['attributes']['user']['external-user-id'])

            self.assertEqual(attendees[0]["is_presenter"], False) # Second user is now the first in the list.

    def test_10_second_user_left(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "user-left",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        },
                        "user": {
                            "internal-user-id": "w_lf51uvwvgqya2",
                            "external-user-id": "w_lf51uvwvgqya2"
                        }
                    },
                    "event": {
                        "ts": 1535122111184
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']
            internal_user_id = event[0]['data']['attributes']['user']['internal-user-id']

            users_events, users_meetings_events = self.engine.users_meetings_events_by_user_id(internal_user_id)
            meetings, meetings_meetings_events = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            self.assertEqual(users_meetings_events, meetings_meetings_events)

            self.assertEqual(users_events.internal_user_id, event[0]['data']['attributes']['user']['internal-user-id'])
            self.assertEqual(users_events.external_user_id, event[0]['data']['attributes']['user']['external-user-id'])
            self.assertEqual(users_events.leave_time, event[0]['data']['event']['ts'])
            self.assertEqual(users_events.meta_data, None)

            self.assertEqual(meetings.running, True)
            self.assertEqual(meetings.has_user_joined, False)
            self.assertEqual(meetings.participant_count, 0)
            self.assertEqual(meetings.listener_count, 0)
            self.assertEqual(meetings.voice_participant_count, 0)
            self.assertEqual(meetings.video_count, 0)
            self.assertEqual(meetings.moderator_count, 0)

            attendees = meetings.attendees

            self.assertEqual(len(attendees), 0)

    def test_11_meeting_ended(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "meeting-ended",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "988edd8ea0726f2276ef93d9d0a1db4b96633117-1535121789863",
                            "external-meeting-id": "random-8730036"
                        }
                    },
                    "event": {
                        "ts": 1535122177435
                    }
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]['data']['attributes']['meeting']['internal-meeting-id']

            meetings = self.engine.meetings_by_meeting_id(internal_meeting_id)

            self.assertIsNone(meetings)

            meetings_events = self.engine.meetings_events_by_meeting_id(internal_meeting_id)

            self.assertEqual(meetings_events.internal_meeting_id, event[0]['data']['attributes']['meeting']['internal-meeting-id'])
            self.assertEqual(meetings_events.external_meeting_id, event[0]['data']['attributes']['meeting']['external-meeting-id'])

            self.__class__.meetings_events.unique_users = meetings_events.unique_users
