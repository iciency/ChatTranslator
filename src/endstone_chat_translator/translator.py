import requests
import traceback

class Translator:
    def __init__(self, plugin):
        self._plugin = plugin

    def _get_api_keys(self, api_name, player_uuid=None):
        if self._plugin.plugin_config.get("use_player_api_keys", False):
            if player_uuid:
                player_keys = self._plugin.player_api_keys.get(str(player_uuid), {})
                return player_keys.get(api_name)
            return None
        return self._plugin.plugin_config.get("api_keys", {}).get(api_name)

    def translate(self, text, target_lang, source_lang=None, player_uuid=None):
        api_name = self._plugin.plugin_config.get("translation_api", "deepl").lower()
        sender_uuid = player_uuid 

        try:
            if api_name == "deepl":
                return self._translate_deepl(text, target_lang, source_lang, sender_uuid)
            elif api_name == "google_translate":
                return self._translate_google(text, target_lang, source_lang, sender_uuid)
            elif api_name == "papago":
                return self._translate_papago(text, target_lang, source_lang, sender_uuid)
            else:
                self._plugin.logger.warning(f"Unsupported translation_api: '{api_name}'.")
                return None
        except Exception:
            self._plugin.logger.error("An unexpected error occurred during translation.")
            self._plugin.logger.error(traceback.format_exc())
            return None

    def _translate_deepl(self, text, target_lang, source_lang, player_uuid):
        api_key = self._get_api_keys("deepl", player_uuid)
        if not api_key or api_key == "YOUR_DEEPL_API_KEY":
            return None
        api_url = "https://api-free.deepl.com/v2/translate"
        params = { "auth_key": api_key, "text": text, "target_lang": target_lang }
        if source_lang: params["source_lang"] = source_lang
        response = requests.post(api_url, data=params)
        response.raise_for_status()
        return response.json()["translations"][0]["text"]

    def _translate_google(self, text, target_lang, source_lang, player_uuid):
        api_key = self._get_api_keys("google_translate", player_uuid)
        if not api_key or api_key == "YOUR_GOOGLE_TRANSLATE_API_KEY":
            return None
        api_url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
        data = { "q": text, "target": target_lang }
        if source_lang: data["source"] = source_lang
        response = requests.post(api_url, json=data)
        response.raise_for_status()
        return response.json()["data"]["translations"][0]["translatedText"]

    def _translate_papago(self, text, target_lang, source_lang, player_uuid):
        papago_keys = self._get_api_keys("papago", player_uuid)
        if not papago_keys or not papago_keys.get("client_id") or not papago_keys.get("client_secret"):
            return None
        api_url = "https://openapi.naver.com/v1/papago/n2mt"
        headers = {"X-Naver-Client-Id": papago_keys["client_id"], "X-Naver-Client-Secret": papago_keys["client_secret"]}
        data = {"source": source_lang.lower() if source_lang else "auto", "target": target_lang.lower(), "text": text}
        response = requests.post(api_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["message"]["result"]["translatedText"]
