from storages.backends.azure_storage import AzureStorage
import os


class AzureMediaStorage(AzureStorage):
    account_name = os.environ.get('AZURE_ACCOUNT_NAME')
    account_key = os.environ.get('AZURE_ACCOUNT_KEY')
    azure_container = os.environ.get('MEDIA_LOCATION')
    expiration_secs = None
