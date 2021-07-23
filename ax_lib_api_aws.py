import ax_lib_general
import boto3


# --Description-- #
# AWS API Helper library.  Contains shared API call functions for AWS.
# --End Description-- #

# --Helper Methods-- #
# Create the AWS Client connection for ec2 activities
# Session token not working - need to figure out why...
def aws_ec2_connection_create(aws_region, aws_api_key=None, aws_api_secret=None, aws_api_session_token=None):
    ec2_connection = boto3.client(service_name='ec2',
                        region_name=aws_region,
                        aws_access_key_id=aws_api_key,
                        aws_secret_access_key=aws_api_secret,
                        aws_session_token=aws_api_session_token)
    return ec2_connection


# Create the EC2 instances in the list
def aws_ec2_instance_create_list(ec2_connection, ec2_list):
    ec2_instances_new = []
    # Set the required MedatataOptions
    metadata_options = {}
    metadata_options['HttpTokens'] = 'required'
    metadata_options['HttpPutResponseHopLimit'] = 1
    metadata_options['HttpEndpoint'] = 'enabled'
    # Loop though the list and create the instances
    for ec2_instance in ec2_list:
        # Create the individual instance
        print("Creating instance name: " + ec2_instance['InstanceName'] + "...")
        ec2_instance['aws_response'] = ec2_connection.run_instances(
                        IamInstanceProfile={'Name':ec2_instance['IamInstanceProfileName']},
                        ImageId=ec2_instance['ImageId'],
                        InstanceType=ec2_instance['InstanceType'],
                        KeyName=ec2_instance['KeyName'],
                        MaxCount=int(ec2_instance['NumberofInstances']),
                        MinCount=int(ec2_instance['NumberofInstances']),
                        SecurityGroupIds=[ec2_instance['SecurityGroupId']],
                        SubnetId=ec2_instance['SubnetId'],
                        TagSpecifications=[{'ResourceType':'instance','Tags':[
                                                                            {'Key':'Name','Value':ec2_instance['InstanceName']},
                                                                            {'Key':'ax-environment','Value':ec2_instance['ax_environment']},
                                                                            {'Key':'ax-org-id','Value':ec2_instance['automox-org-id']}
                                                                            ]}],
                        UserData=ec2_instance['user_data'],
                        MetadataOptions=metadata_options
                        )
        ec2_instances_new.append(ec2_instance)
        for aws_response_instance in ec2_instance['aws_response']['Instances']:
            print(aws_response_instance['InstanceId'])
    return ec2_instances_new


# Destroy the EC2 instances in the list
def aws_ec2_instance_destroy_list(ec2_connection, ec2_instance_id_list):
    aws_response = ec2_connection.terminate_instances(InstanceIds=ec2_instance_id_list)
    return aws_response


# Get a list of the existing EC2 instances
def aws_ec2_instance_get_list(ec2_connection, environment_name):
    list_filter=[{'Name':'tag:ax-environment', 'Values':[environment_name]},
                    {'Name':'instance-state-name', 'Values':['pending','running','stopping','stopped']}
                ]
    aws_response = ec2_connection.describe_instances(Filters=list_filter)
    return aws_response


# Start the AWS Instances in the list
def aws_ec2_instance_start_list(ec2_connection, ec2_instance_id_list):
    aws_response = ec2_connection.start_instances(InstanceIds=ec2_instance_id_list)
    return aws_response


# Stop the AWS Instances in the list
def aws_ec2_instance_stop_list(ec2_connection, ec2_instance_id_list):
    aws_response = ec2_connection.stop_instances(InstanceIds=ec2_instance_id_list)
    return aws_response


