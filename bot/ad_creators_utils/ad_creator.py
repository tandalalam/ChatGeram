import json
import logging
from typing import Dict


class AdCreator:
    @staticmethod
    def telegram_style(conversational_ad, call_to_action, url):
        message_text = f"""<blockquote>{conversational_ad}.
<a href='{url}'>{call_to_action}</a>
</blockquote>"""
        return message_text

    @staticmethod
    def create_ad_spec() -> Dict:
        create_ad_desc = {
            "name": "create_ad",
            "description": "Put the advertisement in proper format",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversational_ad": {
                        "type": "string",
                        "description": "The advertising content that is created as a part of the conversation."
                    },
                    "call_to_action": {
                        "type": "string",
                        "description": "An encouraging phrase to click on the advertising link."
                    }
                },
                "additionalProperties": False,
                "required": [
                    "conversational_ad",
                    "call_to_action"
                ]
            }
        }
        return create_ad_desc

    def __init__(self, openai_client, config):
        self.openai_client = openai_client

        self.generator_instructions = open('ad_creators_utils/files/generator_instruction.txt').read()
        self.generator_assistant_prompt = open('ad_creators_utils/files/generator_assistant_prompt.txt').read()

        self.temperature = config.get('temperature', 0.5)
        self.generator_model = config.get('generator_model', 'gpt-3.5-turbo-0125')

    async def create_ad(self, conversation, ad_detail):
        name, details, call_to_action, url = ad_detail['name'], ad_detail['properties'], ad_detail['call_to_action'], \
            ad_detail['url']
        data = {
            "model": "gpt-3.5-turbo-0125",
            "messages": [
                {
                    "role": "system",
                    "content": self.generator_instructions
                },
                {
                    "role": "assistant",
                    "content": self.generator_assistant_prompt.format(name=name,
                                                                      details=details,
                                                                      call_to_action=call_to_action)
                },
                {
                    "role": "user",
                    "content": str(conversation)
                }
            ],
            "temperature": 0.5,
            "functions": [AdCreator.create_ad_spec()],
            "function_call": {"name": "create_ad"}
        }

        message_resp = await self.openai_client.chat.completions.create(
            **data
        )
        message_resp = message_resp.choices[0].message

        if dict(message_resp).get('function_call'):
            function_args = json.loads(message_resp.function_call.arguments)
            telegram_formatted_string = AdCreator.telegram_style(conversational_ad=function_args['conversational_ad'],
                                                                 call_to_action=function_args['call_to_action'],
                                                                 url=url)
            return telegram_formatted_string
        else:
            return None

#
#     async def execute(self, conversational_ad, call_to_action, ) -> Dict:
#         message_text = """>Here is a test for qouted message in telegram\. [And here is a test for linking\.](https://openai.com)
# """
#         await update.message.reply_text(
#             message_text, parse_mode="MarkdownV2"
#         )
