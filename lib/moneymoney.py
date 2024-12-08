#!/usr/bin/env python3
import re
from datetime import datetime

with open('file.beancount', 'r') as file:
    lines = file.readlines()

date_regex = re.compile(r'^(\d{4}-\d{2}-\d{2})')


def extract_date(transaction):
    for line in transaction:
        match = date_regex.match(line)
        if match:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
    return datetime.min


transactions = []
current_transaction = []

for line in lines:
    if date_regex.match(line) and current_transaction:
        transactions.append(current_transaction)
        current_transaction = [line]
    else:
        current_transaction.append(line)

if current_transaction:
    transactions.append(current_transaction)

transactions = [t for t in transactions if extract_date(t) != datetime.min]

transactions.sort(key=extract_date)

with open('sorted_file.beancount', 'w') as file:
    for transaction in transactions:
        file.writelines(transaction)
