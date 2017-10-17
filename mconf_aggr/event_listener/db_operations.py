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
     meetingEvent_id = Column(Integer, ForeignKey("MeetingsEvents.id"))
     meetingEvent = relationship("MeetingsEvents", backref=backref("Meetings", uselist=False))

     createdAt = Column(String, default=datetime.datetime.now().strftime("%y-%m-%d %H:%M"))
     updatedAt = Column(String, onupdate=datetime.datetime.now().strftime("%y-%m-%d %H:%M"))

     running = Column(Boolean)
     hasUserJoined = Column(Boolean)
     participantCount = Column(Integer)
     listenerCount = Column(Integer)
     voiceParticipantCount = Column(Integer)
     videoCount = Column(Integer)
     moderatorCount = Column(Integer)
     attendees = Column(JSON)

     def __repr__(self):
         return ("<Meetings("
                + "id=" + str(self.id)
                + ", createdAt=" + str(self.createdAt)
                + ", updatedAt=" + str(self.updatedAt)
                + ", running=" + str(self.running)
                + ", hasUserJoined=" + str(self.hasUserJoined)
                + ", participantCount=" + str(self.participantCount)
                + ", listenerCount=" + str(self.listenerCount)
                + ", voiceParticipantCount=" + str(self.voiceParticipantCount)
                + ", videoCount=" + str(self.videoCount)
                + ", moderatorCount=" + str(self.moderatorCount)
                + ", attendees=" + str(self. attendees)
                + ")>")


class MeetingsEvents(Base):
    __tablename__ = "MeetingsEvents"

    id = Column(Integer, primary_key=True)

    sharedSecretGuid = Column(String) #index?
    sharedSecretName = Column(String)
    serverGuid = Column(String)
    serverUrl = Column(String)

    createdAt = Column(String, default=datetime.datetime.now().strftime("%y-%m-%d %H:%M"))
    updatedAt = Column(String, onupdate=datetime.datetime.now().strftime("%y-%m-%d %H:%M"))

    externalMeetingId = Column(String) #index?
    internalMeetingId = Column(String, unique=True) #index?
    name = Column(String)
    createTime = Column(BigInteger)
    createDate = Column(String)
    voiceBridge = Column(Integer)
    dialNumber = Column(String)
    attendeePW = Column(String)
    moderatorPW = Column(String)
    duration = Column(Integer)
    recording = Column(Boolean)
    hasBeenForciblyEnded = Column(Boolean)
    startTime = Column(BigInteger)
    endTime = Column(BigInteger)
    maxUsers = Column(Integer)
    isBreakout = Column(Boolean)
    uniqueUsers = Column(Integer)
    meta_data = Column(JSON)

    def __repr__(self):
        return ("<MeetingsEvents("
                + "id=" + str(self.id)
                + ", sharedSecretGuid=" + str(self. sharedSecretGuid)
                + ", sharedSecretName=" + str(self. sharedSecretName)
                + ", serverGuid=" + str(self. serverGuid)
                + ", serverUrl=" + str(self.serverUrl)
                + ", createdAt=" + str(self.createdAt)
                + ", updatedAt=" + str(self.updatedAt)
                + ", externalMeetingId=" + str(self.externalMeetingId)
                + ", internalMeetingId=" + str(self.internalMeetingId)
                + ", name=" + str(self.name)
                + ", createTime=" + str(self.createTime)
                + ", createDate=" + str(self.createDate)
                + ", voiceBridge=" + str(self.voiceBridge)
                + ", dialNumber=" + str(self.dialNumber)
                + ", attendeePW=" + str(self.attendeePW)
                + ", moderatorPW=" + str(self.moderatorPW)
                + ", duration=" + str(self.duration)
                + ", recording=" + str(self.recording)
                + ", hasBeenForciblyEnded=" + str(self.hasBeenForciblyEnded)
                + ", startTime=" + str(self.startTime)
                + ", endTime=" + str(self.endTime)
                + ", maxUsers=" + str(self.maxUsers)
                + ", isBreakout=" + str(self.isBreakout)
                + ", uniqueUsers=" + str(self.uniqueUsers)
                + ", meta_data=" + str(self.meta_data)
                + ")>")


