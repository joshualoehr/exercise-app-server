from flask import request

from server import app, bcrypt, db
from server.models.blacklist_token import BlacklistToken
from server.models.user import User
from server.utils import authenticated, json_response, with_auth_token


@app.route('/users/me', methods=['GET'])
@authenticated
def get_user(user):
    return json_response(
        200,
        last_updated=user.last_updated,
        user={
            'id': user.id,
            'email': user.email
        }
    )


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()

        if not user:
            return json_response(
                400,
                message='Invalid login',
                debug_message='No user found with email %s' % email
            )

        if bcrypt.check_password_hash(user.password, password):
            auth_token = user.encode_auth_token(user.id)

            if auth_token:
                return json_response(
                    200,
                    message='Successfully logged in',
                    auth_token=auth_token.decode('utf-8')
                )
        else:
            return json_response(
                400,
                message='Invalid login',
                debug_message='Invalid password'
            )
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=e
        )


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        try:
            user = User(email=email, password=data.get('password'))

            db.session.add(user)
            db.session.commit()

            auth_token = user.encode_auth_token(user.id)

            return json_response(
                201,
                message='Successfully registered',
                auth_token=auth_token.decode('utf-8')
            )
        except Exception as e:
            return json_response(
                500,
                message='An error occurred, please try again',
                debug_message=e
            )
    else:
        return json_response(
            202,
            message='User %s already exists' % email
        )


@app.route('/logout', methods=['POST'])
@with_auth_token
def logout(auth_token):
    blacklist_token = BlacklistToken(token=auth_token['raw_token'])
    try:
        db.session.add(blacklist_token)
        db.session.commit()
        return json_response(
            200,
            message='Successfully logged out'
        )
    except Exception as e:
        return json_response(
            500,
            message='An error occurred, please try again',
            debug_message=e
        )
