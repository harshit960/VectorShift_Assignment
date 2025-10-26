# hubspot.py

import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import requests
from integrations.integration_item import IntegrationItem
import os
import base64

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
from dotenv import load_dotenv
import time
from urllib.parse import quote
load_dotenv()

CLIENT_ID = os.environ["HUBSPOT_CLIENT_ID"]
CLIENT_SECRET = os.environ["HUBSPOT_CLIENT_SECRET"]

REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
SCOPES = 'crm.objects.contacts.read crm.objects.companies.read crm.objects.deals.read'
authorization_url = f'https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&scope={quote(SCOPES)}&redirect_uri={quote(REDIRECT_URI)}'


# oAuth 
async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', json.dumps(state_data), expire=600)

    return f'{authorization_url}&state={encoded_state}'

async def oauth2callback_hubspot(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    # Exchange authorization code for access token
    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.hubapi.com/oauth/v1/token',
                data={
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}'),
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail='Failed to exchange code for token')

    response_json = response.json()
    expiry_timestamp = time.time() + response_json.get('expires_in', 0)
    response_json['expiry_timestamp'] = expiry_timestamp # Adding expiry_timestamp for handeling session expiry
    response_json.pop('refresh_token', None) # Removing refresh token as it make cause security leak
    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response_json), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')

    return credentials



# Metadata
def create_integration_item_metadata_object(response_json: dict) -> IntegrationItem:
    """Creates an integration metadata object from the HubSpot response"""
    # Extract properties based on object type
    properties = response_json.get('properties', {})
    
    # Get name based on object type
    name = None
    if 'firstname' in properties and 'lastname' in properties:
        # Contact
        name = f"{properties.get('firstname', '')} {properties.get('lastname', '')}".strip()
        obj_type = 'contact'
    elif 'name' in properties:
        # Company or Deal
        name = properties.get('name')
        obj_type = response_json.get('archived', False) and 'archived_' or ''
        obj_type += 'company' if 'domain' in properties else 'deal'
    else:
        name = properties.get('subject', properties.get('hs_object_id', 'Unknown'))
        obj_type = 'object'

    # Get timestamps
    created_at = properties.get('createdate') or properties.get('hs_createdate')
    modified_at = properties.get('lastmodifieddate') or properties.get('hs_lastmodifieddate')

    integration_item_metadata = IntegrationItem(
        id=response_json.get('id'),
        type=obj_type,
        name=name or 'Unnamed',
        creation_time=created_at,
        last_modified_time=modified_at,
        parent_id=None,  # HubSpot objects typically don't have parent relationships in this context
    )

    return integration_item_metadata

async def get_items_hubspot(credentials) -> list[IntegrationItem]:
    """Aggregates all metadata relevant for a HubSpot integration"""
    if isinstance(credentials, str):
        credentials = json.loads(credentials)
    
    access_token = credentials.get('access_token')
    if not access_token:
        raise HTTPException(status_code=400, detail='No access token found in credentials')

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    list_of_integration_item_metadata = []

    # Fetch contacts
    try:
        contacts_response = requests.get(
            'https://api.hubapi.com/crm/v3/objects/contacts',
            headers=headers,
        )
        if contacts_response.status_code == 200:
            contacts_data = contacts_response.json()
            for contact in contacts_data.get('results', []):
                list_of_integration_item_metadata.append(
                    create_integration_item_metadata_object(contact)
                )
    except Exception as e:
        print(f"Error fetching contacts: {e}")

    # Fetch companies
    try:
        companies_response = requests.get(
            'https://api.hubapi.com/crm/v3/objects/companies',
            headers=headers,
        )
        if companies_response.status_code == 200:
            companies_data = companies_response.json()
            for company in companies_data.get('results', []):
                list_of_integration_item_metadata.append(
                    create_integration_item_metadata_object(company)
                )
    except Exception as e:
        print(f"Error fetching companies: {e}")

    # Fetch deals
    try:
        deals_response = requests.get(
            'https://api.hubapi.com/crm/v3/objects/deals',
            headers=headers,
        )
        if deals_response.status_code == 200:
            deals_data = deals_response.json()
            for deal in deals_data.get('results', []):
                list_of_integration_item_metadata.append(
                    create_integration_item_metadata_object(deal)
                )
    except Exception as e:
        print(f"Error fetching deals: {e}")

    return list_of_integration_item_metadata