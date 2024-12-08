#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import getpass


def get_credential(credential_type, bank_name, use_getpass=False):
    """Generic function to handle credential input and storage"""
    env_key = f'{bank_name}_{credential_type}'.upper()
    value = os.getenv(env_key)

    if not value:
        prompt = f"Enter your {bank_name} {credential_type}: "
        if use_getpass:
            value = getpass.getpass(prompt)
        else:
            value = input(prompt)

        save = input(f"Do you want to save this {
                     credential_type} to .env? (yes/no): ").strip().lower()
        if save == 'yes':
            save_to_env(env_key, value)
    else:
        print(f"Using {credential_type} from .env")
    return value


def save_to_env(key, value):
    """Save a key-value pair to .env file"""
    try:
        with open('.env', 'r') as env_file:
            lines = env_file.readlines()

        with open('.env', 'w') as env_file:
            key_found = False
            for line in lines:
                if line.startswith(f'{key}='):
                    env_file.write(f'{key}={value}\n')
                    key_found = True
                else:
                    env_file.write(line)
            if not key_found:
                env_file.write(f'{key}={value}\n')
    except FileNotFoundError:
        with open('.env', 'w') as env_file:
            env_file.write(f'{key}={value}\n')
