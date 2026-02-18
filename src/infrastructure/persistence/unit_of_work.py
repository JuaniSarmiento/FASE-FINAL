from sqlalchemy.orm import Session
from src.application.shared.unit_of_work import UnitOfWork

class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: Session = None

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
