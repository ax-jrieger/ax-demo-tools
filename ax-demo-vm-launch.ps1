## Launch the VM's into the created environment

param ($name, $location, $winusername, $winpass)

### Easy Button - Set Variables ###
# NOTE: This should be set the same as the EnvName variable used in the environemnt setup script

$EnvName = $name
$EnvLocation = $location
$WindowsUserName = $winusername
$WindowsPasswordClear = $winpass

### Easy Button - Complete ###


### Main Script - Modifications here will break assumptions based on the EnvName variable - please modify with care

# Credentaials
$UserName = $WindowsUserName
$PasswordClear = $WindowsPasswordClear
$Password = ConvertTo-SecureString $passwordclear -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential ($username, $password)

# Set Image Information
$pubName = "MicrosoftWindowsDesktop"
$offerName = "Windows-10"
$skuName = "win10-21h2-pro-g2"
$version = "19044.1586.220303"

# Build the Image name to launch
$ImageName = $pubName + ":" + $offerName + ":" + $skuName + ":" + $version

# Create the VM Config and Launch
$ResourceGroupName = $EnvName + "-RG"
$VMName = $EnvName + "-VM2"
$VMSize = "Standard_DS1"
$VirtualNetworkName = $EnvName + "-VN"
$SubnetName = $EnvName + "-SN"
$SecurityGroupName = $EnvName + "-NSG"
$PublicIpAddressName = $EnvName + "-PIP2"
$OpenPorts = 3389

New-AzVM `
  -ResourceGroupName $ResourceGroupName `
  -Name $VMName `
  -Location $EnvLocation `
  -ImageName $ImageName `
  -Size $VMSize `
  -VirtualNetworkName $VirtualNetworkName `
  -SubnetName $SubnetName `
  -SecurityGroupName $SecurityGroupName `
  -PublicIpAddressName $PublicIpAddressName `
  -Credential $Cred `
  -OpenPorts $OpenPorts `
  -Verbose

# Execute the default script on the VM to load Automox
$ScriptPath = "ax-demo-script-automox-windows.ps1"
Invoke-AzVMRunCommand `
  -ResourceGroupName $ResourceGroupName `
  -VMName $VMName `
  -CommandId 'RunPowerShellScript' `
  -ScriptPath $ScriptPath

#-Parameter @{param1 = "var1"; param2 = "var2"}


  