import datetime
import json

import sqlalchemy
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

# This block is likely to be removed after dev stage
engine = create_engine("postgresql://postgres:postgres@localhost/testdb3", echo=True)
Base = declarative_base()


# DB Tables
class Meetings(Base):
     __tablename__ = "Meetings"

     id = Column(Integer, primary_key=True)
     meeting_event_id = Column(Integer, ForeignKey("MeetingsEvents.id"))
     meeting_event = relationship("MeetingsEvents", backref=backref("Meetings", uselist=False))

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
    __tablename__ = "MeetingsEvents"

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
    has_been_forcibly_ended = Column(Boolean)
    start_time = Column(BigInteger)
    end_time = Column(BigInteger)
    max_users = Column(Integer)
    is_breakout = Column(Boolean)
    unique_users = Column(Integer)
    meta_data = Column(JSON)

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
                + ", has_been_forcibly_ended=" + str(self.has_been_forcibly_ended)
                + ", start_time=" + str(self.start_time)
                + ", end_time=" + str(self.end_time)
                + ", max_users=" + str(self.max_users)
                + ", is_breakout=" + str(self.is_breakout)
                + ", unique_users=" + str(self.unique_users)
                + ", meta_data=" + str(self.meta_data)
                + ")>")


class Recordings(Base):
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
    __tablename__ = "UsersEvents"

    id = Column(Integer, primary_key=True)
    meeting_event_Id = Column(Integer, ForeignKey("MeetingsEvents.id"))

    meeting_event = relationship("MeetingsEvents")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    name = Column(String)
    role = Column(String)
    join_time = Column(BigInteger)
    leave_time = Column(BigInteger)
    internal_user_id = Column(String, unique=True)
    external_user_id = Column(String)

    meta_data = Column(JSON)


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

# This block is likely to be removed after dev stage
#Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# TODO: Lock tables when performing SELECTs/UPDATEs

def create_meeting(db_msg):
    global sessions

    # Create MeetingsEvents and Meetings table
    new_meeting_evt = MeetingsEvents(**db_msg)
    new_meeting = Meetings(running=False,
                           has_user_joined=False,
                           participant_count=0,
                           listener_count=0,
                           voice_participant_count=0,
                           video_count=0,
                           moderator_count=0,
                           attendees="{}")
    new_meeting.meeting_event = new_meeting_evt
    session.add(new_meeting)

    session.commit()
    session.rollback()

def user_join(webhook_msg, db_msg):
    global session
    int_id = webhook_msg["data"]["attributes"]["meeting"]["internal-meeting-id"]

    # Create user table
    new_user = UsersEvents(**db_msg)

    # Create attendee json for meeting table
    attendee = {
        "is_presenter" : webhook_msg["data"]["attributes"]["user"]["presenter"],
        "is_listening_only" : webhook_msg["data"]["attributes"]["user"]["listening-only"],
        "has_joined_voice" : webhook_msg["data"]["attributes"]["user"]["sharing-mic"],
        "has_video" : webhook_msg["data"]["attributes"]["user"]["stream"],
        "ext_user_id" : webhook_msg["data"]["attributes"]["user"]["external-user-id"],
        "int_user_id" : webhook_msg["data"]["attributes"]["user"]["internal-user-id"],
        "full_name" : webhook_msg["data"]["attributes"]["user"]["name"],
        "role" : webhook_msg["data"]["attributes"]["user"]["role"]
    }

    # Query for MeetingsEvents to link with UsersEvents table
    meeting_evt_table = session.query(MeetingsEvents).\
                        filter(MeetingsEvents.internal_meeting_id.match(int_id)).first()
    new_user.meeting_event = meeting_evt_table

    # Meeting table to be updated
    meeting_table = session.query(Meetings).\
                    join(Meetings.meeting_event).\
                    filter(MeetingsEvents.internal_meeting_id == int_id).first()
    meeting_table = session.query(Meetings).get(meeting_table.id)

    def attendee_json(base,new):
        if(base == "{}"):
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

    try:
        session.add(new_user)

        # Update unique users
        meeting_evt_table = session.query(MeetingsEvents).get(meeting_evt_table.id)
        meeting_evt_table.uniqueUsers = int(session.query(UsersEvents.id).\
                                        join(UsersEvents.meeting_event).\
                                        filter(MeetingsEvents.internal_meeting_id == int_id).\
                                        count())
        session.commit()
    except:
        session.rollback()

def meeting_ended(mapped_msg):
    #TODO: When ending a meeting with users still inside, should update their leaveTime
    global session
    int_id = mapped_msg["internal_meeting_id"]

    # MeetingsEvents table to be updated
    meeting_evt_table = session.query(MeetingsEvents).\
                        filter(MeetingsEvents.internal_meeting_id == int_id).first()
    meeting_evt_table = session.query(MeetingsEvents).get(meeting_evt_table.id)
    meeting_evt_table.end_time= mapped_msg["end_time"]

    # Meeting table to be updated
    meeting_table = session.query(Meetings).\
                    join(Meetings.meeting_event).\
                    filter(MeetingsEvents.internal_meeting_id == int_id).first()
    meeting_table = session.query(Meetings).get(meeting_table.id)
    session.delete(meeting_table)

    try:
        session.commit()
    except:
        session.rollback()

