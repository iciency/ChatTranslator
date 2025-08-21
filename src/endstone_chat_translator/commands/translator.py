from endstone.command import CommandSender

command = {
    "translator": {
        "description": "Manages your personal chat translation settings.",
        "usages": [
            "/translator <on|off>",
            "/translator setkey <deepl|google_translate|papago> <key:string>"
        ],
        "aliases": ["trans"],
        "permissions": ["chattranslator.command.toggle", "chattranslator.command.setkey"]
    }
}

def handler(plugin, sender: CommandSender, args: list[str]):
    if not hasattr(sender, 'unique_id'):
        sender.send_message("§cThis command can only be run by a player.")
        return True

    if not args:
        sender.send_message("§cUsage:")
        for usage in command["translator"]["usages"]:
            sender.send_message(f"§c- {usage}")
        return True

    sub_command = args[0].lower()
    player_uuid = str(sender.unique_id)

    if sub_command in ["on", "off"]:
        if not sender.has_permission("chattranslator.command.toggle"):
            sender.send_message("§cYou do not have permission to use this subcommand.")
            return True
        if sub_command == "on":
            # Check for API key if player-specific keys are enabled
            if plugin.plugin_config.get("use_player_api_keys", False):
                api_name = plugin.plugin_config.get("translation_api", "deepl").lower()
                player_keys = plugin.player_api_keys.get(player_uuid, {})
                if not player_keys.get(api_name):
                    sender.send_message(f"§cWarning: Translation is enabled, but you have not set an API key for '{api_name}'.")
                    sender.send_message("§cUse '/translator setkey' to set your key.")
            
            plugin.translation_enabled[player_uuid] = True
            sender.send_message("§aPersonal translation has been enabled.")
        else:
            plugin.translation_enabled[player_uuid] = False
            sender.send_message("§aPersonal translation has been disabled.")
    elif sub_command == "setkey":
        if not plugin.plugin_config.get("use_player_api_keys", False):
            sender.send_message("§cThe server is not configured to allow player-specific API keys.")
            return True
        if not sender.has_permission("chattranslator.command.setkey"):
            sender.send_message("§cYou do not have permission to use this subcommand.")
            return True
        if len(args) < 3:
            sender.send_message(f"§cUsage: {command['translator']['usages'][1]}")
            sender.send_message("§cExample: /translator setkey deepl YOUR_API_KEY")
            sender.send_message("§cExample: /translator setkey papago YOUR_CLIENT_ID YOUR_CLIENT_SECRET")
            return True
        
        api_name = args[1].lower()
        keys = args[2:]
        plugin.save_player_api_key(player_uuid, api_name, keys)
        sender.send_message(f"§aYour API key for {api_name} has been set.")
    else:
        sender.send_message("§cInvalid subcommand.")

    return True
