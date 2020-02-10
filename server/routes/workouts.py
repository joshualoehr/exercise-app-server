from server import app
from flask import abort, request


@app.route('/workouts')
def get_workouts():
    return 'all workouts'


def get_workout(id):
    return 'workout %d' % id


def post_workout(id):
    return 'posted workout %d' % id


def put_workout(id):
    return 'put workout %d' % id


def delete_workout(id):
    return 'deleted workout %d' % id


@app.route('/workouts/<int:id>')
def workout(id, methods=['GET', 'POST', 'PUT', 'DELETE']):
    if request.method == 'GET':
        return get_workout(id)
    elif request.method == 'POST':
        return post_workout(id)
    elif request.method == 'PUT':
        return put_workout(id)
    elif request.method == 'DELETE':
        return delete_workout(id)
    else:
        abort(405)