def user_left(webhook_msg,db_msg):
    global session
    user_id = db_msg["internal_user_id"]
    int_id = webhook_msg["data"]["attributes"]["meeting"]["internal-meeting-id"]

    # Meeting table to be updated
    meeting_table = session.query(Meetings).\
                    join(Meetings.meeting_event).\
                    filter(MeetingsEvents.internal_meeting_id == int_id).first()
    meeting_table = session.query(Meetings).get(meeting_table.id)

    # User table to be updated
    users_table = session.query(UsersEvents).\
                    filter(UsersEvents.internal_user_id == user_id).first()
    users_table = session.query(UsersEvents).get(users_table.id)

    # Update UsersEvents table
    users_table.leave_time = db_msg["leave_time"]

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

    try:
        session.commit()
    except:
        session.rollback()

def user_info_update(mapped_msg):
    global session
    user_id = mapped_msg["internal_user_id"]
    int_id = mapped_msg["internal_meeting_id"]

    # Meeting table to be updated
    meeting_table = session.query(Meetings).\
                    join(Meetings.meeting_event).\
                    filter(MeetingsEvents.internal_meeting_id == int_id).first()
    meeting_table = session.query(Meetings).get(meeting_table.id)

    def update_attendees(base, update):
        if(update["event_name"] == "user-audio-voice-enabled"):
            attr = "hasJoinedVoice"
            value = True
        elif(update["event_name"] == "user-audio-voice-disabled"):
            attr = "hasJoinedVoice"
            value = False
        elif(update["event_name"] == "user-audio-listen-only-enabled"):
            attr = "isListeningOnly"
            value = True
        elif(update["event_name"] == "user-audio-listen-only-disabled"):
            attr = "isListeningOnly"
            value = False
        elif(update["event_name"] == "user-cam-broadcast-start"):
            attr = "hasVideo"
            value = True
        elif(update["event_name"] == "user-cam-broadcast-end"):
            attr = "hasVideo"
            value = False
        for attendee in base:
            if(attendee["int_user_id"] == user_id):
                attendee[attr] = value
        return base

    meeting_table.attendees = update_attendees(meeting_table.attendees, mapped_msg)
    meeting_table.participant_count = len(meeting_table.attendees)
    meeting_table.moderator_count = sum(1 for a in meeting_table.attendees if a["role"] == "MODERATOR")
    meeting_table.listening_only = sum(1 for a in meeting_table.attendees if a["is_listening_only"])
    meeting_table.voice_participant_count = sum(1 for a in meeting_table.attendees if a["has_joined_voice"])
    meeting_table.video_count = sum(1 for a in meeting_table.attendees if a["has_video"])
    flag_modified(meeting_table,"attendees")

    try:
        session.commit()
    except:
        session.rollback()

def rap_events(mapped_msg):
    global session
    int_id = mapped_msg["internal_meeting_id"]
    # Check if table already exists
    try:
        record_table = session.query(Recordings.id).\
                        filter(Recordings.internal_meeting_id == int_id).first()
        # Check if there's record_table
        record_table = session.query(Recordings).get(record_table.id)
    except:
        # Create table
        record_table = Recordings(**mapped_msg)
        record_table.participants = int(session.query(UsersEvents.id).\
                                    join(MeetingsEvents).\
                                    filter(MeetingsEvents.internal_meeting_id == int_id).\
                                    count())
        session.add(record_table)
        record_table = session.query(Recordings.id).\
                        filter(Recordings.internal_meeting_id == int_id).first()
        record_table = session.query(Recordings).get(record_table.id)
    finally:
        # When publish end update most of information
        if(mapped_msg["current_step"] == "rap-publish-ended"):
            record_table.name = mapped_msg["name"]
            record_table.is_breakout = mapped_msg["is_breakout"]
            record_table.start_time = mapped_msg["start_time"]
            record_table.end_time = mapped_msg["end_time"]
            record_table.size = mapped_msg["size"]
            record_table.raw_size = mapped_msg["raw_size"]
            record_table.meta_data = mapped_msg["meta_data"]
            record_table.playback = mapped_msg["playback"]
            record_table.download = mapped_msg["download"]
        record_table.current_step = mapped_msg["current_step"]

        # Update status based on event
        if(mapped_msg["current_step"] == "rap-process-started"):
            record_table.status= "processing"
        elif(mapped_msg["current_step"] == "rap-process-ended"):
            record_table.status= "processed"
        elif(mapped_msg["current_step"] == "rap-publish-ended"):
            record_table.status= "published"
            record_table.published= True
        # treat "unpublished" and "deleted" when webhooks are emitting those events

        try:
            session.commit()
        except:
            session.rollback()

def db_event_selector(post, mapped_msg):
    id = post["data"]["id"]
    if(id == "meeting-created"):
        create_meeting(mapped_msg)
    elif(id == "user-joined"):
        user_join(post,mapped_msg)
    elif(id == "user-left"):
        user_left(post,mapped_msg)
    elif(id == "meeting-ended"):
        meeting_ended(mapped_msg)
    elif(id in ["user-audio-listen-only-enabled","user-audio-listen-only-disabled",
                "user-audio-voice-enabled","user-audio-voice-disabled",
                "user-cam-broadcast-start","user-cam-broadcast-end"]):
        user_info_update(mapped_msg)
    elif(id in ["rap-archive-started","rap-archive-ended",
                "rap-sanity-started","rap-sanity-ended",
                "rap-post-archive-started","rap-post-archive-ended",
                "rap-process-started","rap-process-ended",
                "rap-post-process-started","rap-post-process-ended",
                "rap-publish-started","rap-publish-ended",
                "rap-post-publish-started","rap-post-publish-ended"]):
        rap_events(mapped_msg)