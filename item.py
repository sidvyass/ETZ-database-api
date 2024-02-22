from connection import get_connection
from exceptions import ItemNotFoundError, SchemaError
from general import _get_schema
from test_data import test1_dict
import pyodbc

class MieTrakItem:
    def __init__(self):
        # self.conn = get_connection()
        # self.cursor = self.conn.cursor()
        self.table_name = "item"

        schema = _get_schema(self.table_name)
        self.column_names = [name[0] for name in schema]

        self.insert_not_allowed_column_names = ["itempk", ]
        self.default_values_dict = {

        }


    def update_item(self, part_number: str, update_dict: dict):
        """
        Updates the columns in the item table. 
        Params: part_number: number to search the item table by. (string only)
        update_dict: Key value pairs of column in the table to value to insert
        """
        try:
            query = f"SELECT itempk FROM item WHERE partnumber='?';"
            self.cursor.execute(query, part_number)
            item = self.cursor.fetchone()

            if not item:
                raise ItemNotFoundError(part_number)

            itempk = item[0]

            # we need to add checks here for the column values
            for column_name in update_dict.keys():
                if column_name in self.insert_not_allowed_column_names:
                    raise (column_name)
                if column_name not in self.column_names:
                    raise SchemaError.insertion_not_allowed_error()
            
            update_assignments = ", ".join([f"{column}=?" for column in update_dict.keys()])
            update_values = list(update_dict.values())
            update_query = f"UPDATE item SET {update_assignments} WHERE itempk=?;"

            self.cursor.execute(update_query, (*update_values, itempk))

            return itempk
        except pyodbc.Error as e:
            print(e)

    def _insert_item_inventory(self):
        try:
            with get_connection() as conn:
                self.cursor = conn.cursor()
                query = f"""INSERT INTO iteminventory 
                        (QuantityOnHand, QuantityReserved, QuantityDemand, QuantityWorkInProcess, QuantityPull, QuantityOnDock)
                        VALUES (?, ?, ?, ?, ?, ?)"""
                values_default = [0.000 for x in range(6)]
                self.cursor.execute(query, *values_default)
                print("Inserting into iteminventory")

                query = "SELECT IDENT_CURRENT('iteminventory');"
                self.cursor.execute(query)
                iteminventorypk = self.cursor.fetchone()[0]
                conn.commit()
                print("Insert complete")

                return iteminventorypk
        except pyodbc.Error as e:
            print(e)
    
    def insert_item(self, update_dict: dict):
        """Inserts item"""
        try:
            # do not use this statment after with. Connection is closed twice.
            iteminventoryfk = self._insert_item_inventory()
            with get_connection() as conn:
                self.cursor = conn.cursor()
                column_names, column_len = ", ".join([name for name in update_dict.keys()]), ", ".join(['?' for name in update_dict.keys()])
                values = [str(val) for val in update_dict.values()]
                # print("Inserting into item")
                insert_query = f"""INSERT INTO item ({column_names})
                                    VALUES ({column_len});"""

                self.cursor.execute(insert_query, *values)

                query = "SELECT IDENT_CURRENT('item');"
                self.cursor.execute(query)
                itempk = self.cursor.fetchone()[0]
                conn.commit()
                print("Insert complete")

                return itempk
        except pyodbc.Error as e:
            print(e)
                

if __name__ == "__main__":
    data = MieTrakItem()
    print(data.insert_item(test1_dict))
