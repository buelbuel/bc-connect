#!/usr/bin/env python3
from .deutschebank import DeutscheBankImporter
from beancount.ingest.importers.config import Target

# Define your mappings
mappings = {
    'Salary': Target('Assets:Income', 'Foo Company'),
    'Walmart': Target('Expenses:Food:Groceries'),
}

# Configure the importer
CONFIG = [
    DeutscheBankImporter('Assets:Checking', 'Expenses:ReplaceMe', mappings)
]

# You would then use this CONFIG in your Beancount import process
