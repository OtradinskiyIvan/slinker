from sqlalchemy import Column, String, ForeignKey, Integer
from infrastructure.database import Base

class Link(Base):
    __tablename__ = 'link'

    id = Column(Integer, primary_key=True, index=True)
    real_link = Column(String, index=True)
    short_link = Column(String, unique=True, index=True)

class Usage(Base):
    __tablename__ = 'usage'

    id = Column(Integer, primary_key=True, index=True)
    user_ip = Column(String, index=True)
    user_agent = Column(String, index=True)
    link_id = Column(Integer, ForeignKey('link.id', ondelete='CASCADE'))