from connection import get_connection
from exceptions import ItemNotFoundError
from general import _get_schema
import pyodbc

class MieTrakItem:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        self.schema = _get_schema("item")

        insert_not_allowed_column_names = ["itempk", ]

    def update_item(self, part_number: str, update_dict: dict):
        """
        Updates the columns in the item table. 
        Params: part_number: number to search the item table by. (string only)
        update_dict: Key value pairs of column in the table to value to insert
        """
        try:
            query = f"SELECT itempk FROM item WHERE partnumber='{part_number}';"
            self.cursor.execute(query)
            item = self.cursor.fetchone()

            if not item:
                raise ItemNotFoundError(part_number)

            itempk = item[0]

            # we need to add checks here for the column values
            
            update_assignments = ", ".join([f"{column}=?" for column in update_dict.keys()])
            update_values = list(update_dict.values())
            update_query = f"UPDATE item SET {update_assignments} WHERE itempk=?;"

            self.cursor.execute(update_query, (*update_values, itempk))
            
        except pyodbc.Error as e:
            print(e)
