import datetime

from server import app, db


class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(1024), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: %s>' % self.token

    @staticmethod
    def check_blacklist(auth_token):
        blacklist_token = BlacklistToken.query.filter_by(
            token=str(auth_token)).first()
        return bool(blacklist_token)
