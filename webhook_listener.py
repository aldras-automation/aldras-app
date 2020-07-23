from flask import Flask, request
import json
import requests


def output_to_debugging_webhook():
    pass


app = Flask(__name__)


# listen to webhooks
@app.route('/', methods=['POST'])
def foo():
    stripe_data = json.loads(request.data)

    cryptlex_url = 'https://api.cryptlex.com/v3/licenses'

    cryptlex_headers = '''{
      "Authorization": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJsaWNlbnNlOndyaXRlIiwidHJpYWxBY3RpdmF0aW9uOndyaXRlIl0sInN1YiI6IjlkMGEzMTlmLWEyMDktNGM2YS1hNTEyLTc5ZTliY2VmYTgyMiIsImVtYWlsIjoiZW5naW5lZXJpbmdAYWxkcmFzLmNvbSIsImp0aSI6IjNlMDRkMGJmLThjMGQtNDYwMy05YTQzLTQxZDY3N2ZmNWNjYiIsImlhdCI6MTU5NTUyMjA4OSwidG9rZW5fdXNhZ2UiOiJwZXJzb25hbF9hY2Nlc3NfdG9rZW4iLCJ0ZW5hbnRpZCI6IjU5ZDVkNWIxLTdmMjAtNDA3Ny04YjdiLWM4YTA2ODM1OWVkYSIsImF1ZCI6Imh0dHBzOi8vYXBpLmNyeXB0bGV4LmNvbSJ9.tPlke-U6BYzB_YQc6sxWIXA_AZh5JUnJWdj4qluSCca3RVjC0BWnTMqz3g5zbwWm1FBkvWdAVb6mhEw0YDeN9qcGxMksq2wtv1FzD855SDTwRSPTI0xo_zzLzyRBh3sC2MCteruTHGd50pAYG1jgmzawkWnIqJbZtLpfTJF0Szhji9AFWcxoJZha4WaiIeqXsIlNIOtk-cAQPtC6uBlGS1itBY4VIIHwCmNsrgGPtaynxmYvlcojA9gGrgNbCCA73MIKpRKYDlUvxdhgbRPK3807adGc08GMFnj6AH88S1QMu7cCQZHJgaA9qhCD6_BHD_8L1NBYrheSQG2ojsiAKA"
    }'''

    cryptlex_data = '''{
      "productId": "080cc28d-307d-4705-94b4-c9d1f1b5cdc8"
    }'''

    try:
        cryptlex_response = requests.post(cryptlex_url, headers=cryptlex_headers, data=cryptlex_data)
    except Exception as e:
        # send webhook to test
        webhook_url = 'https://webhook.site/68d72c9a-233d-4d18-8373-09e9108c6276'

        response = requests.post(
            webhook_url, data=json.dumps(f'{{"error": {e}}}'),
            headers={'Content-Type': 'application/json'}
        )

    # send webhook to test
    webhook_url = 'https://webhook.site/68d72c9a-233d-4d18-8373-09e9108c6276'

    response = requests.post(
        webhook_url, data=json.dumps(stripe_data),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )

    return stripe_data
