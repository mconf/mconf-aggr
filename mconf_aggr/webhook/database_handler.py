"""This module provides all classes that manipulate the database for received events

It provides methods to insert/delete/update columns on the database depending on
which event was received by the `update` method on `WebhookDataWriter` and passed to
`update` on `DataProcessor`.

"""
import logging

import sqlalchemy
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from mconf_aggr.aggregator import cfg
from mconf_aggr.aggregator.aggregator import AggregatorCallback, CallbackError
from mconf_aggr.aggregator.utils import time_logger, create_session_scope
from mconf_aggr.webhook.database_model import Meetings, MeetingsEvents, Recordings, UsersEvents, Servers, SharedSecrets
from mconf_aggr.webhook.exceptions import DatabaseNotReadyError, InvalidWebhookEventError, WebhookDatabaseError


Session = sessionmaker()

session_scope = create_session_scope(Session)


class DatabaseEventHandler:
    """This is an abstract class that handles webhook events.
    """

    def __init__(self, session, logger=None):
        """Constructor of the DataEventHandler.

        Parameters
        ----------
        session : sqlalchemy.Session
            Session used by SQLAlchemy to interact with the database.
        """
        self.session = session
        self.logger = logger or logging.getLogger(__name__)

    def handle(self, event):
        """This method is meant to be implemented downstream.

        Raises
        ------
        NotImplementedError
            If called from an object of class DatabaseEventHandler.
        """
        raise NotImplementedError()


class MeetingCreatedHandler(DatabaseEventHandler):
    """This class handles meeting-created events.
    """
    class MeetingCreatedMetadata:
        def __init__(self, metadata, default_value="", logger=None):
            self._metadata = metadata
            self._default_value = default_value
            self._logger = logger or logging.getLogger(__name__)

        def __getattr__(self, name):
            field = name.replace("_", "-")
            value = None
            try:
                value = self._metadata.get(field, self._default_value)
            except AttributeError as err:
                value = self._default_value

            return value

    def handle(self, event):
        """Implementation of abstract handle method from DatabaseEventHandler.

        Parameters
        ----------
        event : event_mapper.WebhookEvent
            Event to be handled and written to database.
        """
        event_type = event.event_type
        event = event.event

        self.logger.info(f"Processing meeting-created event for internal-meeting-id: '{event.internal_meeting_id}'.")

        # Create tables meetings_events and meetings.
        new_meetings_events = MeetingsEvents(**event._asdict())
        new_meetings_events.has_forcibly_ended = False
        new_meetings_events.unique_users = 0

        metadata = self.MeetingCreatedMetadata(event.meta_data, None, self.logger)
        new_meetings_events.shared_secret_guid = metadata.mconf_shared_secret_guid
        new_meetings_events.shared_secret_name = metadata.mconf_shared_secret_name
        new_meetings_events.server_guid = metadata.mconf_server_guid
        new_meetings_events.server_url = metadata.mconf_server_url
        new_meetings_events.institution_guid = metadata.mconf_institution_guid

        if metadata.mconf_shared_secret_guid and not metadata.mconf_shared_secret_name:
            new_meetings_events.shared_secret_name = (
                self.session.query(SharedSecrets)
                .filter(SharedSecrets.guid == metadata.mconf_shared_secret_guid)
                .first()
                .name
            )

        if not metadata.mconf_server_guid and not metadata.mconf_server_url:
            servers_table = (
                self.session.query(Servers)
                .filter(Servers.name == event.server_url)
                .first()
            )

            new_meetings_events.server_url, new_meetings_events.server_guid = (
                servers_table.name, servers_table.guid
            )

        new_meeting = Meetings(running=False,
                               has_user_joined=False,
                               participant_count=0,
                               listener_count=0,
                               voice_participant_count=0,
                               video_count=0,
                               moderator_count=0,
                               attendees=[])
        new_meeting.meeting_event = new_meetings_events

        self.session.add(new_meeting)


