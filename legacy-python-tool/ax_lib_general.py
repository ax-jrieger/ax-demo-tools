import json
import os.path
import sys
import csv

# --Description-- #
# General Helper library and tools
# --End Description-- #


# --Helper Methods-- #
# Exit handler (Error)
def ax_exit_error(error_code, error_message=None, system_message=None):
    print(error_code)
    if error_message is not None:
        print(error_message)
    if system_message is not None:
        print(system_message)
    sys.exit(1)


# Exit handler (Success)
def ax_exit_success():
    sys.exit(0)


# Check to see if a file exists
def ax_file_exists(file_name):
    file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
    if os.path.isfile(file_name_and_path):
        return True    
    else:
        return False

# Read in environment from CSV
def ax_environment_read(environment_file_name):
    if ax_file_exists(environment_file_name):
        ax_environment = ax_file_load_csv_simple(environment_file_name)
        if ax_environment is None or ax_environment == {}:
            ax_exit_error(500, "The environment file appears to exist, but is empty?  Check the envrionment file.")
        else:
            return ax_environment
    else:
        ax_exit_error(400, "Cannot find the environment file.  Please check the file name used for the environment.")


# Read in endpoints from CSV
def ax_endpoints_read(endpoints_file_name):
    if ax_file_exists(endpoints_file_name):
        ax_endpoints = ax_file_load_csv(endpoints_file_name)
        if ax_endpoints is None or ax_endpoints == {}:
            ax_exit_error(500, "The endpoints file appears to exist, but is empty?  Check the endpoints file.")
        else:
            return ax_endpoints
    else:
        ax_exit_error(400, "Cannot find the endpoints file.  Please check the file name used for the endpoints.")


# Load the 2 column CSV directly into a Dict
def ax_file_load_csv_simple(file_name):
    with open(file_name,mode='r') as csv_file:
        file_reader = csv.reader(csv_file)
        csv_dict = dict(file_reader)
    return csv_dict


# Load the CSV file into Dict
def ax_file_load_csv(file_name):
    csv_list = []
    with open(file_name, 'r') as csv_file:
        file_reader = csv.DictReader(csv_file)
        for row in file_reader:
            csv_list.append(row)
    return csv_list


# Read txt file into string
def ax_file_read_txt(file_name):
    txt_data = None
    file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
    try:
        with open(file_name_and_path, 'r') as f:
            txt_data = f.read()
    except Exception as ex:
        ax_exit_error(500, "Failed to read text file.  Check the file name?", ex)
    return txt_data


# Write Dict to JSON file
def ax_file_write_json(file_name, data_to_write):
    file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
    try:
        with open(file_name_and_path, 'w') as f:
            json.dump(data_to_write, f)
    except Exception as ex:
        ax_exit_error(500, "Failed to write JSON file.", ex)


# Read JSON file into Dict
def ax_file_read_json(file_name):
    json_data = None
    file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
    try:
        with open(file_name_and_path, 'r') as f:
            json_data = json.load(f)
    except Exception as ex:
        ax_exit_error(500, "Failed to read JSON file.  Check the file name?", ex)
    return json_data


# JSON Dumps - formatted and default set to avoid unserializable attribs
def ax_json_dumps(var_to_convert):
    return json.dumps(var_to_convert, indent = 4, sort_keys=True, default=str)


# Check for duplicates in a list
def duplicate_check(object_list):  
    object_set = set()
    for single_object in object_list:
        if single_object in object_set:
            return single_object
        else:
            object_set.add(single_object)         
    return None


# Exit and print out a JSON based variable (for debugging)
def ax_json_dumps_and_exit(var_to_convert):
    print()
    print('##############JSON STARTS BELOW#############')
    print()
    print(ax_json_dumps(var_to_convert))
    print()
    ax_exit_success()

