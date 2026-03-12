from src.C4_database.database import with_session
from src.C4_database.models import Exchange


@with_session
def get_exchange_by_name(name, session=None):
    return session.query(Exchange).filter(Exchange.name == name).first()


@with_session
def get_exchange_by_id(exchange_id, session=None):
    return session.query(Exchange).filter(Exchange.id == exchange_id).first()


@with_session
def get_all_exchanges(session=None):
    return session.query(Exchange).all()
