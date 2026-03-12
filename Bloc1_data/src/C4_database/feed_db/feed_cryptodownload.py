import json
import os
from datetime import datetime
from pathlib import Path

from src.C2_query.query_currencies import get_currency_by_symbol
from src.C2_query.query_exchanges import get_exchange_by_name
from src.C2_query.query_trading_pairs import get_trading_pair_by_currencies
from src.C4_database.database import Database
from src.settings import ExtractSettings, logger, LogSettings


def process_all_cd_json():
    files_dir = Path(ExtractSettings.JSON_PATH_CD)

    with Database() as db:
        for file in files_dir.iterdir():
            if file.suffix == ".json":
                exchange_name = file.stem.split("_")[0].capitalize()
                exchange = get_exchange_by_name(exchange_name, session=db.session)
                if not exchange:
                    logger.warning(f"Plateforme d'échange {exchange_name} non trouvée dans la base de données")
                    continue

                logger.info(f"Traitement du fichier {file.name} pour l'échange {exchange_name}")
                process_cd_json(file, exchange, db)


def process_cd_json(file, exchange, db):
    try:
        with open(file, "r") as f:
            json_data = json.load(f)

        items = []
        failed_pairs = []
        for data in json_data["data"]:
            trading_pair = get_trading_pair(data["symbol"], exchange.name, db)
            if not trading_pair:
                failed_pairs.append(data)
                continue

            items.append({
                "exchange_id": exchange.id,
                "trading_pair_id": trading_pair.id,
                "timeframe": data["timeframe"],
                "start_date": datetime.fromisoformat(data["start_date"]),
                "end_date": datetime.fromisoformat(data["end_date"]),
                "file_url": data["file"],
            })

        success_count, failed_entries = db.crypto_csvs.create_many(items)
        logger.info(f"Insertion réussie de {success_count} fichiers CSV pour l'échange {exchange.name}")

        failed_entries = failed_pairs + failed_entries
        if failed_entries:
            os.makedirs(LogSettings.LOG_PATH, exist_ok=True)
            error_file = os.path.join(LogSettings.LOG_PATH, f"failed_csv_entries_{exchange.name}.json")
            with open(error_file, "w") as f:
                json.dump(failed_entries, f, indent=4, default=str)
            logger.info(f"{len(failed_entries)} lignes non insérées pour {exchange.name}. Détails dans {error_file}")

    except Exception as e:
        logger.error(f"Erreur pendant le traitement des données : {e}")


def get_trading_pair(pair, exchange_name, db):
    base = None
    quote = None
    quote_currencies = ["USDT", "USDC", "DAI", "BTC", "ETH", "BNB", "USD", "EUR"]

    if exchange_name == "Binance":
        for quote_curr in quote_currencies:
            if pair.endswith(quote_curr):
                quote = quote_curr
                base = pair[:-len(quote_curr)]
                break
        if not base or not quote:
            return None
    else:
        try:
            base, quote = pair.split("/")
            if quote not in quote_currencies:
                return None
        except ValueError:
            return None

    base_currency = get_currency_by_symbol(base, session=db.session)
    quote_currency = get_currency_by_symbol(quote, session=db.session)
    if not base_currency or not quote_currency:
        return None

    trading_pair = get_trading_pair_by_currencies(
        base_currency_id=base_currency.id,
        quote_currency_id=quote_currency.id,
        session=db.session,
    )
    if trading_pair:
        return trading_pair
    else:
        try:
            trading_pair = db.trading_pairs.create(
                base_currency_id=base_currency.id,
                quote_currency_id=quote_currency.id,
            )
            return trading_pair
        except Exception:
            return None
