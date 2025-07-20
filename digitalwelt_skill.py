import os
import json
import requests
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

TWITCH_CHANNEL = "digitalwelt_original"
TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_ACCESS_TOKEN = os.environ.get("TWITCH_ACCESS_TOKEN")


def check_twitch_online():
    if not TWITCH_CLIENT_ID or not TWITCH_ACCESS_TOKEN:
        return False
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
    }
    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_CHANNEL}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return len(data.get("data", [])) > 0
    except Exception:
        return False


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech = "Willkommen bei Digitalwelt Original. Sage 'Status', um zu erfahren, ob der Kanal live ist."
        return handler_input.response_builder.speak(speech).set_should_end_session(False).response


class StatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("StatusIntent")(handler_input)

    def handle(self, handler_input):
        online = check_twitch_online()
        if online:
            speech = "Digitalwelt Original ist gerade live auf Twitch!"
        else:
            speech = "Der Kanal ist momentan offline."
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech = "Sage 'Status', um den aktuellen Livestatus zu erfahren."
        return handler_input.response_builder.speak(speech).ask(speech).response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speech = "Tschüss!"
        return handler_input.response_builder.speak(speech).response


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StatusIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())

lambda_handler = sb.lambda_handler()
