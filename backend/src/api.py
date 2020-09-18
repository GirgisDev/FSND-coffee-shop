import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/drinks/*": {"origins": "*"}})

@app.after_request
def after_request(response):
  response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
  response.headers.add("Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS")
  return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
  drinks = Drink.query.order_by(Drink.id).all()
  formatted_drinks = [drink.short() for drink in drinks]

  if len(formatted_drinks) == 0:
    abort(404)

  return jsonify({
    "success": True,
    drinks: formatted_drinks
  })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details():
  drinks = Drink.query.order_by(Drink.id).all()
  formatted_drinks = [drink.long() for drink in drinks]

  if len(formatted_drinks) == 0:
    abort(404)

  return jsonify({
    "success": True,
    drinks: formatted_drinks
  })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
  print(request.get_json())
  body = request.get_json()
  title = body.get("title")
  recipe = body.get("recipe")

  try:
    drink = Drink(title = title, recipe = recipe)
    drink.insert()
    
    return jsonify({
      "success": True,
      "drinks": drink.long()
    })

  except:
    abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(drink_id):
  drink = Drink.query.get(drink_id)

  if drink is None:
    abort(404)
  
  try:
    drink.title = request.get_json().get('title')
    drink.recipe = request.get_json().get('recipe')

    drink.update()
    return jsonify({
      "success": True,
      "drinks": drink.long()
    })

  except:
    abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
  try:
    drink = Drink.query.get(drink_id)

    if drink is None:
      abort(404)
    
    drink.delete()
    return jsonify({
      'success': True,
      'delete': drink_id,
    })

  except:
    abort(404)



@app.errorhandler(422)
def unprocessable(error):
  return jsonify({
    "success": False,
    "error": 422,
    "message": "unprocessable"
  }), 422


@app.errorhandler(404)
def not_found(error):
  return jsonify({
    "success": False,
    "error": 404,
    "message": "resource not found"
  }), 404

@app.errorhandler(401)
def unauthorized(error):
  return jsonify({
    "success": False,
    "error": 401,
    "message": "Unauthorized"
  }), 401

@app.errorhandler(422)
def unauthorized(error):
  return jsonify({
    "success": False,
    "error": 422,
    "message": "Unproccessable entity"
  }), 422

@app.errorhandler(AuthError)
def handle_auth_error(ex):
  response = jsonify(ex.error)
  response.status_code = ex.status_code
  return response