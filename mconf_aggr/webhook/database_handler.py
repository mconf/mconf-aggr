"""This module provides all classes that manipulate the database for received events

It provides methods to insert/delete/update columns on the database depending on
which event was received by the `update` method on `WebhookDataWriter` and passed to
`update` on `DataProcessor`.

"""
import logging

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from mconf_aggr.aggregator import cfg
from mconf_aggr.aggregator.aggregator import AggregatorCallback, CallbackError
from mconf_aggr.aggregator.utils import time_logger, create_session_scope
from mconf_aggr.webhook.database_model import Meetings, MeetingsEvents, Recordings, UsersEvents
from mconf_aggr.webhook.exceptions import WebhookDatabaseError


Session = sessionmaker()

session_scope = create_session_scope(Session)


class DatabaseEventHandler:
    def __init__(self, session, logger=None):
        """Constructor of the DataProcessor.

        Parameters
        ----------
        session : sqlalchemy.Session
            Session used by SQLAlchemy to interact with the database.
        data : dict list
            Informations that the methods in this class will use to update the database.
        """
        self.session = session
        #self.webhook_msg = data[0]
        #self.mapped_msg = data[1]
        self.logger = logger or logging.getLogger(__name__)

    def handle(self, event):
        raise NotImplementedError()


class MeetingCreatedHandler(DatabaseEventHandler):
    def handle(self, event):
        event_type = event.event_type
        event = event.event

        self.logger.info("Processing meeting-created event for internal-meeting-id: '{}'."
                        .format(event.internal_meeting_id))

        # Create MeetingsEvents and Meetings table.
        new_meetings_events = MeetingsEvents(**event._asdict())
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

class UserJoinedHandler(DatabaseEventHandler):
    def handle(self, event):
        event_type = event.event_type
        event = event.event

        int_id = event.internal_meeting_id
        self.logger.info("Processing user-joined event for internal-user-id '{}'.'"
                    .format(event.internal_user_id))

        users_events_table = self._get_users_events(event)

        # Create attendee json for meeting table
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

        # Query for MeetingsEvents to link with UsersEvents table
        meetings_events_table = self.session.query(MeetingsEvents).\
                            filter(MeetingsEvents.internal_meeting_id.match(int_id)).first()

        if meetings_events_table:
            users_events_table.meeting_event = meetings_events_table

        # Meeting table to be updated
        meetings_table = self.session.query(Meetings).\
                        join(Meetings.meeting_event).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()

        if meetings_table:
            meetings_table = self.session.query(Meetings).get(meetings_table.id)

            meetings_table.attendees = self._attendee_json(meetings_table.attendees, attendee)
            self._update_meeting(meetings_table)

            # SQLAlchemy was not considering the attendees array as modified, so it had to be forced
            flag_modified(meetings_table, "attendees")

            self.session.add(users_events_table)
            self.session.add(meetings_table)
        else:
            self.logger.warn("No meeting found for user '{}'.".format(event.internal_user_id))
            raise WebhookDatabaseError("no meeting found for user '{}'".format(event.internal_user_id))

        # Update unique users
        meetings_events_table = self.session.query(MeetingsEvents).get(meetings_events_table.id)
        meetings_events_table.unique_users = int(self.session.query(UsersEvents.id).\
                                        join(UsersEvents.meeting_event).\
                                        filter(MeetingsEvents.internal_meeting_id == int_id).\
                                        count())

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


    def _update_meeting(self, meetings_table):
        meetings_table.running = True
        meetings_table.has_user_joined = True

        _update_meeting(meetings_table)


class MeetingEndedHandler(DatabaseEventHandler):
    def handle(self, event):
        event_type = event.event_type
        event = event.event

        int_id = event.internal_meeting_id
        self.logger.info("Processing meeting-ended event for internal-meeting-id: '{}'"
        .format(int_id))

        # MeetingsEvents table to be updated
        meetings_events_table = self.session.query(MeetingsEvents).\
                            filter(MeetingsEvents.internal_meeting_id == int_id).first()

        if meetings_events_table:
            meetings_events_table = self.session.query(MeetingsEvents).get(meetings_events_table.id)
            meetings_events_table.end_time = event.end_time

            self.session.add(meetings_events_table)

            # Meeting table to be updated
            meetings_table = self.session.query(Meetings).\
                            join(Meetings.meeting_event).\
                            filter(MeetingsEvents.internal_meeting_id == int_id).first()

            if meetings_table:
                meetings_table = self.session.query(Meetings).get(meetings_table.id)

                self.session.delete(meetings_table)


