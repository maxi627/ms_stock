import os
import unittest
from datetime import datetime
from app import create_app, db
from app.models import Stock


class StockTestCase(unittest.TestCase):
    def setUp(self):
        # Datos de prueba
        self.IDPRODUCTO_PRUEBA = 1
        self.FECHA_TRANSACCION_PRUEBA = datetime(2020, 1, 1, 0, 0, 0)
        self.CANTIDAD_PRUEBA = 10.0
        self.ENTRADA_SALIDA_PRUEBA = 1  # 1: entrada, 2: salida

        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_stock(self):
        # Crear una instancia del modelo Stock usando datos de prueba
        stock = self.__get_stock()

        # Verificar que los valores sean correctos
        self.assertEqual(stock.producto_id, self.IDPRODUCTO_PRUEBA)
        self.assertEqual(stock.fecha_transaccion, self.FECHA_TRANSACCION_PRUEBA)
        self.assertEqual(stock.cantidad, self.CANTIDAD_PRUEBA)
        self.assertEqual(stock.entrada_salida, self.ENTRADA_SALIDA_PRUEBA)

    def __get_stock(self):
        # Crear y devolver un objeto Stock basado en el modelo
        stock = Stock()
        stock.producto_id = self.IDPRODUCTO_PRUEBA
        stock.fecha_transaccion = self.FECHA_TRANSACCION_PRUEBA
        stock.cantidad = self.CANTIDAD_PRUEBA
        stock.entrada_salida = self.ENTRADA_SALIDA_PRUEBA

        return stock


if __name__ == '__main__':
    unittest.main()