class Recordings(Base):
    __tablename__ = "Recordings"

    id = Column(Integer, primary_key=True)

    createdAt = Column(String, default=datetime.datetime.now().strftime("%y-%m-%d %H:%M"))
    updatedAt = Column(String, onupdate=datetime.datetime.now().strftime("%y-%m-%d %H:%M"))

    name = Column(String)
    status = Column(String)
    internalMeetingId = Column(String, unique=True)
    externalMeetingId = Column(String)

    isBreakout = Column(Boolean)
    published = Column(Boolean)
    startTime = Column(BigInteger)
    endTime = Column(BigInteger)
    participants = Column(Integer)
    size = Column(BigInteger)
    rawSize = Column(BigInteger)
    currentStep = Column(String)

    meta_data = Column(JSON)
    playback = Column(JSON)
    download = Column(JSON)

    def __repr__(self):
     return ("<Recordings("
            + "id=" + str(self.id)
            + ", createdAt=" + str(self.createdAt)
            + ", updatedAt=" + str(self.updatedAt)
            + ", name=" + str(self.name)
            + ", status=" + str(self.status)
            + ", isBreakout=" + str(self.isBreakout)
            + ", published=" + str(self.published)
            + ", startTime=" + str(self.startTime)
            + ", endTime=" + str(self.endTime)
            + ", participants=" + str(self.participants)
            + ", size=" + str(self.size)
            + ", rawSize=" + str(self.rawSize)
            + ", currentStep=" + str(self.currentStep)
            + ", internalMeetingId=" + str(self.internalMeetingId)
            + ", externalMeetingId=" + str(self.externalMeetingId)
            + ", meta_data=" + str(self. meta_data)
            + ", playback=" + str(self. playback)
            + ", download=" + str(self. download)
            + ")>")


class UsersEvents(Base):
    __tablename__ = "UsersEvents"

    id = Column(Integer, primary_key=True)
    meetingEvent_Id = Column(Integer, ForeignKey("MeetingsEvents.id"))

    meetingEvent = relationship("MeetingsEvents")

    createdAt = Column(String, default=datetime.datetime.now().strftime("%y-%m-%d %H:%M"))
    updatedAt = Column(String, onupdate=datetime.datetime.now().strftime("%y-%m-%d %H:%M"))

    name = Column(String)
    role = Column(String)
    joinTime = Column(BigInteger)
    leaveTime = Column(BigInteger)
    internalUserId = Column(String, unique=True)
    externalUserId = Column(String)

    meta_data = Column(JSON)


    def __repr__(self):
        return ("<UsersEvents("
                + "id=" + str(self.id)
                + ", createdAt=" + str(self.createdAt)
                + ", updatedAt=" + str(self.updatedAt)
                + ", name=" + str(self.name)
                + ", role=" + str(self.role)
                + ", joinTime=" + str(self.joinTime)
                + ", leaveTime=" + str(self.leaveTime)
                + ", internalUserId=" + str(self.internalUserId)
                + ", externalUserId=" + str(self.externalUserId)
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
                           hasUserJoined=False,
                           participantCount=0,
                           listenerCount=0,
                           voiceParticipantCount=0,
                           videoCount=0,
                           moderatorCount=0,
                           attendees="{}")
    new_meeting.meetingEvent = new_meeting_evt
    session.add(new_meeting)

    try:
        session.commit()
    except:
        session.rollback()

