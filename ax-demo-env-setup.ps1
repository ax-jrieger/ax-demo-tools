## Set up Azure AX-Demo Environment

# NOTE: Please pass in the name of the CSV environment you want to create
param ($EnvCSVname)

# Load in the CSV environment file
$fileName = "./"+$EnvCSVname
$EnvConfig = Import-CSV -Path $fileName

# Load in the CSV VM information file (Not needed for this file, but maintaining load path for consistancy and error checking)
$fileName = "./"+$config.EnvVMInformationCSVFileName
$VMConfig = Import-CSV -Path $fileName

# Setting some internal variables so I dont need to keep changing them later
$EnvName = $EnvConfig.EnvName
$EnvLocation = $EnvConfig.AzureLocation

### Main Script - Modifications here will break future assumptions based on the EnvName variable - please modify with care
$ResourceGroupName = $EnvName + "-RG"
$ResourceGroupLocation = $EnvLocation

## Create new Resource Group
New-AzResourceGroup `
    -Name $ResourceGroupName `
    -Location $ResourceGroupLocation

## Create the new network
$VirtualNetworkName = $EnvName + "-VN"
$NewVirtualNetwork = New-AzVirtualNetwork `
                        -Name $VirtualNetworkName `
                        -ResourceGroupName $ResourceGroupName `
                        -Location $ResourceGroupLocation `
                        -AddressPrefix '10.0.0.0/16'    

## Create a subnet configuration
$VirtualNetworkSubnetConfigName = $EnvName + "-SN"
Add-AzVirtualNetworkSubnetConfig `
    -Name $VirtualNetworkSubnetConfigName `
    -VirtualNetwork $NewVirtualNetwork `
    -AddressPrefix '10.0.0.0/24'

# Associate the subnet config 
$NewVirtualNetwork | Set-AzVirtualNetwork

## Create a Network Security Group
# Create an inbound RDP rule (Optional)
$NSGRuleRdp = New-AzNetworkSecurityRuleConfig `
                -Name rdp-rule `
                -Description "Allow RDP" `
                -Access Allow `
                -Protocol Tcp `
                -Direction Inbound `
                -Priority 100 `
                -SourceAddressPrefix Internet `
                -SourcePortRange * `
                -DestinationAddressPrefix * `
                -DestinationPortRange 3389

# Create the NSG
# Comment out the SecurityRules line to skip adding a port for RDP
$NetworkSecurityGroupName = $EnvName + "-NSG"
New-AzNetworkSecurityGroup `
    -Name $NetworkSecurityGroupName `
    -ResourceGroupName $ResourceGroupName `
    -Location $ResourceGroupLocation `
    -SecurityRules $NSGRuleRdp
