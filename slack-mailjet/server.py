import os
import requests
from flask import Flask, request, jsonify
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Mailjet API credentials from environment variables
MAILJET_API_KEY = os.getenv('MAILJET_API_KEY')
MAILJET_API_SECRET = os.getenv('MAILJET_API_SECRET')

# Function to query Mailjet API
def query_mailjet(email):
    mailjet_url = 'https://api.mailjet.com/v3/REST/message'
    params = {'To': email, 'Limit': 10}
    response = requests.get(mailjet_url, auth=HTTPBasicAuth(MAILJET_API_KEY, MAILJET_API_SECRET), params=params)
    if response.status_code == 200:
        return response.json().get('Data', [])
    return None

# Slack slash command route
@app.route('/slack/mailjet', methods=['POST'])
def slack_mailjet():
    email = request.form.get('text')  # Email passed by the user in Slack
    if not email:
        return jsonify({'text': 'Please provide an email address.'}), 400

    results = query_mailjet(email)
    if results:
        message = f"Emails sent to {email}:\n"
        for item in results:
            message += f"- ID: {item['ID']}, Status: {item['Status']}, SentAt: {item['SentAt']}\n"
    else:
        message = f"No emails found for {email}."

    return jsonify({'text': message}), 200

if __name__ == '__main__':
    app.run()
