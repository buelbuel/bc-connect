#!/usr/bin/env python3
import json
import requests


def create_request_headers(access_token, session_id, request_id):
    """Create standard request headers used across API calls"""
    return {
        'Accept': 'application/json',
        'Authorization': f"Bearer {access_token}",
        'X-Request-ID': request_id,
        'Session-ID': session_id,
        'Content-Type': 'application/json',
        'x-http-request-info': json.dumps({
            'clientRequestId': {
                'sessionId': session_id,
                'requestId': request_id
            }
        })
    }


def make_request(method, url, headers, params=None, data=None, json_data=None, return_full_response=False):
    """Make HTTP request and handle common response processing"""
    response = requests.request(
        method,
        url,
        headers=headers,
        params=params,
        data=data,
        json=json_data
    )
    response.raise_for_status()
    return response if return_full_response else (response.json() if response.content else None)
