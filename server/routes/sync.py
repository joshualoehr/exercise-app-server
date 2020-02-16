from server import app, db
from flask import abort, request

from server.models.exercise import Exercise
from server.models.exerciseInstance import ExerciseInstance
from server.models.workout import Workout
from server.models.workoutInstance import WorkoutInstance
from server.models.user import User
from server.utils import authenticated, convert_timestamp, json_response


@app.route('/sync', methods=['GET', 'POST'])
@authenticated
def sync(user):
    if request.method == 'GET':
        return get_sync(user)
    else:
        try:
            data = request.get_json()['sync']
            exercises = data['exercises']
            exerciseInstances = data['exerciseInstances']
            workouts = data['workouts']
            workoutInstances = data['workoutInstances']
        except KeyError:
            return json_response(400, message='Invalid sync payload')

        return post_sync(user, exercises, exerciseInstances, workouts, workoutInstances)


def get_sync(user):
    try:
        exercises = Exercise.query.filter_by(user_id=user.id).all()
        exerciseInstances = ExerciseInstance.query.filter_by(
            user_id=user.id).all()
        workouts = Workout.query.filter_by(user_id=user.id).all()
        workoutInstances = WorkoutInstance.query.filter_by(
            user_id=user.id).all()

        exercises = [exercise.toJSON() for exercise in exercises]
        exerciseInstances = [exerciseInstance.toJSON()
                             for exerciseInstance in exerciseInstances]
        workouts = [workout.toJSON() for workout in workouts]
        workoutInstances = [workoutInstance.toJSON()
                            for workoutInstance in workoutInstances]

        return json_response(200, last_updated=user.last_updated, sync={
            'lastUpdated': user.last_updated,
            'exercises': exercises,
            'exerciseInstances': exerciseInstances,
            'workouts': workouts,
            'workoutInstances': workoutInstances
        })
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


def post_sync(user, exercises, exerciseInstances, workouts, workoutInstances):
    try:
        db.session.query(ExerciseInstance).filter_by(
            user_id=user.id).delete(synchronize_session=False)
        db.session.query(Exercise).filter_by(
            user_id=user.id).delete(synchronize_session=False)
        db.session.query(WorkoutInstance).filter_by(
            user_id=user.id).delete(synchronize_session=False)
        db.session.query(Workout).filter_by(
            user_id=user.id).delete(synchronize_session=False)

        exercises = preprocess(exercises)
        exerciseInstances = preprocess(exerciseInstances)
        workouts = preprocess(workouts)
        workoutInstances = preprocess(workoutInstances)

        exercises = [Exercise(user.id, **exercise)
                     for exercise in exercises]
        exerciseInstances = [ExerciseInstance(user.id,
                                              **exerciseInstance) for exerciseInstance in exerciseInstances]
        workouts = [Workout(user.id, **workout) for workout in workouts]
        workoutInstances = [WorkoutInstance(user.id,
                                            **workoutInstance) for workoutInstance in workoutInstances]

        db.session.bulk_save_objects(workouts + exercises +
                                     workoutInstances + exerciseInstances)

        db.session.commit()

        exercises = [exercise.toJSON() for exercise in exercises]
        exerciseInstances = [exerciseInstance.toJSON()
                             for exerciseInstance in exerciseInstances]
        workouts = [workout.toJSON() for workout in workouts]
        workoutInstances = [workoutInstance.toJSON()
                            for workoutInstance in workoutInstances]

        return json_response(200, last_updated=user.last_updated, sync={
            'exercises': exercises,
            'exerciseInstances': exerciseInstances,
            'workouts': workouts,
            'workoutInstances': workoutInstances
        })
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


def preprocess(resources):
    processed = []

    for resource in resources:
        resource['lastUpdated'] = convert_timestamp(
            resource['lastUpdated'])

        processed.append(resource)

    return processed
