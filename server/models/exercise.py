import jwt

from server import app, db


class Exercise(db.Model):
    __tablename__ = 'exercises'
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['user_id', 'workoutId'],
            ['workouts.user_id', 'workouts.id'],
            name='fk_workouts_exercises'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    workoutId = db.Column(db.Integer, nullable=False)
    exerciseName = db.Column(db.String(255), nullable=False)
    numSets = db.Column(db.Integer, nullable=False)
    numReps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    lastUpdated = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, workoutId, **exercise):
        self.id = exercise['id']
        self.user_id = user_id
        self.workoutId = workoutId
        self.update(exercise)

    def update(self, exercise):
        self.exerciseName = exercise['exerciseName']
        self.numSets = exercise['numSets']
        self.numReps = exercise['numReps']
        self.weight = exercise['weight']
        self.lastUpdated = exercise['lastUpdated']
        return self

    def toJSON(self):
        return {
            'id': self.id,
            'workoutId': self.workoutId,
            'exerciseName': self.exerciseName,
            'numSets': self.numSets,
            'numReps': self.numReps,
            'weight': self.weight,
            'lastUpdated': self.lastUpdated
        }
