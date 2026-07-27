from .database import Base, engine

from . import models
from . import incident_model
from . import integrity_models
from . import job_model
from . import job_report_model
from . import reliability_model
from . import alert_model
from . import incident_event_model
print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully")