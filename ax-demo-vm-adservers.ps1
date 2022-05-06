### Set the variables ###

# Set the password to be used for the default admin account (this is stored in clear text in this script so be aware)
$SafeModeAdministratorPasswordClear = "PASSWORDHERE"

# Set the Active Directory Domain (FQDN)
$ADFQDN = "FQDNHERE"

# Set the AD NETBIOS name
$ADNetBIOSName = "NETBIOSNAMEHERE"

###

# Install the services
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools

# Create Secure String for AD Safe Mode Password
$SafeModeAdministratorPasswordSecure = ConvertFrom-SecureString -SecureString $SafeModeAdministratorPasswordClear

Install-ADDSForest `
    -DomainName $ADFQDN `
    -InstallDNS `
    -Force `
    -SafeModeAdministratorPassword $SafeModeAdministratorPasswordSecure `
    -DomainNetBiosName $ADNetBIOSName `
    -NoRebootCompletion
