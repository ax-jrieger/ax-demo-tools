## Destroy Azure AX-Demo Environment

# NOTE: Please pass in the name to the environment you want to destroy
param ($name)

### Easy Button - Set Variables ###
# NOTE: This should be set the same as the EnvName variable used in the environemnt setup script
$EnvName = $name
### Easy Button - Complete ###

# Set the expected RG name
$ResourceGroupName = $EnvName + "-RG"

# Remove the RG and all child resources (Note: this may take a while)
Remove-AzResourceGroup -Name $ResourceGroupName -Force