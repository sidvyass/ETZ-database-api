from connection import get_connection
from exceptions import ItemNotFoundError, SchemaError
from schema import _get_schema, print_schema
import pyodbc
import logging


class Item:
    def __init__(self):
        self.logger = logging.getLogger().getChild(self.__class__.__name__)
        self.table_name = "item"
        self.schema = _get_schema(self.table_name)
        self.column_names = [name[0] for name in self.schema]
        self.insert_not_allowed_column_names = ["itempk", ]
        
        self.logger.info("Init new item class")

    def _column_check(self, columns):
        for value in columns:
            if value not in self.column_names:
                raise SchemaError.column_does_not_exist_error(value)

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

                query = "SELECT IDENT_CURRENT('iteminventory');"
                self.cursor.execute(query)
                iteminventorypk = self.cursor.fetchone()[0]
                conn.commit()

                print(f"Insert into iteminventory complete {iteminventorypk}")
                self.logger.info(f"Inserted ItemInventorypk - {iteminventorypk}")
                
                return iteminventorypk
        except pyodbc.Error as e:
            print(e)
    
    def insert_item(self, update_dict: dict) -> int:
        """Creates a new item. Also inserts into the item inventory table and attaches the FK."""
        self.column_check(update_dict.keys())
        try:
            # do not use this statment after with. Connection is closed twice.
            iteminventoryfk = self._insert_item_inventory()
            with get_connection() as conn:
                self.cursor = conn.cursor()
                column_names, column_len = ", ".join([name for name in update_dict.keys()]), ", ".join(['?' for name in update_dict.keys()])
                values = [str(val) for val in update_dict.values()]
                insert_query = f"""INSERT INTO {self.table_name} ({column_names}, iteminventoryfk)
                                    VALUES ({column_len}, ?);"""
                self.cursor.execute(insert_query, (*values, iteminventoryfk))
                query = f"SELECT IDENT_CURRENT('{self.table_name}');"
                self.cursor.execute(query)
                itempk = self.cursor.fetchone()[0]
                conn.commit()
                self.logger.info(f"Inserted into Item, Itempk: {itempk}")

                return itempk
        except pyodbc.Error as e:
            print(e)
                
    def get(self, *args, **kwargs) -> list:
        """args: define what is returned
            kwargs: define what is passed a parameter. NOTE- kwargs are case sensitive"""
        self._column_check(kwargs.keys())
        return_param_string = ",".join(args) if args else "*" 
        query = f"SELECT {return_param_string} FROM {self.table_name}" 
        search_param_string = " WHERE "
        if kwargs:
            search_param_string += " AND ".join([f"{key}='{str(value)}'" for key, value in kwargs.items()])
            query += search_param_string
        self.logger.info(f"GET METHOD Query Built -> {query}")

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    raise ItemNotFoundError
        except pyodbc.Error as e:
            print(e)


    def delete_item(self, itempk):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                query = "DELETE FROM item WHERE itempk='?';"
                cursor.execute(query, itempk)
        except pyodbc.Error as e:
            print(e)
