from datetime import datetime
import json
import base64
import requests
from django.http import JsonResponse
from .genrateAcesstoken import get_access_token
from django.shortcuts import render
from .forms import PaymentForm
from .models import AccTopUp

def home(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            # After saving the form data, you can redirect to a success page or perform other actions.
    else:
        form = PaymentForm()
    
    context = {
        'form': form
    } 
    return render(request, "payments.html", context)


def get_access_token(request):
    consumer_key = "Amk"  # Fill with your app Consumer Key
    consumer_secret = "AAD3yP"  # Fill with your app Consumer Secret
    access_token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        result = response.json()
        access_token = result['access_token']
        return access_token  # Return the access token as a string, not a JSON response
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}


def initiate_stk_push(request):
    # Call get_access_token directly to retrieve the access token
    access_token = get_access_token(request)
    # print("Access token:", access_token)
    
    if access_token:
        # Implement your STK push initiation logic here
        # ...

        process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        callback_url = 'htphp'
        passkey = "b19"
        business_short_code = '174379'
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
        party_a = '600995'  # Convert to a string
        transaction_desc = 'STK push test'

        stk_push_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }

        original_string = str(request.POST.get("phone")) #convert to a string
        stripped_string = original_string.lstrip('0')  # Remove leading '0'
        phone_number = "254" + stripped_string

        stk_push_payload = {

            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': str(request.POST.get("amount")),  # Convert to a string
            'PartyA': party_a,
            'PartyB': business_short_code,
            'PhoneNumber': phone_number,  
            'CallBackURL': callback_url,
            'AccountReference': 'Tactical Chess',  # Update with your specific reference
            'TransactionDesc': transaction_desc
        }

        try:
            response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
            response.raise_for_status()
            # Raise an exception for non-2xx status codes
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
