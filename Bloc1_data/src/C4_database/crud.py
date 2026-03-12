from typing import Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, Session

from src.C4_database.models import (
    Base,
    Currency,
    TradingPair,
    Exchange,
    CryptocurrencyCSV,
    CSVHistoricalData,
    OHLCVMinute,
    OHLCVHourly,
    OHLCVDaily,
    User,
    PredictionHourly,
    PredictionDaily,
)
from src.settings import logger
from src.utils.functions import validate_date


class BaseCRUD:
    def __init__(self, model, db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        self.db.add(obj)
        try:
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError:
            self.db.rollback()
            raise

    def create_many(self, items: List[Dict], batch_size: int = 10000):
        success_count = 0
        failed = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            try:
                self.db.bulk_insert_mappings(self.model, batch)
                self.db.commit()
                success_count += len(batch)
            except IntegrityError:
                logger.error(f"Erreur lors de l'insertion en batch. Tentative d'insertion individuelle pour {len(batch)} objets.")
                self.db.rollback()
                for item in batch:
                    try:
                        self.create(**item)
                        success_count += 1
                    except IntegrityError:
                        failed.append(item)

        return success_count, failed

    def get(self, id: int):
        return self.db.query(self.model).get(id)

    def list_all(self):
        return self.db.query(self.model).all()

    def update(self, id: int, **kwargs):
        obj = self.get(id)
        for key, value in kwargs.items():
            setattr(obj, key, value)
        try:
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError:
            self.db.rollback()
            raise

    def delete(self, id: int):
        obj = self.get(id)
        try:
            self.db.delete(obj)
            self.db.commit()
            return obj
        except IntegrityError:
            self.db.rollback()
            raise


class CurrencyCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(Currency, db)


class TradingPairCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(TradingPair, db)

    def get_pairs_by_base_currency_symbol(self, symbol: str):
        return (self.db.query(self.model)
                .options(joinedload(self.model.base_currency),
                         joinedload(self.model.quote_currency))
                .filter(self.model.base_currency.has(Currency.symbol == symbol))
                .all())

    def get_pair_by_currency_symbols(self, base_symbol: str, quote_symbol: str):
        return (self.db.query(self.model)
                .options(joinedload(self.model.base_currency),
                         joinedload(self.model.quote_currency))
                .filter(self.model.base_currency.has(Currency.symbol == base_symbol))
                .filter(self.model.quote_currency.has(Currency.symbol == quote_symbol))
                .first())


class ExchangeCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(Exchange, db)


class CryptocurrencyCSVCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(CryptocurrencyCSV, db)


class CSVHistoricalDataCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(CSVHistoricalData, db)


class OHLCVMinuteCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(OHLCVMinute, db)

    def get_ohlcv_by_trading_pair(self, trading_pair_id: int, start_date: Optional[str] = None):
        query = self.db.query(self.model).filter(self.model.trading_pair_id == trading_pair_id)
        if start_date:
            validated_date = validate_date(start_date)
            if validated_date:
                query = query.filter(self.model.date >= validated_date)
        return query.order_by(self.model.date.asc()).all()


class OHLCVHourlyCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(OHLCVHourly, db)

    def get_ohlcv_by_trading_pair(self, trading_pair_id: int, start_date: Optional[str] = None):
        query = self.db.query(self.model).filter(self.model.trading_pair_id == trading_pair_id)
        if start_date:
            validated_date = validate_date(start_date)
            if validated_date:
                query = query.filter(self.model.date >= validated_date)
        return query.order_by(self.model.date.asc()).all()


class OHLCVDailyCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(OHLCVDaily, db)

    def get_ohlcv_by_trading_pair(self, trading_pair_id: int, start_date: Optional[str] = None):
        query = self.db.query(self.model).filter(self.model.trading_pair_id == trading_pair_id)
        if start_date:
            validated_date = validate_date(start_date)
            if validated_date:
                query = query.filter(self.model.date >= validated_date)
        return query.order_by(self.model.date.asc()).all()


class UserCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str):
        return self.db.query(self.model).filter(self.model.username == username).first()


class PredictionHourlyCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(PredictionHourly, db)

    def get_predictions_by_trading_pair(self, trading_pair_id: int, start_date: Optional[str] = None):
        query = self.db.query(self.model).filter(self.model.trading_pair_id == trading_pair_id)
        if start_date:
            validated_date = validate_date(start_date)
            if validated_date:
                query = query.filter(self.model.date >= validated_date)
        return query.order_by(self.model.date.asc()).all()

    def get_last_prediction_by_trading_pair(self, trading_pair_id: int):
        return (self.db.query(self.model)
                .filter(self.model.trading_pair_id == trading_pair_id)
                .order_by(self.model.date.desc())
                .first())


class PredictionDailyCRUD(BaseCRUD):
    def __init__(self, db: Session):
        super().__init__(PredictionDaily, db)

    def get_predictions_by_trading_pair(self, trading_pair_id: int, start_date: Optional[str] = None):
        query = self.db.query(self.model).filter(self.model.trading_pair_id == trading_pair_id)
        if start_date:
            validated_date = validate_date(start_date)
            if validated_date:
                query = query.filter(self.model.date >= validated_date)
        return query.order_by(self.model.date.asc()).all()

    def get_last_prediction_by_trading_pair(self, trading_pair_id: int):
        return (self.db.query(self.model)
                .filter(self.model.trading_pair_id == trading_pair_id)
                .order_by(self.model.date.desc())
                .first())
