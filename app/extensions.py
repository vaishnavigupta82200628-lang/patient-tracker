from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# These are created here (not in __init__.py) to avoid circular imports.
# Other files (models.py, routes.py) can import 'db' and 'login_manager' 
# from this file without creating a loop of imports.

db = SQLAlchemy()
login_manager = LoginManager()