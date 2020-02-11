import datetime

from server import app, db
from flask import abort, request

from server.models.workout import Workout
from server.models.workoutInstance import WorkoutInstance
from server.models.exerciseInstance import ExerciseInstance
from server.utils import authenticated, json_response


@app.route('/workouts/<int:workoutId>/workoutInstances/<int:workoutInstanceId>/exerciseInstances')
@authenticated
def get_exerciseInstances(user, workoutId, workoutInstanceId):
    try:
        exerciseInstances = ExerciseInstance.query.filter_by(
            user_id=user.id,
            workoutInstanceId=workoutInstanceId
        ).all()
        return json_response(200, exerciseInstances=[exerciseInstance.toJSON() for exerciseInstance in exerciseInstances])
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


@app.route('/workouts/<int:workoutId>/workoutInstances/<int:workoutInstanceId>/exerciseInstances/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@authenticated
def exerciseInstance(user, workoutId, workoutInstanceId, id):
    try:
        if request.method == 'GET':
            return get_exerciseInstance(user.id, workoutInstanceId, id)
        elif request.method == 'POST':
            return post_exerciseInstance(user.id, workoutInstanceId, id)
        elif request.method == 'PUT':
            return put_exerciseInstance(user.id, workoutInstanceId, id)
        elif request.method == 'DELETE':
            return delete_exerciseInstance(user.id, workoutInstanceId, id)
        else:
            abort(405)
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


def with_exerciseInstance(func):
    def with_exerciseInstance_wrapper(user_id, workoutInstanceId, id):
        data = request.get_json()
        try:
            exerciseInstance = data['exerciseInstance']
        except KeyError:
            return json_response(400, message='No exerciseInstance provided')

        exerciseInstance['id'] = id

        workoutInstance = WorkoutInstance.query.filter_by(
            user_id=user_id,
            id=workoutInstanceId
        ).first()
        if not workoutInstance:
            return json_response(404, message='workoutInstance %d not found' % workoutInstanceId)

        exerciseInstance['workoutInstanceId'] = workoutInstanceId

        lastUpdated = exerciseInstance['lastUpdated']
        if isinstance(lastUpdated, int):
            lastUpdated = datetime.datetime.fromtimestamp(
                exerciseInstance['lastUpdated'])
        exerciseInstance['lastUpdated'] = lastUpdated

        return func(exerciseInstance, user_id, workoutInstanceId, id)

    with_exerciseInstance_wrapper.__name__ = 'with_exerciseInstance_wrapper_%s' % func.__name__
    return with_exerciseInstance_wrapper


def get_exerciseInstance(user_id, workoutInstanceId, id):
    exerciseInstance = ExerciseInstance.query.filter_by(
        user_id=user_id,
        workoutInstanceId=workoutInstanceId,
        id=id
    ).first()

    if exerciseInstance:
        return json_response(200, exerciseInstance=exerciseInstance.toJSON())
    else:
        return json_response(404, message='ExerciseInstance %d not found' % id)


@with_exerciseInstance
def post_exerciseInstance(exerciseInstance, user_id, workoutInstanceId, id):
    existing = ExerciseInstance.query.filter_by(
        user_id=user_id,
        workoutInstanceId=workoutInstanceId,
        id=id
    ).first()

    if existing:
        return json_response(400, message='ExerciseInstance %d already exists' % id)

    exerciseInstance = ExerciseInstance(user_id, **exerciseInstance)
    db.session.add(exerciseInstance)
    db.session.commit()

    return json_response(201, exerciseInstance=exerciseInstance.toJSON())


@with_exerciseInstance
def put_exerciseInstance(exerciseInstance, user_id, workoutInstanceId, id):
    existing = ExerciseInstance.query.filter_by(
        user_id=user_id,
        workoutInstanceId=workoutInstanceId,
        id=id
    ).first()

    if existing:
        exerciseInstance = existing.update(exerciseInstance)
        status = 200
    else:
        exerciseInstance = ExerciseInstance(user_id, **exerciseInstance)
        status = 201

    db.session.add(exerciseInstance)
    db.session.commit()

    return json_response(status, exerciseInstance=exerciseInstance.toJSON())


def delete_exerciseInstance(user_id, workoutInstanceId, id):
    exerciseInstance = ExerciseInstance.query.filter_by(
        user_id=user_id,
        workoutInstanceId=workoutInstanceId,
        id=id
    ).first()

    if exerciseInstance:
        db.session.delete(exerciseInstance)
        db.session.commit()
        return json_response(200)
    else:
        return json_response(404, message='ExerciseInstance %d not found' % id)
