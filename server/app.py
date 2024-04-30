#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route('/restaurants', methods=["GET"])
def all_restaurants():
    all_restaurants = Restaurant.query.all()
    r_l = []
    for restaurant in all_restaurants:
        r_l.append(restaurant.to_dict(rules = ("-restaurant_pizzas",)))
    return r_l

@app.route('/restaurants/<int:id>', methods=["GET", "DELETE"])
def one_restaurant(id):
    one_restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if one_restaurant:
        if request.method == "GET":
            return one_restaurant.to_dict(),200
        elif request.method == "DELETE":
            db.session.delete(one_restaurant)
            db.session.commit()
            return {},204
    else:
        return {"error": "Restaurant not found"},404
    

@app.route('/pizzas', methods=["GET"])
def all_pizzas():
    all_pizzas = Pizza.query.all()
    r_l = []
    for pizza in all_pizzas:
        r_l.append(pizza.to_dict(rules = ("-restaurant_pizzas",)))
    return r_l

@app.route('/restaurant_pizzas', methods=["POST"])
def all_restaurant_pizzas():
    try:
        data = request.get_json()
        rp = RestaurantPizza(
            price = data['price'],
            pizza_id = data['pizza_id'],
            restaurant_id = data['restaurant_id']
        )
        db.session.add(rp)
        db.session.commit()
        
        new_pizza = RestaurantPizza.query.filter_by(id=rp.id).first()

        response_data = {
                "id": new_pizza.id,
                "price": new_pizza.price,
                "pizza": {
                    "id": new_pizza.pizza.id,
                    "name": new_pizza.pizza.name,
                    "ingredients": new_pizza.pizza.ingredients
                },
                "pizza_id": new_pizza.pizza_id,
                "restaurant": {
                    "id": new_pizza.restaurant.id,
                    "name": new_pizza.restaurant.name,
                    "address": new_pizza.restaurant.address
                },
                "restaurant_id": new_pizza.restaurant_id
            }


        return make_response(response_data, 201)

    except ValueError:
        return {"errors": ["validation errors"]},400





if __name__ == "__main__":
    app.run(port=5555, debug=True)
