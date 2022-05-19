## Destroy Azure AX-Demo Environment

# NOTE: Please pass in the name to the environment you want to destroy
# Env name only - script will append the conf for the conf file
param ($name)

# Load in the JSON config file (this is overkill, but is here for consistancy)
$fileName = "./"+$name+".conf"
$config = Get-Content -Path $fileName | ConvertFrom-Json

# Set the expected RG name
$ResourceGroupName = $config.name + "-RG"

# Remove the RG and all child resources (Note: this may take a while)
Remove-AzResourceGroup -Name $ResourceGroupName -Force