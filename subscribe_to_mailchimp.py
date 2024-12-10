"""
A Small Tool btw for subscribing Strapi user/info to mailchimp
"""
import requests
import json

# Configuration, Fill it on your need
STRAPI_ENDPOINT = ""
STRAPI_API_KEY = ""
MAILCHIMP_API_KEY = ""
MAILCHIMP_AUDIENCE_ID = ""
# Use "us21" for closest data center in Australia, Change it on your need v
MAILCHIMP_BASE_URL = "https://us21.api.mailchimp.com/3.0"
# Change/add more tags on ur need
MAILCHIMP_TAGS = ["Roseneath Holiday Park"]


# Get data from Strapi with round queries to retrieve all data
def get_strapi_data():
    headers = {
        "Authorization": f"Bearer {STRAPI_API_KEY}",
    }
    page = 1
    page_size = 100
    all_data = []

    while True:
        url = f"{STRAPI_ENDPOINT}?pagination[page]={page}&pagination[pageSize]={page_size}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve data from Strapi: {response.status_code}")
            break

        data = response.json().get("data", [])
        if not data:
            break

        all_data.extend(data)
        print(f"Fetched page {page} with {len(data)} records.")
        page += 1

    return all_data


# Subscribe to Mailchimp
def subscribe_to_mailchimp(email, first_name, last_name, address, phone):
    url = f"{MAILCHIMP_BASE_URL}/lists/{MAILCHIMP_AUDIENCE_ID}/members"
    headers = {
        "Authorization": f"Bearer {MAILCHIMP_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email_address": email,
        "status": "subscribed",
        "merge_fields": {
            "FNAME": first_name,
            "LNAME": last_name,
            "ADDRESS": address,
            "PHONE": phone,
        },
        "tags": MAILCHIMP_TAGS
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code in [200, 201]:
        print(f"Successfully subscribed {email} to Mailchimp.")
    else:
        print(f"Failed to subscribe {email}: {response.status_code} - {response.text}")


# Main function / Entry point
def main():
    strapi_data = get_strapi_data()
    for entry in strapi_data:
        # Add a ["attribute"] after entry for strapi 4.x
        # Change the field name as your need in the round bracket
        email = entry.get("Email")
        name = entry.get("Name", "")
        address = entry.get("Address", "")
        phone = entry.get("Phone", "")

        if email and name:
            # Split Name1 into First and Last Name
            name_parts = name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            # Subscribe to Mailchimp
            subscribe_to_mailchimp(email, first_name, last_name, address, phone)
        else:
            print(f"Skipping entry due to missing data: {entry}")


if __name__ == "__main__":
    main()
