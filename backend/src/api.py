import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# -----------------------------------
#               ROUTES
# -----------------------------------

# DONE implement endpoint GET /drinks
# - it should be a public endpoint
# - it should contain only the drink.short() data representation
# - returns:
#   - status code 200
#   - json {"success": True, "drinks": drinks} where drinks is list of drinks
#   - or appropriate status code indicating reason for failure


@app.route("/drinks", methods=["GET"])
def get_drinks():
    drinks = Drink.query.all()

    try:
        drinks_short = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_short
        }), 200

    except Exception as e:
        print(e)
        abort(422)


# DONE implement endpoint GET /drinks-detail
# - it should require the 'get:drinks-detail' permission
# - it should contain the drink.long() data representation
# - returns:
#   - status code 200
#   - json {"success": True, "drinks": drinks} where drinks is list of drinks
#   - or appropriate status code indicating reason for failure


@app.route("/drinks-detail", methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()

    try:
        drinks_long = [drink.long() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": drinks_long
        }), 200

    except Exception as e:
        print(e)
        abort(422)


# DONE implement endpoint POST /drinks
# - it should create a new row in the drinks table
# - it should require the 'post:drinks' permission
# - it should contain the drink.long() data representation
# - returns:
#   - status code 200
#   - json {"success": True, "drinks": drink} where drink is an array with
#     created drink
#   - or appropriate status code indicating reason for failure

# it should require the 'post:drink' permission


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drink')
def create_drink(payload):
    # load request body and data
    body = request.get_json()

    if not ('title' in body and 'recipe' in body):
        abort(422)

    try:
        drink = Drink(
            title=body.get('title'),
            recipe=json.dumps(body.get('recipe')))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        print('ERROR: ', str(e))
        abort(422)


# DONE implement endpoint PATCH /drinks/<id>
# - where <id> is the existing model id
# - it should respond with a 404 error if <id> is not found
# - it should update the corresponding row for <id>
# - it should require the 'patch:drinks' permission
# - it should contain the drink.long() data representation
# - returns:
#   - status code 200
#   - json {"success": True, "drinks": drink} where drink is an array with
#     updated drink
#   - or appropriate status code indicating reason for failure

# it should require the 'patch:drink' permission


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drink')
def patch_drink(payload, drink_id):

    # load request body and data
    body = request.get_json()
    drink = Drink.query.get(drink_id)

    # abort if drink not found
    if not drink:
        return jsonify({
            "success": False,
            "error": 404,
            "message": "No drink was found."
        }), 404

    try:
        if 'title' in body:
            drink.title = body.get('title')

        if 'recipe' in body:
            drink.recepie = json.dumps(body.get('recepie'))

        # update and return success message
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        print('ERROR: ', str(e))
        abort(422)


# DONE implement endpoint DELETE /drinks/<id>
# - where <id> is the existing model id
# - it should respond with a 404 error if <id> is not found
# - it should delete the corresponding row for <id>
# - it should require the 'delete:drinks' permission
# - returns:
#     - status code 200
#     - json {"success": True, "delete": id} where id is the id of the
#       deleted record
#     - or appropriate status code indicating reason for failure

# it should require the 'delete:drink' permission


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drink')
def delete_drink(payload, drink_id):
    try:
        # get drrink by id, use one_or_none to only turn one result
        # or call exception if none selected
        drink = Drink.query.get(drink_id)

        # abort if drink not found
        if not drink:
            return jsonify({
                "success": False,
                "error": 404,
                "message": "No drink was found."
            }), 404

        # delete and return success message
        drink.delete()

        return jsonify({
            'success': True,
            'deleted_drink_id': drink_id
        }), 200
    except Exception as e:
        print('ERROR: ', str(e))
        abort(422)


# -----------------------------------
#           Error Handling
# -----------------------------------


# DONE implement error handler for AuthError
#     - error handler should conform to general task above


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(AuthError)
def authError(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": ["Authorized error", error.error],
        "status_code": error.status_code,
        }), 401


@app.errorhandler(403)
def permissionError(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Permission denied"
        }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable Entity"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500
