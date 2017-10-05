import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Boolean, JSON, BigInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey, update, event
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import flag_modified
import json

engine = create_engine('postgresql://postgres:postgres@localhost/testdb3', echo=True)

import base

import Meetings
import MeetingsEvents
import UsersEvents

from MeetingsEvents import MeetingsEvents
from Meetings import Meetings
from UsersEvents import UsersEvents

#base.Base.metadata.drop_all(engine)
base.Base.metadata.create_all(engine) # May not update schema here
Session = sessionmaker(bind=engine)
session = Session()
# Rolling back a session clear all changes

def accessDB():
    global session
    if(not session):
        # Session to access db
        Session = sessionmaker(bind=engine)
        session = Session()

def addMeetings(meetingData):
    meetingObj = Meetings(meetingData)
    accessDB()
    session.add(meetingObj)

def addUsersEvents(userData):
    userObj = UsersEvents(userData)
    accessDB()
    session.add(userObj)

def commitDB():
    accessDB()
    session.commit()

def createMeeting(dbMsg):
    # Create meetingevent and meeting table
    # Create meetingevt on db
    newMeetingEvt = MeetingsEvents(**dbMsg)
    #update meeting table msg and create table
    newMeeting = Meetings(running=False,hasUserJoined=False,participantCount=0,listenerCount=0,voiceParticipantCount=0,videoCount=0,moderatorCount=0,attendees="{}")
    newMeeting.meetingEvent = newMeetingEvt
    accessDB()
    session.add(newMeeting)
    session.commit()

def userJoin(webhookMsg, dbMsg):
    global session

    # Create user table
    newUser = UsersEvents(**dbMsg)

    # Create attendee json for meeting table
    attendee = {
        "isPresenter" : webhookMsg["data"]["attributes"]["user"]["presenter"],
        "isListeningOnly" : webhookMsg["data"]["attributes"]["user"]["listening-only"],
        "hasJoinedVoice" : webhookMsg["data"]["attributes"]["user"]["sharing-mic"],
        "hasVideo" : webhookMsg["data"]["attributes"]["user"]["stream"],
        "extUserId" : webhookMsg["data"]["attributes"]["user"]["external-user-id"],
        "intUserId" : webhookMsg["data"]["attributes"]["user"]["internal-user-id"],
        "fullName" : webhookMsg["data"]["attributes"]["user"]["name"],
        "role" : webhookMsg["data"]["attributes"]["user"]["role"]
    }

    # Query for MeetingEventsTable to link with user table
    intId = webhookMsg["data"]["attributes"]["meeting"]["internal-meeting-id"]
    meetingEvtTable = session.query(MeetingsEvents).filter(MeetingsEvents.internalMeetingId.match(intId)).first()
    newUser.meetingEvent = meetingEvtTable
    session.add(newUser)

    # Meeting table to be updated
    meetingTable = session.query(Meetings).\
        join(Meetings.meetingEvent).\
        filter(MeetingsEvents.internalMeetingId == intId).first()

    meetingTable = session.query(Meetings).get(meetingTable.id)

    def attendeeJson(base,new):
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

    meetingTable.running= True
    meetingTable.hasUserJoined= True
    meetingTable.attendees= attendeeJson(meetingTable.attendees,attendee)
    meetingTable.participantCount= len(meetingTable.attendees)
    meetingTable.moderatorCount= sum(1 for a in meetingTable.attendees if a["role"]=="MODERATOR")
    meetingTable.listenerCount= sum(1 for a in meetingTable.attendees if a["isListeningOnly"])
    meetingTable.voiceParticipantCount= sum(1 for a in meetingTable.attendees if a["hasJoinedVoice"])
    meetingTable.videoCount= sum(1 for a in meetingTable.attendees if a["hasVideo"])
    # SQLAlchemy was not considering the attendees array as modified, so it had to be forced
    flag_modified(meetingTable,"attendees")

    # Commit all previous operations, if fails, all will be rolled back
    session.commit()

    # Display tables instances
    # for x in session.query(Meetings):
    #     print(x)
    # for x in session.query(UsersEvents):
    #     print(x)
    # for x in session.query(MeetingsEvents):
    #     print(x)

