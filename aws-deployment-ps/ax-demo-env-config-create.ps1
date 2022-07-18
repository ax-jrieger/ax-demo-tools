## Use this file to create your configuration for the reaminder of the scripts

# $name is for the name of the environment.  Please keep this to 9 characters to prevent some limits from being reached.
# $location is the Azure region to use (centralus, etc.)
# $winusername is the admin username to set on the created windows servers
# $winuserpass is the clear text password you want to use for the admin account above
# $number is the number of VM's you want to create
# $axaccesskey is the Access Key for the agent installer for the Automox tenant
# $axgroup is the Automox group you want your systems to be defaulted to

param ($name, $location, $winusername, $winpass, $number, $axaccesskey, $axgroup)

#Create splatter block
$config = @{
    AWSAccessKey = $AWSAccessKey;
    AWSSecretKey = $AWSSecretKey;
    AWSStoreAs = $AWSStoreAs;
    AWSRegion = $AWSRegion;
    number = $number;
    axaccesskey = $axaccesskey;
    axgroup = $axgroup;
    }

# Convert to JSON
$configJSON = ConvertTo-Json -InputObject $config

# Save config to a file
$fileName = "./"+$name+".conf"
Out-File -FilePath $fileName -InputObject $configJSON