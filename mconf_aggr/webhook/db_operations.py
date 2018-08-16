"""This module provides all classes that manipulate the database for received events

It provides methods to insert/delete/update columns on the database depending on
which event was received by the `update` method on `WebhookDataWriter` and passed to
`update` on `DataProcessor`.

"""
import datetime
import logging
import json

import sqlalchemy
from contextlib import contextmanager
from sqlalchemy import (BigInteger,
                        Boolean,
                        create_engine,
                        Column,
                        DateTime,
                        ForeignKey,
                        Integer,
                        JSON,
                        String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (backref,
                            sessionmaker,
                            relationship)
from sqlalchemy.orm.attributes import flag_modified

from mconf_aggr.aggregator import cfg
from mconf_aggr.aggregator.aggregator import AggregatorCallback
from mconf_aggr.aggregator.utils import time_logger

Base = declarative_base()
Session = sessionmaker()


# DB Tables
class Meetings(Base):
    """Table Meetings in the database.

    Each row in this table represents an information about the attendees of a meeting,
    retrieved from the webhooks.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of the type Integer
        Primary key. Identifier of the table.
    meeting_event_id : Column of the type Integer
        Foreign Key. Identifier of the associated MeetingsEvents table (instatiated by id).
    created_at : Column of the type DateTime
        Datetime of the meeting creation.
    updated_at : Column of the type DateTime
        Last datetime the meeting was updated.
    running : Column of the type Boolean
        Indicates if the meeting is running.
    has_user_joined : Column of the type Boolean
        Indicates if a user has already joined.
    participant_count : Column of the type Integer
        Number of participants on the meeting.
    listener_count : Column of the type Integer
        Number of listeners on the meeting.
    voice_participant_count : Column of the type Integer
        Number of participants on the meeting with active voice chat.
    video_count : Column of the type Integer
        Number of participants on the meeting with video share.
    moderator_count : Column of the type Integer
        Number of moderators on the meeting.
    attendees : Column of the type JSON
        Each attendee on the meeting, especified on the format::

        [
            {
                "is_presenter": boolean,
                "is_listening_only": boolean,
                "has_joined_voice": boolean,
                "has_video": boolean,
                "ext_user_id": string,
                "int_user_id": string,
                "full_name": string,
                "role": string,
            },
            {
                ...
            }
        ]
    """
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True)
    meeting_event_id = Column(Integer, ForeignKey("meetings_events.id"))
    #meeting_event = relationship("MeetingsEvents", backref=backref("Meetings", uselist=False))
    meeting_event = relationship("MeetingsEvents")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    running = Column(Boolean)
    has_user_joined = Column(Boolean)
    participant_count = Column(Integer)
    listener_count = Column(Integer)
    voice_participant_count = Column(Integer)
    video_count = Column(Integer)
    moderator_count = Column(Integer)
    attendees = Column(JSON)

    def __repr__(self):
     return ("<Meetings("
            + "id=" + str(self.id)
            + ", created_at=" + str(self.created_at)
            + ", updated_at=" + str(self.updated_at)
            + ", running=" + str(self.running)
            + ", has_user_joined=" + str(self.has_user_joined)
            + ", participant_count=" + str(self.participant_count)
            + ", listener_count=" + str(self.listener_count)
            + ", voice_participant_count=" + str(self.voice_participant_count)
            + ", video_count=" + str(self.video_count)
            + ", moderator_count=" + str(self.moderator_count)
            + ", attendees=" + str(self. attendees)
            + ")>")


