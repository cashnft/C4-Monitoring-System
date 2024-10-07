from api.controllers import app
from api.database import init_database

# Initialize the database
init_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
