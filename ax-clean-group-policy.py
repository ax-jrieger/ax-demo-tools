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
    help='Name of the environment to clean.')

args = parser.parse_args()
# --End parse command line arguments-- #


# --Main-- #
# Set the envrionment directory path
ax_environment_directory = "./" + args.ax_environment_name + "/"

# Set the envionment name for all tagging and identificaiton to lowercase for consistency
ax_environment_name_lower = args.ax_environment_name.lower()

# Load environment
ax_environment = ax_lib_general.ax_environment_read(ax_environment_directory + "environment.csv")

# Load the groups list
print()
print("API - Getting groups list...")
ax_group_list_api = ax_lib_api_ax.ax_group_list_get(ax_environment)['data']

# Find the default group and remove it from the clean list
print()
print("List - Removing the default group from the clean list...")
for i in range(len(ax_group_list_api)):
    if ax_group_list_api[i]['name'] == "":
        del ax_group_list_api[i]
        break

# Load the policy list
print()
print("API - Getting policy list...")
ax_policy_list_api = ax_lib_api_ax.ax_policy_list_get(ax_environment)['data']

# Remove the policies
print()
print("Removing the policies...")
for policy in ax_policy_list_api:
    print("API - Deleting policy: " + policy['name'])
    ax_api_response = ax_lib_api_ax.ax_policy_delete(ax_environment, policy['id'])

# Remove the groups
print()
print("Removing the groups...")
for group in ax_group_list_api:
    print("API - Deleting group: " + group['name'])
    ax_api_response = ax_lib_api_ax.ax_group_delete(ax_environment, group['id'])
