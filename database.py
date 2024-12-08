from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String(50))
    transcription_text = Column(String(500))
    task_description = Column(String(500))
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class Transcript(Base):
    __tablename__ = 'transcripts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String(50))
    transcription_text = Column(String(500))
    order = Column(Integer)
    start_stamp = Column(Integer)
    created_at =Column(DateTime, default=datetime.utcnow)


engine = create_engine("sqlite:///tasks.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


async_engine = create_async_engine("sqlite+aiosqlite:///tasks.db", echo=False)

async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)



def add_tasks_to_db(client_id, tasks):
    for k, task in tasks.items():
        task_obj = Task(client_id=client_id, task_description=task['task_description'], status=task['status'], transcription_text = "")
        session.add(task_obj)
    session.commit()