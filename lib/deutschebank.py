#!/usr/bin/env python3
import os
import re
import codecs
import csv
import datetime
from beancount.core import number, data, amount
from beancount.ingest import importer


class Target(object):
    def __init__(self, account, payee=None, narration=None):
        self.account = account
        self.payee = payee
        self.narration = narration


class DeutscheBankImporter(importer.ImporterProtocol):
    def __init__(self, account, default, mapping):
        self.account = account
        self.default = default
        self.mapping = mapping

    def identify(self, fname):
        return re.match(r"Kontoumsaetze_\d+_\d+_\d+_\d+.csv",
                        os.path.basename(fname.name))

    def file_account(self, fname):
        return self.account

    def extract(self, fname):
        fp = codecs.open(fname.name, 'r', 'iso-8859-1')
        lines = fp.readlines()

        # drop top and bottom stuff
        lines = lines[5:]
        lines = lines[:-1]
        entries = []

        def fix_decimals(s):
            return s.replace('.', '').replace(',', '.')

        for index, row in enumerate(csv.reader(lines, delimiter=';')):
            meta = data.new_metadata(fname.name, index)
            date = datetime.datetime.strptime(row[0], '%d.%m.%Y').date()
            desc = row[4]
            payee = row[3]
            credit = fix_decimals(row[15]) if row[15] != '' else None
            debit = fix_decimals(row[16]) if row[16] != '' else None
            currency = row[17]
            account = self.default
            num = number.D(credit if credit else debit)
            units = amount.Amount(num, currency)

            for p, t in self.mapping.items():
                if p in desc:
                    account = t.account

                    if t.narration:
                        desc = t.narration

                    if t.payee:
                        payee = t.payee

            frm = data.Posting(self.account, units, None, None, None, None)
            to = data.Posting(account, -units, None, None, None, None)
            txn = data.Transaction(meta, date, "*", payee, desc,
                                   data.EMPTY_SET, data.EMPTY_SET, [frm, to])

            entries.append(txn)

        return entries
