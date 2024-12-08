#!/usr/bin/env python3
import os
from dotenv import load_dotenv


class BankAPIBase:
    def __init__(self, env_prefix):
        load_dotenv()
        self.client_id = os.getenv(f'{env_prefix}_CLIENT_ID')
        self.client_secret = os.getenv(f'{env_prefix}_CLIENT_SECRET')
        self.username = os.getenv(f'{env_prefix}_USERNAME')
        self.pin = os.getenv(f'{env_prefix}_PIN')

    def authenticate(self):
        raise NotImplementedError(
            "This method should be overridden by subclasses")

    def get_accounts(self):
        raise NotImplementedError(
            "This method should be overridden by subclasses")

    def get_transactions(self, account_id, from_date=None, to_date=None):
        raise NotImplementedError(
            "This method should be overridden by subclasses")

    def get_all_balances(self):
        raise NotImplementedError(
            "This method should be overridden by subclasses")

    def get_account_balance(self, account_id):
        raise NotImplementedError(
            "This method should be overridden by subclasses")
