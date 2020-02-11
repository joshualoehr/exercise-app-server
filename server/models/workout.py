import datetime
import jwt

from server import app, db


class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        primary_key=True)
    workoutName = db.Column(db.String(255), nullable=False)
    lastUpdated = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, **workout):
        self.id = workout['id']
        self.user_id = user_id
        self.update(workout)

    def update(self, workout):
        self.workoutName = workout['workoutName']
        self.lastUpdated = workout['lastUpdated']
        return self

    def toJSON(self):
        return {
            'id': self.id,
            'workoutName': self.workoutName,
            'lastUpdated': self.lastUpdated
        }
