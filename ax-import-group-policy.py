from __future__ import print_function

from requests import NullHandler
try:
    input = raw_input
except NameError:
    pass
import ax_lib_api_ax
import ax_lib_general
import argparse
import json


# --Execution Block-- #
# --Parse command line arguments-- #
parser = argparse.ArgumentParser()

parser.add_argument(
    'ax_environment_name',
    type=str,
    help='Name of the environment to import.')

args = parser.parse_args()
# --End parse command line arguments-- #


# --Main-- #
# Set the envrionment directory path
ax_environment_directory = "./" + args.ax_environment_name + "/"

# Set the envionment name for all tagging and identificaiton to lowercase for consistency
ax_environment_name_lower = args.ax_environment_name.lower()

# Load environment
ax_environment = ax_lib_general.ax_environment_read(ax_environment_directory + "environment.csv")

## Import the data from disk
# Load the existing groups from disk
file_name = ax_environment_directory + "groups.json"
print()
print("Groups - Reading " + file_name + " from disk...")
ax_group_list_disk = ax_lib_general.ax_file_read_json(file_name)

# Load the existing policies from disk
file_name = ax_environment_directory + "policy.json"
print()
print("Policies - Reading " + file_name + " from disk...")
ax_policy_list_disk = ax_lib_general.ax_file_read_json(file_name)

# Need to find out the default group ID in the new environment
print()
print("Calling the new environment API to get the default group ID...")
ax_group_list_api = ax_lib_api_ax.ax_group_list_get(ax_environment)['data']
default_group_id_api = None
for ax_group in ax_group_list_api:
    if ax_group['name'] == "":
        default_group_id_api = ax_group['id']
        break

# Find the imported default ID and remove the default group from the import list
default_group_id_disk = None
for i in range(len(ax_group_list_disk)):
    if ax_group_list_disk[i]['name'] == "":
        default_group_id_disk = ax_group_list_disk[i]['id']
        del ax_group_list_disk[i]
        break

## Update the import lists
# Group import list updates
for i in range(len(ax_group_list_disk)):
    # Fix the default group ID
    if ax_group_list_disk[i]['parent_server_group_id'] == default_group_id_disk:
        ax_group_list_disk[i]['parent_server_group_id'] = default_group_id_api
    # Add the correct wsus info
    if 'wsus_config' in ax_group_list_disk[i]:
        ax_group_list_disk[i]['wsus_server'] = ax_group_list_disk[i]['wsus_config']['server_url']
        ax_group_list_disk[i]['enable_wsus'] = ax_group_list_disk[i]['wsus_config']['is_managed']
    else:
        ax_group_list_disk[i]['wsus_server'] = None
        ax_group_list_disk[i]['enable_wsus'] = None
    # Add in a flag to determine if it has already been added below
    ax_group_list_disk[i]['has_been_added'] = False

# Policy import list updates
for i in range(len(ax_policy_list_disk)):
    # Fix the default group ID in the policy list
    if len(ax_policy_list_disk[i]['server_groups']) > 0:
        for group_id in ax_policy_list_disk[i]['server_groups']:
            if group_id == default_group_id_disk:
                group_id = default_group_id_api

# Build a parent ID list for tree checking (mostly for sanity)
ax_group_id_list_api = []
for ax_group in ax_group_list_api:
    ax_group_id_list_api.append(ax_group['id'])

