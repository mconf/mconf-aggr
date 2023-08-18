import unittest
import unittest.mock as mock

from mconf_aggr.webhook.event_mapper import (
    MeetingCreatedEvent,
    MeetingEndedEvent,
    RapPublishEndedEvent,
    RapPublishEvent,
    UserEvent,
    UserJoinedEvent,
    UserLeftEvent,
    UserVoiceEnabledEvent,
    WebhookEvent,
    _get_nested,
    map_webhook_event,
)
from mconf_aggr.webhook.exceptions import (
    InvalidWebhookEventError,
    InvalidWebhookMessageError,
)


class TestMapping(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_missing_event_type(self):
        event = {
            "data": {
                "type": "event",
                "attributes": {"meeting": {}, "event": {"ts": 1502810164922}},
            }
        }

        with self.assertRaises(InvalidWebhookMessageError):
            map_webhook_event(event)

    def test_invalid_event_type(self):
        event = {
            "data": {
                "type": "event",
                "id": "invalid-event",
                "attributes": {"meeting": {}, "event": {"ts": 1502810164922}},
            },
            "server_url": "mocked-server",
        }

        with self.assertRaises(InvalidWebhookEventError):
            map_webhook_event(event)

    def test_map_create_event(self):
        event = {
            "server_url": "localhost",
            "data": {
                "type": "event",
                "id": "meeting-created",
                "attributes": {
                    "meeting": {
                        "external-meeting-id": "mock_e",
                        "internal-meeting-id": "mock_i",
                        "name": "mock_n",
                        "create-time": 0000000,
                        "create-date": "Mock Date",
                        "dial-number": "000-000-0000",
                        "moderator-pass": "mp",
                        "duration": 0,
                        "recording": False,
                        "max-users": 0,
                        "is-breakout": False,
                        "metadata": {"mock_data": "mock", "another_mock": "mocked"},
                    },
                    "event": {"ts": 1502810164922},
                },
            },
        }

        expected = WebhookEvent(
            event_type="meeting-created",
            server_url="localhost",
            event=MeetingCreatedEvent(
                server_url="localhost",
                external_meeting_id="mock_e",
                internal_meeting_id="mock_i",
                parent_meeting_id="",
                name="mock_n",
                create_time=0000000,
                create_date="Mock Date",
                voice_bridge="",
                dial_number="000-000-0000",
                attendee_pw="",
                moderator_pw="mp",
                duration=0,
                recording=False,
                max_users=0,
                is_breakout=False,
                meta_data={"mock_data": "mock", "another_mock": "mocked"},
            ),
        )

        with mock.patch(
            "mconf_aggr.webhook.event_mapper._map_create_event"
        ) as _map_create_event_mock:
            map_webhook_event(event)
            _map_create_event_mock.assert_called_with(
                event, "meeting-created", "localhost"
            )

        got = map_webhook_event(event)

        self.assertEqual(got, expected)

    def test_map_end_event(self):
        event = {
            "server_url": "mocked-server",
            "data": {
                "type": "event",
                "id": "meeting-ended",
                "attributes": {
                    "meeting": {
                        "external-meeting-id": "mock_e",
                        "internal-meeting-id": "mock_i",
                    }
                },
                "event": {"ts": 1502810164922},
            },
        }

        expected = WebhookEvent(
            event_type="meeting-ended",
            server_url="mocked-server",
            event=MeetingEndedEvent(
                external_meeting_id="mock_e",
                internal_meeting_id="mock_i",
                end_time=1502810164922,
            ),
        )

        with mock.patch(
            "mconf_aggr.webhook.event_mapper._map_end_event"
        ) as _map_end_event_mock:
            map_webhook_event(event)
            _map_end_event_mock.assert_called_with(
                event, "meeting-ended", "mocked-server"
            )

        got = map_webhook_event(event)

        self.assertEqual(got, expected)

    def test_map_user_joined_event(self):
        event = {
            "server_url": "mocked-server",
            "data": {
                "type": "event",
                "id": "user-joined",
                "attributes": {
                    "meeting": {
                        "external-meeting-id": "madeup-external-meeting-id",
                        "internal-meeting-id": "madeup-internal-meeting-id",
                    },
                    "user": {
                        "name": "madeup-user",
                        "role": "MODERATOR",
                        "presenter": True,
                        "internal-user-id": "madeup-internal-user-id",
                        "external-user-id": "madeup-external-user-id",
                    },
                },
                "event": {"ts": 1502810164922},
            },
        }

        expected = WebhookEvent(
            event_type="user-joined",
            server_url="mocked-server",
            event=UserJoinedEvent(
                name="madeup-user",
                role="MODERATOR",
                internal_user_id="madeup-internal-user-id",
                external_user_id="madeup-external-user-id",
                internal_meeting_id="madeup-internal-meeting-id",
                external_meeting_id="madeup-external-meeting-id",
                join_time=1502810164922,
                is_presenter=True,
                userdata={},
            ),
        )

        with mock.patch(
            "mconf_aggr.webhook.event_mapper._map_user_joined_event"
        ) as _map_user_joined_event_mock:
            map_webhook_event(event)
            _map_user_joined_event_mock.assert_called_with(
                event, "user-joined", "mocked-server"
            )

        got = map_webhook_event(event)

        self.assertEqual(got, expected)

    def test_map_user_left_event(self):
        event = {
            "server_url": "mocked-server",
            "data": {
                "type": "event",
                "id": "user-left",
                "attributes": {
                    "meeting": {
                        "external-meeting-id": "madeup-external-meeting-id",
                        "internal-meeting-id": "madeup-internal-meeting-id",
                    },
                    "user": {
                        "internal-user-id": "madeup-internal-user-id",
                        "external-user-id": "madeup-external-user-id",
                    },
                },
                "event": {"ts": 1502810164922},
            },
        }

        expected = WebhookEvent(
            event_type="user-left",
            server_url="mocked-server",
            event=UserLeftEvent(
                internal_user_id="madeup-internal-user-id",
                external_user_id="madeup-external-user-id",
                internal_meeting_id="madeup-internal-meeting-id",
                external_meeting_id="madeup-external-meeting-id",
                leave_time=1502810164922,
                userdata={},
            ),
        )

        with mock.patch(
            "mconf_aggr.webhook.event_mapper._map_user_left_event"
        ) as _map_user_left_event_mock:
            map_webhook_event(event)
            _map_user_left_event_mock.assert_called_with(
                event, "user-left", "mocked-server"
            )

        got = map_webhook_event(event)

        self.assertEqual(got, expected)

    def test_map_user_voice_enabled_event(self):
        event = {
            "server_url": "mocked-server",
            "data": {
                "type": "event",
                "id": "user-audio-voice-enabled",
                "attributes": {
                    "meeting": {
                        "internal-meeting-id": "madeup-internal-meeting-id",
                        "external-meeting-id": "madeup-external-meeting-id",
                    },
                    "user": {
                        "internal-user-id": "madeup-internal-user-id",
                        "external-user-id": "madeup-external-user-id",
                        "sharing-mic": False,
                        "listening-only": True,
                    },
                },
                "event": {"ts": 1502810164922},
            },
        }

        expected = WebhookEvent(
            event_type="user-audio-voice-enabled",
            server_url="mocked-server",
            event=UserVoiceEnabledEvent(
                internal_user_id="madeup-internal-user-id",
                external_user_id="madeup-external-user-id",
                internal_meeting_id="madeup-internal-meeting-id",
                external_meeting_id="madeup-external-meeting-id",
                has_joined_voice=False,
                is_listening_only=True,
                event_name="user-audio-voice-enabled",
            ),
        )

        with mock.patch(
            "mconf_aggr.webhook.event_mapper._map_user_voice_enabled_event"
        ) as _map_user_voice_enabled_event_mock:
            map_webhook_event(event)
            _map_user_voice_enabled_event_mock.assert_called_with(
                event, "user-audio-voice-enabled", "mocked-server"
            )

        got = map_webhook_event(event)

        self.assertEqual(got, expected)

    def test_map_user_event(self):
        event = {
            "server_url": "mocked-server",
            "data": {
                "type": "event",
                "id": "user-audio-voice-disabled",
                "attributes": {
                    "meeting": {
                        "internal-meeting-id": "madeup-internal-meeting-id",
                        "external-meeting-id": "madeup-external-meeting-id",
                    },
                    "user": {
                        "internal-user-id": "madeup-internal-user-id",
                        "external-user-id": "madeup-external-user-id",
                    },
                },
                "event": {"ts": 1502810164922},
            },
        }

        expected = WebhookEvent(
            event_type="user-audio-voice-disabled",
            server_url="mocked-server",
            event=UserEvent(
                internal_user_id="madeup-internal-user-id",
                external_user_id="madeup-external-user-id",
                internal_meeting_id="madeup-internal-meeting-id",
                external_meeting_id="madeup-external-meeting-id",
                event_name="user-audio-voice-disabled",
            ),
        )

        with mock.patch(
            "mconf_aggr.webhook.event_mapper._map_user_event"
        ) as _map_user_event_mock:
            map_webhook_event(event)
            _map_user_event_mock.assert_called_with(
                event, "user-audio-voice-disabled", "mocked-server"
            )

        got = map_webhook_event(event)

        self.assertEqual(got, expected)

    def test_map_rap_publish_ended_event(self):
        event = {
            "server_url": "mocked-server",
            "data": {
                "type": "event",
                "id": "rap-publish-ended",
                "attributes": {
                    "meeting": {
                        "internal-meeting-id": "madeup-internal-meeting-id",
                        "external-meeting-id": "madeup-external-meeting-id",
                    },
                    "record-id": "madeup-internal-meeting-id",
                    "success": True,
                    "step-time": 480,
                    "recording": {
                        "name": "madeup-recording-name",
                        "isBreakout": False,
                        "size": 213541,
                        "raw-size": 213542,
                        "start-time": 1,
                        "end-time": 2,
                        "metadata": {
                            "meetingId": "madeup-external-meeting-id",
                            "meetingName": "madeup-external-meeting-id",
                            "isBreakout": False,
                        },
                        "playback": {
                            "format": "presentation",
                            "link": "madeup-link",
                            "processing_time": 2060,
                            "duration": 5663,
                            "extensions": {
                                "preview": {"images": {"image": "madeup-image-link"}}
                            },
                            "size": 213541,
                        },
                        "download": {},
                    },
                },
                "event": {"ts": 1502810164922},
            },
        }

        expected = WebhookEvent(
            event_type="rap-publish-ended",
            server_url="mocked-server",
            event=RapPublishEndedEvent(
                name="madeup-recording-name",
                is_breakout=False,
                start_time=1,
                end_time=2,
                size=213541,
                raw_size=213542,
                meta_data={
                    "meetingId": "madeup-external-meeting-id",
                    "meetingName": "madeup-external-meeting-id",
                    "isBreakout": False,
                },
                playback={
                    "format": "presentation",
                    "link": "madeup-link",
                    "processing_time": 2060,
                    "duration": 5663,
                    "extensions": {
                        "preview": {"images": {"image": "madeup-image-link"}}
                    },
                    "size": 213541,
                },
                download={},
                workflow={},
                external_meeting_id="madeup-external-meeting-id",
                internal_meeting_id="madeup-internal-meeting-id",
                record_id="madeup-internal-meeting-id",
                current_step="rap-publish-ended",
            ),
        )

        with mock.patch(
            "mconf_aggr.webhook.event_mapper._map_rap_publish_ended_event"
        ) as _map_rap_publish_ended_event_mock:
            map_webhook_event(event)
            _map_rap_publish_ended_event_mock.assert_called_with(
                event, "rap-publish-ended", "mocked-server"
            )

        got = map_webhook_event(event)

        self.assertEqual(got, expected)

    def test_map_rap_event(self):
        event = {
            "server_url": "mocked-server",
            "data": {
                "type": "event",
                "id": "rap-publish-started",
                "attributes": {
                    "meeting": {
                        "internal-meeting-id": "madeup-internal-meeting-id",
                        "external-meeting-id": "madeup-external-meeting-id",
                    },
                    "record-id": "madeup-record-id",
                },
                "event": {"ts": 1502810164922},
            },
        }

        expected = WebhookEvent(
            event_type="rap-publish-started",
            server_url="mocked-server",
            event=RapPublishEvent(
                external_meeting_id="madeup-external-meeting-id",
                internal_meeting_id="madeup-internal-meeting-id",
                record_id="madeup-record-id",
                current_step="rap-publish-started",
                workflow={},
            ),
        )

        with mock.patch(
            "mconf_aggr.webhook.event_mapper._map_rap_publish_event"
        ) as _map_rap_event_mock:
            map_webhook_event(event)
            _map_rap_event_mock.assert_called_with(
                event, "rap-publish-started", "mocked-server"
            )

        got = map_webhook_event(event)

        self.assertEqual(got, expected)

    def test_get_nested(self):
        d = {}
        expected = ""
        got = _get_nested(d, ["key1"], "")

        self.assertEqual(got, expected)

        d = {"key1": "value1", "key2": True}
        expected = "value1"
        got = _get_nested(d, ["key1"], "")

        self.assertEqual(got, expected)

        d = {"key1": {"key2": {"key3": "value3"}}, "key4": True}
        expected = "value3"
        got = _get_nested(d, ["key1", "key2", "key3"], "")

        self.assertEqual(got, expected)

        d = {"key1": {"key2": {"key3": "value3"}}, "key4": False}
        expected = True
        got = _get_nested(d, ["key1", "key2", "key5"], True)

        self.assertEqual(got, expected)

        d = {"key1": {"key2": {"key3": "value3"}}, "key4": False}
        expected = {"key3": "value3"}
        got = _get_nested(d, ["key1", "key2"], True)

        self.assertEqual(got, expected)
