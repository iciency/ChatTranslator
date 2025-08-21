import os
import toml
import json
from endstone.plugin import Plugin
from endstone.event import event_handler, PlayerChatEvent, PlayerJoinEvent, PlayerQuitEvent
from endstone.command import Command, CommandSender
from .commands import preloaded_commands, preloaded_handlers
from .translator import Translator

class ChatTranslatorPlugin(Plugin):
    api_version = "0.10"
    commands = preloaded_commands

    def __init__(self):
        super().__init__()
        self.handlers = preloaded_handlers
        self.translation_enabled = {}
        self.player_language_settings = {}
        self.player_api_keys = {}
        self.translator = None
        self.plugin_config = {}

    def on_load(self):
        self.logger.info("ChatTranslatorPlugin has been loaded.")
        self.load_config()
        self.load_player_api_keys()
        self.translator = Translator(self)

    def on_enable(self):
        self.logger.info("ChatTranslatorPlugin has been enabled.")
        self.register_events(self)
        for player in self.server.online_players:
            self._initialize_player_settings(player)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name in self.handlers:
            handler = self.handlers[command.name]
            return handler(self, sender, args)
        return False

    def load_config(self):
        config_path = os.path.join(self.data_folder, "config.toml")
        if not os.path.exists(config_path):
            os.makedirs(self.data_folder, exist_ok=True)
            default_config = {
                "translation_api": "google_translate",
                "use_player_api_keys": False,
                "api_keys": {
                    "deepl": "YOUR_DEEPL_API_KEY",
                    "google_translate": "YOUR_GOOGLE_TRANSLATE_API_KEY",
                    "papago": {"client_id": "YOUR_PAPAGO_CLIENT_ID", "client_secret": "YOUR_PAPAGO_CLIENT_SECRET"}
                }
            }
            with open(config_path, 'w', encoding='utf-8') as f: toml.dump(default_config, f)
            self.plugin_config = default_config
        else:
            with open(config_path, 'r', encoding='utf-8') as f: self.plugin_config = toml.load(f)

    def load_player_api_keys(self):
        keys_path = os.path.join(self.data_folder, "player_keys.json")
        if os.path.exists(keys_path):
            with open(keys_path, 'r', encoding='utf-8') as f: self.player_api_keys = json.load(f)

    def save_player_api_key(self, player_uuid, api_name, keys):
        if player_uuid not in self.player_api_keys: self.player_api_keys[player_uuid] = {}
        if api_name == "papago":
            self.player_api_keys[player_uuid][api_name] = {"client_id": keys[0], "client_secret": keys[1]}
        else:
            self.player_api_keys[player_uuid][api_name] = keys[0]
        keys_path = os.path.join(self.data_folder, "player_keys.json")
        with open(keys_path, 'w', encoding='utf-8') as f: json.dump(self.player_api_keys, f, indent=4)

    def _initialize_player_settings(self, player):
        player_uuid = str(player.unique_id)
        is_enabled = self.plugin_config.get("translation_enabled_by_default", True)
        self.translation_enabled[player_uuid] = is_enabled
        player_locale = player.locale.split('_')[0].upper()
        self.player_language_settings[player_uuid] = {"target": player_locale}

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        self._initialize_player_settings(event.player)

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent):
        player_uuid = str(event.player.unique_id)
        if player_uuid in self.translation_enabled: del self.translation_enabled[player_uuid]
        if player_uuid in self.player_language_settings: del self.player_language_settings[player_uuid]

    @event_handler
    def on_player_chat(self, event: PlayerChatEvent):
        self.logger.info(f"!!!!!!!!!! CHAT EVENT TRIGGERED BY {event.player.name} !!!!!!!!!!")
        if event.is_cancelled:
            self.logger.info("-> Event was already cancelled before ChatTranslator.")
            return
        
        event.cancel()
        
        sender = event.player
        sender_uuid = str(sender.unique_id)
        original_message = event.message

        if sender_uuid not in self.player_language_settings:
            self._initialize_player_settings(sender)
        
        translated_messages = {}

        for recipient in self.server.online_players:
            recipient_uuid = str(recipient.unique_id)
            if not self.translation_enabled.get(recipient_uuid, False):
                recipient.send_message(f"<{sender.name}> {original_message}")
                continue

            if recipient_uuid not in self.player_language_settings:
                self._initialize_player_settings(recipient)
            
            target_lang = self.player_language_settings.get(recipient_uuid, {}).get("target")
            sender_lang = self.player_language_settings.get(sender_uuid, {}).get("target")

            if not target_lang or sender_lang == target_lang:
                recipient.send_message(f"<{sender.name}> {original_message}")
                continue

            if target_lang in translated_messages:
                if translated_messages[target_lang]: # Check if translation was successful
                    recipient.send_message(f"§d<{sender.name}>§f {translated_messages[target_lang]}")
                else: # Send original if previous translation for this language failed
                    recipient.send_message(f"<{sender.name}> {original_message}")
                continue

            # Let the API auto-detect the source language by passing source_lang=None
            translated_message = self.translator.translate(original_message, target_lang, source_lang=None, player_uuid=sender_uuid)
            
            translated_messages[target_lang] = translated_message # Cache the result (even if it's None)
            
            if translated_message:
                recipient.send_message(f"§d<{sender.name}>§f {translated_message}")
            else:
                recipient.send_message(f"<{sender.name}> {original_message}")
