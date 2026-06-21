"""
The browser_session_model code is in the worker.py is not imported through
the dependency chain. When SQLAlchemy tries to find BrowserSessionORM
by string, it does not see it in the registry because
the module has not yet been "read" by Python.
Imports in __init__.py The models are forcibly "read" when the application
is launched. This ensures that by the time the database is first accessed,
all classes have already been registered and SQLAlchemy can find them.
"""

from app.infrastructure.database.models.browser_session_model import BrowserSessionORM
from app.infrastructure.database.models.job_model import JobORM

__all__ = ["BrowserSessionORM", "JobORM"]
