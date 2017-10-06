from sqlalchemy import *
from base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, event
from sqlalchemy import distinct
from sqlalchemy import func

class UsersEvents(Base):
    __tablename__ = 'UsersEvents'

    id = Column(Integer, primary_key=True)
    meetingEvent_Id = Column(Integer, ForeignKey('MeetingsEvents.id'))

    meetingEvent = relationship("MeetingsEvents")

    createdAt = Column(Date)
    updatedAt = Column(Date)
    name = Column(String)
    role = Column(String)
    joinTime = Column(BigInteger)
    leaveTime = Column(BigInteger)
    internalUserId = Column(String)
    externalUserId = Column(String)

    meta_data = Column(JSON)


    def __repr__(self):
        return ("<UsersEvents(" +
                "id=" + str(self.id) +
                ", createdAt=" + str(self.createdAt) +
                ", updatedAt=" + str(self.updatedAt) +
                ", name=" + str(self.name) +
                ", role=" + str(self.role) +
                ", joinTime=" + str(self.joinTime) +
                ", leaveTime=" + str(self.leaveTime) +
                ", internalUserId=" + str(self.internalUserId) +
                ", externalUserId=" + str(self.externalUserId) +
                ")>")