class MeetingEndedHandler(DatabaseEventHandler):
    """This class handles meeting-ended events.
    """

    def handle(self, event):
        """Implementation of abstract handle method from DatabaseEventHandler.

        Parameters
        ----------
        event : event_mapper.WebhookEvent
            Event to be handled and written to database.
        """
        event_type = event.event_type
        event = event.event

        int_id = event.internal_meeting_id
        self.logger.info(f"Processing meeting-ended event for internal-meeting-id: '{int_id}'.")

        # Table meetings_events to be updated.
        meetings_events_table = (
            self.session.query(MeetingsEvents)
            .filter(MeetingsEvents.internal_meeting_id == int_id)
            .first()
        )

        if meetings_events_table:
            meetings_events_table.end_time = event.end_time

            self.session.add(meetings_events_table)

            # Table meetings to be updated.
            meetings_table = (
                self.session.query(Meetings)
                .join(Meetings.meeting_event)
                .filter(MeetingsEvents.internal_meeting_id == int_id)
                .first()
            )

            if meetings_table:
                self.session.delete(meetings_table)


class UserJoinedHandler(DatabaseEventHandler):
    """This class handles user-joined events.
    """

    def handle(self, event):
        """Implementation of abstract handle method from DatabaseEventHandler.

        Parameters
        ----------
        event : event_mapper.WebhookEvent
            Event to be handled and written to database.
        """
        event_type = event.event_type
        event = event.event

        int_id = event.internal_meeting_id
        self.logger.info(f"Processing user-joined event for internal-user-id '{event.internal_user_id}'.'")

        users_events_table = self._get_users_events(event)

        # Create attendee JSON for meetings table.
        attendee = {
            "external_user_id" : event.external_user_id,
            "internal_user_id" : event.internal_user_id,
            "full_name" : event.name,
            "role" : event.role,
            "is_presenter" : event.is_presenter,
            "is_listening_only" : False,
            "has_joined_voice" : False,
            "has_video" : False
        }

        # Query for meetings_events to link with users_events table.
        meetings_events_table = (
            self.session.query(MeetingsEvents)
            .filter(MeetingsEvents.internal_meeting_id.match(int_id))
            .first()
        )

        if meetings_events_table:
            users_events_table.meeting_event = meetings_events_table

            # Table meetings to be updated.
            meetings_table = (
                self.session.query(Meetings)
                .join(Meetings.meeting_event)
                .filter(MeetingsEvents.internal_meeting_id == int_id)
                .first()
            )

            if meetings_table:
                meetings_table.attendees = self._attendee_json(meetings_table.attendees, attendee)
                self._update_meeting(meetings_table)

                # SQLAlchemy was not considering the attendees array as modified, so it had to be forced.
                flag_modified(meetings_table, "attendees")

                self.session.add(users_events_table)
                self.session.add(meetings_table)
                self.session.flush()
            else:
                self.logger.warn(f"No meeting found for user '{event.internal_user_id}'.")
                raise WebhookDatabaseError(f"no meeting found for user '{event.internal_user_id}'")

            # Update unique_users in table meetings_events.
            users_joined = (
                self.session.query(UsersEvents)
                .join(UsersEvents.meeting_event)
                .filter(MeetingsEvents.internal_meeting_id == int_id)
                .count()
            )

            meetings_events_table.unique_users = users_joined

            # Meeting starts when first user joins it.
            if users_joined == 1:
                meetings_events_table.start_time = event.join_time

            self.session.add(meetings_events_table)

    def _get_users_events(self, raw_event):
        event_dict = raw_event._asdict()

        column_names = set(column.key for column in UsersEvents.__table__.columns)
        keys = event_dict.keys()

        for key in list(keys):
            if key not in column_names:
                del event_dict[key]

        users_events = UsersEvents(**event_dict)

        return users_events

    def _attendee_json(self, base, new):
        if not base:
            arr = []
            arr.append(new)

            return arr
        else:
            arr = base
            for elem in arr:
                if(elem["internal_user_id"] == new["internal_user_id"]):
                    return arr
            arr.append(new)

            return arr

    def _update_meeting(self, meetings_table):
        meetings_table.running = True
        _update_meeting(meetings_table)
        meetings_table.has_user_joined = True