class UserLeftHandler(DatabaseEventHandler):
    def handle(self, event):
        event_type = event.event_type
        event = event.event

        user_id = event.internal_user_id
        int_id = event.internal_meeting_id
        self.logger.info("Processing user-left message for internal-user-id: {} in {}"
                        .format(user_id, int_id))

        # Meeting table to be updated
        meetings_table = self.session.query(Meetings).\
                        join(Meetings.meeting_event).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()

        if meetings_table:
            meetings_table = self.session.query(Meetings).get(meetings_table.id)

            self._remove_attendee(meetings_table, user_id)
            self._update_meeting(meetings_table)

            # Mark Meetings.attendees as modified for SQLAlchemy
            flag_modified(meetings_table, "attendees")

            self.session.add(meetings_table)
        else:
            self.logger.warn("No meeting found with internal-meeting-id '{}'".format(int_id))

        # User table to be updated
        users_table = self.session.query(UsersEvents).\
                        filter(UsersEvents.internal_user_id == user_id).first()

        if users_table:
            # Update UsersEvents table
            users_table = self.session.query(UsersEvents).get(users_table.id)
            users_table.leave_time = event.leave_time
        else:
            self.logger.warn("No user found with internal-user-id '{}'".format(user_id))


    def _remove_attendee(self, meetings_table, user_id):
        for idx, attendee in enumerate(meetings_table.attendees):
            if(attendee["internal_user_id"] == user_id):
                del meetings_table.attendees[idx]


    def _update_meeting(self, meetings_table):
        _update_meeting(meetings_table)


class UserEventHandler(DatabaseEventHandler):
    def handle(self, event):
        event_type = event.event_type
        event = event.event

        self.event_type = event_type

        user_id = event.internal_user_id
        int_id = event.internal_meeting_id
        self.logger.info("Processing {} event for internal-user-id '{}' on meeting '{}'"
                        .format(event.event_name, user_id, int_id))

        # Meeting table to be updated
        meetings_table = self.session.query(Meetings).\
                        join(Meetings.meeting_event).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()

        if meetings_table:
            meetings_table = self.session.query(Meetings).get(meetings_table.id)

            self._update_attendees(meetings_table.attendees, event, user_id)
            self._update_meeting(meetings_table)

            flag_modified(meetings_table,"attendees")

            self.session.add(meetings_table)
        else:
            self.logger.warn("No meeting found with internal-meeting-id '{}'".format(int_id))


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
    def _update_attendee(self, attendee, update):
        attendee["has_joined_voice"] = update.has_joined_voice
        attendee["is_listening_only"] = update.is_listening_only


class UserVoiceDisabledHandler(UserEventHandler):
    def _update_attendee(self, attendee, update):
        attendee["has_joined_voice"] = False


class UserListenOnlyEnabledHandler(UserEventHandler):
    def _update_attendee(self, attendee, update):
        attendee["is_listening_only"] = True


class UserListenOnlyDisabledHandler(UserEventHandler):
    def _update_attendee(self, attendee, update):
        attendee["is_listening_only"] = False


class UserCamBroadCastStartHandler(UserEventHandler):
    def _update_attendee(self, attendee, update):
        attendee["has_video"] = True


class UserCamBroadCastEndHandler(UserEventHandler):
    def _update_attendee(self, attendee, update):
        attendee["has_video"] = False


class UserPresenterAssignedHandler(UserEventHandler):
    def _update_attendee(self, attendee, update):
        attendee["is_presenter"] = True


class UserPresenterUnassignedHandler(UserEventHandler):
    def _update_attendee(self, attendee, update):
        attendee["is_presenter"] = False


