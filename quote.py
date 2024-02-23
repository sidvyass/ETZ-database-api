from connection import get_connection
from exceptions import ItemNotFoundError, SchemaError
from schema import _get_schema, print_schema
from test_data import quote_test 
import pyodbc
import logging

class Quote:
    def __init__(self):
        self.logger = logging.getLogger().getChild(self.__class__.__name__)
        self.table_name = "Quote"
        schema = _get_schema(self.table_name)
        self.column_names = [name[0] for name in schema]
        self.insert_not_allowed = ["QuotePK", ]

    def column_check(self, columns):
        for value in columns:
            if value not in self.column_names:
                raise SchemaError.column_does_not_exist_error(value)
            elif value in self.insert_not_allowed:
                raise SchemaError.insertion_not_allowed_error(value)

    def insert_quote(self, update_dict: dict) -> int:
        self.column_check(update_dict.keys())
        assert all(val in update_dict.keys() for val in ["CustomerFK", "ItemFK"])

        column_names, column_len = ", ".join([val for val in update_dict.keys()]), ", ".join(["?" for val in update_dict.values()])
        values = [val for val in update_dict.values()]

        insert_query = f"""INSERT INTO {self.table_name} ({column_names})
        VALUES ({column_len})"""

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(insert_query, *values)

                query = f"SELECT IDENT_CURRENT('{self.table_name}')"
                cursor.execute(query)
                quotepk = cursor.fetchone()[0]
                self.logger.info(f"Inserted quote. QuotePK: {quotepk}")
                return quotepk
                
        except pyodbc.Error as e:
            print(e)

                
if __name__ == "__main__":
    q = Quote()
    print(q.insert_quote(quote_test))