## Launch the VM's into the created environment

# NOTE: Please pass in the name of the CSV environment you want to create
param ($EnvCSVname)

# Load in the CSV environment file
$fileName = "./"+$EnvCSVname
$EnvConfig = Import-CSV -Path $fileName

# Load in the CSV VM information file
$fileName = "./"+$config.EnvVMInformationCSVFileName
$VMConfig = Import-CSV -Path $fileName

# Setting some internal variables so I dont need to keep changing them later
$EnvName = $EnvConfig.EnvName
$EnvLocation = $EnvConfig.AzureLocation

# Credentaials
$UserName = $WindowsUserName
$PasswordClear = $WindowsPasswordClear
$Password = ConvertTo-SecureString $passwordclear -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential ($username, $password)

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