class UserLeftHandler(DatabaseEventHandler):
    """This class handles user-left events.
    """

    def handle(self, event):
        """Implementation of abstract handle method from DatabaseEventHandler.

        Parameters
        ----------
        event : event_mapper.WebhookEvent
            Event to be handled and written to database.
        """
        event_type = event.event_type
        event = event.event

        user_id = event.internal_user_id
        int_id = event.internal_meeting_id
        self.logger.info(f"Processing user-left message for internal-user-id '{user_id}' in meeting '{int_id}'.")

        # Table meetings to be updated.
        meetings_table = self.session.query(Meetings).\
                        join(Meetings.meeting_event).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()

        if meetings_table:
            self._remove_attendee(meetings_table, user_id)
            self._update_meeting(meetings_table)

            # Mark meetings.attendees as modified for SQLAlchemy.
            flag_modified(meetings_table, "attendees")

            self.session.add(meetings_table)
        else:
            self.logger.warn(f"No meeting found with internal-meeting-id '{int_id}'.")

        # Table users_events to be updated.
        users_table = self.session.query(UsersEvents).\
                        filter(UsersEvents.internal_user_id == user_id).first()

        if users_table:
            # Update table users_events.
            users_table.leave_time = event.leave_time
        else:
            self.logger.warn(f"No user found with internal-user-id '{user_id}'.")


    def _remove_attendee(self, meetings_table, user_id):
        for idx, attendee in enumerate(meetings_table.attendees):
            if(attendee["internal_user_id"] == user_id):
                del meetings_table.attendees[idx]


    def _update_meeting(self, meetings_table):
        _update_meeting(meetings_table)


class UserEventHandler(DatabaseEventHandler):
    """This class handles general user events.
    """

    def handle(self, event):
        """Implementation of abstract handle method from DatabaseEventHandler.

        Parameters
        ----------
        event : event_mapper.WebhookEvent
            Event to be handled and written to database.
        """
        event_type = event.event_type
        event = event.event

        self.event_type = event_type

        user_id = event.internal_user_id
        int_id = event.internal_meeting_id
        self.logger.info(f"Processing {event.event_name} event for internal-user-id '{user_id}' on meeting '{int_id}'.")

        # Table meetings to be updated.
        meetings_table = self.session.query(Meetings).\
                        join(Meetings.meeting_event).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()

        if meetings_table:
            self._update_attendees(meetings_table.attendees, event, user_id)
            self._update_meeting(meetings_table)

            flag_modified(meetings_table, "attendees")

            self.session.add(meetings_table)
        else:
            self.logger.warn(f"No meeting found with internal-meeting-id '{int_id}'.")


    def _update_meeting(self, meetings_table):
        _update_meeting(meetings_table)


    def _update_attendees(self, base, update, user_id):
        for attendee in base:
            if(attendee["internal_user_id"] == user_id):
                if(update.event_name == self.event_type):
                    self._update_attendee(attendee, update)


    def _update_attendee(self, attendee, update):
        raise NotImplementedError("Give specific behavior for the user event")


class UserVoiceEnabledHandler(UserEventHandler):
    """This class adds specific behavior for user-audio-voice-enabled events.
    """

    def _update_attendee(self, attendee, update):
        attendee["has_joined_voice"] = update.has_joined_voice
        attendee["is_listening_only"] = update.is_listening_only


class UserVoiceDisabledHandler(UserEventHandler):
    """This class adds specific behavior for user-audio-voice-disabled events.
    """

    def _update_attendee(self, attendee, update):
        attendee["has_joined_voice"] = False


class UserListenOnlyEnabledHandler(UserEventHandler):
    """This class adds specific behavior for user-audio-listen-only-enabled events.
    """
    def _update_attendee(self, attendee, update):
        attendee["is_listening_only"] = True


class UserListenOnlyDisabledHandler(UserEventHandler):
    """This class adds specific behavior for user-audio-listen-only-disabled events.
    """

    def _update_attendee(self, attendee, update):
        attendee["is_listening_only"] = False


class UserCamBroadcastStartHandler(UserEventHandler):
    """This class adds specific behavior for user-cam-broadcast-start events.
    """

    def _update_attendee(self, attendee, update):
        attendee["has_video"] = True


