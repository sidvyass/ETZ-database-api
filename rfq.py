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
            elif value in self.insert_not_allowed:
                raise SchemaError.insertion_not_allowed_error(value)
            
    def insert_rfq(self, update_dict: dict) -> int:
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


class RFQLine:
    def __init__(self):
        self.logger = logging.getLogger().getChild(self.__class__.__name__)
        self.table_name = "RequestForQuoteLine"
        schema = _get_schema(self.table_name)
        self.column_names = [name[0] for name in schema]
        self.insert_not_allowed = ["RequestForQuoteLinePK", ]
        
    def column_check(self, columns):
        for value in columns:
            if value not in self.column_names:
                raise SchemaError.column_does_not_exist_error(value)
            elif value in self.insert_not_allowed:
                raise SchemaError.insertion_not_allowed_error(value)

    def insert_rfq_line(self, RequestForQuoteFK:int, update_dict:dict) -> int:
        """QuoteFK goes in the update_dict as of now, can be changed"""
        self.column_check(update_dict.keys())
        assert "ItemFK" in update_dict.keys()
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                column_names, column_len = ", ".join([str(name) for name in update_dict.keys()]), ", ".join(["?" for name in update_dict.keys()])
                values = [val for val in update_dict.values()]
                insert_query = f"""INSERT INTO {self.table_name} ({column_names}, RequestForQuoteFK)
                                    VALUES ({column_len}, ?);"""
                cursor.execute(insert_query, (*values, RequestForQuoteFK))
                query = f"SELECT IDENT_CURRENT('{self.table_name}')"
                cursor.execute(query)

                rfq_line_pk = cursor.fetchone()[0]

                self.logger.info(f"Inserted line item to RFQPK: {RequestForQuoteFK}, RFQlinePK: {rfq_line_pk}")

                return rfq_line_pk
        except pyodbc.Error as e:
            print(e)

    def get_rfq_line(self, *args, **kwargs) -> list:
        """args: define what is returned as a tuple
            kwargs: define what is passed a parameter"""
        self.column_check(kwargs.keys())
        return_param_string = ",".join(args) if args else "*" 
        query = f"SELECT {return_param_string} FROM {self.table_name}" 

        search_param_string = " WHERE "

        if kwargs:
            search_param_string += " AND ".join([f"{key}={str(value)}" for key, value in kwargs.items()])
            query += search_param_string

        self.logger.info(f"Query Built -> {query}")

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)

            return cursor.fetchall()


if __name__ == "__main__":
    x = RFQLine()
    print(x.get_rfq_line("ItemFK", "QuoteFK", RequestForQuoteFK=1585))
