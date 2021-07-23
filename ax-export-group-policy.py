from __future__ import print_function
try:
    input = raw_input
except NameError:
    pass
import ax_lib_api_ax
import ax_lib_general
import argparse


# --Execution Block-- #
# --Parse command line arguments-- #
parser = argparse.ArgumentParser()

parser.add_argument(
    'ax_environment_name',
    type=str,
    help='Name of the environment to export.')

args = parser.parse_args()
# --End parse command line arguments-- #


# --Main-- #
# Set the envrionment directory path
ax_environment_directory = "./" + args.ax_environment_name + "/"

# Set the envionment name for all tagging and identificaiton to lowercase for consistency
ax_environment_name_lower = args.ax_environment_name.lower()

# Load environment
ax_environment = ax_lib_general.ax_environment_read(ax_environment_directory + "environment.csv")

# Export the group data to disk
# Load the existing groups from the environment
print()
print("Groups - Reading from the API...")
ax_group_current = ax_lib_api_ax.ax_group_list_get(ax_environment)
# Write them out to disk
file_name = ax_environment_directory + "groups.json"
print()
print("Groups - Writing " + file_name + " to disk...")
ax_lib_general.ax_file_write_json(file_name, ax_group_current['data'])

# Export the policy data to disk
# Load the existing policy data from the environment
print()
print("Policies - Reading from the API...")
ax_policy_current = ax_lib_api_ax.ax_policy_list_get(ax_environment)
# Write them out to disk
file_name = ax_environment_directory + "policy.json"
print()
print("Policies - Writing " + file_name + " to disk...")
ax_lib_general.ax_file_write_json(file_name, ax_policy_current['data'])

print()
print("Export complete.")
print()
