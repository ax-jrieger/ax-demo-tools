from __future__ import print_function
try:
    input = raw_input
except NameError:
    pass
import ax_lib_api_ax
import ax_lib_general
import ax_lib_api_aws
import argparse
import time


# --Execution Block-- #
# --Parse command line arguments-- #
parser = argparse.ArgumentParser()

parser.add_argument(
    'ax_environment_name',
    type=str,
    help='Name of the environment to load.  With no other switches, this will sync the existing environment with the settings files.')

parser.add_argument(
    '-create',
    action='store_true',
    help='(Optional) - Only create missing instances.  Do not terminate any existing instances even if they do not exist in the environment settings files.')

parser.add_argument(
    '-destroy',
    action='store_true',
    help='(Optional) - Only terminate instances running that are not currently in the environment settings files.')

parser.add_argument(
    '-purge',
    action='store_true',
    help='(Optional) - Completely terminate all instances with the selected environment tag.  '
            'NOTE: This will completely remove all instances from AWS with the specified environment settings.')

parser.add_argument(
    '-refresh',
    action='store_true',
    help='(Optional) - Refresh any instances that are not marked to ignore a refresh.')

parser.add_argument(
    '-ax_ignore',
    action='store_true',
    help='(Optional) - Do not delete/clean devices from the Automox environment.')

parser.add_argument(
    '-start',
    action='store_true',
    help='(Optional) - Start all stopped instances for this environment tag in AWS.')

parser.add_argument(
    '-stop',
    action='store_true',
    help='(Optional) - Stop all instances for this environment tag in AWS.')

args = parser.parse_args()
# --End parse command line arguments-- #


# --Main-- #
# Set the envrionment directory path
ax_environment_directory = "./" + args.ax_environment_name + "/"

# Set the envionment name for all tagging and identificaiton to lowercase for consistency
ax_environment_name_lower = args.ax_environment_name.lower()

# Load environment
ax_environment = ax_lib_general.ax_environment_read(ax_environment_directory + "environment.csv")

# Create AWS API client connection
# Pass in the variables - Not working for some reason.
#aws_ec2_connection = ax_lib_api_aws.aws_ec2_connection_create(ax_environment['aws-region'], ax_environment['aws-api-key'], ax_environment['aws-api-secret'], ax_environment['aws-api-session-token'])
# Use the environment variables that have been set in the OS / session
aws_ec2_connection = ax_lib_api_aws.aws_ec2_connection_create(ax_environment['aws-region'])

# Load existing AWS EC2 instance list for the specified environment
aws_instances = ax_lib_api_aws.aws_ec2_instance_get_list(aws_ec2_connection, ax_environment_name_lower)

# Collapse the AWS instance list for sanity
aws_instance_list = []
if len(aws_instances['Reservations']) > 0:
    for reservation in aws_instances['Reservations']:
            for instance in reservation['Instances']:
                aws_instance_list.append(instance)

## Check for start and stop functions which are AWS only before continuing with any further API calls
# Check for the start flag
if args.start:
    aws_instance_stopped = False
    aws_instance_start_list = []
    if len(aws_instance_list) > 0:
        for aws_instance in aws_instance_list:
            if aws_instance['State']['Name'] == 'stopped':
                aws_instance_stopped = True
                aws_instance_start_list.append(aws_instance['InstanceId'])
    
    if aws_instance_stopped:
        # Call the API to start the instances
        aws_response = ax_lib_api_aws.aws_ec2_instance_start_list(aws_ec2_connection, aws_instance_start_list)
        print()
        for aws_instance_id in aws_instance_start_list:
            print('Started AWS Instance ID: ' + aws_instance_id)
        ax_lib_general.ax_exit_success()
    else:
        print()
        print('No stopped instances detected.  Exiting.')
        ax_lib_general.ax_exit_success()

# Check for the stop flag
if args.stop:
    aws_instance_started = False
    aws_instance_stop_list = []
    if len(aws_instance_list) > 0:
        for aws_instance in aws_instance_list:
            if aws_instance['State']['Name'] == 'running':
                aws_instance_started = True
                aws_instance_stop_list.append(aws_instance['InstanceId'])
    
    if aws_instance_started:
        # Call the API to stop the instances
        aws_response = ax_lib_api_aws.aws_ec2_instance_stop_list(aws_ec2_connection, aws_instance_stop_list)
        print()
        for aws_instance_id in aws_instance_stop_list:
            print('Stopped AWS Instance ID: ' + aws_instance_id)
        ax_lib_general.ax_exit_success()
    else:
        print()
        print('No running instances detected.  Exiting.')
        ax_lib_general.ax_exit_success()

