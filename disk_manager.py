import os, time
import database_cryptography
from database import backup_folder, database_file_path
import re

def create_backup(name: str):
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
    
    backup_filename = get_backup_name(name)
    with open(backup_filename, "wb") as backup_file:
        backup_file.write(database_file_binary_data)
        parsed_backup_filename = parse_backup_filename(backup_filename.removeprefix(f"{backup_folder}/"))

        if (parsed_backup_filename is not None):
            if (parsed_backup_filename["counter"] is not None):
                print(f"CREATED: {get_pretty_printed_backup_string(parsed_backup_filename)}")
            else:
                print(f"CREATED: {get_pretty_printed_backup_string(parsed_backup_filename)}")
        else:
            print(f"CREATED: BACKUP - {name} WITH UNKNOWN PROPERTIES")

def get_current_time_string() -> str:
    """Gets the current time and date components, formatted into a string"""
    current_time = time.localtime()
    return (f"{current_time.tm_year}-{current_time.tm_mon}-{current_time.tm_mday}-{current_time.tm_hour}-{current_time.tm_min}-{current_time.tm_sec}")

def get_backup_name(backup_name: str) -> str:
    current_time_string = get_current_time_string()
    backup_filename: str = f"{backup_folder}/BACKUP-{backup_name}-{current_time_string}.db"
    counter = advanced_existing_backup_lookup(backup_name)

    if (counter != 0):
        backup_filename = f"{backup_folder}/BACKUP-{counter}-{backup_name}-{current_time_string}.db"

    return backup_filename

def advanced_existing_backup_lookup(backup_name: str) -> int:
    backup_list = get_backup_list()
    if (backup_list is not None):
        relevant_backup_list = [
            backup for backup in backup_list if backup["backup_name"] == backup_name
        ]
    else:
        return 0

    return len(relevant_backup_list)


def parse_backup_filename(filename: str) -> dict:
  """
  Parses a backup filename and extracts the backup name, counter (if any), and publish time.

  Args:
      filename: The backup filename (str).

  Returns:
      A dictionary containing the extracted information:
          - backup_name: The original backup name (str).
          - counter: The counter value (int) or None if no counter exists.
          - publish_time: The publish time string (str).
          - original_filename: The original filename associated with the backup (str).
  """
  match = re.search(r"^BACKUP-(\d+)?(-)?(.*?)-(\d{4}-\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2})\.db$", filename)
  if match:
    counter_str = match.group(1)
    counter = int(counter_str) if counter_str else None
    backup_name = match.group(3)
    publish_time = match.group(4)
    return {
      "backup_name": backup_name,
      "counter": counter,
      "publish_time": publish_time,
      "original_filename": filename
    }
  else:
      return None

def get_backup_list():
    backup_list: list[dict[str]] = []
    for filename in os.listdir(backup_folder):

        parsed_filename: dict = parse_backup_filename(filename)
        if (filename.endswith(".db") and parsed_filename is not None):
            backup_list.append(parsed_filename)
    return backup_list

def get_pretty_printed_backup_string(parsed_filename: dict[str, str]) -> str:
    if (parsed_filename["counter"] is not None):
        return f'BACKUP - UPDATE #{parsed_filename["counter"]} OF {parsed_filename["backup_name"]}: CREATED ON {parsed_filename["publish_time"]}'
    else:
        return f'BACKUP - {parsed_filename["backup_name"]}: CREATED ON {parsed_filename["publish_time"]}'

def list_backups():
    backup_list = get_backup_list()
    if (backup_list is not None):
        for parsed_filename in backup_list:
            print(get_pretty_printed_backup_string(parsed_filename))
    else:
        print("Failed to list the backups: Could not safely parse the backup filename!")

def remove_backup(backup_name: str, counter: str = None):
    backup_list = get_backup_list()
    if (backup_list is not None):
        print("Backup List is not None!")
        for parsed_filename in backup_list:
            if (counter is not None):
                # The user is trying to delete a copy.
                if (backup_name == parsed_filename["backup_name"]):
                    if (int(counter) == parsed_filename["counter"]):
                        os.remove(f'{backup_folder}/{parsed_filename["original_filename"]}')
                        backup_list.remove(parsed_filename)

                        sorted_backup_list = [backup for backup in backup_list if backup["counter"] is not None]
                        sorted_backup_list = sorted(sorted_backup_list, key=lambda x: x.get("counter", 0))

                        # Iteratively rename backups with higher counters to prevent extreme fuckery:
                        for subsequent_filename in sorted_backup_list:
                            if subsequent_filename["backup_name"] == backup_name and subsequent_filename["counter"] > int(counter):
                                new_counter = subsequent_filename["counter"] - 1
                                new_filename = f"{parsed_filename['original_filename'].replace(str(parsed_filename['counter']), str(new_counter))}"
                                os.rename(f'{backup_folder}/{subsequent_filename["original_filename"]}', f'{backup_folder}/{new_filename}')
                                subsequent_filename["counter"] = new_counter
                                subsequent_filename["original_filename"] = new_filename
                        
                        print(f"DELETED: {get_pretty_printed_backup_string(parsed_filename)}")
                        return # Return early out of the loop, since there is nothing else to remove.
            else:
                # The backup in question is not a copy, and the user is trying to delete the original backup.
                if (backup_name == parsed_filename["backup_name"] and parsed_filename["counter"] is None):
                    os.remove(f'{backup_folder}/{parsed_filename["original_filename"]}')
                    backup_list.remove(parsed_filename)
                    return # Return early out of the loop, since there is nothing else to remove.
    else:
        print("Failed to remove the backup: Could not safely parse the backup filename!")