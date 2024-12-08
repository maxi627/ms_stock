from flask import Blueprint, jsonify, request

from app.mapping import StockSchema
from app.services import StockService

Stock = Blueprint('Stock', __name__)
service = StockService()
Stock_schema =StockSchema()

"""
Obtiene todos las Stocks
"""
@Stock.route('/Stocks', methods=['GET'])
def all():
    resp = Stock_schema.dump(service.get_all(), many=True) 
    return resp, 200

"""
Obtiene una Stock por id
"""
@Stock.route('/Stocks/<int:id>', methods=['GET'])
def one(id):
    resp = Stock_schema.dump(service.get_by_id(id)) 
    return resp, 200

"""
Crea nueva Stock
"""
@Stock.route('/Stocks', methods=['POST'])
def create():
    Stock = Stock_schema.load(request.json)
    resp = Stock_schema.dump(service.create(Stock))
    return resp, 201

"""
Actualiza una Stock existente
"""
@Stock.route('/Stocks/<int:id>', methods=['PUT'])
def update(id):
    Stock = Stock_schema.load(request.json)
    resp = Stock_schema.dump(service.update(id, Stock))
    return resp, 200

"""
Elimina una Stock existente
"""
@Stock.route('/Stocks/<int:id>', methods=['DELETE'])
def delete(id):
    msg = "Stock eliminado correctamente"
    resp = service.delete(id)
    if not resp:
        msg = "No se pudo eliminar el Stock"
    return jsonify(msg), 204