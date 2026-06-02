param(
    [string]$OutputPath = ".\windows_audit.json"
)

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

function New-Check {
    param(
        [string]$CheckId,
        [string]$Category,
        [string]$Name,
        [string]$Status,
        [string]$CurrentValue,
        [string]$RecommendedValue,
        [string]$Severity,
        [string]$Remediation,
        [hashtable]$ComplianceMappings
    )
    [ordered]@{
        check_id = $CheckId
        category = $Category
        name = $Name
        status = $Status
        current_value = $CurrentValue
        recommended_value = $RecommendedValue
        severity = $Severity
        evidence = $CurrentValue
        remediation = $Remediation
        compliance_mappings = $ComplianceMappings
    }
}

$firewallProfiles = Get-NetFirewallProfile -ErrorAction SilentlyContinue
$firewallEnabled = $firewallProfiles -and (($firewallProfiles | Where-Object { $_.Enabled -eq $false }).Count -eq 0)
$defender = Get-MpComputerStatus -ErrorAction SilentlyContinue
$bitlocker = Get-BitLockerVolume -ErrorAction SilentlyContinue
$admins = Get-LocalGroupMember -Group "Administrators" -ErrorAction SilentlyContinue

$checks = @()
$checks += New-Check "WIN-FIREWALL-001" "network" "Windows Firewall is enabled for all profiles" `
    $(if ($firewallEnabled) { "PASS" } else { "FAIL" }) `
    "Firewall profiles enabled: $firewallEnabled" "All firewall profiles enabled" "high" `
    "Enable Windows Firewall for Domain, Private, and Public profiles." `
    @{ cis="CIS Windows Firewall"; nist_800_53="SC-7"; iso_27001="A.8.20"; soc2="CC6" }

$checks += New-Check "WIN-DEFENDER-001" "endpoint_protection" "Microsoft Defender real-time protection is enabled" `
    $(if ($defender -and $defender.RealTimeProtectionEnabled) { "PASS" } else { "WARN" }) `
    "RealTimeProtectionEnabled=$($defender.RealTimeProtectionEnabled)" "Real-time protection enabled" "high" `
    "Enable Microsoft Defender or approved endpoint protection." `
    @{ cis="CIS Defender"; nist_800_53="SI-3"; iso_27001="A.8.7"; soc2="CC7" }

$checks += New-Check "WIN-BITLOCKER-001" "storage" "BitLocker encryption is enabled where required" `
    $(if ($bitlocker -and (($bitlocker | Where-Object { $_.ProtectionStatus -eq 'On' }).Count -gt 0)) { "PASS" } else { "WARN" }) `
    "BitLocker volumes found: $($bitlocker.Count)" "Protected fixed data and OS volumes" "medium" `
    "Enable BitLocker for devices that store sensitive business data." `
    @{ cis="CIS BitLocker"; nist_800_53="SC-28"; iso_27001="A.8.24"; gdpr="Article 32" }

$checks += New-Check "WIN-ADMINS-001" "identity" "Local Administrators group is reviewed" `
    "WARN" "Administrators: $($admins.Name -join ', ')" "Only approved admins are present" "medium" `
    "Review Local Administrators membership and remove stale or unauthorized accounts." `
    @{ cis="CIS Local Groups"; nist_800_53="AC-2"; iso_27001="A.5.18"; soc2="CC6" }

$payload = [ordered]@{
    scan_id = "windows-$([guid]::NewGuid().ToString('N').Substring(0,12))"
    client_name = "Local Assessment"
    hostname = $env:COMPUTERNAME
    os_family = "windows"
    os_version = (Get-CimInstance Win32_OperatingSystem).Caption
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
    collector = @{
        name = "windows-powershell-readonly"
        requires_admin = $true
        is_admin = $isAdmin
        mode = "audit-only"
    }
    checks = $checks
}

$payload | ConvertTo-Json -Depth 8 | Out-File -FilePath $OutputPath -Encoding UTF8
Write-Output $OutputPath