class UserCamBroadcastEndHandler(UserEventHandler):
    """This class adds specific behavior for user-cam-broadcast-end events.
    """

    def _update_attendee(self, attendee, update):
        attendee["has_video"] = False


class UserPresenterAssignedHandler(UserEventHandler):
    """This class adds specific behavior for user-presenter-assigned events.
    """

    def _update_attendee(self, attendee, update):
        attendee["is_presenter"] = True


class UserPresenterUnassignedHandler(UserEventHandler):
    """This class adds specific behavior for user-presenter-unassigned events.
    """

    def _update_attendee(self, attendee, update):
        attendee["is_presenter"] = False


class RapHandler(DatabaseEventHandler):
    """This class handles general recording events.
    """

    def handle(self, event):
        """Implementation of abstract handle method from DatabaseEventHandler.

        Parameters
        ----------
        event : event_mapper.WebhookEvent
            Event to be handled and written to database.
        """
        event_type = event.event_type
        event = event.event

        int_id = event.internal_meeting_id
        self.logger.info(f"Processing {event_type} event for internal-meeting-id '{int_id}'.")

        records_table = (
            self.session.query(Recordings).
            filter(Recordings.internal_meeting_id == int_id).
            first()
        )

        # Table recordings already exists.
        if records_table:
            # Update status based on event.
            # Handle "unpublished" and "deleted" when webhooks are emitting those events.
            if(event.current_step == "rap-process-ended"):
                records_table.status = "processed"
            elif(event.current_step == "rap-publish-ended"):
                records_table.status = "published"
                records_table.published = True
            else:
                records_table.status = "processing"
        else:
            # Create and initialize table recordings.
            records_table = Recordings(**event._asdict())
            records_table.status = "processing"
            records_table.participants = (
                int(
                    self.session.query(UsersEvents.id).
                    join(MeetingsEvents).
                    filter(MeetingsEvents.internal_meeting_id == int_id).
                    count()
                )
            )

            meetings_events_table = (
                self.session.query(MeetingsEvents).
                filter(MeetingsEvents.internal_meeting_id == int_id).
                first()
            )

            if meetings_events_table:
                records_table.meeting_event_id = meetings_events_table.id
                records_table.start_time = meetings_events_table.start_time
                records_table.end_time = meetings_events_table.end_time

                servers_table = (
                    self.session.query(Servers).
                    filter(Servers.guid == meetings_events_table.server_guid).
                    first()
                )

                if servers_table:
                    records_table.server_id = servers_table.id
                else:
                    self.logger.warn(f"No server found for recording '{event.record_id}'.")
            else:
                self.logger.warn(f"No meeting found for recording '{event.record_id}'.")


        records_table.current_step = event.current_step

        if(event.current_step == "rap-publish-ended"):
            times = (
                self.session.query(MeetingsEvents.start_time, MeetingsEvents.end_time).
                filter(MeetingsEvents.internal_meeting_id == int_id).first()
            )
            start_time, end_time = times

            records_table.name = event.name
            records_table.is_breakout = event.is_breakout
            records_table.start_time = start_time
            records_table.end_time = end_time
            records_table.size = event.size
            records_table.raw_size = event.raw_size
            records_table.meta_data = event.meta_data
            records_table.playback = event.playback
            records_table.download = event.download
            records_table.current_step = event.current_step

        self.session.add(records_table)


def _update_meeting(meetings_table):
    """Common updates on table meetings.
    """
    meetings_table.participant_count = len(meetings_table.attendees)
    meetings_table.has_user_joined = meetings_table.participant_count != 0
    meetings_table.moderator_count = sum(1 for attendee in meetings_table.attendees if attendee["role"] == "MODERATOR")
    meetings_table.listener_count = sum(1 for attendee in meetings_table.attendees if attendee["is_listening_only"])
    meetings_table.voice_participant_count = sum(1 for attendee in meetings_table.attendees if attendee["has_joined_voice"])
    meetings_table.video_count = sum(1 for a in meetings_table.attendees if a["has_video"])


