### Set variables for the VM ###

# UUID of the Automox Environment you want to attach to
$AccessKey = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

# Group name in Automox that this system should default to
$GroupName = "GROUPNAMEHERE"

# Parent group name for the Group name above (Only required if you are using nested groups)
#$ParentGroupName = "Default"
###

$DownloadFileURL = "https://patch.automox.com/rs/923-VQX-349/images/Install-AxAgentMsi.ps1"
$DownloadFileLocation = "c:\Install-AxAgentMsi.ps1"
Set-ExecutionPolicy Unrestricted -Force
(new-object net.webclient).DownloadFile($DownloadFileURL,$DownloadFileLocation)
c:\Install-AxAgentMsi.ps1 -AccessKey $AccessKey -GroupName $GroupName #-ParentGroupName $ParentGroupName