class MeetingsEvents(Base):
    """Table MeetingsEvents in the database.

    Each row in the table represents an information about a meeting, retrieve
    from the webhooks.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of type Integer
        Primary key. Identifier of the table.
    shared_secret_guid : Column of type String
        Shared Secret Guid.
    shared_secret_name : Column of type String
        Shared Secret Name.
    server_guid : Column of type String
        Server Guid.
    server_url : Column of type String
        Url of the server the meeting is hosted.
    created_at : Column of type DateTime
        Datetime of the meeting creation.
    updated_at : Column of type DateTime
        Last datetime the meeting was updated.
    external_meeting_id : Column of type String
        External meeting id of the meeting.
    internal_meeting_id : Column of type String
        Internal meeting id of the meeting.
    name : Column of type String
        Name of the meeting.
    create_time : Column of type BigInteger
        Timestamp of the time when the meeting was created.
    create_date : Column of type String
        Date when the meeting was created.
    voice_bridge : Column of type Integer
        Voice bridge of the meeting.
    dial_number : Column of type string
        Dial number of the meeting.
    attendee_pw : Column of type String
        Password for attendees on this meeting.
    moderator_pw : Column of type String
        Password for moderators on this meeting.
    duration : Column of type Integer
        Duration of the meeting.
    recording : Column of type Boolean
        Indicates if the meeting is being recorded.
    has_forcibly_ended : Column of type Boolean
        Indicates if the meeting was ended through an API call.
    start_time : Column of type BigInteger
        Timestamp of the moment when the meeting started.
    end_time : Column of type BigInteger
        Timestamp of the moment when the meeting ended.
    max_users : Column of type Integer
        Maximum number of users on the meeting.
    is_breakout : Column of type Boolean
        Indicates if the meeting is a breakout room.
    unique_users : Column of type Integer
        Number of unique users on the meeting.
    meta_data : Column of type JSON
        Metadata of the meeting, especified in the format::

        [
            {
                "mconf-shared-secret-guid": value,
                "mconf-shared-secret-name": value,
                "mconf-institution-guid": value,
                "mconf-institution-name": value,
                "mconf-server-guid": value,
                "mconf-server-url": value,
                "mconf-request-query": value,
                "mconf-user-ip": value,
                "mconf-user-agent": value
            },
            {
                ...
            }
        ]
    """
    __tablename__ = "meetings_events"

    id = Column(Integer, primary_key=True)

    shared_secret_guid = Column(String) #index?
    shared_secret_name = Column(String)
    server_guid = Column(String)
    server_url = Column(String)

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    external_meeting_id = Column(String) #index?
    internal_meeting_id = Column(String, unique=True) #index?
    name = Column(String)
    create_time = Column(BigInteger)
    create_date = Column(String)
    voice_bridge = Column(Integer)
    dial_number = Column(String)
    attendee_pw = Column(String)
    moderator_pw = Column(String)
    duration = Column(Integer)
    recording = Column(Boolean)
    has_forcibly_ended = Column(Boolean)
    start_time = Column(BigInteger)
    end_time = Column(BigInteger)
    max_users = Column(Integer)
    is_breakout = Column(Boolean)
    unique_users = Column(Integer)
    meta_data = Column("metadata", JSON)

    def __repr__(self):
        return ("<MeetingsEvents("
                + "id=" + str(self.id)
                + ", shared_secret_guid=" + str(self. shared_secret_guid)
                + ", shared_secret_name=" + str(self. shared_secret_name)
                + ", server_guid=" + str(self. server_guid)
                + ", server_url=" + str(self.server_url)
                + ", created_at=" + str(self.created_at)
                + ", updated_at=" + str(self.updated_at)
                + ", external_meeting_id=" + str(self.external_meeting_id)
                + ", internal_meeting_id=" + str(self.internal_meeting_id)
                + ", name=" + str(self.name)
                + ", create_time=" + str(self.create_time)
                + ", create_date=" + str(self.create_date)
                + ", voice_bridge=" + str(self.voice_bridge)
                + ", dial_number=" + str(self.dial_number)
                + ", attendee_pw=" + str(self.attendee_pw)
                + ", moderator_pw=" + str(self.moderator_pw)
                + ", duration=" + str(self.duration)
                + ", recording=" + str(self.recording)
                + ", has_forcibly_ended=" + str(self.has_forcibly_ended)
                + ", start_time=" + str(self.start_time)
                + ", end_time=" + str(self.end_time)
                + ", max_users=" + str(self.max_users)
                + ", is_breakout=" + str(self.is_breakout)
                + ", unique_users=" + str(self.unique_users)
                + ", meta_data=" + str(self.meta_data)
                + ")>")


