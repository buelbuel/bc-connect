#!/usr/bin/env python3
from .api_base import BankAPIBase
from utils.api import create_request_headers, make_request
from utils.credentials import get_credential
import requests
import base64
import json
import time
import uuid
from datetime import datetime, timedelta


class DeutscheBankAPI(BankAPIBase):
    def __init__(self):
        super().__init__('DEUTSCHEBANK')
        self.base_url = ""
        self.session_id = self.get_session_id()
        self.access_token = None
        self.client_id = self.get_client_id()
        self.client_secret = self.get_client_secret()
        self.username = self.get_username()
        self.pin = self.get_pin()

    def get_pin(self):
        return get_credential('PIN', 'DEUTSCHEBANK', use_getpass=True)

    def get_client_id(self):
        return get_credential('CLIENT_ID', 'DEUTSCHEBANK')

    def get_client_secret(self):
        return get_credential('CLIENT_SECRET', 'DEUTSCHEBANK')

    def get_username(self):
        return get_credential('USERNAME', 'DEUTSCHEBANK')

    def get_session_id(self):
        return str(uuid.uuid4())

    def get_request_id(self):
        return str(uuid.uuid4())

    def authenticate(self):
        """Authenticate with Deutsche Bank"""
        pass

    def get_accounts(self):
        """Get all accounts"""
        pass

    def get_transactions(self, account_id, from_date=None, to_date=None):
        """Get transactions for a specific account"""
        pass
