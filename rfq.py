from connection import get_connection
from exceptions import ItemNotFoundError, SchemaError
from general import _get_schema
from test_data import test1_dict, test2_rfq
import pyodbc
import logging


class RFQ:
    def __init__(self):
        self.logger = logging.getLogger().getChild(self.__class__.__name__)
        self.table_name = "RequestForQuote"
        
        schema = _get_schema(self.table_name)
        self.column_names = [name[0] for name in schema]

        self.insert_not_allowed = ["RequestForQuotePK",]

    def column_check(self, columns):
        for value in columns:
            if value not in self.column_names:
                raise SchemaError.column_does_not_exist_error(value)
            
    def insert_rfq(self, update_dict: dict):
        self.column_check(update_dict.keys())
        try:
            with get_connection() as conn:
                self.cursor = conn.cursor()
                column_names, column_len = ", ".join([name for name in update_dict.keys()]), ", ".join(['?' for name in update_dict.keys()])
                values = [str(val) for val in update_dict.values()]
                insert_query = f"""INSERT INTO {self.table_name} ({column_names})
                                    VALUES ({column_len});"""

                self.cursor.execute(insert_query, *values)

                query = f"SELECT IDENT_CURRENT('{self.table_name}');"
                self.cursor.execute(query)
                request_for_quote_pk = self.cursor.fetchone()[0]
                conn.commit()

                self.logger.info(f"Inserted into RFQ, RequestForQuotePK: {request_for_quote_pk}")

                return request_for_quote_pk
        except pyodbc.Error as e:
            print(e)

