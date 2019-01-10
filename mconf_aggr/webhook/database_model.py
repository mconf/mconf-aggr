import datetime

from sqlalchemy import (BigInteger,
                        Boolean,
                        create_engine,
                        Column,
                        DateTime,
                        ForeignKey,
                        Integer,
                        JSON,
                        String,
                        Enum)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship


"""Base class from which we extend table classes.
"""
Base = declarative_base()

"""Status of a recording life-cycle.
"""
STATUS = ('processing', 'processed', 'published', 'unpublished', 'deleted')

"""New data type in database.
"""
status_enum = Enum(*STATUS, name="status")


class Meetings(Base):
    """Table meetings in the database.

    Each row in this table represents an information about the attendees of a meeting,
    retrieved from the webhooks.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of type Integer
        Primary key. Identifier of the table.
    meeting_event_id : Column of type Integer
        Foreign Key. Identifier of the associated MeetingsEvents table (instatiated by id).
    created_at : Column of type DateTime
        Datetime of the meeting creation.
    updated_at : Column of type DateTime
        Last datetime the meeting was updated.
    running : Column of type Boolean
        Indicates if the meeting is running.
    has_user_joined : Column of type Boolean
        Indicates if a user has already joined.
    participant_count : Column of type Integer
        Number of participants on the meeting.
    listener_count : Column of type Integer
        Number of listeners on the meeting.
    voice_participant_count : Column of type Integer
        Number of participants on the meeting with active voice chat.
    video_count : Column of type Integer
        Number of participants on the meeting with video share.
    moderator_count : Column of type Integer
        Number of moderators on the meeting.
    attendees : Column of type JSON
        Each attendee on the meeting, especified on the format:

        [
            {
                "is_presenter": boolean,
                "is_listening_only": boolean,
                "has_joined_voice": boolean,
                "has_video": boolean,
                "external_user_id": string,
                "internal_user_id": string,
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
    meeting_event = relationship("MeetingsEvents")

    #meeting_event = relationship("MeetingsEvents", backref=backref("meetings", uselist=False))

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

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
    """Table meetings_events in the database.

    Each row in the table represents an information about a meeting, retrieve
    from the webhooks.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of type Integer
        Primary key. Identifier of the table.
    shared_secret_guid : Column of type String
        Shared secret GUID.
    shared_secret_name : Column of type String
        Shared secret Name.
    server_guid : Column of type String
        Server GUID.
    server_url : Column of type String
        URL of the server the meeting is hosted.
    institution_guid : Column of the type String.
        Institution GUID.
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

    shared_secret_guid = Column(String) # Index?
    shared_secret_name = Column(String)
    server_guid = Column(String)
    server_url = Column(String)
    institution_guid = Column(String)

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    external_meeting_id = Column(String) # Index?
    internal_meeting_id = Column(String, unique=True) # Index?
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
    meta_data = Column("metadata", JSON) # Name metadata is used by Base class.

    def __repr__(self):
        return ("<MeetingsEvents("
                + "id=" + str(self.id)
                + ", shared_secret_guid=" + str(self. shared_secret_guid)
                + ", shared_secret_name=" + str(self. shared_secret_name)
                + ", server_guid=" + str(self. server_guid)
                + ", server_url=" + str(self.server_url)
                + ", institution_guid=" + str(self.institution_guid)
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
    """Table recordings in the database.

    Each row in this table represents information about a recording, retrieved
    from the webhooks.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of type Integer
        Primary key. Identifier of the recording.
    created_at : Column of type DateTime
        Datetime of the recording creation.
    updated_at : Column of type DateTime
        Last datetime the recording was updated.
    record_id : Column of type String.
        Internal identifier of the recording.
    meeting_event_id : Column of type Integer.
        Identifier of the associated meetings_events table.
    server_id : Column of type Integer.
        Identifier of the associated servers table.
    name : Column of type String
        Name of the recording.
    status : Column of type String
        Current status of the recording.
    internal_meeting_id : Column of type String
        Internal meeting ID of the recording.
    external_meeting_id : Column of type String
        External meeting ID of the recording.
    is_breakout : Column of type Boolean
        Indicates if the recording if from a breakout room.
    published : Column of type Boolean
        Indicates if the recording's been published.
    start_time : Column of type BigInteger
        Timestamp of when the recording was created.
    end_time : Column of type BigInteger
        Timestamp of when the recording ended.
    participants : Column of type Integer
        Number of participants on the recorded meeting.
    size : Column of type BigInteger
        Size of the recording.
    raw_size : Column of type BigInteger.
        Raw size of the recording.
    current_step : Column of type String.
        Current step of the recordig.
    meta_data : Column of type JSON
        Information about the recording metadata.
    playback : Column of type JSON
        Information about the recording playback.
    download : Column of type JSON
        Information about the recording download.
    """
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    record_id = Column(String, unique=True)
    meeting_event_id = Column(Integer)
    server_id = Column(Integer)

    name = Column(String)
    status = Column(status_enum)
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

    meta_data = Column("metadata", JSON) # Name metadata is used by Base class.
    playback = Column(JSON)
    download = Column(JSON)

    def __repr__(self):
     return ("<Recordings("
            + "id=" + str(self.id)
            + ", created_at=" + str(self.created_at)
            + ", updated_at=" + str(self.updated_at)
            + ", record_id=" + str(self.record_id)
            + ", server_id=" + str(self.server_id)
            + ", name=" + str(self.name)
            + ", status=" + str(self.status)
            + ", internal_meeting_id=" + str(self.internal_meeting_id)
            + ", external_meeting_id=" + str(self.external_meeting_id)
            + ", is_breakout=" + str(self.is_breakout)
            + ", published=" + str(self.published)
            + ", start_time=" + str(self.start_time)
            + ", end_time=" + str(self.end_time)
            + ", participants=" + str(self.participants)
            + ", size=" + str(self.size)
            + ", raw_size=" + str(self.raw_size)
            + ", current_step=" + str(self.current_step)
            + ", meta_data=" + str(self. meta_data)
            + ", playback=" + str(self. playback)
            + ", download=" + str(self. download)
            + ")>")


class UsersEvents(Base):
    """Table users_events in the database.

    Each row in the table represents information about a specific user, retrieved
    from webhooks.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of type Integer
        Primary key. Identifier of the table.
    meeting_event_id : Column of type Integer
        Foreign Key. Identifier of the associated MeetingsEvents table (instatiated by id).
    created_at : Column of type DateTime
        Datetime of the user creation.
    updated_at : Column of type DateTime
        Last datetime the user was updated.
    name : Column of type String
        Name of the user.
    role : Column of type String
        Role of the user.
    join_time : Column of type BigInteger
        Timestamp of when the user joined.
    leave_time : Column of type BigInteger
        Timestamp of when the user left.
    internal_user_id : Column of type String
        Internal user ID of the user.
    external_user_id : Column of type String
        External user ID of the user.
    metadata : Column of type JSON
        Information about the user metadata.
    """
    __tablename__ = "users_events"

    id = Column(Integer, primary_key=True)
    meeting_event_id = Column(Integer, ForeignKey("meetings_events.id"))
    meeting_event = relationship("MeetingsEvents")

    #meeting_event = relationship("MeetingsEvents", backref=backref("users_events", uselist=False))

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    name = Column(String)
    role = Column(String)
    join_time = Column(BigInteger)
    leave_time = Column(BigInteger)
    internal_user_id = Column(String, unique=True)
    external_user_id = Column(String)

    meta_data = Column("metadata", JSON) # Name metadata is used by Base class.

    def __repr__(self):
        return ("<UsersEvents("
                + "id=" + str(self.id)
                + ", meeting_event_id=" + str(self.meeting_event_id)
                + ", created_at=" + str(self.created_at)
                + ", updated_at=" + str(self.updated_at)
                + ", name=" + str(self.name)
                + ", role=" + str(self.role)
                + ", join_time=" + str(self.join_time)
                + ", leave_time=" + str(self.leave_time)
                + ", internal_user_id=" + str(self.internal_user_id)
                + ", external_user_id=" + str(self.external_user_id)
                + ", meta_data=" + str(self.meta_data)
                + ")>")


class Servers(Base):
    """Table servers in the database.

    Each row in the table represents information about a specific server.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of type Integer
        Primary key. Identifier of the table.
    guid : Column of type String
        Server GUID.
    institution_guid : Column of type String
        Institution GUID.
    secret : Column of type String
        Shared secret.
    ip : Column of type String
        Server IP.
    """
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    institution_guid = Column(String, unique=True)
    name = Column(String)
    secret = Column(String)
    ip = Column(String)
    enabled = Column(Boolean)

    def __repr__(self):
        return ("<Servers("
                + "id=" + str(self.id)
                + ", guid=" + str(self.guid)
                + ", institution_guid=" + str(self.institution_guid)
                + ", name=" + str(self.name)
                + ", secret=" + str(self.secret)
                + ", ip=" + str(self.ip)
                + ")>")


class SharedSecrets(Base):
    """Table shared_secrets in the database.

    Each row in the table represents information about a specific shared secret.
    It inherits from Base - a base class to represent tables by SQLAlchemy.

    Attributes
    ----------
    id : Column of type Integer
        Primary key. Identifier of the table.
    guid : Column of type String
        Shared secret GUID.
    institution_guid : Column of type String
        Institution GUID.
    secret : Column of type String
        Shared secret.
    name : Column of type String
        Name of the shared secret.
    scope : Column of type String
        Scope of the shared secret.
    created_at : Column of type DateTime
        Datetime of the meeting creation.
    updated_at : Column of type DateTime
        Last datetime the meeting was updated.
    """
    __tablename__ = "shared_secrets"

    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True)
    institution_guid = Column(String, unique=True)
    name = Column(String)
    secret = Column(String)
    scope = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return ("<SharedSecrets("
                + "id=" + str(self.id)
                + ", guid=" + str(self.guid)
                + ", institution_guid=" + str(self.institution_guid)
                + ", name=" + str(self.name)
                + ", secret=" + str(self.secret)
                + ", scope=" + str(self.scope)
                + ", created_at=" + str(self.created_at)
                + ", updated_at=" + str(self.updated_at)
                + ")>")
