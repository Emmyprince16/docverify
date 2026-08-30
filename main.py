from app.database import Base, engine
from app.models import models

Base.metadata.create_all(bind=engine)
print("Tables created:", list(Base.metadata.tables.keys()))