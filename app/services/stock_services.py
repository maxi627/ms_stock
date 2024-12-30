from app import cache
from app.models import Stock
from app.repositories import StockRepository

repository = StockRepository()



#TODO:refactorizar
#TODO: falta manejar los egresos/ingresos 
#TODO: un bloqueador en redis por producto para resolver problemas de concurrenciass 

class StockService:
    def all(self) -> list[Stock]:
        result = cache.get('stocks')
        if result is None:
            result = repository.get_all()
            if result:
                cache.set('stocks', result, timeout=60)  # Considera un timeout más largo
        return result

    def add(self, stock: Stock) -> Stock:
        stock = repository.save(stock)
        cache.set(f'stock_{stock.id}', stock, timeout=60)
        cache.delete('stocks')  # Invalida la lista de stocks
        return stock

    def delete(self, id: int) -> bool:
        result = repository.delete(id)
        if result:
            cache.delete(f'stock_{id}')
            cache.delete('stocks')  # Invalida la lista de stocks
        return result

    def find(self, id: int) -> Stock:
        result = cache.get(f'stock_{id}')
        if result is None:
            result = repository.get_by_id(id)
            if result:
                cache.set(f'stock_{id}', result, timeout=60)
        return result
