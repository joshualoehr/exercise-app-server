import datetime
import jwt

from server import app, db


class ExerciseInstance(db.Model):
    __tablename__ = 'exerciseInstances'
    __table_args__ = tuple(
        db.ForeignKeyConstraint(['user_id', 'workoutId'], [
            'workoutInstances.user_id', 'workoutInstances.id'], name='fk_workoutInstances_exerciseInstances')
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    workoutInstanceId = db.Column(db.Integer, nullable=False)
    exerciseName = db.Column(db.String(255), nullable=False)
    maxReps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.JSON, nullable=False)
    lastUpdated = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, **exerciseInstance):
        lastUpdated = exerciseInstance['lastUpdated']
        if isinstance(lastUpdated, int):
            lastUpdated = datetime.datetime.fromtimestamp(lastUpdated)
            exerciseInstance['lastUpdated'] = lastUpdated

        self.id = exerciseInstance['id']
        self.user_id = user_id
        self.update(exerciseInstance)

    def update(self, exerciseInstance):
        self.workoutInstanceId = exerciseInstance['workoutInstanceId']
        self.exerciseName = exerciseInstance['exerciseName']
        self.maxReps = exerciseInstance['maxReps']
        self.weight = exerciseInstance['weight']
        self.sets = exerciseInstance['sets']
        self.lastUpdated = exerciseInstance['lastUpdated']
        return self

    def toJSON(self):
        return {
            'id': self.id,
            'workoutInstanceId': self.workoutInstanceId,
            'exerciseName': self.exerciseName,
            'maxReps': self.maxReps,
            'weight': self.weight,
            'sets': self.sets,
            'lastUpdated': self.lastUpdated
        }
