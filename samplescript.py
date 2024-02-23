from general_class import GeneralAPI
from item import Item
from rfq import RFQ, RFQLine
from schema import print_schema

quote_update = {}

item_update = {
    "DaysEarly": 0,
    "Name": "test-api-sample",
    # can add more here
}

rfq_update = {
   "CustomerFK": 2504,
   "Comment":"test-api-sample", 
}



party_table = GeneralAPI("Party")
# print(party_table.insert(item_update))
# schema = party_table.schema
# print_schema(schema)

print(party_table.get("DaysEarly", "Name", DaysEarly=0, Name="test-api-sample"))