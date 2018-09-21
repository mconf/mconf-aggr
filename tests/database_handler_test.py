import json
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock, call

import sqlalchemy

from mconf_aggr.aggregator.aggregator import CallbackError
from mconf_aggr.webhook.database_handler import *
from mconf_aggr.webhook.event_mapper import *
from mconf_aggr.webhook.exceptions import WebhookDatabaseError, InvalidWebhookEventError
from mconf_aggr.webhook.database_model import Meetings, MeetingsEvents

class SessionMock(mock.Mock):
    def get_first_add_arg(self):
        args, kwargs = self.add.call_args

        return args[0]

    def get_first_delete_arg(self):
        args, kwargs = self.delete.call_args

        return args[0]

class TestMeetingCreatedHandler(unittest.TestCase):
    def setUp(self):
        session_mock = SessionMock()

        self.handler = MeetingCreatedHandler(session_mock)

        self.event = WebhookEvent(
            event_type="meeting-created",
            event=MeetingCreatedEvent(
                server_url="localhost",
                external_meeting_id="mock_e",
                internal_meeting_id="mock_i",
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
                meta_data={
                    "mock_data": "mock",
                    "another_mock": "mocked"
                }
            )
        )

    def test_meeting_created_handle(self):
        self.handler.handle(self.event)

        meetings = self.handler.session.get_first_add_arg()
        meetings_events = meetings.meeting_event

        self.handler.session.add.assert_called_once()

        self.assertIsInstance(meetings, Meetings)
        self.assertIsInstance(meetings_events, MeetingsEvents)

        self.assertEqual(meetings.running, False)
        self.assertEqual(meetings.has_user_joined, False)
        self.assertEqual(meetings.participant_count, 0)
        self.assertEqual(meetings.listener_count, 0)
        self.assertEqual(meetings.voice_participant_count, 0)
        self.assertEqual(meetings.video_count, 0)
        self.assertEqual(meetings.moderator_count, 0)
        self.assertEqual(meetings.attendees, [])

        self.assertEqual(meetings_events.server_url, "localhost")
        self.assertEqual(meetings_events.external_meeting_id, "mock_e")
        self.assertEqual(meetings_events.internal_meeting_id, "mock_i")
        self.assertEqual(meetings_events.name, "mock_n")
        self.assertEqual(meetings_events.create_time, 0)
        self.assertEqual(meetings_events.create_date, "Mock Date")
        self.assertEqual(meetings_events.voice_bridge, "")
        self.assertEqual(meetings_events.dial_number, "000-000-0000")
        self.assertEqual(meetings_events.attendee_pw, "")
        self.assertEqual(meetings_events.moderator_pw, "mp")
        self.assertEqual(meetings_events.duration, 0)
        self.assertEqual(meetings_events.recording, False)
        self.assertEqual(meetings_events.max_users, 0)
        self.assertEqual(meetings_events.is_breakout, False)
        self.assertEqual(meetings_events.meta_data, {"mock_data": "mock", "another_mock": "mocked"})


