from typing import List

from app import db
from app.models import Stock

from .repository import Repository_delete, Repository_get, Repository_save


class StockRepository(Repository_save, Repository_get, Repository_delete):
    def save(self, entity: Stock) -> Stock:
        db.session.add(entity)
        db.session.commit()
        return entity

    def get_all(self) -> List[Stock]:
        return Stock.query.all()

    def get_by_id(self, id: int) -> Stock:
        return Stock.query.get(id)

    def delete(self, id: int) -> bool:
        Stock = self.get_by_id(id)
        if Stock:
            db.session.delete(Stock)
            db.session.commit()
            return True
        return False
