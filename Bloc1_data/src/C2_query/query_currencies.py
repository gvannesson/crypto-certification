from src.C4_database.database import with_session
from src.C4_database.models import Currency


@with_session
def get_currency_by_name(name, currency_type=None, session=None):
    query = session.query(Currency).filter(Currency.name == name)
    if currency_type:
        query = query.filter(Currency.type == currency_type)
    return query.first()


@with_session
def get_currency_by_symbol(symbol, currency_type=None, session=None):
    query = session.query(Currency).filter(Currency.symbol == symbol)
    if currency_type:
        query = query.filter(Currency.type == currency_type)
    return query.first()


@with_session
def get_all_currencies(currency_type=None, session=None):
    query = session.query(Currency)
    if currency_type:
        query = query.filter(Currency.type == currency_type)
    return query.all()
