import os
import time
import sqlite3
import database_cryptography
import re
import traceback
import disk_manager

backup_folder: str = "database_backups"
database_file_path: str = "database.db"

conn = sqlite3.connect(database_file_path)
cursor = conn.cursor()

# Create table (if it doesn't exist)
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                  username TEXT PRIMARY KEY,
                  password BLOB
                )""")

def display_table():
    """Displays the contents of the users table."""
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    print("Username\tPassword")  # Print header
    for row in rows:
        print(f"{row[0]}\t{row[1]}")  # Print each row with tab separation

def add_user(username: str, password: str):
    # TODO: Implement database
  """Adds a user to the database

  Args:
      username: The username of the user
      password: The inputted password of the user
  """
  try:
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, database_cryptography.hash_salt_password(password)))
    conn.commit()
    print(f"User {username} added successfully!")
  except sqlite3.IntegrityError:
    print(f"A user by that name already exists!")

def remove_user(username: str):
  """Removes a user from the database.

  Args:
      username: The username of the user to remove.
  """
  try:
    cursor.execute('DELETE FROM users WHERE username=?', (username,))
    conn.commit()
    print(f"User {username} removed successfully!")
  except sqlite3.Error as e:
    print(f"An error occurred while removing user: {e}")

def get_user_from_database(username: str):
    # TODO: Implement database
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    return cursor.fetchone()

def login(username: str, password: str):
    user = get_user_from_database(username)
    if (user is not None):
        if (database_cryptography.check_correct_password(password, user[1]) is True):
           print(f"Successfully logged into {username}!")
        else:
           print("Invalid username or password.")
    else:
       print("Invalid username or password.")

import re


def split_by_quotes(text: str) -> list[str]:
  """
  Splits a string based on whitespaces, ignoring whitespaces inside double quotes.

  Args:
      text: The string to split (str).

  Returns:
      A list of words split from the text (List[str]).
  """
  buffer: list[str] = []
  current_word: str = ""
  in_quotes: bool = False

  for char in text:
    if char == '"':
      in_quotes = not in_quotes
    elif not in_quotes and char.isspace():
      if current_word:
        buffer.append(current_word)
      current_word = ""
    else:
      current_word += char

  if current_word:
    buffer.append(current_word)

  return buffer

if __name__ == "__main__":
    add_user("John", "zingerburger")
    login("John", "zingerburger")
    print("Loading Terminal... Type HELP for help.")

    while True:
        try:
            user_input = input("root@authme $> ")
            split_input = split_by_quotes(user_input)

            match (split_input[0].upper()):
                case "HELP":
                    print("Avaliable Commands (not case sensitive):")
                    print(" - HELP: Displays this message you see right now.")
                    print(" - REMOVE: Removes a user from the database. Args: Username")
                    print(" - ADD: Adds a user to the database. Args: Username, Password")
                    print(" - LOGIN: Perform a mock login to a user. Args: Username, Password")
                    print(" - LIST: List all users currently signed into the database.")
                    print("""
 - BACKUP: Tools to Create, Remove and List Backups.
     - Sub Commands:
         - CREATE: Creates a backup with the given name. You can create more than one backup with the same name.
         - REMOVE: Removes a backup, optionally specify which copy it is of the backup you are trying to remove.
         - LIST: Lists all backups.
                          """)
                case "REMOVE":
                    if (len(split_input) < 2):
                        print("Not enough arguments!")
                        continue
                    remove_user(split_input[1])
                case "ADD":
                    if (len(split_input) < 3):
                        print("Not enough arguments!")
                        continue
                    add_user(split_input[1], split_input[2])
                case "LOGIN":
                    if (len(split_input) < 3):
                        print("Not enough arguments!")
                        continue
                    login(split_input[1], split_input[2])
                case "LIST":
                    display_table()
                case "BACKUP":
                    if (len(split_input) < 2):
                        print("Not enough arguments!")
                        continue
                    match (split_input[1].upper()):
                        case "CREATE":
                            if (len(split_input) < 3):
                                print("Not enough arguments!")
                                continue
                            disk_manager.create_backup(split_input[2])
                        case "REMOVE":
                            if (len(split_input) < 3):
                                print("Not enough arguments!")
                                continue

                            if (len(split_input) > 3):
                                disk_manager.remove_backup(split_input[2], split_input[3])
                            else:
                                disk_manager.remove_backup(split_input[2])
                        case "LIST":
                            if (len(split_input) < 2):
                                print("Not enough arguments!")
                                continue
                            disk_manager.list_backups()
                        case _:
                            print("Unknown Sub Command! Type HELP for help.")
                case _:
                    print("Unknown Command! Type HELP for help.")
        except IndexError:
            pass
        except Exception:
            traceback.print_exc()
                