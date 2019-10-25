import configparser
import sys
from time import sleep
import pyodbc
from prettytable import from_db_cursor


def read_configuration_file():
    tool_configuration = configparser.ConfigParser()

    sandbox_config_path = sys.path[0] + '\configurationFile.ini'

    tool_configuration.read(sandbox_config_path)

    default_settings = tool_configuration["DEFAULT"]

    server_name = default_settings["server_name"]
    database_name = default_settings["database_name"]
    db_user = default_settings["user_id"]
    db_password = default_settings["database_password"]

    return  server_name, database_name, db_user, db_password


def gather_zip_filename():
    source_files_for_reset = input("Info: Enter .txt or .log location which contains zip filename's for reset:")

    if source_files_for_reset.endswith(".txt") or source_files_for_reset.endswith(".log"):
        print(f"Info: Checking file for reset with retry counter equals to 3.")

        zip_filename_in_file = open(source_files_for_reset, "r")
        zip_files = zip_filename_in_file.read().replace("\n", "','")

        if zip_files.endswith("','"):
            zip_files = zip_files[:-3]

    else:
        print(f"Error: Please enter correct file instead!")

    return zip_files


def reset_from_database(server, database, db_user, db_password, zip_files):
    if len(zip_files) > 0:
        conn = pyodbc.connect('Driver={SQL Server};'
                              'Server=' + server + ';'
                              'Database=' + database + ';'
                              'UID=' + db_user + ';'
                              'PWD=' + db_password + ';'
                              "Trusted_Connection=No")

        cursor = conn.cursor()

        sql_query = "SELECT FileName, FileSize, DownloadedBy, RetryCounter, RemoteFolder " \
                    "FROM FTPCrawlerDB " \
                    "WHERE filename in('" + zip_files + "') and RetryCounter = '3'"

        cursor.execute(sql_query)
        for_update_files = from_db_cursor(cursor)

        print(for_update_files)

        confirmation = input("Info: Enter 'y' to reset retry counter to 0 on displayed filename:")

        if confirmation.lower() == 'y':
            # print(f"{for_update_files.get_string(fields=['FileName'])}")
            # for_update_files.header = False
            # for_update_files.border = False

            sql_query_update = "UPDATE [dbo].[FTPCrawlerDB] " \
                               "SET [RetryCounter] = 0 " \
                               "WHERE FileName in('" + for_update_files.get_string(fields=['FileName'],
                                                                                   border=False,
                                                                                   header=False)\
                .strip()\
                .replace('\n', '\',\'')\
                .replace(' ', '') + "')"

            cursor.execute(sql_query_update)
            cursor.commit()

            print(f"Info: Please check since done updating to 0.")

        else:
            print("Info: Exiting tool.")

    else:
        print("Error: Empty content found on file.")


def main():
    try:
        server, database, db_user, db_password = read_configuration_file()
        zip_files = gather_zip_filename()
        reset_from_database(server,
                            database,
                            db_user,
                            db_password,
                            zip_files)
        # print(f"zip files: {zip_files}")

    except Exception as e:
        print(f"Error: {e}")

    sleep(5)


main()