class Recordings(Base):
    """Table Recordings in the database.

    Each row in this table represents information about a recording, retrieved
    from the webhooks.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of the type Interger
        Primary key. Identifier of the recording.
    created_at : Column of the type DateTime
        Datetime of the recording creation.
    updated_at : Column of the type DateTime
        Last datetime the recording was updated.
    name : Column of the type String
        Name of the recording.
    status : Column of the type String
        Current status of the recording.
    internal_meeting_id : Column of the type String
        Internal meeting ID of the recording.
    external_meeting_id : Column of the type String
        External meeting ID of the recording.
    is_breakout : Column of the type Boolean
        Indicates if the recording if from a breakout room.
    published : Column of the type Boolean
        Indicates if the recording's been published.
    start_time : Column of the type BigInteger
        Timestamp of when the recording was created.
    end_time : Column of the type BigInteger
        Timestamp of when the recording ended.
    participants : Column of the type Integer
        Number of participants on the recorded meeting.
    size : Column of the type BigInteger
        Size of the recording.
    raw_size : Column of the type BigInteger.
        Raw size of the recording.
    current_step : Column of the type String.
        Current step of the recordig.
    meta_data : Column of the type JSON
        Information about the recording metadata.
    playback : Column of the type JSON
        Information about the recording playback.
    download : Column of the type JSON
        Information about the recording download.
    """
    __tablename__ = "Recordings"

    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    name = Column(String)
    status = Column(String)
    internal_meeting_id = Column(String, unique=True)
    external_meeting_id = Column(String)

    is_breakout = Column(Boolean)
    published = Column(Boolean)
    start_time = Column(BigInteger)
    end_time = Column(BigInteger)
    participants = Column(Integer)
    size = Column(BigInteger)
    raw_size = Column(BigInteger)
    current_step = Column(String)

    meta_data = Column(JSON)
    playback = Column(JSON)
    download = Column(JSON)

    def __repr__(self):
     return ("<Recordings("
            + "id=" + str(self.id)
            + ", created_at=" + str(self.created_at)
            + ", updated_at=" + str(self.updated_at)
            + ", name=" + str(self.name)
            + ", status=" + str(self.status)
            + ", is_breakout=" + str(self.is_breakout)
            + ", published=" + str(self.published)
            + ", start_time=" + str(self.start_time)
            + ", end_time=" + str(self.end_time)
            + ", participants=" + str(self.participants)
            + ", size=" + str(self.size)
            + ", raw_size=" + str(self.raw_size)
            + ", current_step=" + str(self.current_step)
            + ", internal_meeting_id=" + str(self.internal_meeting_id)
            + ", external_meeting_id=" + str(self.external_meeting_id)
            + ", meta_data=" + str(self. meta_data)
            + ", playback=" + str(self. playback)
            + ", download=" + str(self. download)
            + ")>")


