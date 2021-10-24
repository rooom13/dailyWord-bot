import logging

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth, ServiceAccountCredentials

from daily_word_bot.config import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


class BackupService:  # pragma: no cover
    is_ready = False

    def __init__(self):
        self.__authenticate()

    def __authenticate(self):
        try:
            gauth = GoogleAuth()
            scope = ["https://www.googleapis.com/auth/drive"]
            gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name("service-account.json", scope)
            self.drive = GoogleDrive(gauth)
            self.is_ready = True
        except Exception as e:
            logger.info(f"Can't authenticate BackupService, setting it to not ready: {e}", exc_info=e)
            self.is_ready = False

    def backup(self):
        """Uploads the file in 'config.BACKUP_FILE_PATH_IN' to a google drive
        file with id 'config.BACKUP_FILE_ID_OUT' in folder 'config.BACKUP_FOLDER_ID_OUT'"""
        self.__authenticate()

        if not self.is_ready:
            raise Exception("Can't backup, BackupService is not ready")

        file = self.drive.CreateFile({
            'parents': [{'id': config.BACKUP_FOLDER_ID_OUT}],
            'id': config.BACKUP_FILE_ID_OUT
        })

        file.SetContentFile(config.BACKUP_FILE_PATH_IN)
        file.Upload()
