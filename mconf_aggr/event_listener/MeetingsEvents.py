from sqlalchemy import *
from base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class MeetingsEvents(Base):
    __tablename__ = 'MeetingsEvents'

    id = Column(Integer, primary_key=True)

    sharedSecretGuid = Column(String) #index?
    sharedSecretName = Column(String)
    serverGuid = Column(String)
    serverUrl = Column(String)

    createdAt = Column(Date)
    updatedAt = Column(Date)
    externalMeetingId = Column(String) #index?
    internalMeetingId = Column(String) #index?
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
        return ("<MeetingsEvents(" +
                "id=" + str(self.id) +
                ", sharedSecretGuid=" + str(self. sharedSecretGuid) +
                ", sharedSecretName=" + str(self. sharedSecretName) +
                ", serverGuid=" + str(self. serverGuid) +
                ", serverUrl=" + str(self.serverUrl) +
                ", createdAt=" + str(self.createdAt) +
                ", updatedAt=" + str(self.updatedAt) +
                ", externalMeetingId=" + str(self.externalMeetingId) +
                ", internalMeetingId=" + str(self.internalMeetingId) +
                ", name=" + str(self.name) +
                ", createTime=" + str(self.createTime) +
                ", createDate=" + str(self.createDate) +
                ", voiceBridge=" + str(self.voiceBridge) +
                ", dialNumber=" + str(self.dialNumber) +
                ", attendeePW=" + str(self.attendeePW) +
                ", moderatorPW=" + str(self.moderatorPW) +
                ", duration=" + str(self.duration) +
                ", recording=" + str(self.recording) +
                ", hasBeenForciblyEnded=" + str(self.hasBeenForciblyEnded) +
                ", startTime=" + str(self.startTime) +
                ", endTime=" + str(self.endTime) +
                ", maxUsers=" + str(self.maxUsers) +
                ", isBreakout=" + str(self.isBreakout) +
                ", uniqueUsers=" + str(self.uniqueUsers) +
                ", meta_data=" + str(self.meta_data) +
                ")>")
