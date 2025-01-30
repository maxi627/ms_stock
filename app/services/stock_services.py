from app import cache, redis_client  # Se asume que `redis_client` es una instancia de Redis ya configurada
from app.models import Stock
from app.repositories import StockRepository
from contextlib import contextmanager
import time

class StockService:

    CACHE_TIMEOUT = 60  # Tiempo de expiración de caché en segundos
    REDIS_LOCK_TIMEOUT = 10  # Tiempo de bloqueo en Redis en segundos

    def __init__(self, repository=None):
        self.repository = repository or StockRepository()

    @contextmanager
    def redis_lock(self, stock_id: int):
        """
        Context manager para gestionar el bloqueo de recursos en Redis.
        :param stock_id: ID del stock que se bloqueará.
        """
        lock_key = f"stock_lock_{stock_id}"
        lock_value = str(time.time())
        
        # Intentar adquirir el bloqueo
        if redis_client.set(lock_key, lock_value, ex=self.REDIS_LOCK_TIMEOUT, nx=True):
            try:
                yield  # Permite la ejecución del bloque protegido
            finally:
                # Eliminar el bloqueo después de usarlo
                redis_client.delete(lock_key)
        else:
            raise Exception(f"El recurso está bloqueado para el stock {stock_id}.")

    def all(self) -> list[Stock]:
        """
        Obtiene la lista de todos los stocks, con caché.
        :return: Lista de objetos Stock.
        """
        cached_stocks = cache.get('stocks')
        if cached_stocks is None:
            stocks = self.repository.get_all()
            if stocks:
                cache.set('stocks', stocks, timeout=self.CACHE_TIMEOUT)
            return stocks
        return cached_stocks

    def add(self, stock: Stock) -> Stock:
        """
        Agrega un nuevo stock y actualiza la caché.
        :param stock: Objeto Stock a agregar.
        :return: Objeto Stock recién creado.
        """
        new_stock = self.repository.add(stock)
        cache.set(f'stock_{new_stock.id}', new_stock, timeout=self.CACHE_TIMEOUT)
        cache.delete('stocks')  # Invalida la lista de stocks en caché
        return new_stock

    def update(self, stock_id: int, updated_stock: Stock) -> Stock:
        """
        Actualiza un stock existente.
        :param stock_id: ID del stock a actualizar.
        :param updated_stock: Datos del stock actualizado.
        :return: Objeto Stock actualizado.
        """
        with self.redis_lock(stock_id):
            existing_stock = self.find(stock_id)
            if not existing_stock:
                raise Exception(f"Stock con ID {stock_id} no encontrado.")

            # Actualizar los datos del stock existente
            existing_stock.nombre = updated_stock.nombre
            existing_stock.cantidad = updated_stock.cantidad
            existing_stock.precio = updated_stock.precio
            
            saved_stock = self.repository.save(existing_stock)
            
            # Actualizar la caché
            cache.set(f'stock_{stock_id}', saved_stock, timeout=self.CACHE_TIMEOUT)
            cache.delete('stocks')  # Invalida la lista de stocks en caché

            return saved_stock


    def delete(self, stock_id: int) -> bool:
        """
        Elimina un stock por su ID y actualiza la caché.
        :param stock_id: ID del stock a eliminar.
        :return: True si el stock fue eliminado, False en caso contrario.
        """
        with self.redis_lock(stock_id):
            deleted = self.repository.delete(stock_id)
            if deleted:
                cache.delete(f'stock_{stock_id}')
                cache.delete('stocks')  # Invalida la lista de stocks en caché
            return deleted

    def find(self, stock_id: int) -> Stock:
        """
        Busca un stock por su ID, con caché.
        :param stock_id: ID del stock a buscar.
        :return: Objeto Stock si se encuentra, None en caso contrario.
        """
        cached_stock = cache.get(f'stock_{stock_id}')
        if cached_stock is None:
            stock = self.repository.get_by_id(stock_id)
            if stock:
                cache.set(f'stock_{stock_id}', stock, timeout=self.CACHE_TIMEOUT)
            return stock
        return cached_stock

    def manage_stock(self, stock_id: int, cantidad: int) -> Stock:
        """
        Maneja el ingreso o egreso de stock asegurando consistencia.
        :param stock_id: ID del stock.
        :param cantidad: Cantidad a ingresar (positiva) o egresar (negativa).
        :return: Objeto Stock actualizado.
        :raises Exception: Si no hay suficiente stock disponible para un egreso.
        """
        with self.redis_lock(stock_id):
            stock = self.find(stock_id)
            if not stock:
                raise Exception(f"Stock con ID {stock_id} no encontrado.")
            
            nuevo_stock = stock.cantidad + cantidad
            if nuevo_stock < 0:
                raise Exception(f"No hay suficiente stock para egresar {abs(cantidad)} unidades.")
            
            stock.cantidad = nuevo_stock
            updated_stock = self.repository.save(stock)

            # Actualizar caché
            cache.set(f'stock_{stock_id}', updated_stock, timeout=self.CACHE_TIMEOUT)
            cache.delete('stocks')  # Invalida la lista de stocks en caché

            return updated_stock


#TODO//LISTO// REVISAR:refactorizar
#TODO //LISTO//REVISAR: falta manejar los egresos/ingresos 
#TODO//LISO//REVISAR: un bloqueador en redis por producto para resolver problemas de concurrenciass 
