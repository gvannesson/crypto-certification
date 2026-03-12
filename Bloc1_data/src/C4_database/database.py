from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.C4_database.crud import (
    CurrencyCRUD,
    TradingPairCRUD,
    ExchangeCRUD,
    CryptocurrencyCSVCRUD,
    CSVHistoricalDataCRUD,
    OHLCVMinuteCRUD,
    OHLCVHourlyCRUD,
    OHLCVDailyCRUD,
    UserCRUD,
    PredictionHourlyCRUD,
    PredictionDailyCRUD,
)
from src.C4_database.models import Base
from src.settings import SecretSettings

db_username = SecretSettings.DB_USERNAME
db_password = SecretSettings.DB_PASSWORD
db_host = SecretSettings.DB_HOST
db_port = SecretSettings.DB_PORT
db_name = SecretSettings.DB_NAME

if not all([db_username, db_password, db_host, db_port, db_name]):
    raise ValueError("Certaines informations de connexion à la base de données sont manquantes. Vérifiez vos variables d'environnement.")

engine = create_engine(
    f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def with_session(func):
    @wraps(func)
    def wrapper(*args, session=None, **kwargs):
        if session is not None:
            return func(*args, session=session, **kwargs)
        else:
            with Database() as db:
                return func(*args, session=db.session, **kwargs)
    return wrapper


class Database:
    def __init__(self):
        self.session = Session()

        self.currencies = CurrencyCRUD(self.session)
        self.trading_pairs = TradingPairCRUD(self.session)
        self.exchanges = ExchangeCRUD(self.session)
        self.crypto_csvs = CryptocurrencyCSVCRUD(self.session)
        self.historical_data = CSVHistoricalDataCRUD(self.session)
        self.ohlcv_minute = OHLCVMinuteCRUD(self.session)
        self.ohlcv_hourly = OHLCVHourlyCRUD(self.session)
        self.ohlcv_daily = OHLCVDailyCRUD(self.session)
        self.users = UserCRUD(self.session)
        self.prediction_hourly = PredictionHourlyCRUD(self.session)
        self.prediction_daily = PredictionDailyCRUD(self.session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
