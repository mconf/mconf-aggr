from sqlalchemy import *
from base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import backref
import json


class Meetings(Base):
     __tablename__ = 'Meetings'

     id = Column(Integer, primary_key=True)
     meetingEvent_id = Column(Integer, ForeignKey('MeetingsEvents.id'))
     meetingEvent = relationship("MeetingsEvents", backref=backref("Meetings", uselist=False))

     createdAt = Column(Date)
     updatedAt = Column(Date)

     running = Column(Boolean)
     hasUserJoined = Column(Boolean)
     participantCount = Column(Integer)
     listenerCount = Column(Integer)
     voiceParticipantCount = Column(Integer)
     videoCount = Column(Integer)
     moderatorCount = Column(Integer)
     attendees = Column(JSON)

     def __repr__(self):
         return ("<Meetings(" +
                "id=" + str(self.id) +
                ", createdAt=" + str(self.createdAt) +
                ", updatedAt=" + str(self.updatedAt) +
                ", running=" + str(self.running) +
                ", hasUserJoined=" + str(self.hasUserJoined) +
                ", participantCount=" + str(self.participantCount) +
                ", listenerCount=" + str(self.listenerCount) +
                ", voiceParticipantCount=" + str(self.voiceParticipantCount) +
                ", videoCount=" + str(self.videoCount) +
                ", moderatorCount=" + str(self.moderatorCount) +
                ", attendees=" + str(self. attendees) +
                ")>")