def user_join(webhook_msg, db_msg):
    global session
    int_id = webhook_msg["data"]["attributes"]["meeting"]["internal-meeting-id"]

    # Create user table
    new_user = UsersEvents(**db_msg)

    # Create attendee json for meeting table
    attendee = {
        "isPresenter" : webhook_msg["data"]["attributes"]["user"]["presenter"],
        "isListeningOnly" : webhook_msg["data"]["attributes"]["user"]["listening-only"],
        "hasJoinedVoice" : webhook_msg["data"]["attributes"]["user"]["sharing-mic"],
        "hasVideo" : webhook_msg["data"]["attributes"]["user"]["stream"],
        "extUserId" : webhook_msg["data"]["attributes"]["user"]["external-user-id"],
        "intUserId" : webhook_msg["data"]["attributes"]["user"]["internal-user-id"],
        "fullName" : webhook_msg["data"]["attributes"]["user"]["name"],
        "role" : webhook_msg["data"]["attributes"]["user"]["role"]
    }

    # Query for MeetingsEvents to link with UsersEvents table
    meeting_evt_table = session.query(MeetingsEvents).\
                        filter(MeetingsEvents.internalMeetingId.match(int_id)).first()
    new_user.meetingEvent = meeting_evt_table

    # Meeting table to be updated
    meeting_table = session.query(Meetings).\
                    join(Meetings.meetingEvent).\
                    filter(MeetingsEvents.internalMeetingId == int_id).first()
    meeting_table = session.query(Meetings).get(meeting_table.id)

    def attendee_json(base,new):
        if(base == "{}"):
            arr = []
            arr.append(new)
            return arr
        else:
            arr = base
            for elem in arr:
                if(elem["intUserId"] == new["intUserId"]):
                    return arr
            arr.append(new)
            return arr

    meeting_table.running = True
    meeting_table.hasUserJoined = True
    meeting_table.attendees = attendee_json(meeting_table.attendees,attendee)
    meeting_table.participantCount = len(meeting_table.attendees)
    meeting_table.moderatorCount = sum(1 for a in meeting_table.attendees if a["role"] == "MODERATOR")
    meeting_table.listenerCount = sum(1 for a in meeting_table.attendees if a["isListeningOnly"])
    meeting_table.voiceParticipantCount = sum(1 for a in meeting_table.attendees if a["hasJoinedVoice"])
    meeting_table.videoCount = sum(1 for a in meeting_table.attendees if a["hasVideo"])

    # SQLAlchemy was not considering the attendees array as modified, so it had to be forced
    flag_modified(meeting_table, "attendees")

    try:
        session.add(new_user)

        # Update unique users
        meeting_evt_table = session.query(MeetingsEvents).get(meeting_evt_table.id)
        meeting_evt_table.uniqueUsers = int(session.query(UsersEvents.id).\
                                        join(UsersEvents.meetingEvent).\
                                        filter(MeetingsEvents.internalMeetingId == int_id).\
                                        count())
        session.commit()
    except:
        session.rollback()

def meeting_ended(map):
    #TODO: When ending a meeting with users still inside, should update their leaveTime
    global session
    int_id = map["internalMeetingId"]

    # MeetingsEvents table to be updated
    meeting_evt_table = session.query(MeetingsEvents).\
                        filter(MeetingsEvents.internalMeetingId == int_id).first()
    meeting_evt_table = session.query(MeetingsEvents).get(meeting_evt_table.id)
    meeting_evt_table.endTime= map["endTime"]

    # Meeting table to be updated
    meeting_table = session.query(Meetings).\
                    join(Meetings.meetingEvent).\
                    filter(MeetingsEvents.internalMeetingId == int_id).first()
    meeting_table = session.query(Meetings).get(meeting_table.id)
    session.delete(meeting_table)

    try:
        session.commit()
    except:
        session.rollback()

def user_left(webhook_msg,db_msg):
    global session
    user_id = db_msg["internalUserId"]
    int_id = webhook_msg["data"]["attributes"]["meeting"]["internal-meeting-id"]

    # Meeting table to be updated
    meeting_table = session.query(Meetings).\
                    join(Meetings.meetingEvent).\
                    filter(MeetingsEvents.internalMeetingId == int_id).first()
    meeting_table = session.query(Meetings).get(meeting_table.id)

    # User table to be updated
    users_table = session.query(UsersEvents).\
                    filter(UsersEvents.internalUserId == user_id).first()
    users_table = session.query(UsersEvents).get(users_table.id)

    # Update UsersEvents table
    users_table.leaveTime = db_msg["leaveTime"]

    def remove_attendee(base,remove):
        for idx,attendee in enumerate(base):
            if(attendee["intUserId"] == remove):
                del base[idx]
        return base

    # Update Meetings table
    meeting_table.attendees = remove_attendee(meeting_table.attendees,user_id)
    meeting_table.participantCount = len(meeting_table.attendees)
    meeting_table.moderatorCount = sum(1 for a in meeting_table.attendees if a["role"]=="MODERATOR")
    meeting_table.listenerCount = sum(1 for a in meeting_table.attendees if a["isListeningOnly"])
    meeting_table.voiceParticipantCount = sum(1 for a in meeting_table.attendees if a["hasJoinedVoice"])
    meeting_table.videoCount = sum(1 for a in meeting_table.attendees if a["hasVideo"])

    # Mark Meetings.attendees as modified for SQLAlchemy
    flag_modified(meeting_table,"attendees")

    try:
        session.commit()
    except:
        session.rollback()