# Add the new groups and maintain the tree
groups_list_incomplete = True
while groups_list_incomplete:
    groups_list_incomplete = False
    for i in range(len(ax_group_list_disk)):
        # Check to see if we have already added the group
        if ax_group_list_disk[i]['has_been_added'] == False:
            # Set the while loop flag indicating we are not done yet
            groups_list_incomplete = True
            # Check to see if the parent exists
            if ax_group_list_disk[i]['parent_server_group_id'] in ax_group_id_list_api:
                # Add the new group to the API
                print("Creating group name " + ax_group_list_disk[i]['name'])
                ax_api_response = ax_lib_api_ax.ax_group_create(ax_environment, 
                                                                ax_group_list_disk[i]['name'], 
                                                                ax_group_list_disk[i]['refresh_interval'], 
                                                                ax_group_list_disk[i]['parent_server_group_id'], 
                                                                ax_group_list_disk[i]['ui_color'], 
                                                                ax_group_list_disk[i]['notes'], 
                                                                ax_group_list_disk[i]['enable_os_auto_update'], 
                                                                ax_group_list_disk[i]['enable_wsus'], 
                                                                ax_group_list_disk[i]['wsus_server'])
                # Update the new parent ID in the group disk list
                for j in range(len(ax_group_list_disk)):
                    if ax_group_list_disk[j]['parent_server_group_id'] == ax_group_list_disk[i]['id']:
                        ax_group_list_disk[j]['parent_server_group_id'] = ax_api_response['data']['id']
                
                # Update the new parent ID in the policy disk list
                for j in range(len(ax_policy_list_disk)):
                    if len(ax_policy_list_disk[j]['server_groups']) > 0:
                        for k in range(len(ax_policy_list_disk[j]['server_groups'])):
                            if ax_policy_list_disk[j]['server_groups'][k] == ax_group_list_disk[i]['id']:
                                ax_policy_list_disk[j]['server_groups'][k] = ax_api_response['data']['id']
                
                # Add the new ID to the existing API list
                ax_group_id_list_api.append(ax_api_response['data']['id'])

                # Set the added flag
                ax_group_list_disk[i]['has_been_added'] = True

