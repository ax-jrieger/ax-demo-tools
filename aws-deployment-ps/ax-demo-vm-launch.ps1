## Scrip to launch the AWS based demo environment

## It is assumed that you have already had an AWS account and core items provisioned by IT for your use
# This will generally include a VPC & Security groups.
## It is also assumed that you have entered in your credentials to the session for access (from Okta in the case of Automox)

## Parameters to pass in
# $awsregion is the AWS region to deploy to.
# $env_dir_name is the list of VM's and information to build in the environment
# $ax_access_key is the Access Key for the Automox API key

param ($env_dir_name, $aws_region, $ax_access_key)

# Set some "static" variables
$ax_api_url_base = "https://console.automox.com/api"






# Set Image Information
#$pubName = "MicrosoftWindowsDesktop"
#$offerName = "Windows-10"
#$skuName = "win10-21h2-pro-g2"
#$version = "latest"

# Build the Image name to launch
#$ImageName = $pubName + ":" + $offerName + ":" + $skuName + ":" + $version

# Create the VM Config and Launch
$ResourceGroupName = $EnvName + "-RG"
$VMSize = "Standard_DS1"
$VirtualNetworkName = $EnvName + "-VN"
$SubnetName = $EnvName + "-SN"
$SecurityGroupName = $EnvName + "-NSG"
$OpenPorts = 3389

# Script path for the AX load script
#$ScriptFileName = "ax-demo-script-automox-windows.ps1"
$ScriptFullNameAndPath = Join-Path $PSScriptRoot $ScriptFileName
#Write-Output $ScriptFullNameAndPath

for ($num = 1; $num -lt $NumberOfVM+1; $num++) {
  # Start working through the names of the VM and Public IP assignments
  $VMName = $EnvName + "-VM" + $num
  $PublicIpAddressName = $EnvName + "-PIP" + $num

  # VM Details
  $WindowsUserName = $VMConfig.WinAdminUserName
  $WindowsPasswordClear = $VMConfig.WinAdminPassword
  $NumberOfVM = $VMConfig.number
  $AXAccessKey = $VMConfig.AutomoxAccessKey
  $AXGroupName = $VMConfig.AutomoxGroup
  $ImageName = $VMConfig.ImageName
  $ScriptFileName = $VMConfig.AutomoxAgentScriptName
  $VMName = $VMConfig.VMName
  $VMSize = $VMConfig.AzureVMSize

  #Create hashtable with parameters and their values
  $VMInfo = @{
    ResourceGroupName = $ResourceGroupName;
    Name = $VMName;
    Location = $EnvLocation;
    ImageName = $ImageName;
    Size = $VMSize;
    VirtualNetworkName = $VirtualNetworkName;
    SubnetName = $SubnetName;
    SecurityGroupName = $SecurityGroupName;
    PublicIpAddressName = $PublicIpAddressName;
    Credential = $Cred;
    OpenPorts = $OpenPorts;
    #Verbose = $true
  }

  $VMRunCommandInfo = @{
    ResourceGroupName = $ResourceGroupName;
    VMName = $VMName;
    CommandId = 'RunPowerShellScript';
    ScriptPath = $ScriptFullNameAndPath
    Parameter = @{"AccessKey"=$AXAccessKey;"GroupName"=$AXGroupName}
  }

  # Spawn jobs for each VM
  $ScriptBlock = {
    # Get the passed in paramaters
    param ($VMInfo, $VMRunCommandInfo)

    # Spawn the VM
    New-AzVM @VMInfo

    # Execute the default script on the VM to load Automox
    Invoke-AzVMRunCommand @VMRunCommandInfo
  }

  $Job = Start-Job -ScriptBlock $ScriptBlock -ArgumentList $VMInfo,$VMRunCommandInfo
  Write-Output $Job
}