def meetingEnded(map):
    global session
    # MeetingsEvents table to be updated
    intId = map["internalMeetingId"]

    meetingEvtTable = session.query(MeetingsEvents).\
        filter(MeetingsEvents.internalMeetingId == intId).first()

    meetingEvtTable = session.query(MeetingsEvents).get(meetingEvtTable.id)
    # Meeting table to be updated
    meetingTable = session.query(Meetings).\
        join(Meetings.meetingEvent).\
        filter(MeetingsEvents.internalMeetingId == intId).first()

    meetingTable = session.query(Meetings).get(meetingTable.id)

    session.delete(meetingTable)

    meetingEvtTable.endTime= map["endTime"]

    session.commit()

def userLeft(webhookMsg,dbMsg):
    global session
    userId = dbMsg["internalUserId"]
    intId = webhookMsg["data"]["attributes"]["meeting"]["internal-meeting-id"]

    # Meeting table to be updated
    meetingTable = session.query(Meetings).\
        join(Meetings.meetingEvent).\
        filter(MeetingsEvents.internalMeetingId == intId).first()

    meetingTable = session.query(Meetings).get(meetingTable.id)

    # User table to be updated
    usersTable = session.query(UsersEvents).\
        filter(UsersEvents.internalUserId == userId).first()

    usersTable = session.query(UsersEvents).get(usersTable.id)

    # Update Meetings table

    def removeAttendee(base,remove):
        for idx,attendee in enumerate(base):
            if(attendee["intUserId"] == remove):
                del base[idx]
        return base

    meetingTable.attendees= removeAttendee(meetingTable.attendees,userId)
    meetingTable.participantCount= len(meetingTable.attendees)
    meetingTable.moderatorCount= sum(1 for a in meetingTable.attendees if a["role"]=="MODERATOR")
    meetingTable.listenerCount= sum(1 for a in meetingTable.attendees if a["isListeningOnly"])
    meetingTable.voiceParticipantCount= sum(1 for a in meetingTable.attendees if a["hasJoinedVoice"])
    meetingTable.videoCount= sum(1 for a in meetingTable.attendees if a["hasVideo"])
    flag_modified(meetingTable,"attendees")

    # Update UsersEvents table
    usersTable.leaveTime= dbMsg["leaveTime"]

    session.commit()

def userInfoUpdate(map):
    global session
    userId = map["internalUserId"]
    intId = map["internalMeetingId"]

    # Meeting table to be updated
    meetingTable = session.query(Meetings).\
        join(Meetings.meetingEvent).\
        filter(MeetingsEvents.internalMeetingId == intId).first()

    meetingTable = session.query(Meetings).get(meetingTable.id)

    def updateAttendees(base, update):
        # TODO: Iterate over list and update inf -> think if every event could be done by one funct
        if(update["id"] == "user-audio-voice-enabled"):
            attr = "hasJoinedVoice"
            value = True
        elif(update["id"] == "user-audio-voice-disabled"):
            attr = "hasJoinedVoice"
            value = True
        elif(update["id"] == "user-audio-listen-only-enabled"):
            attr = "isListeningOnly"
            value = True
        elif(update["id"] == "user-audio-listen-only-disabled"):
            attr = "isListeningOnly"
            value = False
        elif(update["id"] == "user-cam-broadcast-start"):
            attr = "hasVideo"
            value = True
        elif(update["id"] == "user-cam-broadcast-end"):
            attr = "hasVideo"
            value = False
        for attendee in base:
            if(attendee["intUserId"] == userId):
                base[attr] = value
        return base

    meetingTable.attendees= updateAttendees(meetingTable.attendees, map)
    meetingTable.participantCount= len(meetingTable.attendees)
    meetingTable.moderatorCount= sum(1 for a in meetingTable.attendees if a["role"]=="MODERATOR")
    meetingTable.listenerCount= sum(1 for a in meetingTable.attendees if a["isListeningOnly"])
    meetingTable.voiceParticipantCount= sum(1 for a in meetingTable.attendees if a["hasJoinedVoice"])
    meetingTable.videoCount= sum(1 for a in meetingTable.attendees if a["hasVideo"])
    flag_modified(meetingTable,"attendees")

    session.commit()

def dbEventSelector(post, map):
    id = post["data"]["id"]
    if(id == "meeting-created"):
        createMeeting(map)
    elif(id == "user-joined"):
        userJoin(post,map)
    elif(id == "user-left"):
        userLeft(post,map)
    elif(id == "meeting-ended"):
        meetingEnded(map)
    elif(id in ["user-audio-listen-only-enabled","user-audio-listen-only-disabled","user-audio-voice-enabled",
      "user-audio-voice-disabled","user-cam-broadcast-start","user-cam-broadcast-end"]):
      userInfoUpdate(map)
