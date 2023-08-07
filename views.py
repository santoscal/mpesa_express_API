from datetime import datetime
import json
import base64
import requests
from django.http import JsonResponse
from .genrateAcesstoken import get_access_token
from django.shortcuts import render
from .models import AccTopUp


def home(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone')
        top_amount = request.POST.get('amount')


        print("print ", request.POST)

        if len(phone_number) != 10:
            return JsonResponse({'error': 'Enter a valid phone number!'})
        else:
            acc_top_up = AccTopUp(phone=phone_number, amount=top_amount)
            acc_top_up.save()

            # Call initiate_stk_push function with phone_number and top_amount
            stk_push_response = initiate_stk_push(phone_number, top_amount)

            # Handle the response from the stk_push function if needed
            # For example, you can return a JsonResponse with the response data
            return JsonResponse(stk_push_response)

    return render(request, "payments.html")

def initiate_stk_push(phone_number, top_amount):
    # Call get_access_token directly to retrieve the access token
    access_token_response = get_access_token()
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')
        if access_token:
            # Implement your STK push initiation logic here
            # ...

            process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
            callback_url = 'https://kariukijames.com/pesa/callback.php'
            passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
            business_short_code = '174379'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
            party_a = phone_number
            transaction_desc = 'STK push test'
            
            stk_push_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
            
            stk_push_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': top_amount,
                'PartyA': party_a,
                'PartyB': business_short_code,
                'PhoneNumber': party_a,
                'CallBackURL': callback_url,
                'AccountReference': 'Tactical Chess',  # Update with your specific reference
                'TransactionDesc': transaction_desc
            }

            try:
                response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                response.raise_for_status()   
                # Raise exception for non-2xx status codes
                response_data = response.json()
                checkout_request_id = response_data.get('CheckoutRequestID')
                response_code = response_data.get('ResponseCode')
                
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