# API for Mie Trak
## Introduction
This is a simple API for CRUD operations performed on the database using python built using pyodbc. The goal for this API is to abstract away direct SQL handling. 

## Prerequisites
- Python 3.12
- Pyodbc

## Installation
(Note: While this is intended to be a package, it has not been tested to be installed using `pip .`)
- Clone the repository or download the 'src' folder
- Set up a virtual environment (optional)
- Install the dependencies using `pip install -r requirements.txt`
- Connection.py file is not provided, obtain the file from the local Etezazi server and add it to 'src/'

## Configuration
Only the logger can be configured. To configure the log folder, go to logging_config.py and change the directory and filename on line 4.

## Usage
Except the 'item' table all other tables can be accessed through TableManger. For 'item' initialize the Item class from item.py
The only criteria for passing arguments in the methods of this class is that the arguments should be present in the schema of the database. The code has been configured to throw an error before the query execution takes place if the arguments are not present in the schema.

### Examples
- Initialize a class:
`rfq = TableManager("<table name>")`
- Insert function which takes in a dictionary with key, value pairs. Eg: \
`update_dict = {
    column1: value1,
    column2: value2,
}`\
`rfq.insert(update_dict)`
- Get function has more flexibility with *args and **kwargs which can be passed like so \
`rfq.get(name, last_access, rfq_pk=1234)` \
The args are returned as a tuple in the return list and the kwargs are used to filter entries in the database.

## Disclaimer
This software, developed by Etezazi Industries, is intended for internal use only and is not designed for or intended for use by the general public. The software is provided 'as is' without warranty of any kind, either expressed or implied. Etezazi Industries disclaims all liability for any damage or issues that may result from using this software.

The software may use open-source libraries or frameworks; their use does not imply endorsement by the original creators. Etezazi Industries offers no support or maintenance services for this software. Users are responsible for ensuring that their use of the software complies with all applicable company policies and laws.

Modification, redistribution, or use of this software outside of Etezazi Industries is not permitted without express written consent. Users are also responsible for managing and protecting any sensitive or personal data handled by the software in accordance with data privacy laws and company policies.