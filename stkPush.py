import requests
from datetime import datetime
import json
import base64
from django.http import JsonResponse
from .genrateAcesstoken import get_access_token

def initiate_stk_push(phone_number, top_amount):
    access_token_response = get_access_token(request)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if access_token:
            phone = phone_number
            amount = top_amount
            process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            callback_url = 'https://kariukijames.com/pesa/callback.php'
            passkey = ""
            business_short_code = '174379'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            party_a = phone
            party_b = phone_number
            account_reference = 'Tactical Chess'
            transaction_desc = 'stkpush test'
            stk_push_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
            
            stk_push_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': amount,
                'PartyA': party_a,
                'PartyB': business_short_code,
                'PhoneNumber': party_a,
                'CallBackURL': callback_url,
                'AccountReference': account_reference,
                'TransactionDesc': transaction_desc
            }

            try:
                response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                response.raise_for_status()   
                # Raise exception for non-2xx status codes
                response_data = response.json()
                checkout_request_id = response_data['CheckoutRequestID']
                response_code = response_data['ResponseCode']
                
                if response_code == "0":
                    return JsonResponse({'CheckoutRequestID': checkout_request_id})
                else:
                    return JsonResponse({'error': 'STK push failed.'})
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})
