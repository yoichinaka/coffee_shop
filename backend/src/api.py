import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, JWTError

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true'
                        )
    response.headers.add('Access-Control-Allow-Methods', 
                         'GET,POST,DELETE,PACTH,OPTIONS'
                        )
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
     where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def retrieve_drinks():
    drinks = []
    drink_query = Drink.query.order_by(Drink.id).all()
    for drink in drink_query:
        drinks.append(drink.short())
    if len(drinks) == 0:
        abort(404)
    return jsonify({'success': True,
                    'drinks': drinks,
                    }), 200


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
     where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drink_detail(payload):
    drink_query = Drink.query.all()
    drinks = []
    drink_query = Drink.query.order_by(Drink.id).all()
    for drink in drink_query:
        drinks.append(drink.long())
    if len(drinks) == 0:
        abort(404)
    return jsonify({'success': True,
                    'drinks': drinks,
                    }), 200


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    # the required datatype is [{'color': string, 'name':string,
    # 'parts':number}]
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    # new_recipe = [body.get('recipe', None)] 
    # this was used for postman test 
    try:
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()
        return jsonify({'success': True,
                        'drinks': [new_drink.long()],
                        }), 200
    except BaseException:
        abort(422)


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    body = request.get_json()
    update_recipe = body.get('recipe', None)
    try:
        drink.recipe = json.dumps(update_recipe)
        drink.update()
        return jsonify({'success': True,
                        'drinks': [drink.long()],
                        }), 200
    except BaseException:
        abort(422)


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
     where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({'success': True,
                        'delete': drink_id,
                        }), 200
    except BaseException:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


'''
@DONE implement error handler for 404
    error handler should conform to general task above.
'''


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above.
'''


@app.errorhandler(AuthError)
def auth_error(AuthError):
    return jsonify({
        "success": False,
        "error code": AuthError.status_code,
        "discription": AuthError.error
    }), AuthError.status_code


@app.errorhandler(JWTError)
def jwt_error(e):
    return jsonify({
        "success": False,
        "error code": 401,
        "discription": str(e),
    }), 401
