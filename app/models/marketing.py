from sqlalchemy import Column, String, Integer, DateTime, JSON
import uuid
from datetime import datetime
from app.core.database import Base

class ProductFeature(Base):
    __tablename__ = "product_features"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon_name = Column(String, default="Zap")
    benefit_highlight = Column(String, nullable=True) # e.g. "40% faster execution"
    display_order = Column(Integer, default=0)
    category = Column(String, default="Platform") # Platform, AI, Admin, Analytics
    created_at = Column(DateTime, default=datetime.utcnow)
