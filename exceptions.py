

class ItemNotFoundError(Exception):
    def __init__(self, part_number, message="Search value does not exist in item table, cannot update"):
        self.part_number = part_number
        self.message = message

    def __str__(self):
        return f"{self.message} Part Number: {self.part_number}"