class DataProcessor:
    """Data processor (dispatcher) of the received event.
    """
    def __init__(self, session, logger=None):
        """Constructor of the DataProcessor.

        Parameters
        ----------
        session : sqlalchemy.Session
            Session used by SQLAlchemy to interact with the database.
        """
        self.session = session
        self.logger = logger or logging.getLogger(__name__)

    def update(self, event):
        event_handler = self._select_handler(event.event_type)

        event_handler.handle(event)

    def _select_handler(self, event_type):
        """Event dispatcher.

        Choose which handler will process the event based on the event type.

        Parameters
        ----------
        event : event_mapper.WebhookEvent
            An event to be handled and persisted into database.
        """
        self.logger.debug("Selecting event processor.")

        if(event_type == "meeting-created"):
            event_handler = MeetingCreatedHandler(self.session)

        elif(event_type == "user-joined"):
            event_handler = UserJoinedHandler(self.session)

        elif(event_type == "user-left"):
            event_handler = UserLeftHandler(self.session)

        elif(event_type == "meeting-ended"):
            event_handler = MeetingEndedHandler(self.session)

        elif event_type == "user-audio-voice-enabled":
            event_handler = UserVoiceEnabledHandler(self.session)

        elif event_type == "user-audio-voice-disabled":
            event_handler = UserVoiceDisabledHandler(self.session)

        elif event_type == "user-audio-listen-only-enabled":
            event_handler = UserListenOnlyEnabledHandler(self.session)

        elif event_type == "user-audio-listen-only-disabled":
            event_handler = UserListenOnlyDisabledHandler(self.session)

        elif event_type == "user-cam-broadcast-start":
            event_handler = UserCamBroadcastStartHandler(self.session)

        elif event_type == "user-cam-broadcast-end":
            event_handler = UserCamBroadcastEndHandler(self.session)

        elif event_type == "user-presenter-assigned":
            event_handler = UserPresenterAssignedHandler(self.session)

        elif event_type == "user-presenter-unassigned":
            event_handler = UserPresenterUnassignedHandler(self.session)

        elif(event_type in ["rap-archive-started", "rap-archive-ended",
                    "rap-sanity-started", "rap-sanity-ended",
                    "rap-post-archive-started", "rap-post-archive-ended",
                    "rap-process-started", "rap-process-ended",
                    "rap-post-process-started", "rap-post-process-ended",
                    "rap-publish-started", "rap-publish-ended",
                    "rap-post-publish-started", "rap-post-publish-ended"]):
            event_handler = RapHandler(self.session)
        else:
            self.logger.warn(f"Unknown event type '{event_type}'.")
            raise InvalidWebhookEventError(f"unknown event type '{event_type}'")

        return event_handler


class PostgresConnector:
    """Wrapper of PostgreSQL connection.

    It encapsulates the inner workings of the SQLAlchemy connection process.

    Before using it, one must call once its method `connect()` to configure and
    create a connection to the database. Then, the `update()` method can be
    called for each metric whenever it is necessary to update the database.
    When finished, one must call `close()` to definitely close the connection
    to the database (currently it does nothing).
    """
    def __init__(self, database_uri=None, logger=None):
        """Constructor of the PostgresConnector.

        Parameters
        ----------
        database_uri : str
            URI of the PostgreSQL database instance either local or remote.
        """
        self.config = cfg.config['webhook']['database']
        self.database_uri = database_uri or self._build_uri()
        self.logger = logger or logging.getLogger(__name__)

    def connect(self):
        """Configure and connect the database.

        It is responsible for creating an engine for the URI provided and
        configure the session.
        """
        self.logger.debug("Creating new database session.")
        engine = create_engine(self.database_uri, echo=False)
        Session.configure(bind=engine)

    def close(self):
        """Close the connection to the database.

        It currently does nothing.
        """
        self.logger.info("Closing connection to PostgreSQL. Nothing to do.")
        pass

    def update(self, data):
        """Update the database with new data.

        Parameters
        ----------
        data : dict
            The data to be updated in the database.

        Raises
        ------
        sqlalchemy.exc.OperationalError
            If an error occur while persisting data into database.
        """
        try:
            with time_logger(self.logger.debug,
                             "Processing information to database took {elapsed}s."):
                with session_scope() as session:
                    DataProcessor(session).update(data)
        except Exception as err:
            self.logger.error(err)
            raise

    def _build_uri(self):
        user = self.config['user']
        password = self.config['password']
        host = self.config['host']
        database = self.config['database']

        return f"postgresql://{user}:{password}@{host}/{database}"


