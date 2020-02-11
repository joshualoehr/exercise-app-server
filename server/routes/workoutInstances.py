import datetime

from server import app, db
from flask import abort, request

from server.models.workout import Workout
from server.models.workoutInstance import WorkoutInstance
from server.utils import authenticated, json_response


@app.route('/workouts/<int:workoutId>/workoutInstances')
@authenticated
def get_workoutInstances(user, workoutId):
    try:
        workoutInstances = WorkoutInstance.query.filter_by(
            user_id=user.id,
            workoutId=workoutId
        ).all()
        return json_response(200, workoutInstances=[workoutInstance.toJSON() for workoutInstance in workoutInstances])
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


@app.route('/workouts/<int:workoutId>/workoutInstances/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@authenticated
def workoutInstance(user, workoutId, id):
    try:
        if request.method == 'GET':
            return get_workoutInstance(user.id, workoutId, id)
        elif request.method == 'POST':
            return post_workoutInstance(user.id, workoutId, id)
        elif request.method == 'PUT':
            return put_workoutInstance(user.id, workoutId, id)
        elif request.method == 'DELETE':
            return delete_workoutInstance(user.id, workoutId, id)
        else:
            abort(405)
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


def with_workoutInstance(func):
    def with_workoutInstance_wrapper(user_id, workoutId, id):
        data = request.get_json()
        try:
            workoutInstance = data['workoutInstance']
        except KeyError:
            return json_response(400, message='No workoutInstance provided')

        workoutInstance['id'] = id

        workout = Workout.query.filter_by(
            user_id=user_id,
            id=workoutId
        ).first()
        if not workout:
            return json_response(404, message='Workout %d not found' % workoutId)

        workoutInstance['workoutId'] = workoutId

        date = workoutInstance['date']
        if isinstance(date, int):
            date = datetime.datetime.fromtimestamp(
                workoutInstance['date'])
        workoutInstance['date'] = date

        lastUpdated = workoutInstance['lastUpdated']
        if isinstance(lastUpdated, int):
            lastUpdated = datetime.datetime.fromtimestamp(
                workoutInstance['lastUpdated'])
        workoutInstance['lastUpdated'] = lastUpdated

        return func(workoutInstance, user_id, workoutId, id)

    with_workoutInstance_wrapper.__name__ = 'with_workoutInstance_wrapper_%s' % func.__name__
    return with_workoutInstance_wrapper


def get_workoutInstance(user_id, workoutId, id):
    workoutInstance = WorkoutInstance.query.filter_by(
        user_id=user_id,
        workoutId=workoutId,
        id=id
    ).first()

    if workoutInstance:
        return json_response(200, workoutInstance=workoutInstance.toJSON())
    else:
        return json_response(404, message='WorkoutInstance %d not found' % id)


@with_workoutInstance
def post_workoutInstance(workoutInstance, user_id, workoutId, id):
    existing = WorkoutInstance.query.filter_by(
        user_id=user_id,
        workoutId=workoutId,
        id=id
    ).first()

    if existing:
        return json_response(400, message='WorkoutInstance %d already exists' % id)

    workoutInstance = WorkoutInstance(user_id, **workoutInstance)
    db.session.add(workoutInstance)
    db.session.commit()

    return json_response(201, workoutInstance=workoutInstance.toJSON())


@with_workoutInstance
def put_workoutInstance(workoutInstance, user_id, workoutId, id):
    existing = WorkoutInstance.query.filter_by(
        user_id=user_id,
        workoutId=workoutId,
        id=id
    ).first()

    if existing:
        workoutInstance = existing.update(workoutInstance)
        status = 200
    else:
        workoutInstance = WorkoutInstance(user_id, **workoutInstance)
        status = 201

    db.session.add(workoutInstance)
    db.session.commit()

    return json_response(status, workoutInstance=workoutInstance.toJSON())


def delete_workoutInstance(user_id, workoutId, id):
    workoutInstance = WorkoutInstance.query.filter_by(
        user_id=user_id,
        workoutId=workoutId,
        id=id
    ).first()

    if workoutInstance:
        db.session.delete(workoutInstance)
        db.session.commit()
        return json_response(200)
    else:
        return json_response(404, message='WorkoutInstance %d not found' % id)