class TestMeetingEndedHandler(unittest.TestCase):
    def setUp(self):
        session_mock = SessionMock()

        self.handler = MeetingEndedHandler(session_mock)

        self.event = WebhookEvent(
            event_type="meeting-ended",
            event=MeetingEndedEvent(
                external_meeting_id="mock_e",
                internal_meeting_id="mock_i",
                end_time=1502810164922
            )
        )

    def test_meeting_ended_no_meeting_event(self):
        self.handler.session.query().filter().first.return_value = None

        self.handler.handle(self.event)

        self.handler.session.add.assert_not_called()

    def test_meeting_ended_no_meeting(self):
        meetings_events = MeetingsEvents(
            server_url="localhost",
            external_meeting_id="mock_e",
            internal_meeting_id="mock_i",
            name="mock_n",
            create_time=0,
            create_date="Mock Date",
            voice_bridge="",
            dial_number="000-000-0000",
            attendee_pw="",
            moderator_pw="mp",
            duration=0,
            recording=False,
            max_users=0,
            is_breakout=False,
            meta_data={"mock_data": "mock", "another_mock": "mocked"}
        )

        self.handler.session.query().filter().first.return_value = meetings_events
        self.handler.session.query().get.return_value = meetings_events
        self.handler.session.query().join().filter().first.return_value = None

        self.handler.handle(self.event)

        self.handler.session.delete.assert_not_called()

    def test_meeting_ended_succeeds(self):
        meetings_events = MeetingsEvents(
            server_url="localhost",
            external_meeting_id="mock_e",
            internal_meeting_id="mock_i",
            name="mock_n",
            create_time=0,
            create_date="Mock Date",
            voice_bridge="",
            dial_number="000-000-0000",
            attendee_pw="",
            moderator_pw="mp",
            duration=0,
            recording=False,
            max_users=0,
            is_breakout=False,
            meta_data={"mock_data": "mock", "another_mock": "mocked"}
        )

        meetings = Meetings(
            running=False,
            has_user_joined=False,
            participant_count=0,
            listener_count=0,
            voice_participant_count=0,
            video_count=0,
            moderator_count=0,
            attendees=[]
        )

        self.handler.session.query().filter().first.return_value = meetings_events
        self.handler.session.query().get = mock.Mock(side_effect=[meetings_events, meetings])

        self.handler.handle(self.event)

        meetings_events = self.handler.session.get_first_add_arg()
        meetings = self.handler.session.get_first_delete_arg()

        self.assertEqual(meetings_events.end_time, self.event.event.end_time)

        self.handler.session.add.assert_called_once_with(meetings_events)
        self.handler.session.delete.assert_called_once_with(meetings)


class TestUserJoinedHandler(unittest.TestCase):
    def setUp(self):
        session_mock = SessionMock()

        self.handler = UserJoinedHandler(session_mock)

        self.event = WebhookEvent(
            event_type="user-joined",
            event=UserJoinedEvent(
                name="madeup-user",
                role="MODERATOR",
                internal_user_id="madeup-internal-user-id",
                external_user_id="madeup-external-user-id",
                internal_meeting_id="madeup-internal-meeting-id",
                external_meeting_id="madeup-external-meeting-id",
                join_time=1502810164922,
                is_presenter=True,
                meta_data={}
            )
        )

    def test_get_users_events(self):
        users_events = self.handler._get_users_events(self.event.event)

        self.assertIsInstance(users_events, UsersEvents)

        self.assertEqual(users_events.name, self.event.event.name)
        self.assertEqual(users_events.role, self.event.event.role)
        self.assertEqual(users_events.join_time, self.event.event.join_time)
        self.assertEqual(users_events.internal_user_id, self.event.event.internal_user_id)
        self.assertEqual(users_events.external_user_id, self.event.event.external_user_id)

    def test_user_joined_no_meeting_event(self):
        self.handler.session.query().filter().first.return_value = None

        self.handler.handle(self.event)

        self.handler.session.add.assert_not_called()
        self.handler.session.flush.assert_not_called()

    def test_user_joined_no_meeting(self):
        meetings_events = MeetingsEvents(
            server_url="localhost",
            external_meeting_id="mock_e",
            internal_meeting_id="mock_i",
            name="mock_n",
            create_time=0,
            create_date="Mock Date",
            voice_bridge="",
            dial_number="000-000-0000",
            attendee_pw="",
            moderator_pw="mp",
            duration=0,
            recording=False,
            max_users=0,
            is_breakout=False,
            meta_data={"mock_data": "mock", "another_mock": "mocked"}
        )

        self.handler.session.query().filter().first.return_value = meetings_events

        self.handler.session.query().join().filter().first.return_value = None

        with self.assertRaises(WebhookDatabaseError):
            self.handler.handle(self.event)

    def test_user_joined_succeeds(self):
        meetings_events = MeetingsEvents(
            server_url="localhost",
            external_meeting_id="mock_e",
            internal_meeting_id="mock_i",
            name="mock_n",
            create_time=0,
            create_date="Mock Date",
            voice_bridge="",
            dial_number="000-000-0000",
            attendee_pw="",
            moderator_pw="mp",
            duration=0,
            recording=False,
            max_users=0,
            is_breakout=False,
            meta_data={"mock_data": "mock", "another_mock": "mocked"}
        )

        meetings = Meetings(
            running=False,
            has_user_joined=False,
            participant_count=0,
            listener_count=0,
            voice_participant_count=0,
            video_count=0,
            moderator_count=0,
            attendees=[]
        )

        self.handler.session.query().filter().first.return_value = meetings_events
        self.handler.session.query().join().filter().first.return_value = meetings
        self.handler.session.query().get.return_value = meetings

        self.handler.handle(self.event)

        self.assertEqual(self.handler.session.add.call_count, 3)
        self.handler.session.flush.assert_called_once()