# Load existing AX device list
ax_devices_current = ax_lib_api_ax.ax_device_list_get(ax_environment)

# Load endpoints list
ax_endpoints = ax_lib_general.ax_endpoints_read(ax_environment_directory + "endpoints.csv")

# Verify all of the endpoint required data exists and add in extra data required
ax_endpoints_updated = []
ax_endpoints_names = []
for ax_endpoint in ax_endpoints:
    if not ax_endpoint['InstanceName']:
        ax_lib_general.ax_exit_error(404, "InstanceName is missing in one of the endpoints.")
    ax_endpoints_names.append(ax_endpoint['InstanceName'])
    if not ax_endpoint['ImageId']:
        ax_lib_general.ax_exit_error(404, "ImageId is missing on the endpoint named: " + ax_endpoint['InstanceName'])
    if not ax_endpoint['InstanceType']:
        ax_lib_general.ax_exit_error(404, "InstanceType is missing on the endpoint named: " + ax_endpoint['InstanceName'])
    if not ax_endpoint['NumberofInstances']:
        ax_lib_general.ax_exit_error(404, "NumberofInstances is missing on the endpoint named: " + ax_endpoint['InstanceName'])
    if not ax_endpoint['SecurityGroupId']:
        ax_lib_general.ax_exit_error(404, "SecurityGroupId is missing on the endpoint named: " + ax_endpoint['InstanceName'])
    if not ax_endpoint['SubnetId']:
        ax_lib_general.ax_exit_error(404, "SubnetId is missing on the endpoint named: " + ax_endpoint['InstanceName'])
    
    # Verify and load in the UserData (if needed)
    if ax_endpoint['UserDataScript']:
        if ax_lib_general.ax_file_exists(ax_environment_directory + ax_endpoint['UserDataScript']):
            ax_endpoint['user_data'] = ax_lib_general.ax_file_read_txt(ax_environment_directory + ax_endpoint['UserDataScript'])
        else:
            ax_lib_general.ax_exit_error(404, "UserData defined script in endpoints CSV does not appear to be included in the environment directory.")
    
    # Add in the environment label
    ax_endpoint['ax_environment'] = ax_environment_name_lower

    # Add in the AX Org ID
    ax_endpoint['automox-org-id'] = ax_environment['automox-org-id']

    # Build the new list
    ax_endpoints_updated.append(ax_endpoint)

# Replace the endpoints list
ax_endpoints = ax_endpoints_updated

# Check for duplicate instance names (Not supported)
ax_duplicate_check = ax_lib_general.duplicate_check(ax_endpoints_names)
if ax_duplicate_check is not None:
    ax_lib_general.ax_exit_error(400, "Endpoints list appears to contain a duplicate instance name: " + ax_duplicate_check + ".  This is not supported at this time.")

# Build the create and destroy lists
if len(aws_instance_list) > 0:
    # Sort the lists into what needs to be created and what needs to be destroyed
    # Find the instances to destroy
    ax_endpoints_destroy_instanceids = []
    # Check to see if the purge flag is set
    if args.purge:
        for instance in aws_instance_list:
            ax_endpoints_destroy_instanceids.append(instance['InstanceId'])
    else:
        for instance in aws_instance_list:
            instance_found = False
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    for ax_endpoint in ax_endpoints:
                        if tag['Value'] == ax_endpoint['InstanceName']:
                            if args.refresh:
                                if ax_endpoint['IgnoreRefresh'] == 1:
                                    instance_found = True
                                    break
                            else:
                                instance_found = True
                                break
                # Break out of the nested loop if we found it already
                if instance_found:
                    break
            if not instance_found:
                ax_endpoints_destroy_instanceids.append(instance['InstanceId'])
    
    # Find the instances to create
    if args.purge:
        ax_endpoints_create = []
    else:
        ax_endpoints_create = []
        if len(ax_endpoints) > 0:
            for ax_endpoint in ax_endpoints:
                for instance in aws_instance_list:
                    instance_found = False
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            if tag['Value'] == ax_endpoint['InstanceName']:
                                if args.refresh:
                                    if ax_endpoint['IgnoreRefresh'] == 1:
                                        instance_found = True
                                        break
                                else:
                                    instance_found = True
                                    break
                    # Break out of the nested loop if we found it already
                    if instance_found:
                        break
                if not instance_found:
                    ax_endpoints_create.append(ax_endpoint)
