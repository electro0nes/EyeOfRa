import requests
import json
from datetime import datetime

EVENT_COLORS = {
    'new_program': 0x00ff66,
    'removed_program': 0xff3333,
    'new_inscope': 0x33ccff,
    'removed_inscope': 0xff9966,
    'new_out_of_scope': 0xcccccc,
    'removed_out_of_scope': 0x999999,
    'changed_scope': 0xffcc00,
    'new_type': 0x9966ff
}

def notify_event(event_type, platform, name, url, data, webhook_url):
    embed = {
        "title": f"[{platform.upper()}] {event_type.replace('_', ' ').title()}",
        "description": f"**[{name}]({url})**",
        "color": EVENT_COLORS.get(event_type, 0x00ffcc),
        "fields": [],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "Eagle • github.com/electro0nes"
        }
    }

    if event_type == 'new_program':
        scopes = data.get('targets', {}).get('in_scope', [])
        value = ""
        for scope in scopes:
            ident = scope.get('asset_identifier', scope.get('name', 'N/A'))
            typ = scope.get('asset_type', scope.get('type', 'N/A'))
            severity = scope.get('max_severity', 'N/A')
            value += f"• **`{ident}`** ({typ}) → 🔥 **{severity}**\n"
        embed['fields'].append({
            "name": "🎯 In Scope Assets",
            "value": value or 'N/A',
            "inline": False
        })

    elif event_type in ['new_inscope', 'removed_inscope']:
        embed['fields'].append({
            "name": f"🎯 {event_type.replace('_', ' ').title()}",
            "value": f"**`{data.get('asset_identifier', data.get('name', 'N/A'))}`** "
                     f"({data.get('asset_type', data.get('type', 'N/A'))}) → **{data.get('max_severity', 'N/A')}**",
            "inline": False
        })

    elif event_type in ['new_out_of_scope', 'removed_out_of_scope']:
        embed['fields'].append({
            "name": f"🚫 {event_type.replace('_', ' ').title()}",
            "value": f"**`{data.get('identifier', data.get('name', 'N/A'))}`**",
            "inline": False
        })

    elif event_type == 'changed_scope':
        embed['fields'].append({
            "name": "🔁 Scope Changes",
            "value": data.get('change_details', 'No details available.'),
            "inline": False
        })

    elif event_type == 'removed_program':
        embed['description'] += "\n\n❌ **This program has been removed.**"

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
                details += f"- `{key}`: ~~{old_val}~~ → **{new_val}**\n"
        if "dictionary_item_added" in changes_json:
            added = "\n".join(changes_json["dictionary_item_added"])
            details += f"\n➕ **Added:**\n{added}\n"
        if "dictionary_item_removed" in changes_json:
            removed = "\n".join(changes_json["dictionary_item_removed"])
            details += f"\n➖ **Removed:**\n{removed}\n"

        embed['fields'].append({
            "name": "🔧 Program Metadata Changes",
            "value": details or "Changes detected.",
            "inline": False
        })

    try:
        requests.post(webhook_url, json={"embeds": [embed]})
    except Exception as e:
        print(f"[!] Failed to send notification: {e}")