# Add the new policys with the updated group ID's
for policy in ax_policy_list_disk:
    # Build the update package
    update_data = {}
    update_data['configuration'] = {}
    update_data['name'] = policy['name']
    update_data['policy_type_name'] = policy['policy_type_name']
    update_data['organization_id'] = ax_environment['automox-org-id']
    update_data['schedule_days'] = policy['schedule_days']
    update_data['schedule_weeks_of_month'] = policy['schedule_weeks_of_month']
    update_data['schedule_months'] = policy['schedule_months']
    update_data['schedule_time'] = policy['schedule_time']
    update_data['notes'] = policy['notes']
    update_data['server_groups'] = policy['server_groups']
    if 'notify_user' in policy['configuration']:
        update_data['configuration']['notify_user'] = policy['configuration']['notify_user']
    if 'auto_patch' in policy['configuration']:
        update_data['configuration']['auto_patch'] = policy['configuration']['auto_patch']
    if 'auto_reboot' in policy['configuration']:
        update_data['configuration']['auto_reboot'] = policy['configuration']['auto_reboot']
    if 'notify_reboot_user' in policy['configuration']:
        update_data['configuration']['notify_reboot_user'] = policy['configuration']['notify_reboot_user']
    if 'missed_patch_window' in policy['configuration']:
        update_data['configuration']['missed_patch_window'] = policy['configuration']['missed_patch_window']
    if 'patch_rule' in policy['configuration']:
        update_data['configuration']['patch_rule'] = policy['configuration']['patch_rule']
    if 'filter_type' in policy['configuration']:
        update_data['configuration']['filter_type'] = policy['configuration']['filter_type']
    if 'filters' in policy['configuration']:
        update_data['configuration']['filters'] = policy['configuration']['filters']
    if 'severity_filter' in policy['configuration']:
        update_data['configuration']['severity_filter'] = policy['configuration']['severity_filter']
    if 'advanced_filter' in policy['configuration']:
        update_data['configuration']['advanced_filter'] = policy['configuration']['advanced_filter']
    if 'include_optional' in policy['configuration']:
        update_data['configuration']['include_optional'] = policy['configuration']['include_optional']
    if 'custom_notification_max_delays' in policy['configuration']:
        update_data['configuration']['custom_notification_max_delays'] = policy['configuration']['custom_notification_max_delays']
    if 'custom_notification_deferment_periods' in policy['configuration']:
        update_data['configuration']['custom_notification_deferment_periods'] = policy['configuration']['custom_notification_deferment_periods']
    if 'custom_notification_patch_message' in policy['configuration']:
        update_data['configuration']['custom_notification_patch_message'] = policy['configuration']['custom_notification_patch_message']
    if 'custom_notification_reboot_message' in policy['configuration']:
        update_data['configuration']['custom_notification_reboot_message'] = policy['configuration']['custom_notification_reboot_message']
    if 'custom_notification_patch_message_mac' in policy['configuration']:
        update_data['configuration']['custom_notification_patch_message_mac'] = policy['configuration']['custom_notification_patch_message_mac']
    if 'custom_notification_reboot_message_mac' in policy['configuration']:
        update_data['configuration']['custom_notification_reboot_message_mac'] = policy['configuration']['custom_notification_reboot_message_mac']
    if 'patch_rule' in policy['configuration']:
        update_data['configuration']['patch_rule'] = policy['configuration']['patch_rule']
    if 'device_filters' in policy['configuration']:
        update_data['configuration']['device_filters'] = policy['configuration']['device_filters']
    if 'evaluation_code' in policy['configuration']:
        update_data['configuration']['evaluation_code'] = policy['configuration']['evaluation_code']
    if 'remediation_code' in policy['configuration']:
        update_data['configuration']['remediation_code'] = policy['configuration']['remediation_code']
    if 'installation_code' in policy['configuration']:
        update_data['configuration']['installation_code'] = policy['configuration']['installation_code']
    if 'notify_deferred_reboot_user' in policy['configuration']:
        update_data['configuration']['notify_deferred_reboot_user'] = policy['configuration']['notify_deferred_reboot_user']
    if 'custom_pending_reboot_notification_message' in policy['configuration']:
        update_data['configuration']['custom_pending_reboot_notification_message'] = policy['configuration']['custom_pending_reboot_notification_message']
    if 'notify_deferred_reboot_user_message_timeout' in policy['configuration']:
        update_data['configuration']['notify_deferred_reboot_user_message_timeout'] = policy['configuration']['notify_deferred_reboot_user_message_timeout']
    if 'custom_pending_reboot_notification_max_delays' in policy['configuration']:
        update_data['configuration']['custom_pending_reboot_notification_max_delays'] = policy['configuration']['custom_pending_reboot_notification_max_delays']
    if 'custom_pending_reboot_notification_message_mac' in policy['configuration']:
        update_data['configuration']['custom_pending_reboot_notification_message_mac'] = policy['configuration']['custom_pending_reboot_notification_message_mac']
    if 'notify_deferred_reboot_user_auto_deferral_enabled' in policy['configuration']:
        update_data['configuration']['notify_deferred_reboot_user_auto_deferral_enabled'] = policy['configuration']['notify_deferred_reboot_user_auto_deferral_enabled']
    if 'custom_pending_reboot_notification_deferment_periods' in policy['configuration']:
        update_data['configuration']['custom_pending_reboot_notification_deferment_periods'] = policy['configuration']['custom_pending_reboot_notification_deferment_periods']
    if 'os_family' in policy['configuration']:
        update_data['configuration']['os_family'] = policy['configuration']['os_family']
    if 'package_name' in policy['configuration']:
        update_data['configuration']['package_name'] = policy['configuration']['package_name']
    if 'package_version' in policy['configuration']:
        update_data['configuration']['package_version'] = policy['configuration']['package_version']
    if 'use_scheduled_timezone' in policy['configuration']:
        update_data['configuration']['use_scheduled_timezone'] = policy['configuration']['use_scheduled_timezone']

    # Add the new policy to the API
    print("Creating policy name " + policy['name'])
    ax_api_response = ax_lib_api_ax.ax_policy_create(ax_environment, update_data)
