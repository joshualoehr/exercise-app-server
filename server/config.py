import os
basedir = os.path.abspath(os.path.dirname(__file__))
postgres_local_base = 'postgresql://postgres:%s@localhost/%s'
database_name = 'liftjl'
database_passwd = os.getenv('POSTGRES_PASSWORD')
jwt_private_key = os.getenv('JWT_PRIVATE_KEY')
jwt_public_key = os.getenv('JWT_PUBLIC_KEY')


class BaseConfig:
    """Base configuration."""
    JWT_PRIVATE_KEY = jwt_private_key
    JWT_PUBLIC_KEY = jwt_public_key
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = postgres_local_base % (
        database_passwd, database_name)


class ProductionConfig(BaseConfig):
    """Production configuration."""
    JWT_PRIVATE_KEY = jwt_private_key
    JWT_PUBLIC_KEY = jwt_public_key
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql:///example'
