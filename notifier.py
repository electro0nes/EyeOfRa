# notifier.py
import requests
import json

def notify_event(event_type, platform, name, url, data, webhook_url):
    embed = {
        "title": f"[{platform.upper()}] {event_type.replace('_', ' ').title()}",
        "description": f"[{name}]({url})",
        "color": 0x00ffcc,
        "fields": []
    }

    if event_type == 'new_program':
        scopes = data.get('targets', {}).get('in_scope', [])
        value = ""
        for scope in scopes:
            value += f"• `{scope.get('asset_identifier', scope.get('name', 'N/A'))}` ({scope.get('asset_type', scope.get('type', 'N/A'))}) → **{scope.get('max_severity', 'N/A')}**\n"
        embed['fields'].append({"name": "In Scope Assets", "value": value or 'N/A', "inline": False})

    elif event_type in ['new_inscope', 'removed_inscope']:
        embed['fields'].append({
            "name": f"{event_type.replace('_', ' ').title()} Scope",
            "value": f"`{data.get('asset_identifier', data.get('name', 'N/A'))}` ({data.get('asset_type', data.get('type', 'N/A'))}) → **{data.get('max_severity', 'N/A')}**",
            "inline": False
        })

    elif event_type in ['new_out_of_scope', 'removed_out_of_scope']:
        embed['fields'].append({
            "name": f"{event_type.replace('_', ' ').title()}",
            "value": f"`{data.get('identifier', data.get('name', 'N/A'))}`",
            "inline": False
        })

    elif event_type == 'changed_scope':
        embed['fields'].append({
            "name": "Scope Changes",
            "value": data['change_details'],  
            "inline": False
        })

    elif event_type == 'removed_program':
        embed['description'] += "\n🚫 **Program Removed**"

    elif event_type == 'new_type':
        changes = data.get("changes", "{}")
        try:
            changes_json = json.loads(changes)
        except Exception:
            changes_json = {}

        details = ""
        if "values_changed" in changes_json:
            for key, change in changes_json["values_changed"].items():
                old_val = change.get("old_value")
                new_val = change.get("new_value")
                details += f"{key}: {old_val} -> {new_val}\n"
        if "dictionary_item_added" in changes_json:
            added = ", ".join(changes_json["dictionary_item_added"])
            details += f"Added: {added}\n"
        if "dictionary_item_removed" in changes_json:
            removed = ", ".join(changes_json["dictionary_item_removed"])
            details += f"Removed: {removed}\n"

        if not details:
            details = changes

        embed['fields'].append({
            "name": "Program Meta Updated",
            "value": f"```diff\n{details}```",
            "inline": False
        })

    requests.post(webhook_url, json={"embeds": [embed]})
