from pyodbc import Error

# we need this as pyodbc will happily return an empty fetchall list
class ItemNotFoundError(Exception):
    def __init__(self, part_number, message="Search value does not exist in item table, cannot update"):
        self.part_number = part_number
        self.message = message

    def __str__(self):
        return f"{self.message} Part Number: {self.part_number}"

class SchemaError(Exception):
    def __init__(self, column_name, message="Schema Error"):
        self.column_name = column_name
        self.message = message

    @staticmethod
    def insertion_not_allowed_error(column_name):
        SchemaError(column_name, message="Cannot insert into column.") 

    def __str__(self):
        return f"{self.message} Column Name: {self.column_name}"
