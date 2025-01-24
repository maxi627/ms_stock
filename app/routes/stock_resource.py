from flask import Blueprint, request
from marshmallow import ValidationError

from app.mapping import StockSchema, ResponseSchema
from app.services import StockService, ResponseBuilder

Stock = Blueprint('Stock', __name__)
service = StockService()
Stock_schema = StockSchema()
response_schema = ResponseSchema()

@Stock.route('/stock', methods=['GET'])
def all():
    response_builder = ResponseBuilder()
    try:
        data = Stock_schema.dump(service.all(), many=True)
        response_builder.add_message("Stock found").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except Exception as e:
        response_builder.add_message("Error fetching Stock").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Stock.route('/stock/<int:id>', methods=['GET'])
def one(id):
    response_builder = ResponseBuilder()
    try:
        data = service.find(id)
        if data:
            serialized_data = Stock_schema.dump(data)
            response_builder.add_message("Stock found").add_status_code(200).add_data(serialized_data)
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Stock not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error fetching Stock").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Stock.route('/stock', methods=['POST'])
def add():
    response_builder = ResponseBuilder()
    try:
        stock = Stock_schema.load(request.json)
        data = Stock_schema.dump(service.add(stock))
        response_builder.add_message("Stock created").add_status_code(201).add_data(data)
        return response_schema.dump(response_builder.build()), 201
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error creating Stock").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Stock.route('/stock/<int:id>', methods=['PUT'])
def update(id):
    response_builder = ResponseBuilder()
    try:
        stock = Stock_schema.load(request.json)
        data = Stock_schema.dump(service.update(id, stock))
        response_builder.add_message("Stock updated").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error updating Stock").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Stock.route('/stock/<int:id>', methods=['DELETE'])
def delete(id):
    response_builder = ResponseBuilder()
    try:
        if service.delete(id):
            response_builder.add_message("Stock deleted").add_status_code(200).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Stock not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error deleting Stock").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500
        
