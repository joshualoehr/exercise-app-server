import datetime
import jwt

from server import app, db
from server.models.workout import Workout
from server.models.exerciseInstance import ExerciseInstance
from server.utils import convert_timestamp


class WorkoutInstance(db.Model):
    __tablename__ = 'workoutInstances'
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['user_id', 'workoutId'],
            ['workouts.user_id', 'workouts.id'],
            name='fk_workouts_workoutInstances'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    workoutId = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    recordedWeight = db.Column(db.Integer, nullable=False)
    lastUpdated = db.Column(db.DateTime, nullable=False)
    exerciseInstances = db.relation('ExerciseInstance')

    def __init__(self, user_id, **workoutInstance):
        self.id = workoutInstance['id']
        self.user_id = user_id
        self.workoutId = workoutInstance['workoutId']
        self.update(workoutInstance)

    def update(self, workoutInstance):
        print(workoutInstance)
        self.workoutId = workoutInstance['workoutId']
        self.date = convert_timestamp(workoutInstance['date'])
        self.recordedWeight = workoutInstance['recordedWeight']
        self.lastUpdated = workoutInstance['lastUpdated']
        return self

    def toJSON(self):
        return {
            'id': self.id,
            'workoutId': self.workoutId,
            'date': self.date,
            'recordedWeight': self.recordedWeight,
            'lastUpdated': self.lastUpdated
        }
