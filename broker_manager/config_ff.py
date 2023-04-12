class configuration:
    """base virual class"""

class production_config(configuration):
    FLASK_ENV = "production"
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:eshamanideep25@localhost:5432/broker_manager"
    )
    DEBUG = False
    TESTING = False


class development_config(configuration):
    FLASK_ENV = "development"
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:eshamanideep25@localhost:5432/broker_manager"
    )
    DEBUG = True
    TESTING = True