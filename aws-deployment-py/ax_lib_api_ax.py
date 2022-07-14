import json
import requests
import time
import ax_lib_general


# --Description-- #
# Automox API Helper library.  Contains shared API call functions.
# --End Description-- #


# --Helper Methods-- #
# Main API Call Function
def ax_call_api(action, api_url, ax_api_key, data=None, params=None, try_count=0, max_retries=2):
    retry_statuses = [429, 500, 502, 503, 504]
    retry_wait_timer = 5
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + ax_api_key}

    # Make the API Call
    response = requests.request(action, api_url, params=params, headers=headers, data=json.dumps(data))

    # Check for an error to retry, re-auth, or fail
    if response.status_code in retry_statuses:
        try_count = try_count + 1
        if try_count <= max_retries:
            time.sleep(retry_wait_timer)
            return ax_call_api(action=action, api_url=api_url, ax_api_key=ax_api_key, data=data, params=params,
                               try_count=try_count, max_retries=max_retries)
        else:
            if not response:
                print(response.json())
            response.raise_for_status()
    else:
        if not response:
                print(response.json())
        response.raise_for_status()

    # Check for valid response and catch if blank or unexpected
    api_response_package = {}
    api_response_package['statusCode'] = response.status_code
    try:
        api_response_package['data'] = response.json()
    except ValueError:
        if response.text == '':
            api_response_package['data'] = None
        else:
            ax_lib_general.ax_exit_error(501, 'The server returned an unexpected server response.')
    return api_response_package


# Get groups list
def ax_group_list_get(ax_environment):
    url = ax_environment['automox-api-url-base'] + "/servergroups"
    querystring = {"o":ax_environment['automox-org-id']}
    action = "GET"
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring)


# Get specific group details
def ax_group_get(ax_environment, ax_group_id):
    url = ax_environment['automox-api-url-base'] + "/servergroups" + "/" + str(ax_group_id)
    querystring = {"o":ax_environment['automox-org-id']}
    action = "GET"
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring)


# Create group
def ax_group_create(ax_environment, name, refresh_interval, parent_server_group_id, ui_color=None, notes=None, 
                    enable_os_auto_update=None, enable_wsus=None, wsus_server=None, policies=None):
    url = ax_environment['automox-api-url-base'] + "/servergroups"
    querystring = {"o":ax_environment['automox-org-id']}
    action = "POST"
    # Set up the create package for the API
    update_data = {}
    update_data['name'] = name
    update_data['refresh_interval'] = refresh_interval
    update_data['parent_server_group_id'] = parent_server_group_id
    if ui_color:
        update_data['ui_color'] = ui_color
    if notes:
        update_data['notes'] = notes
    if enable_os_auto_update:
        update_data['enable_os_auto_update'] = enable_os_auto_update
    if enable_wsus:
        update_data['enable_wsus'] = enable_wsus
    if wsus_server:
        update_data['wsus_server'] = wsus_server
    if policies:
        update_data['policies'] = policies
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring, data=update_data)


# Delete Group
def ax_group_delete(ax_environment, ax_group_id):
    url = ax_environment['automox-api-url-base'] + "/servergroups" + "/" + str(ax_group_id)
    querystring = {"o":ax_environment['automox-org-id']}
    action = "DELETE"
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring)


# Get Devices list(with details)
def ax_device_list_get(ax_environment, ax_environment_name=None):
    url = ax_environment['automox-api-url-base'] + "/servers"
    querystring = {"o":ax_environment['automox-org-id']}
    action = "GET"
    # Call the API
    ax_devices_response = ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring)
    # Filter out the correct environment (if provided)
    ax_devices_filtered = []
    if ax_environment_name:
        for ax_device in ax_devices_response['data']:
            for tag in ax_device['tags']:
                if tag.lower() == ax_environment_name.lower():
                    ax_devices_filtered.append(ax_device)
                    break
    else:
        for ax_device in ax_devices_response['data']:
            ax_devices_filtered.append(ax_device)
    return ax_devices_filtered


# Get specific device details
def ax_device_get(ax_environment, ax_device_id):
    url = ax_environment['automox-api-url-base'] + "/servers" + "/" + str(ax_device_id)
    querystring = {"o":ax_environment['automox-org-id']}
    action = "GET"
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring)


# Modify device
def ax_device_put(ax_environment, ax_device_id, server_group_id=None, ip_addrs=None, exception=None, tags=None, custom_name=None):
    url = ax_environment['automox-api-url-base'] + "/servers" + "/" + str(ax_device_id)
    querystring = {"o":ax_environment['automox-org-id']}
    action = "PUT"
    # Build the update package
    update_data = {}
    if server_group_id:
        update_data['server_group_id'] = server_group_id
    if ip_addrs:
        update_data['ip_addrs'] = ip_addrs
    if exception:
        update_data['exception'] = exception
    if tags:
        update_data['tags'] = tags
    if custom_name:
        update_data['custom_name'] = custom_name
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring, data=update_data)


# Delete Device
def ax_device_delete(ax_environment, ax_device_id):
    url = ax_environment['automox-api-url-base'] + "/servers" + "/" + str(ax_device_id)
    querystring = {"o":ax_environment['automox-org-id']}
    action = "DELETE"
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring)


# Get policy list
def ax_policy_list_get(ax_environment):
    url = ax_environment['automox-api-url-base'] + "/policies"
    querystring = {"o":ax_environment['automox-org-id']}
    action = "GET"
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring)


# Get specific policy details
def ax_policy_get(ax_environment, ax_policy_id):
    url = ax_environment['automox-api-url-base'] + "/policies" + "/" + str(ax_policy_id)
    querystring = {"o":ax_environment['automox-org-id']}
    action = "GET"
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring)


# Create Policy
def ax_policy_create(ax_environment, update_data):
    url = ax_environment['automox-api-url-base'] + "/policies"
    querystring = {"o":ax_environment['automox-org-id']}
    action = "POST"
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring, data=update_data)


# Delete Policy
def ax_policy_delete(ax_environment, ax_policy_id):
    url = ax_environment['automox-api-url-base'] + "/policies" + "/" + str(ax_policy_id)
    querystring = {"o":ax_environment['automox-org-id']}
    action = "DELETE"
    # Call the API
    return ax_call_api(action, url, ax_environment['automox-api-key'], params=querystring)