class UsersEvents(Base):
    """Table UsersEvents in the database.

    Each row in the table represents information about a specific user, retrieved
    from webhooks.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of the type Integer
        Primary key. Identifier of the table.
    meeting_event_Id : Column of the type Integer
        Foreign Key. Identifier of the associated MeetingsEvents table (instatiated by id).
    created_at : Column of the type DateTime
        Datetime of the user creation.
    updated_at : Column of the type DateTime
        Last datetime the user was updated.
    name : Column of the type String
        Name of the user.
    role : Column of the type String
        Role of the user.
    join_time : Column of the type BigInteger
        Timestamp of when the user joined.
    leave_time : Column of the type BigInteger
        Timestamp of when the user left.
    internal_user_id : Column of the type String
        Internal user ID of the user.
    external_user_id : Column of the type String
        External user ID of the user.
    metadata : Column of the type JSON
        Information about the user metadata.
    """
    __tablename__ = "UsersEvents"

    id = Column(Integer, primary_key=True)
    meeting_event_Id = Column(Integer, ForeignKey("meetings_events.id"))

    meeting_event = relationship("MeetingsEvents")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    name = Column(String)
    role = Column(String)
    join_time = Column(BigInteger)
    leave_time = Column(BigInteger)
    internal_user_id = Column(String, unique=True)
    external_user_id = Column(String)

    meta_data = Column("metadata", JSON)


    def __repr__(self):
        return ("<UsersEvents("
                + "id=" + str(self.id)
                + ", created_at=" + str(self.created_at)
                + ", updated_at=" + str(self.updated_at)
                + ", name=" + str(self.name)
                + ", role=" + str(self.role)
                + ", join_time=" + str(self.join_time)
                + ", leave_time=" + str(self.leave_time)
                + ", internal_user_id=" + str(self.internal_user_id)
                + ", external_user_id=" + str(self.external_user_id)
                + ")>")