class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.session_mock = mock.Mock()
        self.data_processor = DataProcessor(self.session_mock)

    def test_select_meeting_created(self):
        event_handler = self.data_processor._select_handler("meeting-created")

        self.assertIsInstance(event_handler, MeetingCreatedHandler)

    def test_select_user_joined(self):
        event_handler = self.data_processor._select_handler("user-joined")

        self.assertIsInstance(event_handler, UserJoinedHandler)

    def test_select_user_left(self):
        event_handler = self.data_processor._select_handler("user-left")

        self.assertIsInstance(event_handler, UserLeftHandler)

    def test_select_meeting_ended(self):
        event_handler = self.data_processor._select_handler("meeting-ended")

        self.assertIsInstance(event_handler, MeetingEndedHandler)

    def test_select_user_audio_voice_enabled(self):
        event_handler = self.data_processor._select_handler("user-audio-voice-enabled")

        self.assertIsInstance(event_handler, UserVoiceEnabledHandler)

    def test_select_user_audio_listen_only_enabled(self):
        event_handler = self.data_processor._select_handler("user-audio-listen-only-enabled")

        self.assertIsInstance(event_handler, UserListenOnlyEnabledHandler)

    def test_select_user_audio_listen_only_disabled(self):
        event_handler = self.data_processor._select_handler("user-audio-listen-only-disabled")

        self.assertIsInstance(event_handler, UserListenOnlyDisabledHandler)

    def test_select_user_audio_voice_disabled(self):
        event_handler = self.data_processor._select_handler("user-audio-voice-disabled")

        self.assertIsInstance(event_handler, UserVoiceDisabledHandler)

    def test_select_user_cam_broadcast_start(self):
        event_handler = self.data_processor._select_handler("user-cam-broadcast-start")

        self.assertIsInstance(event_handler, UserCamBroadcastStartHandler)

    def test_select_user_cam_broadcast_end(self):
        event_handler = self.data_processor._select_handler("user-cam-broadcast-end")

        self.assertIsInstance(event_handler, UserCamBroadcastEndHandler)

    def test_select_user_presenter_assigned(self):
        event_handler = self.data_processor._select_handler("user-presenter-assigned")

        self.assertIsInstance(event_handler, UserPresenterAssignedHandler)

    def test_select_user_presenter_unassigned(self):
        event_handler = self.data_processor._select_handler("user-presenter-unassigned")

        self.assertIsInstance(event_handler, UserPresenterUnassignedHandler)

    def test_select_user_presenter_(self):
        for event_type in ["rap-archive-started", "rap-archive-ended",
                    "rap-sanity-started", "rap-sanity-ended",
                    "rap-post-archive-started", "rap-post-archive-ended",
                    "rap-process-started", "rap-process-ended",
                    "rap-post-process-started", "rap-post-process-ended",
                    "rap-publish-started", "rap-publish-ended",
                    "rap-post-publish-started", "rap-post-publish-ended"]:
                    event_handler = self.data_processor._select_handler(event_type)

                    self.assertIsInstance(event_handler, RapHandler)

    def test_select_invalid_event_type(self):
        with self.assertRaises(InvalidWebhookEventError):
            event_handler = self.data_processor._select_handler("invalid-event-type")

    def test_select_handler_called(self):
        event = WebhookEvent(event_type="valid-event-type", event=None)
        self.data_processor._select_handler = mock.MagicMock()
        self.data_processor.update(event)

        self.data_processor._select_handler.assert_called_once_with(event.event_type)

    def test_handle_called(self):
        event = WebhookEvent(event_type="valid-event-type", event=None)
        handler_mock = mock.Mock()
        handler_mock.handle = mock.MagicMock()
        self.data_processor._select_handler = mock.MagicMock(return_value=handler_mock)

        self.data_processor.update(event)

        handler_mock.handle.assert_called_once_with(event)


