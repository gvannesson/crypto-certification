from src.C4_database.database import Database
from src.C5_api.utils.auth import hash_password
from src.settings import SecretSettings, logger


def create_script_user():
    with Database() as db:
        existing = db.users.get_by_username(SecretSettings.API_USERNAME)
        if existing:
            logger.info(f"Utilisateur script '{SecretSettings.API_USERNAME}' déjà existant")
            return existing

        user = db.users.create(
            username=SecretSettings.API_USERNAME,
            password_hashed=hash_password(SecretSettings.API_PASSWORD),
            role=SecretSettings.API_ROLE or "script",
        )
        logger.info(f"Utilisateur script '{SecretSettings.API_USERNAME}' créé avec succès")
        return user
