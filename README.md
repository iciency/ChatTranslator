# ChatTranslator for Endstone

ChatTranslator is a real-time, multi-language chat translation plugin for Endstone-based Minecraft servers. It enables players from different countries to communicate seamlessly by automatically translating chat messages based on their individual client language settings.

## Key Features

- **Personalized Real-Time Translation:** Each player receives chat messages translated into their own Minecraft client's language.
- **Automatic Language Detection:** The plugin automatically detects the language of incoming messages, eliminating the need for manual language settings.
- **Multi-API Support:** Supports various translation services, including Google Translate, DeepL, and Papago, easily configurable in `config.toml`.
- **Flexible API Key Management:** The server owner can provide a global API key, or allow each player to register and use their own.
- **Efficient API Usage:** Avoids unnecessary translations between users of the same language and caches translations to minimize API calls when multiple players need the same translation.

## Installation

1.  Download the latest plugin release (`.whl` file) from the [Releases](https://github.com/your-repo/ChatTranslator/releases) page.
2.  Place the downloaded file into your server's `plugins` directory.
3.  Start or reload your server.
4.  The `plugins/ChatTranslator/config.toml` file will be generated automatically on the first load.

## Configuration (`config.toml`)

```toml
# Choose the translation API to use (e.g., "google_translate", "deepl", "papago").
translation_api = "google_translate"

# Set to true to allow players to use their own API keys.
# If true, each player must register their key using the /translator setkey command.
use_player_api_keys = false

# Server-wide API keys.
# These are only used if use_player_api_keys is set to false.
[api_keys]
deepl = "YOUR_DEEPL_API_KEY"
google_translate = "YOUR_GOOGLE_TRANSLATE_API_KEY"

[api_keys.papago]
client_id = "YOUR_PAPAGO_CLIENT_ID"
client_secret = "YOUR_PAPAGO_CLIENT_SECRET"
```

## Commands

-   `/translator <on|off>` (or `/trans <on|off>`)
    -   Toggles personal chat translation on or off for yourself.
    -   Permission: `chattranslator.command.toggle`

-   `/translator setkey <api_name> <key...>`
    -   Registers your personal API key when `use_player_api_keys` is enabled on the server.
    -   Permission: `chattranslator.command.setkey`
    -   **Examples:**
        -   `/translator setkey google_translate YOUR_API_KEY`
        -   `/translator setkey papago YOUR_CLIENT_ID YOUR_CLIENT_SECRET`

## Contributing

Bug reports and feature requests are welcome! Please open an issue on GitHub. Pull requests are also greatly appreciated.