def user_info_update(map):
    global session
    user_id = map["internalUserId"]
    int_id = map["internalMeetingId"]

    # Meeting table to be updated
    meeting_table = session.query(Meetings).\
                    join(Meetings.meetingEvent).\
                    filter(MeetingsEvents.internalMeetingId == int_id).first()
    meeting_table = session.query(Meetings).get(meeting_table.id)

    def update_attendees(base, update):
        print("map", update)
        if(update["eventName"] == "user-audio-voice-enabled"):
            attr = "hasJoinedVoice"
            value = True
        elif(update["eventName"] == "user-audio-voice-disabled"):
            attr = "hasJoinedVoice"
            value = False
        elif(update["eventName"] == "user-audio-listen-only-enabled"):
            attr = "isListeningOnly"
            value = True
        elif(update["eventName"] == "user-audio-listen-only-disabled"):
            attr = "isListeningOnly"
            value = False
        elif(update["eventName"] == "user-cam-broadcast-start"):
            attr = "hasVideo"
            value = True
        elif(update["eventName"] == "user-cam-broadcast-end"):
            attr = "hasVideo"
            value = False
        for attendee in base:
            if(attendee["intUserId"] == user_id):
                attendee[attr] = value
        return base

    meeting_table.attendees = update_attendees(meeting_table.attendees, map)
    meeting_table.participantCount = len(meeting_table.attendees)
    meeting_table.moderatorCount = sum(1 for a in meeting_table.attendees if a["role"] == "MODERATOR")
    meeting_table.listenerCount = sum(1 for a in meeting_table.attendees if a["isListeningOnly"])
    meeting_table.voiceParticipantCount = sum(1 for a in meeting_table.attendees if a["hasJoinedVoice"])
    meeting_table.videoCount = sum(1 for a in meeting_table.attendees if a["hasVideo"])
    flag_modified(meeting_table,"attendees")

    try:
        session.commit()
    except:
        session.rollback()

def rap_events(map):
    global session
    int_id = map["internalMeetingId"]
    # Check if table already exists
    try:
        record_table = session.query(Recordings.id).\
                        filter(Recordings.internalMeetingId == int_id).first()
        # Check if there's record_table
        record_table = session.query(Recordings).get(record_table.id)
    except:
        # Create table
        record_table = Recordings(**map)
        record_table.participants = int(session.query(UsersEvents.id).\
                                    join(MeetingsEvents).\
                                    filter(MeetingsEvents.internalMeetingId == int_id).\
                                    count())
        session.add(record_table)
        record_table = session.query(Recordings.id).\
                        filter(Recordings.internalMeetingId == int_id).first()
        record_table = session.query(Recordings).get(record_table.id)
    finally:
        # When publish end update most of information
        if(map["currentStep"] == "rap-publish-ended"):
            record_table.name= map["name"]
            record_table.isBreakout= map["isBreakout"]
            record_table.startTime= map["startTime"]
            record_table.endTime= map["endTime"]
            record_table.size= map["size"]
            record_table.rawSize= map["rawSize"]
            record_table.meta_data= map["meta_data"]
            record_table.playback= map["playback"]
            record_table.download= map["download"]
        record_table.currentStep= map["currentStep"]

        # Update status based on event
        if(map["currentStep"] == "rap-process-started"):
            record_table.status= "processing"
        elif(map["currentStep"] == "rap-process-ended"):
            record_table.status= "processed"
        elif(map["currentStep"] == "rap-publish-ended"):
            record_table.status= "published"
            record_table.published= True
        # treat "unpublished" and "deleted" when webhooks are emitting those events

        try:
            session.commit()
        except:
            session.rollback()

def db_event_selector(post, map):
    id = post["data"]["id"]
    if(id == "meeting-created"):
        create_meeting(map)
    elif(id == "user-joined"):
        user_join(post,map)
    elif(id == "user-left"):
        user_left(post,map)
    elif(id == "meeting-ended"):
        meeting_ended(map)
    elif(id in ["user-audio-listen-only-enabled","user-audio-listen-only-disabled",
                "user-audio-voice-enabled","user-audio-voice-disabled",
                "user-cam-broadcast-start","user-cam-broadcast-end"]):
        user_info_update(map)
    elif(id in ["rap-archive-started","rap-archive-ended",
                "rap-sanity-started","rap-sanity-ended",
                "rap-post-archive-started","rap-post-archive-ended",
                "rap-process-started","rap-process-ended",
                "rap-post-process-started","rap-post-process-ended",
                "rap-publish-started","rap-publish-ended",
                "rap-post-publish-started","rap-post-publish-ended"]):
        rap_events(map)
