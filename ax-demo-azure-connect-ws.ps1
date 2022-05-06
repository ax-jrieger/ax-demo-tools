## Set up Azure PS scripting from a workstation

# Install the required modules
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Install-Module -Name Az -Scope CurrentUser -Repository PSGallery -Force

# Authenticate
Connect-AzAccount
