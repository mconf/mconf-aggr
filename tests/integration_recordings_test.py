import copy
import unittest

from tests.integration import IntegrationEngine


class RecordingsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = IntegrationEngine(
            token="my-authorization-token",
            database_uri="postgresql://mconf:postgres@192.168.122.1/mconf",
            delay=2,
        )

    def test_01_meeting_created(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "meeting-created",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864",
                            "external-meeting-id": "random-1625548",
                            "name": "random-1625548",
                            "is-breakout": False,
                            "duration": 0,
                            "create-time": 1535121789863,
                            "create-date": "Fri Aug 24 14:43:09 UTC 2018",
                            "moderator-pass": "mp",
                            "viewer-pass": "ap",
                            "record": True,
                            "voice-conf": "71096",
                            "dial-number": "613-555-1234",
                            "max-users": 0,
                            "metadata": {},
                        }
                    },
                    "event": {"ts": 1535121789919},
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]["data"]["attributes"]["meeting"][
                "internal-meeting-id"
            ]

            (
                meetings,
                meetings_events,
            ) = self.engine.meetings_meetings_events_by_meeting_id(internal_meeting_id)

            self.assertEqual(meetings.running, False)
            self.assertEqual(meetings.has_user_joined, False)
            self.assertEqual(meetings.participant_count, 0)
            self.assertEqual(meetings.listener_count, 0)
            self.assertEqual(meetings.voice_participant_count, 0)
            self.assertEqual(meetings.video_count, 0)
            self.assertEqual(meetings.moderator_count, 0)
            self.assertEqual(meetings.attendees, [])

            self.assertEqual(meetings_events.server_url, "https://localhost")
            self.assertEqual(
                meetings_events.create_time,
                event[0]["data"]["attributes"]["meeting"]["create-time"],
            )
            self.assertEqual(
                meetings_events.create_date,
                event[0]["data"]["attributes"]["meeting"]["create-date"],
            )
            self.assertEqual(meetings_events.start_time, None)
            self.assertEqual(meetings_events.end_time, None)
            self.assertEqual(
                meetings_events.internal_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["internal-meeting-id"],
            )
            self.assertEqual(
                meetings_events.external_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["external-meeting-id"],
            )
            self.assertEqual(
                meetings_events.name, event[0]["data"]["attributes"]["meeting"]["name"]
            )
            self.assertEqual(
                meetings_events.dial_number,
                event[0]["data"]["attributes"]["meeting"]["dial-number"],
            )
            self.assertEqual(
                meetings_events.moderator_pw,
                event[0]["data"]["attributes"]["meeting"]["moderator-pass"],
            )
            self.assertEqual(
                meetings_events.attendee_pw,
                event[0]["data"]["attributes"]["meeting"]["viewer-pass"],
            )
            self.assertEqual(
                meetings_events.recording,
                event[0]["data"]["attributes"]["meeting"]["record"],
            )
            self.assertEqual(meetings_events.has_forcibly_ended, False)
            self.assertEqual(meetings_events.max_users, 0)
            self.assertEqual(meetings_events.is_breakout, False)
            self.assertEqual(meetings_events.unique_users, 0)

            self.__class__.meetings_events = copy.deepcopy(meetings_events)

    def test_02_meeting_ended(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "meeting-ended",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864",
                            "external-meeting-id": "random-1625548",
                        }
                    },
                    "event": {"ts": 1535122177435},
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]["data"]["attributes"]["meeting"][
                "internal-meeting-id"
            ]

            meetings = self.engine.meetings_by_meeting_id(internal_meeting_id)

            self.assertIsNone(meetings)

            meetings_events = self.engine.meetings_events_by_meeting_id(
                internal_meeting_id
            )

            self.assertEqual(
                meetings_events.internal_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["internal-meeting-id"],
            )
            self.assertEqual(
                meetings_events.external_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["external-meeting-id"],
            )

    def test_03_sanity_started(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "rap-sanity-started",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864",
                            "external-meeting-id": "random-1625548",
                        }
                    },
                    "event": {"ts": 1535140287},
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]["data"]["attributes"]["meeting"][
                "internal-meeting-id"
            ]

            recordings = self.engine.recordings_by_meeting_id(internal_meeting_id)

            self.assertEqual(
                recordings.internal_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["internal-meeting-id"],
            )
            self.assertEqual(
                recordings.external_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["external-meeting-id"],
            )
            self.assertEqual(recordings.current_step, "rap-sanity-started")
            self.assertEqual(recordings.published, False)

    def test_04_sanity_ended(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "rap-sanity-ended",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864",
                            "external-meeting-id": "random-1625548",
                        },
                        "success": True,
                        "step-time": 243,
                    },
                    "event": {"ts": 1535140288},
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]["data"]["attributes"]["meeting"][
                "internal-meeting-id"
            ]

            recordings = self.engine.recordings_by_meeting_id(internal_meeting_id)

            self.assertEqual(
                recordings.internal_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["internal-meeting-id"],
            )
            self.assertEqual(
                recordings.external_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["external-meeting-id"],
            )
            self.assertEqual(recordings.current_step, event[0]["data"]["id"])
            self.assertEqual(recordings.published, False)

    def test_05_process_started(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "rap-process-started",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864",
                            "external-meeting-id": "random-1625548",
                        }
                    },
                    "event": {"ts": 1535140318},
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]["data"]["attributes"]["meeting"][
                "internal-meeting-id"
            ]

            recordings = self.engine.recordings_by_meeting_id(internal_meeting_id)

            self.assertEqual(
                recordings.internal_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["internal-meeting-id"],
            )
            self.assertEqual(
                recordings.external_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["external-meeting-id"],
            )
            self.assertEqual(recordings.current_step, event[0]["data"]["id"])
            self.assertEqual(recordings.status, "processing")
            self.assertEqual(recordings.published, False)

    def test_06_process_ended(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "rap-process-ended",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864",
                            "external-meeting-id": "random-1625548",
                        },
                        "success": True,
                        "step-time": 2060,
                    },
                    "event": {"ts": 1535140320},
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]["data"]["attributes"]["meeting"][
                "internal-meeting-id"
            ]

            recordings = self.engine.recordings_by_meeting_id(internal_meeting_id)

            self.assertEqual(
                recordings.internal_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["internal-meeting-id"],
            )
            self.assertEqual(
                recordings.external_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["external-meeting-id"],
            )
            self.assertEqual(recordings.current_step, event[0]["data"]["id"])
            self.assertEqual(recordings.status, "processed")
            self.assertEqual(recordings.published, False)

    def test_07_publish_started(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "rap-publish-started",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864",
                            "external-meeting-id": "random-1625548",
                        }
                    },
                    "event": {"ts": 1535140355},
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]["data"]["attributes"]["meeting"][
                "internal-meeting-id"
            ]

            recordings = self.engine.recordings_by_meeting_id(internal_meeting_id)

            self.assertEqual(
                recordings.internal_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["internal-meeting-id"],
            )
            self.assertEqual(
                recordings.external_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["external-meeting-id"],
            )
            self.assertEqual(recordings.current_step, event[0]["data"]["id"])
            self.assertEqual(recordings.published, False)

    def test_08_publish_ended(self):
        event = [
            {
                "data": {
                    "type": "event",
                    "id": "rap-publish-ended",
                    "attributes": {
                        "meeting": {
                            "internal-meeting-id": "de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864",
                            "external-meeting-id": "random-1625548",
                        },
                        "success": True,
                        "step-time": 480,
                        "recording": {
                            "name": "random-1625548",
                            "isBreakout": "false",
                            "size": 213541,
                            "metadata": {
                                "meetingId": "random-1625548",
                                "meetingName": "random-1625548",
                                "isBreakout": "false",
                            },
                            "playback": {
                                "format": "presentation",
                                "link": "https://felipe.dev.mconf.com/playback/presentation/2.0/playback.html?meetingId=de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864",
                                "processing_time": 2060,
                                "duration": 5663,
                                "extensions": {
                                    "preview": {
                                        "images": {
                                            "image": "https://felipe.dev.mconf.com/presentation/de175d1e1882a8c06b5315c075d03ea730ee73af-1535129295864/presentation/d2d9a672040fbde2a47a10bf6c37b6a4b5ae187f-1535129297162/thumbnails/thumb-1.png"
                                        }
                                    }
                                },
                                "size": 213541,
                            },
                            "download": {},
                        },
                    },
                    "event": {"ts": 1535140356},
                }
            }
        ]

        self.engine.post_and_wait(event)

        with self.engine.database_session():
            internal_meeting_id = event[0]["data"]["attributes"]["meeting"][
                "internal-meeting-id"
            ]

            recordings = self.engine.recordings_by_meeting_id(internal_meeting_id)

            self.assertEqual(
                recordings.internal_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["internal-meeting-id"],
            )
            self.assertEqual(
                recordings.external_meeting_id,
                event[0]["data"]["attributes"]["meeting"]["external-meeting-id"],
            )
            self.assertEqual(recordings.current_step, event[0]["data"]["id"])
            self.assertEqual(recordings.status, "published")
            self.assertEqual(recordings.published, True)
