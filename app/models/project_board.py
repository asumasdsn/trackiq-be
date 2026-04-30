from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Board(Base):
    __tablename__ = "boards"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True) # Link to project
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", backref="board")
    columns = relationship("BoardColumn", back_populates="board", cascade="all, delete-orphan")
    epics = relationship("BoardEpic", back_populates="board", cascade="all, delete-orphan")

class BoardColumn(Base):
    __tablename__ = "board_columns"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, default=0)
    
    board = relationship("Board", back_populates="columns")
    tasks = relationship("BoardTask", back_populates="column", cascade="all, delete-orphan")

class BoardEpic(Base):
    __tablename__ = "board_epics"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    name = Column(String, nullable=False)
    color = Column(String, default="bg-slate-100")
    
    board = relationship("Board", back_populates="epics")
    tasks = relationship("BoardTask", back_populates="epic")

class BoardTask(Base):
    __tablename__ = "board_tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    column_id = Column(String, ForeignKey("board_columns.id"), nullable=False)
    epic_id = Column(String, ForeignKey("board_epics.id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assignee_name = Column(String, nullable=True)
    assignee_avatar = Column(String, nullable=True)
    reporter_name = Column(String, nullable=True)
    reporter_avatar = Column(String, nullable=True)
    priority = Column(String, default="Medium")
    identifier = Column(String, nullable=False) # e.g. FRONT-401
    labels = Column(JSON, default=list) # List of strings
    due_date = Column(DateTime, nullable=True)
    github_data = Column(JSON, default=dict) # Linked VCS metadata: {branch, pr_url, repo, status}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    column = relationship("BoardColumn", back_populates="tasks")
    epic = relationship("BoardEpic", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan", order_by="desc(TaskComment.created_at)")

class TaskComment(Base):
    __tablename__ = "task_comments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    task_id = Column(String, ForeignKey("board_tasks.id"), nullable=False)
    author_name = Column(String, nullable=False)
    author_avatar = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    task = relationship("BoardTask", back_populates="comments")