class WebhookDataWriter(AggregatorCallback):
    """Writer of data retrieved from webhooks.

    This class implements the AggregatorCallback which means its `run()` method
    is intended to run in a separate thread, writing incoming data to the
    database.

    Before using it, one should call its `setup()` method to configure
    any resource used to write data such as database connections etc.
    After that, its `run()` method can be run in a separate thread continuously.
    When finished, its `teardown` can be called to close any opened resource.
    """
    def __init__(self, connector=None, logger=None):
        """Constructor of the WebhookDataWriter.

        Parameters
        ----------
        connector : Database connector (driver).
            If not supplied, it will instantiate a new `PostgresConnector`.
        """
        self.connector = connector or PostgresConnector()
        self.logger = logger or logging.getLogger(__name__)

    def setup(self):
        """Setup any resources needed to iteract with the database.
        """
        self.logger.info("Setting up WebhookDataWriter")
        self.connector.connect()

    def teardown(self):
        """Release any resources used to iteract with the database.
        """
        self.logger.info("Tearing down WebhookDataWriter")
        self.connector.close()

    def run(self, data):
        """Run main logic of the writer.

        This method is intended to run in a separate thread by the aggregator
        whenever new data must be persisted.

        data : event_mapper.WebhookEvent
            This is a single event to be handled and persisted into database.

        Raises
        ------
        aggregator.aggregator.CallbackError
            If any error occur while persisting event into database.
        """
        try:
            self.connector.update(data)
        except sqlalchemy.exc.OperationalError as err:
            self.logger.error("Operational error on database. Not persisting data.")
            self.logger.debug(err)

            raise CallbackError() from err
        except WebhookDatabaseError as err:
            self.logger.error("An error occurred while persisting data. Not persisting data.")
            self.logger.debug(err)

            raise CallbackError() from err
        except Exception as err:
            self.logger.error("Unknown error on database handler. Not persisting data.")
            self.logger.debug(err)

            raise CallbackError() from err


class AuthenticationHandler:
    """Provide a way to get server data from database.
    """
    def __init__(self, logger=None):
        """Constructor of the `AuthenticationHandler`.

        Parameters
        ----------
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.logger = logger or logging.getLogger(__name__)

    def secret(self, server):
        """Get a shared secret for a given server in the database.

        Parameters
        ----------
        server : str
            Server for which it should get a token from database.

        Returns
        -------
        token : str
            Token of the server as retrieved from database.
        """
        found_secret = None
        with session_scope() as session:
            try:
                server = session.query(Servers.secret).filter(Servers.name == server).first()
            except sqlalchemy.exc.OperationalError as err:
                self.logger.error("Operational error on database while validating token.")
                server = None
            except Exception as err:
                self.logger.warn(f"Unknown error while validating token: {err}")
                server = None

            if server:
                # If it found a row for the given server, extract its secret column.
                found_secret = server.secret

        return found_secret


class WebhookServerHandler:
    """Provide a way to get all available servers from database.
    """
    def __init__(self, logger=None):
        """Constructor of the `WebhookServerHandler`.

        Parameters
        ----------
        logger : logging.Logger
            If not supplied, it will instantiate a new logger from __name__.
        """
        self.logger = logger or logging.getLogger(__name__)

    def servers(self):
        """Get all available servers from database.

        Returns
        -------
        servers : Servers.
            The list of all available servers from database.
        """
        servers = None
        with session_scope() as session:
            try:
                servers = session.query(Servers).all()
            except sqlalchemy.exc.OperationalError as err:
                self.logger.error("Operational error on database while gathering Zabbix servers.")

                raise DatabaseNotReadyError()
            except Exception as err:
                self.logger.warn(f"Unknown error while gathering Zabbix servers: {err}")

                raise DatabaseNotReadyError()
            else:
                # Since it returns Servers objects used by the database, we need
                # to detach the objects returned from the database's session.
                session.expunge_all()

                return servers
