import logging

from ad_creators_utils.ad_creator import AdCreator
from ad_creators_utils.content_extractor import ContentExtractor


class AdManager:
    ad_manager = None

    @staticmethod
    def get_ad_manager(**kwargs):
        if AdManager.ad_manager is None:
            AdManager.ad_manager = AdManager(**kwargs)
        return AdManager.ad_manager

    def __init__(self, ad_creator=None, content_extractor=None, openai_client=None):
        if ad_creator is None:
            if openai_client is None:
                raise ValueError("You must provide either openai_client or the ad_creator")
            ad_creator = AdCreator(openai_client=openai_client,
                                   config={})
        self.ad_creator = ad_creator

        if content_extractor is None:
            if openai_client is None:
                raise ValueError("You must provide either openai_client or the ad_creator")
            content_extractor = ContentExtractor(openai_client=openai_client,
                                                 config={})
        self.content_extractor = content_extractor

        self.ad_list = {}

    def get_ad(self, chat_id):
        return_ad = self.ad_list.get(chat_id, None)
        self.ad_list[chat_id] = None
        return return_ad

    async def __call__(self, conversation, chat_id):
        advertisement_content = await self.content_extractor.retrieve_advertisement(conversation)
        if advertisement_content is None:
            logging.info(
                f'There was not any advertisement for this conversation. ({chat_id})'
            )
        ad_message = await self.ad_creator.create_ad(chat_id, advertisement_content)
        self.ad_list[chat_id] = ad_message