class RapHandler(DatabaseEventHandler):
    def handle(self, event):
        event_type = event.event_type
        event = event.event

        int_id = event.internal_meeting_id
        self.logger.info("Processing {} event for internal-meeting-id '{}'"
                        .format(event_type, int_id))
        # Check if table already exists
        try:
            records_table = self.session.query(Recordings.id).\
                            filter(Recordings.internal_meeting_id == int_id).first()
            # Check if there's records_table
            records_table = self.session.query(Recordings).get(records_table.id)
        except:
            # Create table
            records_table = Recordings(**event._asdict())
            records_table.participants = int(self.session.query(UsersEvents.id).\
                                        join(MeetingsEvents).\
                                        filter(MeetingsEvents.internal_meeting_id == int_id).\
                                        count())
            self.session.add(records_table)
            records_table = self.session.query(Recordings.id).\
                            filter(Recordings.internal_meeting_id == int_id).first()
            records_table = self.session.query(Recordings).get(records_table.id)
        finally:
            # When publish end update most of information
            if(event.current_step == "rap-publish-ended"):
                records_table.name = event.name
                records_table.is_breakout = event.is_breakout
                records_table.start_time = event.start_time
                records_table.end_time = event.end_time
                records_table.size = event.size
                records_table.raw_size = event.raw_size
                records_table.meta_data = event.meta_data
                records_table.playback = event.playback
                records_table.download = event.download
                records_table.current_step = event.current_step

            # Update status based on event
            # Treat "unpublished" and "deleted" when webhooks are emitting those events.
            if(event.current_step == "rap-process-started"):
                records_table.status = "processing"
            elif(event.current_step == "rap-process-ended"):
                records_table.status = "processed"
            elif(event.current_step == "rap-publish-ended"):
                records_table.status = "published"
                records_table.published = True

            self.session.add(records_table)


def _update_meeting(meetings_table):
    meetings_table.has_user_joined = meetings_table.participant_count != 0
    meetings_table.participant_count = len(meetings_table.attendees)
    meetings_table.moderator_count = sum(1 for attendee in meetings_table.attendees if attendee["role"] == "MODERATOR")
    meetings_table.listener_count = sum(1 for attendee in meetings_table.attendees if attendee["is_listening_only"])
    meetings_table.voice_participant_count = sum(1 for attendee in meetings_table.attendees if attendee["has_joined_voice"])
    meetings_table.video_count = sum(1 for a in meetings_table.attendees if a["has_video"])


class DataProcessor:
    """Data processor of the received information.

    It provides methods to update rows in the following tables:
        -Meetings;
        -MeetingsEvents;
        -Recordings;
        -UsersEvents.
    """
    def __init__(self, session, logger=None):
        """Constructor of the DataProcessor.

        Parameters
        ----------
        session : sqlalchemy.Session
            Session used by SQLAlchemy to interact with the database.
        data : dict list
            Informations that the methods in this class will use to update the database.
        """
        self.session = session
        self.logger = logger or logging.getLogger(__name__)

    def update(self, event):
        """Event Selector.

        Choose which event will be processed (which method to call), based on
        the received data.

        The methods won't commit any update, just add them to the session.
        """
        self.logger.info("Selecting event processor")
        event_type = event.event_type

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
            event_handler = UserCamBroadCastStartHandler(self.session)

        elif event_type == "user-cam-broadcast-end":
            event_handler = UserCamBroadCastEndHandler(self.session)

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
            self.logger.warn("Unknown event type '{}'.".format(event_type))
            raise InvalidWebhookEventError("unknown event type '{}'".format(event_type))

        event_handler.handle(event)


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
        """
        try:
            with time_logger(self.logger.debug,
                             "Processing information to database took {elapsed}s."):
                with session_scope() as session:
                    DataProcessor(session).update(data)
        except sqlalchemy.exc.OperationalError as err:
            self.logger.error(err)

            raise

    def _build_uri(self):
        return "postgresql://{}:{}@{}/{}".format(self.config['user'],
                                                 self.config['password'],
                                                 self.config['host'],
                                                 self.config['database'])


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

        data : dict
            The data may be compound of many metrics of different server hosts.
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