@contextmanager
def session_scope(raise_exception=True):
    """Provide a transactional scope around a series of operations.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        if raise_exception:
            raise
    finally:
        session.close()


class DataProcessor:
    """Data processor of the received information.

    It provides methods to update rows in the following tables:
        -Meetings;
        -MeetingsEvents;
        -Recordings;
        -UsersEvents.
    """
    def __init__(self, session, data, logger=None):
        """Constructor of the DataProcessor.

        Parameters
        ----------
        session : sqlalchemy.Session
            Session used by SQLAlchemy to interact with the database.
        data : dict list
            Informations that the methods in this class will use to update the database.
        """
        self.session = session
        self.webhook_msg = data[0]
        self.mapped_msg = data[1]
        self.logger = logger or logging.getLogger(__name__)

    def create_meeting(self):
        """Event meetings_created.

        It creates a new instance of MeetingsEvents with the received data and a
        new Meetings table that's related to the MeetingsEvents.

        Then add them to the session.
        """
        self.logger.info("Processing meeting_created message for internal_meeting_id: {}"
                        .format(self.mapped_msg["internal_meeting_id"]))
        # Create MeetingsEvents and Meetings table
        new_meeting_evt = MeetingsEvents(**self.mapped_msg)
        new_meeting = Meetings(running=False,
                               has_user_joined=False,
                               participant_count=0,
                               listener_count=0,
                               voice_participant_count=0,
                               video_count=0,
                               moderator_count=0,
                               attendees=[])
        new_meeting.meeting_event = new_meeting_evt
        self.session.add(new_meeting)

    def user_join(self):
        """Event user_joined.

        It creates a new instance of UsersEvents with the received data, and
        update the Meetings and MeetingsEvents tables that are related to the
        new user.

        Then add them to the session.
        """
        int_id = self.webhook_msg["data"]["attributes"]["meeting"]["internal-meeting-id"]
        self.logger.info("Processing user_join message for int_user_id: {}, on {}"
                    .format(self.webhook_msg["data"]["attributes"]["user"]["internal-user-id"],int_id))

        # Create user table
        new_user = UsersEvents(**self.mapped_msg)

        # Create attendee json for meeting table
        attendee = {
            "is_presenter" : self.webhook_msg["data"]["attributes"]["user"]["presenter"],
            "is_listening_only" : self.webhook_msg["data"]["attributes"]["user"]["listening-only"],
            "has_joined_voice" : self.webhook_msg["data"]["attributes"]["user"]["sharing-mic"],
            "has_video" : self.webhook_msg["data"]["attributes"]["user"]["stream"],
            "ext_user_id" : self.webhook_msg["data"]["attributes"]["user"]["external-user-id"],
            "int_user_id" : self.webhook_msg["data"]["attributes"]["user"]["internal-user-id"],
            "full_name" : self.webhook_msg["data"]["attributes"]["user"]["name"],
            "role" : self.webhook_msg["data"]["attributes"]["user"]["role"]
        }

        # Query for MeetingsEvents to link with UsersEvents table
        meeting_evt_table = self.session.query(MeetingsEvents).\
                            filter(MeetingsEvents.internal_meeting_id.match(int_id)).first()
        new_user.meeting_event = meeting_evt_table

        # Meeting table to be updated
        meeting_table = self.session.query(Meetings).\
                        join(Meetings.meeting_event).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()
        meeting_table = self.session.query(Meetings).get(meeting_table.id)

        def attendee_json(base,new):
            if not base:
                arr = []
                arr.append(new)
                return arr
            else:
                arr = base
                for elem in arr:
                    if(elem["int_user_id"] == new["int_user_id"]):
                        return arr
                arr.append(new)
                return arr

        meeting_table.running = True
        meeting_table.has_user_joined = True
        meeting_table.attendees = attendee_json(meeting_table.attendees,attendee)
        meeting_table.participant_count = len(meeting_table.attendees)
        meeting_table.moderator_count = sum(1 for a in meeting_table.attendees if a["role"] == "MODERATOR")
        meeting_table.listener_count = sum(1 for a in meeting_table.attendees if a["is_listening_only"])
        meeting_table.voice_participant_count = sum(1 for a in meeting_table.attendees if a["has_joined_voice"])
        meeting_table.video_count = sum(1 for a in meeting_table.attendees if a["has_video"])


        # SQLAlchemy was not considering the attendees array as modified, so it had to be forced
        flag_modified(meeting_table, "attendees")

        self.session.add(new_user)
        self.session.add(meeting_table)

        # Update unique users
        meeting_evt_table = self.session.query(MeetingsEvents).get(meeting_evt_table.id)
        meeting_evt_table.unique_users = int(self.session.query(UsersEvents.id).\
                                        join(UsersEvents.meeting_event).\
                                        filter(MeetingsEvents.internal_meeting_id == int_id).\
                                        count())

    def meeting_ended(self):
        """Event meeting_ended.

        It removes the Meetings table associated with the event and update the
        MeetingsEvents table.

        Then add them to the session.
        """
        int_id = self.mapped_msg["internal_meeting_id"]
        self.logger.info("Processing meeting_ended message for internal_meeting_id: {}"
        .format(int_id))

        # MeetingsEvents table to be updated
        meeting_evt_table = self.session.query(MeetingsEvents).\
                            filter(MeetingsEvents.internal_meeting_id == int_id).first()
        meeting_evt_table = self.session.query(MeetingsEvents).get(meeting_evt_table.id)
        meeting_evt_table.end_time = self.mapped_msg["end_time"]
        self.session.add(meeting_evt_table)

        # Meeting table to be updated
        meeting_table = self.session.query(Meetings).\
                        join(Meetings.meeting_event).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()
        meeting_table = self.session.query(Meetings).get(meeting_table.id)
        self.session.delete(meeting_table)

    def user_left(self):
        """Event user_left

        It updates the UsersEvents and Meeting tables associated with the user.

        Then add them to the session.
        """
        user_id = self.mapped_msg["internal_user_id"]
        int_id = self.webhook_msg["data"]["attributes"]["meeting"]["internal-meeting-id"]
        self.logger.info("Processing user_left message for int_user_id: {} in {}"
                        .format(user_id,int_id))

        # Meeting table to be updated
        meeting_table = self.session.query(Meetings).\
                        join(Meetings.meeting_event).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()
        meeting_table = self.session.query(Meetings).get(meeting_table.id)

        # User table to be updated
        users_table = self.session.query(UsersEvents).\
                        filter(UsersEvents.internal_user_id == user_id).first()
        users_table = self.session.query(UsersEvents).get(users_table.id)

        # Update UsersEvents table
        users_table.leave_time = self.mapped_msg["leave_time"]

        def remove_attendee(base,remove):
            for idx,attendee in enumerate(base):
                if(attendee["int_user_id"] == remove):
                    del base[idx]
            return base

        # Update Meetings table
        meeting_table.attendees = remove_attendee(meeting_table.attendees,user_id)
        meeting_table.participant_count = len(meeting_table.attendees)
        meeting_table.moderator_count = sum(1 for a in meeting_table.attendees if a["role"]=="MODERATOR")
        meeting_table.listener_count = sum(1 for a in meeting_table.attendees if a["is_listening_only"])
        meeting_table.voice_participant_count = sum(1 for a in meeting_table.attendees if a["has_joined_voice"])
        meeting_table.video_count = sum(1 for a in meeting_table.attendees if a["has_video"])

        # Mark Meetings.attendees as modified for SQLAlchemy
        flag_modified(meeting_table,"attendees")
        self.session.add(meeting_table)

    def user_info_update(self):
        """Events user-audio-listen-only-enabled, user-audio-listen-only-disabled,
                    user-audio-voice-enabled, user-audio-voice-disabled,
                    user-cam-broadcast-start, user-cam-broadcast-end,
                    user-presenter-assigned, user-presenter-unassigned

        It updates the Meetings table related to the user that received those events.

        Then add them to the session.
        """
        user_id = self.mapped_msg["internal_user_id"]
        int_id = self.mapped_msg["internal_meeting_id"]
        self.logger.info("Processing {} message for int_user_id: {} on {}"
                        .format(self.webhook_msg["data"]["id"],user_id,int_id))

        # Meeting table to be updated
        meeting_table = self.session.query(Meetings).\
                        join(Meetings.meeting_event).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()
        meeting_table = self.session.query(Meetings).get(meeting_table.id)

        def update_attendees(base, update):
            if(update["event_name"] == "user-audio-voice-enabled"):
                attr = "has_joined_voice"
                value = True
            elif(update["event_name"] == "user-audio-voice-disabled"):
                attr = "has_joined_voice"
                value = False
            elif(update["event_name"] == "user-audio-listen-only-enabled"):
                attr = "is_listening_only"
                value = True
            elif(update["event_name"] == "user-audio-listen-only-disabled"):
                attr = "is_listening_only"
                value = False
            elif(update["event_name"] == "user-cam-broadcast-start"):
                attr = "has_video"
                value = True
            elif(update["event_name"] == "user-cam-broadcast-end"):
                attr = "has_video"
                value = False
            elif(update["event_name"] == "user-presenter-assigned"):
                attr="is_presenter"
                value = True
            elif(update["event_name"] == "user-presenter-unassigned"):
                attr = "is_presenter"
                value = False
            for attendee in base:
                if(attendee["int_user_id"] == user_id):
                    attendee[attr] = value
            return base

        meeting_table.attendees = update_attendees(meeting_table.attendees, self.mapped_msg)
        meeting_table.participant_count = len(meeting_table.attendees)
        meeting_table.moderator_count = sum(1 for a in meeting_table.attendees if a["role"] == "MODERATOR")
        meeting_table.listening_only = sum(1 for a in meeting_table.attendees if a["is_listening_only"])
        meeting_table.voice_participant_count = sum(1 for a in meeting_table.attendees if a["has_joined_voice"])
        meeting_table.video_count = sum(1 for a in meeting_table.attendees if a["has_video"])
        flag_modified(meeting_table,"attendees")

        self.session.add(meeting_table)

    def rap_events(self):
        """Events   rap-archive-started, rap-archive-ended,
                    rap-sanity-started, rap-sanity-ended,
                    rap-post-archive-started, rap-post-archive-ended,
                    rap-process-started, rap-process-ended,
                    rap-post-process-started, rap-post-process-ended,
                    rap-publish-started, rap-publish-ended,
                    rap-post-publish-started, rap-post-publish-ended

        It updates the Recordings table related to the event.

        Then add them to the session.
        """
        int_id = self.mapped_msg["internal_meeting_id"]
        self.logger.info("Processing {} message for internal_meeting_id: {}"
                        .format(self.webhook_msg["data"]["id"],int_id))
        # Check if table already exists
        try:
            record_table = self.session.query(Recordings.id).\
                            filter(Recordings.internal_meeting_id == int_id).first()
            # Check if there's record_table
            record_table = self.session.query(Recordings).get(record_table.id)
        except:
            # Create table
            record_table = Recordings(**self.mapped_msg)
            record_table.participants = int(self.session.query(UsersEvents.id).\
                                        join(MeetingsEvents).\
                                        filter(MeetingsEvents.internal_meeting_id == int_id).\
                                        count())
            self.session.add(record_table)
            record_table = self.session.query(Recordings.id).\
                            filter(Recordings.internal_meeting_id == int_id).first()
            record_table = self.session.query(Recordings).get(record_table.id)
        finally:
            # When publish end update most of information
            if(self.mapped_msg["current_step"] == "rap-publish-ended"):
                record_table.name = self.mapped_msg["name"]
                record_table.is_breakout = self.mapped_msg["is_breakout"]
                record_table.start_time = self.mapped_msg["start_time"]
                record_table.end_time = self.mapped_msg["end_time"]
                record_table.size = self.mapped_msg["size"]
                record_table.raw_size = self.mapped_msg["raw_size"]
                record_table.meta_data = self.mapped_msg["meta_data"]
                record_table.playback = self.mapped_msg["playback"]
                record_table.download = self.mapped_msg["download"]
            record_table.current_step = self.mapped_msg["current_step"]

            # Update status based on event
            if(self.mapped_msg["current_step"] == "rap-process-started"):
                record_table.status= "processing"
            elif(self.mapped_msg["current_step"] == "rap-process-ended"):
                record_table.status= "processed"
            elif(self.mapped_msg["current_step"] == "rap-publish-ended"):
                record_table.status= "published"
                record_table.published= True
            # treat "unpublished" and "deleted" when webhooks are emitting those events
            self.session.add(record_table)

    def db_event_selector(self):
        """Event Selector.

        Choose which event will be processed (which method to call), based on
        the received data.

        The methods won't commit any update, just add them to the session.
        """
        self.logger.info("Selecting event processor")
        id = self.webhook_msg["data"]["id"]
        if(id == "meeting-created"):
            self.create_meeting()
        elif(id == "user-joined"):
            self.user_join()
        elif(id == "user-left"):
            self.user_left()
        elif(id == "meeting-ended"):
            self.meeting_ended()
        elif(id in ["user-audio-listen-only-enabled", "user-audio-listen-only-disabled",
                    "user-audio-voice-enabled", "user-audio-voice-disabled",
                    "user-cam-broadcast-start", "user-cam-broadcast-end",
                    "user-presenter-assigned", "user-presenter-unassigned"]):
            self.user_info_update()
        elif(id in ["rap-archive-started", "rap-archive-ended",
                    "rap-sanity-started", "rap-sanity-ended",
                    "rap-post-archive-started", "rap-post-archive-ended",
                    "rap-process-started", "rap-process-ended",
                    "rap-post-process-started", "rap-post-process-ended",
                    "rap-publish-started", "rap-publish-ended",
                    "rap-post-publish-started", "rap-post-publish-ended"]):
            self.rap_events()

    def update(self):
        """Update tables with new data.

        Call the selector to decide which event will be processed.
        """
        self.db_event_selector()


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
        engine = create_engine(self.database_uri, echo=True)
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
                    DataProcessor(session, data).update()
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
            self.logger.error("Operational error on database.")

            raise CallbackError() from err
