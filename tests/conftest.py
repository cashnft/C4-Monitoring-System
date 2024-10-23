# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import Base, engine as prod_engine
from main import app

@pytest.fixture(scope="session")
def app_fixture():
    app.config['TESTING'] = True
    return app

@pytest.fixture(scope="function")
def client(app_fixture):
    with app_fixture.test_client() as client:

        Base.metadata.create_all(prod_engine)
        yield client
 
        Base.metadata.drop_all(prod_engine)
        prod_engine.dispose()  
