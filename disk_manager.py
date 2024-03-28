import os, time
import database_cryptography
from database import backup_folder, database_file_path

def load_database():
    """Loads database from disk, if it dosen't exist on disk, create a new database."""
    global database
    if (os.path.exists(database_file_path)):
        # TODO: Implement database
        pass
    else:
        # TODO: Implement database
        pass

def create_backup():
    """
    Copies the current database into the backups folder, then prefixes that file with BACKUP-, and suffixes it with the current time (YY-MM-DD-SS).
    Additionally, if the specified backup already exists, instead of overwriting it, 
    it will iteratively change its name similar to how windows does it when you copy a file with the same name
    """
    if not (os.path.exists(backup_folder)):
        # backup folder dosen't exist
        os.makedirs(backup_folder)
    
    database_file_binary_data: bin = None
    with open(database_file_path, "rb") as database_file:
        database_file_binary_data = database_file.read()
    
    with open(get_backup_name()) as backup_file:
        backup_file.write(database_file_binary_data)

def get_current_time_string() -> str:
    """Gets the current time and date components, formatted into a string"""
    current_time = time.localtime()
    return (f"{current_time.tm_year}-{current_time.tm_mon}-{current_time.tm_mday}-{current_time.tm_hour}-{current_time.tm_min}-{current_time.tm_sec}")

def get_backup_name() -> str:
    backup_filename: str = f"{backup_folder}/BACKUP-{database_file_path.removesuffix('.db')}-{get_current_time_string()}.db"
    counter = 0
    while (os.path.exists(backup_filename)):
        counter += 1
        backup_filename = f"{backup_folder}/BACKUP-{counter}-{database_file_path.removesuffix('.db')}-{get_current_time_string()}.db"

    return backup_filename