else:
    if args.purge:
        print('No instances with this environment tag are running in this region.  Exiting...')
        ax_lib_general.ax_exit_success()
    else:
        # Nothing in AWS yet.  Create it all.
        ax_endpoints_destroy_instanceids = []
        ax_endpoints_create = ax_endpoints

# Terminate anything running that should no longer be running
if not args.create:
    if len(ax_endpoints_destroy_instanceids) > 0:
        print()
        print('Terminating instances:')
        for ax_endpoint in ax_endpoints_destroy_instanceids:
            print(ax_endpoint)
        aws_response = ax_lib_api_aws.aws_ec2_instance_destroy_list(aws_ec2_connection, ax_endpoints_destroy_instanceids)
        print('Done.')

        # Delete any device references from AX for terminated instances
        print()
        print('Sleeping for 10 seconds to allow for AWS termination to begin.')
        time.sleep(10)

        # Check to see if we are ignoring the Automox updates
        if args.ax_ignore:
            print()
            print('AX Ignore flag detected - skipping the removal of terminated instances from Automox.')
        else:
            print()
            print('Removing terminated instances from Automox...')
            for instance_id in ax_endpoints_destroy_instanceids:
                for ax_device in ax_devices_current:
                    if len(ax_device['tags']) > 0:
                        if instance_id in ax_device['tags']:
                            print("Deleting instance id " + instance_id)
                            ax_response = ax_lib_api_ax.ax_device_delete(ax_environment, ax_device['id'])
            print()
            print('Done.')
    else:
        print()
        print('Nothing to terminate.  Skipping.')
else:
    print()
    print('Create flag detected, skipping termination.')

# Create new instances that are missing
if not args.destroy:
    if len(ax_endpoints_create) > 0:
        print()
        print('Creating new instances...')
        aws_instances_new = ax_lib_api_aws.aws_ec2_instance_create_list(aws_ec2_connection, ax_endpoints_create)
        print()
        print("Instance creation complete.")

        # Giving some time for the instances to come up and check in to AX
        print()
        print('Sleeping script for 3 minutes to give AWS time to create and load instances...')
        time.sleep(180)
        print('Done.')

        # Get the AX devices list and check to verify everything was imported
        ax_devices_retry = True
        while ax_devices_retry:
            # Grab the new devices list from AX
            ax_devices_current = ax_lib_api_ax.ax_device_list_get(ax_environment)

            # Check the device list to see if we have them all checked in
            ax_devices_not_found = []
            for aws_instances in aws_instances_new:
                for aws_instance in aws_instances['aws_response']['Instances']:
                    device_found = False
                    for ax_deivce in ax_devices_current:
                        for aws_instance_nic in aws_instance['NetworkInterfaces']:
                            if 'NICS' in ax_deivce['detail']:
                                for ax_deivce_nic in ax_deivce['detail']['NICS']:
                                    if aws_instance_nic['MacAddress'].lower() == ax_deivce_nic['MAC'].lower():
                                        device_found = True

                                        # Update the AX Instance
                                        server_group_id = aws_instances['AxGroupId']
                                        custom_name = aws_instances['InstanceName']
                                        ax_device_id = ax_deivce['id']
                                        tags = ax_deivce['tags']
                                        tags.append(ax_endpoint['ax_environment'])
                                        tags.append(aws_instance['InstanceId'])

                                        print()
                                        print('Updating custom name and group for Automox device ' + custom_name + ' at device ID ' + str(ax_device_id))
                                        # Call the API
                                        ax_response = ax_lib_api_ax.ax_device_put(ax_environment, ax_device_id, server_group_id=server_group_id, custom_name=custom_name, 
                                                                                    tags=tags)

                                        # Found what we were looking for and break out of the device loop
                                        break
                            if device_found:
                                break
                        if device_found:
                            break
                    if not device_found:
                        # Appending the top level object - note this will break if AWS does more than 1 instance in the list - need to clean this up.
                        ax_devices_not_found.append(aws_instances)


            # Set the loop status
            if len(ax_devices_not_found) > 0:
                ax_devices_retry = True
                aws_instances_new = ax_devices_not_found
                print()
                print('Not all devices have checked in to Automox yet.  Sleeping script for 10 seconds.')
                time.sleep(10)
            else:
                ax_devices_retry = False

        print()
        print('Done.')

    else:
        print()
        print('Nothing to create.  Skipping.')
else:
    print()
    print('Destroy flag detected, skipping creation.')

print()
print('Environment activity complete.')

