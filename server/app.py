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

class Restaurants(Resource):
    def get(self):
        restaurant_list = [r.to_dict() for r in Restaurant.query.all()]
        response = make_response(restaurant_list, 200)
        return response

api.add_resource(Restaurants, '/restaurants')

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        restaurant_dict = restaurant.to_dict(['address', 'id', 'name', 'restaurant_pizzas'])
        response = make_response(restaurant_dict, 200)
        return response

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        response = make_response('', 204)
        return response

api.add_resource(RestaurantByID, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizza_list = [p.to_dict() for p in Pizza.query.all()]
        response = make_response(pizza_list, 200,)
        return response

api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            price = data.get('price')
            pizza_id = data.get('pizza_id')
            restaurant_id = data.get('restaurant_id')

            new_restaurant_pizza= RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            response_dict = new_restaurant_pizza.to_dict()
            response = make_response(response_dict, 201)
            return response
        except (ValueError, TypeError) as e:
            return {"errors": ["validation errors"]}, 400

api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
