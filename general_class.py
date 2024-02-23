from connection import get_connection
from exceptions import ItemNotFoundError, SchemaError
from schema import _get_schema, print_schema
from test_data import party_test 
import pyodbc
import logging


class GeneralAPI:
    """General API that processes all table requests
    Pass table name in the constructor. Use insert, get, delete to get data.
    Import print_schema from schema and use self.schema to print with better visibility.
    Add any mandetory field to insert_mandetory or insert_not_allowed lists to run checks on them.
    """

    def __init__(self, table_name):
        "Table name is the same as MieTrak"
        self.table_name = table_name
        # this changes to being the name table potentially
        self.logger = logging.getLogger().getChild(self.__class__.__name__)
        self.schema = _get_schema(self.table_name)
        self.column_names = [name[0] for name in self.schema]
        # always use .append in self.insert_not_allowed
        self.insert_not_allowed = [f"{self.table_name}PK", ]
        self.insert_mandetory = []

    def _column_check(self, columns):
        for value in columns:
            if value not in self.column_names:
                raise SchemaError.column_does_not_exist_error(value)
            elif value in self.insert_not_allowed:
                raise SchemaError.insertion_not_allowed_error(value)
        for val in self.insert_mandetory:
            if val not in columns:
                raise SchemaError.mandetory_column_missing_error(val, self.table_name)   

    def insert(self, update_dict: dict):
        self._column_check(update_dict.keys())
        column_names, column_len = ", ".join([val for val in update_dict.keys()]), ", ".join(["?" for val in update_dict.keys()])
        values = [val for val in update_dict.values()]
        query = f"""INSERT INTO {self.table_name} ({column_names})
                    VALUES ({column_len})"""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, *values)
                query = f"SELECT IDENT_CURRENT('{self.table_name}')"
                cursor.execute(query)
                return_pk = cursor.fetchone()[0]
                self.logger.info(f"Inserted {self.table_name}. {self.table_name}PK: {return_pk}")
                conn.commit()
            return return_pk
        except pyodbc.Error as e:
            print(e)

    def get(self, *args, **kwargs) -> list:
        """args: define what is returned as a tuple
            kwargs: define what is passed a parameter"""
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
                return cursor.fetchall()
        except pyodbc.Error as e:
            print(e)

    def update(self):
        pass

    def delete(self, pk):
        f"""Takes {self.table_name}PK and deletes that entry"""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                query = f"DELETE FROM {self.table_name} WHERE {self.table_name}PK='?';"
                self.logger.info(f"DELETE - {self.table_name}PK: {pk}")
                cursor.execute(query, pk)
                conn.commit()
        except pyodbc.Error as e:
            print(e)
