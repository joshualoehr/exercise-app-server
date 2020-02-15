from server import app, db
from flask import abort, request

from server.models.exercise import Exercise
from server.utils import authenticated, convert_timestamp, json_response


@app.route('/workouts/<int:workoutId>/exercises')
@authenticated
def get_exercises(user, workoutId):
    try:
        exercises = Exercise.query.filter_by(
            user_id=user.id,
            workoutId=workoutId
        ).all()
        return json_response(200, exercises=[exercise.toJSON() for exercise in exercises])
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


@app.route('/workouts/<int:workoutId>/exercises/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@authenticated
def exercise(user, workoutId, id):
    try:
        if request.method == 'GET':
            return get_exercise(user.id, workoutId, id)
        elif request.method == 'POST':
            return post_exercise(user.id, workoutId, id)
        elif request.method == 'PUT':
            return put_exercise(user.id, workoutId, id)
        elif request.method == 'DELETE':
            return delete_exercise(user.id, workoutId, id)
        else:
            abort(405)
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=str(e)
        )


def with_exercise(func):
    def with_exercise_wrapper(user_id, workoutId, id):
        data = request.get_json()
        try:
            exercise = data['exercise']
        except KeyError:
            return json_response(400, message='No exercise provided')

        exercise['id'] = id
        exercise['workoutId'] = workoutId
        exercise['lastUpdated'] = convert_timestamp(
            exercise['lastUpdated'])

        return func(exercise, user_id, workoutId, id)

    with_exercise_wrapper.__name__ = 'with_exercise_wrapper_%s' % func.__name__
    return with_exercise_wrapper


def get_exercise(user_id, workoutId, id):
    exercise = Exercise.query.filter_by(
        user_id=user_id,
        workoutId=workoutId,
        id=id
    ).first()

    if exercise:
        return json_response(200, exercise=exercise.toJSON())
    else:
        return json_response(404, message='Exercise %d not found' % id)


@with_exercise
def post_exercise(exercise, user_id, workoutId, id):
    existing = Exercise.query.filter_by(
        user_id=user_id,
        workoutId=workoutId,
        id=id
    ).first()

    if existing:
        return json_response(400, message='Exercise %d already exists' % id)

    exercise = Exercise(user_id, **exercise)
    db.session.add(exercise)
    db.session.commit()

    return json_response(201, exercise=exercise.toJSON())


@with_exercise
def put_exercise(exercise, user_id, workoutId, id):
    existing = Exercise.query.filter_by(
        user_id=user_id,
        workoutId=workoutId,
        id=id
    ).first()

    if existing:
        exercise = existing.update(exercise)
        status = 200
    else:
        exercise = Exercise(user_id, **exercise)
        status = 201

    db.session.add(exercise)
    db.session.commit()

    return json_response(status, exercise=exercise.toJSON())


def delete_exercise(user_id, workoutId, id):
    exercise = Exercise.query.filter_by(
        user_id=user_id,
        workoutId=workoutId,
        id=id
    ).first()

    if exercise:
        db.session.delete(exercise)
        db.session.commit()
        return json_response(200)
    else:
        return json_response(404, message='Exercise %d not found' % id)
