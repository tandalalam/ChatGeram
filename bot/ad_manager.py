import logging
import os
import requests
import json


class AdManager:
    ad_manager = None

    @staticmethod
    def get_ad_manager():
        if AdManager.ad_manager is None:
            AdManager.ad_manager = AdManager()
        return AdManager.ad_manager

    def __init__(self):
        ad_service_url = os.environ.get('AD_SERVICE_URL', '')
        self.ad_generator_url = ad_service_url

    def get_ad(self, conversations):
        payload = json.dumps({
            "conversation": conversations
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", self.ad_generator_url + '/api/get_ad', headers=headers, data=payload)
        try:
            return response.json()['ad']
        except KeyError:
            logging.info('Could not get ad!')
        except requests.exceptions.JSONDecodeError:
            logging.info(response.text)
