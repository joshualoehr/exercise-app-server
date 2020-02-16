import datetime
from flask import make_response, jsonify, request

from server import app, db
from server.models.user import User


def with_auth_token(route):
    def with_auth_token_wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return json_response(
                400,
                message='No authorization header provided'
            )

        try:
            auth_token = auth_header.split(' ')[1]
        except Exception:
            return json_response(
                400,
                message='Malformed authorization header'
            )

        if not auth_token:
            return json_response(
                403,
                message='No auth token provided'
            )

        decoded_auth_token = User.decode_auth_token(auth_token)
        if isinstance(decoded_auth_token, str):
            return json_response(
                401,
                message=decoded_auth_token
            )

        decoded_auth_token['raw_token'] = auth_token

        return route(decoded_auth_token, *args, **kwargs)

    with_auth_token_wrapper.__name__ = 'with_auth_token_wrapper_%s' % route.__name__
    return with_auth_token_wrapper


def authenticated(route):
    @with_auth_token
    def authenticated_wrapper(auth_token, *args, **kwargs):
        user = User.query.filter_by(id=auth_token['sub']).first()
        if not user:
            return json_response(
                401,
                message='User with id %d not found' % auth_token['sub']
            )

        data = request.get_json() or {}
        lastSync = data.get('lastSync')
        if (lastSync):
            user.last_updated = convert_timestamp(lastSync)
            db.session.add(user)
            db.session.commit()
        else:
            lastSync = user.last_updated

        return route(user, *args, **kwargs)

    authenticated_wrapper.__name__ = 'authenticated_wrapper_%s' % route.__name__
    return authenticated_wrapper


def authenticated_json_response(status_code, debug_message=None, **kwargs):
    def with_last_udpated(last_updated):
        return json_response(status_code, debug_message=debug_message, last_updated=last_updated, **kwargs)


def json_response(status_code, debug_message=None, **kwargs):
    success = 200 <= status_code < 400
    response_object = {
        'success': success,
        **kwargs
    }
    if app.config.get('DEBUG') and debug_message is not None:
        response_object['debug_message'] = debug_message
    return make_response(jsonify(response_object)), status_code


def convert_timestamp(timestamp):
    if isinstance(timestamp, int):
        timestamp = datetime.datetime.fromtimestamp(
            timestamp)
    return timestamp
