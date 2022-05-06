## Set up Azure AX-Demo Environment

# NOTE: Please set the name to 10 characters or less and no spaces
# Location should be the Azure location for the environment Ex: centralus
param ($name, $location)

### Easy Button - Set Variables ###
$EnvName = $name
$EnvLocation = $location
### Easy Button - Complete ###


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
