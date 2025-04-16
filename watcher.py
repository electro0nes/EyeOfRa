# watcher.py
import requests
from db_utils import get_program, insert_or_update_program, get_all_handles, delete_program
from deepdiff import DeepDiff
from notifier import notify_event
import json
from deepdiff import DeepDiff
from deepdiff.model import SetOrdered


def fetch_and_process(platform, url, discord_webhook=None):
    print(f"[+] Fetching {platform} data...")
    response = requests.get(url)
    programs = response.json()

    existing_handles = set(get_all_handles(platform))
    current_handles = set()

    for program in programs:
        handle = program['handle']
        current_handles.add(handle)
        name = program['name']
        program_url = program.get('url', 'N/A')
        old_data = get_program(platform, handle)

        if not old_data:
            if discord_webhook:
                notify_event('new_program', platform, name, program_url, program, discord_webhook)
            insert_or_update_program(platform, handle, name, program)
            continue

        diff = DeepDiff(old_data, program, ignore_order=True)
        if diff:
            detect_changses(platform, name, program_url, old_data, program, diff, discord_webhook)

        insert_or_update_program(platform, handle, name, program)

    db_handles = get_all_handles(platform)
    removed = set(db_handles) - current_handles
    for removed_handle in removed:
        old = get_program(platform, removed_handle)
        if old and discord_webhook:
            notify_event('removed_program', platform, old['name'], old.get('url', 'N/A'), old, discord_webhook)
        delete_program(platform, removed_handle)


def serialize_diff(diff):
    if isinstance(diff, SetOrdered):
        return list(diff)  
    elif isinstance(diff, set):
        return list(diff)  
    elif isinstance(diff, dict):
        return {k: serialize_diff(v) for k, v in diff.items()}
    elif isinstance(diff, list):
        return [serialize_diff(v) for v in diff]
    else:
        return diff

def detect_changses(platform, name, url, old, new, diff, webhook):
    alerts = []

    # Check for open <-> paused
    old_state = old.get('submission_state')
    new_state = new.get('submission_state')
    if old_state != new_state:
        if {old_state, new_state} == {"open", "paused"}:
            alerts.append(f"Program state changed: `{old_state}` → `{new_state}`")

    # BBP <-> VDP
    old_bbp = old.get('allows_bounty_splitting')
    new_bbp = new.get('allows_bounty_splitting')
    if old_bbp != new_bbp:
        if old_bbp:
            alerts.append("Changed from **BBP** to **VDP** ")
        else:
            alerts.append("Changed from **VDP** to **BBP** ")

    # Scope change detection
    old_targets = old.get('targets', {})
    new_targets = new.get('targets', {})

    old_scopes = {s['asset_identifier']: s for s in old_targets.get('in_scope', []) if s}
    new_scopes = {s['asset_identifier']: s for s in new_targets.get('in_scope', []) if s}

    for identifier in new_scopes:
        if identifier not in old_scopes:
            alerts.append(f"New Scope: `{identifier}` → **{new_scopes[identifier].get('max_severity', 'N/A')}**")
        elif identifier in old_scopes:
            old_sev = old_scopes[identifier].get('max_severity')
            new_sev = new_scopes[identifier].get('max_severity')
            if old_sev != new_sev:
                alerts.append(f"Severity Changed: `{identifier}` → `{old_sev}` → `{new_sev}`")

    for identifier in old_scopes:
        if identifier not in new_scopes:
            alerts.append(f"Removed Scope: `{identifier}` → **{old_scopes[identifier].get('max_severity', 'N/A')}**")

    if alerts:
        notify_event('changed_scope', platform, name, url, {
            "change_details": "\n".join(alerts)
        }, webhook)