class TestWebhookDataWriter(unittest.TestCase):
    def setUp(self):
        self.connector_mock = mock.Mock()
        self.webhook_data_writer = WebhookDataWriter(connector=self.connector_mock)

    def test_setup_connect(self):
        self.webhook_data_writer.connector.connect = mock.MagicMock()
        self.webhook_data_writer.setup()

        self.webhook_data_writer.connector.connect.assert_called_once_with()

    def test_teardown_close(self):
        self.webhook_data_writer.connector.close = mock.MagicMock()
        self.webhook_data_writer.teardown()

        self.webhook_data_writer.connector.close.assert_called_once_with()

    def test_run_called_with_data(self):
        self.connector_mock.update = mock.MagicMock()

        self.webhook_data_writer.run({})
        self.connector_mock.update.assert_called_with({})

        self.webhook_data_writer.run(None)
        self.connector_mock.update.assert_called_with(None)

    def test_run_operational_error(self):
        self.connector_mock.update = mock.MagicMock(side_effect=sqlalchemy.exc.OperationalError(None, None, None))

        with self.assertRaises(CallbackError):
            self.webhook_data_writer.run(None)

    def test_run_webhook_database_error(self):
        self.connector_mock.update = mock.MagicMock(side_effect=WebhookDatabaseError)

        with self.assertRaises(CallbackError):
            self.webhook_data_writer.run(None)

    def test_run_exception(self):
        self.connector_mock.update = mock.MagicMock(side_effect=Exception)

        with self.assertRaises(CallbackError):
            self.webhook_data_writer.run(None)


class TestPostgresConnector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg.config = {
            "webhook": {
                "database": {
                    "user": "madeup-user",
                    "password": "madeup-password",
                    "host": "madeup-host",
                    "database": "madeup-database"
                }
            }
        }

    def setUp(self):
        self.postgres_connector = PostgresConnector()

    def test_update_fails(self):
        data_processor_mock = mock.Mock()
        data_processor_mock.update = mock.MagicMock(side_effect=Exception)
        DataProcessor_mock = mock.Mock(return_value=data_processor_mock)

        with mock.patch("mconf_aggr.webhook.database_handler.DataProcessor", DataProcessor_mock):
            with self.assertRaises(Exception):
                self.postgres_connector.update(None)
                data_processor_mock.update.assert_called_once_with(None)

    def test_update_succeeds(self):
        data_processor_mock = mock.Mock()
        data_processor_mock.update = mock.Mock()
        data_processor_mock.update.return_value = True
        DataProcessor_mock = mock.Mock(return_value=data_processor_mock)

        with mock.patch("mconf_aggr.webhook.database_handler.DataProcessor", DataProcessor_mock):
            self.postgres_connector.update(None)
            data_processor_mock.update.assert_called_once_with(None)

    def test_build_uri(self):
        self.assertEqual(
            "postgresql://madeup-user:madeup-password@madeup-host/madeup-database",
            self.postgres_connector._build_uri()
        )
