from .models import init_db, SessionLocal

#init database
def init_database():
    init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
