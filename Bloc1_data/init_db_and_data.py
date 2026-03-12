import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.C1_extraction.extract_coinmarketcap import extract_all_coinmarketcap
from src.C1_extraction.extract_cryptodownload import extract_all_cryptodownload
from src.C1_extraction.extract_csv_data import extract_all_pairs_data
from src.C3_aggregate_ohlcv.aggregate_ohlcv import aggregate_all_ohlcv
from src.C4_database.feed_db.feed_coinmarketcap import process_all_cmc_json
from src.C4_database.feed_db.feed_cryptodownload import process_all_cd_json
from src.C4_database.feed_db.feed_user import create_script_user
from src.settings import logger


def parse_args():
    parser = argparse.ArgumentParser(description="Exécute les composants du pipeline Bloc1")

    parser.add_argument("--extract_files", action="store_true", help="Extraction des fichiers JSON/CSV")
    parser.add_argument("--feed_raw_db", action="store_true", help="Alimentation brute de la BDD (CMC + CryptoDownload)")
    parser.add_argument("--extract_data", action="store_true", help="Extraction des données CSV vers la BDD")
    parser.add_argument("--aggregate", action="store_true", help="Agrégation OHLCV (minute → hour → day)")
    parser.add_argument("--initiate_api_user", action="store_true", help="Création de l'utilisateur API script")
    parser.add_argument("--all", action="store_true", help="Exécute le pipeline complet")

    return parser.parse_args()


def main():
    args = parse_args()

    run_all = args.all or not any([
        args.extract_files,
        args.feed_raw_db,
        args.extract_data,
        args.aggregate,
        args.initiate_api_user,
    ])

    logger.info("Démarrage du pipeline ETL")

    if args.extract_files or run_all:
        logger.info("Exécute les étapes d'extraction des fichiers")
        extract_all_coinmarketcap()
        extract_all_cryptodownload()

    if args.feed_raw_db or run_all:
        logger.info("Exécute les étapes d'alimentation brutes de la base de données")
        process_all_cmc_json()
        process_all_cd_json()

    if args.extract_data or run_all:
        logger.info("Exécute les étapes d'extraction des données à partir des CSV de la BDD")
        extract_all_pairs_data()

    if args.aggregate or run_all:
        logger.info("Exécute les étapes d'agrégation")
        aggregate_all_ohlcv()

    if args.initiate_api_user or run_all:
        logger.info("Exécute les étapes d'initialisation de l'utilisateur API")
        create_script_user()

    logger.info("Composants du pipeline ETL sélectionnés terminés avec succès")


if __name__ == "__main__":
    main()
