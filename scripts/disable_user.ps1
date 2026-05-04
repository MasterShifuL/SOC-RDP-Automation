param(
    [string]$username
)

Import-Module ActiveDirectory

try {
    Disable-ADAccount -Identity $username
    Write-Output "SUCCESS: User $username disabled"
}
catch {
    Write-Output "ERROR: $_"
}
