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


class ComdirectAPI(BankAPIBase):
    def __init__(self):
        super().__init__('COMDIRECT')
        self.base_url = "https://api.comdirect.de"
        self.session_id = self.get_session_id()
        self.access_token = None
        self.client_id = self.get_client_id()
        self.client_secret = self.get_client_secret()
        self.username = self.get_username()
        self.pin = self.get_pin()

    def get_pin(self):
        return get_credential('PIN', 'COMDIRECT', use_getpass=True)

    def get_client_id(self):
        return get_credential('CLIENT_ID', 'COMDIRECT')

    def get_client_secret(self):
        return get_credential('CLIENT_SECRET', 'COMDIRECT')

    def get_username(self):
        return get_credential('USERNAME', 'COMDIRECT')

    def get_session_id(self):
        return str(uuid.uuid4())

    def get_request_id(self):
        return str(uuid.uuid4())

    def authenticate(self):
        """Authenticate with Comdirect"""
        auth_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.username,
            'password': self.pin,
            'grant_type': 'password'
        }

        auth_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Request-ID': self.get_request_id(),
            'Authorization': 'Basic ' + base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
        }

        token_data = make_request(
            'POST',
            f"{self.base_url}/oauth/token",
            auth_headers,
            data=auth_data
        )
        self.access_token = token_data['access_token']

        if token_data.get('scope') == 'TWO_FACTOR':
            session_headers = create_request_headers(
                self.access_token,
                self.session_id,
                self.get_request_id()
            )

            client_id = token_data['kdnr']
            session_data = make_request(
                'GET',
                f'{self.base_url}/api/session/clients/{client_id}/v1/sessions',
                session_headers
            )[0]

            challenge = make_request(
                'POST',
                f'{self.base_url}/api/session/clients/{client_id}/v1/sessions/{
                    session_data["identifier"]}/validate',
                session_headers,
                json_data={
                    'identifier': session_data['identifier'],
                    'sessionTanActive': True,
                    'activated2FA': True
                },
                return_full_response=True
            )

            challenge_info = json.loads(challenge.headers.get(
                'x-once-authentication-info', '{}'))
            challenge_id = challenge_info.get('id')

            if challenge_info.get('typ') == 'P_TAN_PUSH':
                auth_status_url = self.base_url + \
                    challenge_info['link']['href']
                start_time = time.time()
                timeout = 120

                while (time.time() - start_time) < timeout:
                    status_response = requests.get(
                        auth_status_url,
                        headers=session_headers
                    )

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get('status') == 'AUTHENTICATED':
                            activation_headers = session_headers.copy()
                            activation_headers['x-once-authentication-info'] = json.dumps(
                                {'id': challenge_id})

                            session_activate = requests.patch(
                                f'{self.base_url}/api/session/clients/{
                                    client_id}/v1/sessions/{session_data["identifier"]}',
                                headers=activation_headers,
                                json={
                                    'identifier': session_data['identifier'],
                                    'sessionTanActive': True,
                                    'activated2FA': True
                                }
                            )
                            session_activate.raise_for_status()
                            break
                    time.sleep(2)
                else:
                    raise TimeoutError(
                        "Push notification confirmation timed out")

        final_auth = requests.post(
            f'{self.base_url}/oauth/token',
            headers=auth_headers,
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'cd_secondary',
                'token': self.access_token
            }
        )
        final_auth.raise_for_status()
        token_data = final_auth.json()
        self.access_token = token_data['access_token']

    def get_accounts(self):
        """Get all accounts"""
        headers = create_request_headers(
            self.access_token,
            self.session_id,
            self.get_request_id()
        )
        return make_request(
            'GET',
            f"{self.base_url}/api/banking/clients/user/v2/accounts",
            headers
        )

    def get_transactions(self, account_id, from_date=None, to_date=None):
        """Get transactions for a specific account"""
        headers = create_request_headers(
            self.access_token,
            self.session_id,
            self.get_request_id()
        )
        params = {
            'with-attr': 'account',
            'bookingStatus': 'BOTH'
        }
        if from_date:
            params['min-bookingDate'] = from_date

        return make_request(
            'GET',
            f"{self.base_url}/api/banking/v1/accounts/{account_id}/transactions",
            headers,
            params=params
        )

    def get_all_balances(self):
        """Get balances for all accounts including cash balance and buying power"""
        headers = create_request_headers(
            self.access_token,
            self.session_id,
            self.get_request_id()
        )
        return make_request(
            'GET',
            f"{self.base_url}/api/banking/clients/user/v2/accounts/balances",
            headers
        )

    def get_account_balance(self, account_id):
        """Get balance information for a specific account"""
        headers = create_request_headers(
            self.access_token,
            self.session_id,
            self.get_request_id()
        )
        return make_request(
            'GET',
            f"{self.base_url}/api/banking/v2/accounts/{account_id}/balances",
            headers
        )
