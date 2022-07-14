## Destroy Azure AX-Demo Environment

# NOTE: Please pass in the name of the CSV environment you want to create
param ($EnvCSVname)

# Load in the CSV environment file
$fileName = "./"+$EnvCSVname
$EnvConfig = Import-CSV -Path $fileName

# Set the expected RG name
$ResourceGroupName = $EnvConfig.EnvName + "-RG"

# Remove the RG and all child resources (Note: this may take a while)
Remove-AzResourceGroup -Name $ResourceGroupName -Force