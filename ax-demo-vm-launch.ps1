## Launch the VM's into the created environment

param($name)

# Load in the JSON config file
$fileName = "./"+$name+".conf"
$config = Get-Content -Path $fileName | ConvertFrom-Json

# Setting some internal variables so I dont need to keep changing them later
$EnvName = $config.name
$EnvLocation = $config.location
$WindowsUserName = $config.winusername
$WindowsPasswordClear = $config.winpass
$NumberOfVM = $config.number
$AXAccessKey = $config.axaccesskey
$AXGroupName = $config.axgroup

# Credentaials
$UserName = $WindowsUserName
$PasswordClear = $WindowsPasswordClear
$Password = ConvertTo-SecureString $passwordclear -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential ($username, $password)

# Set Image Information
$pubName = "MicrosoftWindowsDesktop"
$offerName = "Windows-10"
$skuName = "win10-21h2-pro-g2"
$version = "latest"

# Build the Image name to launch
$ImageName = $pubName + ":" + $offerName + ":" + $skuName + ":" + $version

# Create the VM Config and Launch
$ResourceGroupName = $EnvName + "-RG"
$VMSize = "Standard_DS1"
$VirtualNetworkName = $EnvName + "-VN"
$SubnetName = $EnvName + "-SN"
$SecurityGroupName = $EnvName + "-NSG"
$OpenPorts = 3389

# Script path for the AX load script
$ScriptFileName = "ax-demo-script-automox-windows.ps1"
$ScriptFullNameAndPath = Join-Path $PSScriptRoot $ScriptFileName
#Write-Output $ScriptFullNameAndPath

for ($num = 1; $num -lt $NumberOfVM+1; $num++) {
  # Start working through the names of the VM and Public IP assignments
  $VMName = $EnvName + "-VM" + $num
  $PublicIpAddressName = $EnvName + "-PIP" + $num

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
