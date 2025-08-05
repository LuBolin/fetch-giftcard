import datetime
from enum import Enum
import requests
import json
import os
import sys

gift_card_file_path = "gift_card_source_accounts.txt"

def print_dict(dictionary, indentation=0):
    for key, value in dictionary.items():
        if value is dict:
            print_dict(value, indentation + 1)
        else:
            print("\t" * indentation + f"{key}: {value}")

class myCleancloudClient:
    GIFT_CARD_SOURCE_ACCOUNTS = []
    headers = {"Content-Type": "application/json"}

    def __init__(self, API_TOKEN, print_gift_card_source_accounts=True):
        self.API_TOKEN = API_TOKEN
        self.API_URL = "https://cleancloudapp.com/api/"

        current_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)

        try:
            with open(os.path.join(current_dir, gift_card_file_path), "r") as file:
                for line in file:
                    account_number = line.strip()
                    self.GIFT_CARD_SOURCE_ACCOUNTS.append(account_number)
            if print_gift_card_source_accounts:
                print(f"Gift card source accounts loaded from {gift_card_file_path}:")
                print("Gift card source accounts:")
                print(self.GIFT_CARD_SOURCE_ACCOUNTS)
            else:
                print(f"Gift card source accounts loaded from {gift_card_file_path}, but not printed.")
        except FileNotFoundError:
            print(f"File {gift_card_file_path} not found")
        
        print()


    def make_request(self, api_suffix, data):
        data["api_token"] = self.API_TOKEN
        response = requests.post(
            f"{self.API_URL}{api_suffix}", json=data, headers=self.headers
        )
        response_body = response.text
        response_json = json.loads(response_body)
        return response_json

    # The customerID is the ID of the customer that is buying the gift card which will charge their saved card.
    def gift_card_buy(self, to_name, to_email, to_tel, 
                      amount, send_date, send_hour, message, notify_by=2):
        api_suffix = "giftCardBuy"
        data = {
            "customerID": None,
            "toName": to_name,
            "toEmail": to_email,
            "toTel": to_tel,
            "sendDate": send_date,
            "sendHour": send_hour,
            "amount": amount,
            "message": message,
            "notifyBy": notify_by
        }

        print(f"Attempting to buy gift card for {to_name} ({to_email}, {to_tel}) ")
        print(f"Amount: ${amount}, Send Date: {send_date}, Send Hour: {send_hour}, Message: {message}, Notify By: {notify_by}")

        response = "Default response before any account is tried"
        for account_number in self.GIFT_CARD_SOURCE_ACCOUNTS:
            print(f"Trying to buy gift card with account {account_number}")
            data["customerID"] = account_number
            # Try to buy gift card with each account number
            response = self.make_request(api_suffix, data)
            # if success, it should contain "Success" in the response
            if "Success" in str(response):
                print(f"Gift card bought successfully with account {account_number}")
                return response
            else:
                print(f"Gift card buy failed with account {account_number}. Response: {response}")
        
        # all failed
        print(f"Gift card buy failed with all accounts.")
        return response


# API_TOKEN = "2d6094e44c3d0bf1ac023e40feb5ed833254ff0e"
# cc_client = myCleancloudClient(API_TOKEN, print_driver_table=False)


# # Gift card must be at least $5
# hour = "22:10"
# amount = 5.0
# response = cc_client.gift_card_buy(
#     to_name="Bolin",
#     to_email="andy518420@gmail.com", 
#     to_tel="85330618",
#     send_date="2025-7-4",
#     send_hour=hour,
#     amount=amount,
#     message=f"Sending ${amount} at {hour} test",
#     notify_by=2 # 1 = SMS, 2 = EMAIL, 3 = DO NOT NOTIFY, 4 = EMAIL & SMS
# )
# print("Gift card response:")
# print_dict(response)



# {
#     "api_token":"API_TOKEN_HERE",
#     "customerID": "414",
#     "toName" : "Eugene",
#     "toEmail" : "Eugene@cleancloud.com",
#     "toTel" : "234234234",
#     "sendDate" : "2022-12-17",
#     "sendHour" : "9",
#     "amount": 5.0,
#     "message": "Gift card time!",
#     "notifyBy": 2
# }