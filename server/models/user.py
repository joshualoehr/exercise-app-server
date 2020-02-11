import datetime
import jwt

from server import app, db, bcrypt
from server.models.blacklist_token import BlacklistToken
from server.models.workout import Workout


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    workouts = db.relationship('Workout')

    def __init__(self, email, password):
        self.email = email
        self.password = User.hash_password(password)
        self.last_updated = datetime.datetime.now()

    @staticmethod
    def hash_password(password):
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=1),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('JWT_PRIVATE_KEY'),
                algorithm='RS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            decoded_auth_token = jwt.decode(
                auth_token, app.config.get('JWT_PUBLIC_KEY'), algorithms='RS256')
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Invalid JWT: blacklisted'
            else:
                return decoded_auth_token
        except jwt.ExpiredSignatureError:
            return 'Invalid JWT: expired'
        except jwt.InvalidTokenError:
            return 'Invalid JWT: invalid'
