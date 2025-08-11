import requests
from utils.get_fcm_token import get_access_token

def send_fcm_v1_message(token, title, body, data=None):
    project_id = "storezee-b5f0e"  # from Firebase project settings
    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8",
    }

    payload = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": data or {}
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# notification = send_fcm_v1_message(token='eGYqgJ6EQ4uodkhLkqFdx5:APA91bHCd3X0eAnenCK-6EtLPfIFAjxixIG6-VmbJZvS3w-y1kQX_M3a9xaJ-I52lvTjws-FxKYvKwXQBcYxqvEPiPabADqduUglkZCY4TwLcvy95hQdff0',
#                                    title='Booking Confirmed',
#                                    body='Your luggage pickup is scheduled.',
#                                    data={"booking_id": "123456"})

# print(notification)