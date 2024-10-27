import logging

import pandas as pd
import numpy as np


class ContentExtractor:
    def __init__(self, openai_client, config):
        self.openai_client = openai_client

        ad_details_embedding = pd.read_csv('bot/ad_creators_utils/files/ads_detail_embedding.csv')
        detail_columns = ['url', 'name', 'properties', 'call_to_action']
        self.ads_detail = ad_details_embedding[detail_columns]
        self.embeddings = ad_details_embedding.drop(columns=detail_columns).to_numpy()

        self.threshold = config.get('threshold', 0.75)
        self.keyword_extractor_model = config.get('keyword_extractor_model', 'gpt-3.5-turbo-0125')
        self.embedding_model = config.get('embedding_model', 'text-embedding-ada-002')

        self.client_instruction = open('bot/ad_creators_utils/files/keyword_instruction.txt').read()

    async def retrieve_advertisement(self, history):
        messages = [
            {
                "role": "system",
                "content": self.client_instruction
            },
            {
                "role": "user",
                "content": str(history)
            }
        ]

        data = {
            "model": self.keyword_extractor_model,
            "messages": messages
        }

        response = await self.openai_client.chat.completions.create(
            **data
        )

        logging.info(f'{response.choices[0].message.content} is a list of content that user is interested in.')

        query_embedding = await self.openai_client.embeddings.create(input=response.choices[0].message.content,
                                                                     model='text-embedding-ada-002')
        query_embedding = np.array(query_embedding.data[0].embedding)

        similarities = np.matmul(self.embeddings, query_embedding)

        logging.info(f'{similarities}')

        best_option = similarities.argmax()

        return self.ads_detail.loc[best_option] if similarities[best_option] > self.threshold else None
