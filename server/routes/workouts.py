from server import app, db
from flask import abort, request

from server.models.workout import Workout
from server.utils import authenticated, convert_timestamp, json_response


@app.route('/workouts')
@authenticated
def get_workouts(user):
    try:
        workouts = Workout.query.filter_by(user_id=user.id).all()
        return json_response(200, last_updated=user.last_updated, workouts=[workout.toJSON() for workout in workouts])
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


@app.route('/workouts/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@authenticated
def workout(user, id):
    try:
        if request.method == 'GET':
            return get_workout(user, id)
        elif request.method == 'POST':
            return post_workout(user, id)
        elif request.method == 'PUT':
            return put_workout(user, id)
        elif request.method == 'DELETE':
            return delete_workout(user, id)
        else:
            abort(405)
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


def with_workout(func):
    def with_workout_wrapper(user, id):
        data = request.get_json()
        try:
            workout = data['workout']
        except KeyError:
            return json_response(400, message='No workout provided')

        workout['id'] = id
        workout['lastUpdated'] = convert_timestamp(
            workout['lastUpdated'])

        return func(workout, user.id, id)

    with_workout_wrapper.__name__ = 'with_workout_wrapper_%s' % func.__name__
    return with_workout_wrapper


def get_workout(user, id):
    workout = Workout.query.filter_by(user_id=user.id, id=id).first()

    if workout:
        return json_response(200, last_updated=user.last_updated, workout=workout.toJSON())
    else:
        return json_response(404, message='Workout %d not found' % id)


@with_workout
def post_workout(workout, user, id):
    existing = Workout.query.filter_by(user_id=user.id, id=id).first()

    if existing:
        return json_response(400, message='Workout %d already exists' % id)

    workout = Workout(user.id, **workout)
    db.session.add(workout)
    db.session.commit()

    return json_response(201, last_updated=user.last_updated, workout=workout.toJSON())


@with_workout
def put_workout(workout, user, id):
    existing = Workout.query.filter_by(user_id=user.id, id=id).first()

    if existing:
        workout = existing.update(workout)
        status = 200
    else:
        workout = Workout(user.id, **workout)
        status = 201

    db.session.add(workout)
    db.session.commit()

    return json_response(status, last_updated=user.last_updated, workout=workout.toJSON())


def delete_workout(user, id):
    workout = Workout.query.filter_by(user_id=user.id, id=id).first()

    if workout:
        db.session.delete(workout)
        db.session.commit()
        return json_response(200, last_updated=user.last_updated)
    else:
        return json_response(404, message='Workout %d not found' % id)
