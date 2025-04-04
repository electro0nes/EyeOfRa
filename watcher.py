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
            detect_changes(platform, name, program_url, old_data, program, diff, discord_webhook)

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

def detect_changes(platform, name, url, old, new, diff, webhook):
    old_targets = old.get('targets', {}) if old else {}
    new_targets = new.get('targets', {}) if new else {}

    old_scopes = {s['asset_identifier']: s for s in old_targets.get('in_scope', []) if s}
    new_scopes = {s['asset_identifier']: s for s in new_targets.get('in_scope', []) if s}

    added_scopes = []
    removed_scopes = []
    changed_scopes = {}

    for identifier in new_scopes:
        if identifier not in old_scopes:
            added_scopes.append(new_scopes[identifier])
    
    for identifier in old_scopes:
        if identifier not in new_scopes:
            removed_scopes.append(old_scopes[identifier])
        elif identifier in new_scopes:
            scope_diff = DeepDiff(old_scopes[identifier], new_scopes[identifier], ignore_order=True)
            if scope_diff:
                changed_scopes[identifier] = scope_diff

    if added_scopes or removed_scopes or changed_scopes:
        change_details = []
        
        for scope in added_scopes:
            change_details.append(f"New Inscope: `{scope['asset_identifier']}` ({scope.get('asset_type', 'N/A')}) → **{scope.get('max_severity', 'N/A')}**")
        
        for scope in removed_scopes:
            change_details.append(f"Removed Inscope: `{scope['asset_identifier']}` ({scope.get('asset_type', 'N/A')}) → **{scope.get('max_severity', 'N/A')}**")
        
        for identifier, diff in changed_scopes.items():
            change_details.append(f"Changed Inscope ({identifier}): ```diff\n{json.dumps(diff, indent=2)}```")

        if change_details:
            notify_event('changed_scope', platform, name, url, {
                "change_details": "\n".join(change_details)
            }, webhook)

    old_out = set(x['asset_identifier'] for x in old_targets.get('out_of_scope', []) if x)
    new_out = set(x['asset_identifier'] for x in new_targets.get('out_of_scope', []) if x)

    out_of_scope_details = []
    for added in new_out - old_out:
        out_of_scope_details.append(f"New Out of Scope: `{added}`")
    for removed in old_out - new_out:
        out_of_scope_details.append(f"Removed Out of Scope: `{removed}`")
    
    if out_of_scope_details:
        notify_event('changed_scope', platform, name, url, {
            "change_details": "\n".join(out_of_scope_details)
        }, webhook)

    general_diff = DeepDiff(
        old, new, ignore_order=True, 
        exclude_paths=["root['targets']", "root['response_efficiency_percentage']"]
    )
    
    if general_diff and webhook:
        notify_event('new_type', platform, name, url, {"changes": json.dumps(general_diff, indent=2)}, webhook)
