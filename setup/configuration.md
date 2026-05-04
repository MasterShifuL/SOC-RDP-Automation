# ⚙️ Configuration Guide

This document explains how each component in the SOC automation pipeline is configured and integrated.

---

## 🧩 System Overview

This project integrates the following components:

- Splunk (SIEM)
- Shuffle (SOAR)
- Active Directory (Domain Controller)
- Python API Server
- PowerShell Script
- Ngrok (secure tunnel)
- Telegram Bot
- Email (User Action)

---

## 🖥️ 1. Active Directory Configuration

### Create User

```powershell
New-ADUser -Name "Tamala Yunfa" `
-SamAccountName TYunfa `
-UserPrincipalName TYunfa@MasterShifu.local `
-AccountPassword (ConvertTo-SecureString "Minin12345_" -AsPlainText -Force) `
-Enabled $true
````

---

### Add User to RDP Group

```powershell
Add-ADGroupMember "Remote Desktop Users" TYunfa
```

---

### Enable RDP on Client Machine

```powershell
Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
Restart-Service TermService -Force
```

---

## 📊 2. Splunk Configuration

### SPL Detection Query

```spl
index=MasterShifu-ad EventCode=4624 (Logon_Type=10 OR Logon_Type=7)
| eval user=coalesce(TargetUserName, Account_Name, user)
| eval user=mvfilter(NOT match(user, "\$"))
| search user!="ANONYMOUS LOGON" user!="SYSTEM"
| dedup user Source_Network_Address
| eval readable_time=strftime(_time, "%Y-%m-%d %H:%M:%S")
| stats count by ComputerName, Source_Network_Address, user, Logon_Type, readable_time
```

---

### Alert Configuration

* Trigger: **Number of Results > 0**
* Schedule: **Every 1 minute**
* Time Range: **Last 2 minutes**
* Action: **Webhook**

---

## 🔄 3. Shuffle (SOAR) Configuration

### Workflow Components

The workflow includes:

* Webhook (from Splunk)
* Telegram Alert Node
* User Action (Email)
* Disable Webhook
* HTTP Node (API call)
* Telegram Confirmation Node

---

### User Action Email Content

```text
🚨 RDP Alert - Action Required

User: ${exec.result.user}
Time: $exec.result.readable_time
IP: ${exec.result.Source_Network_Address}

Disable User:
https://shuffler.io/api/v1/hooks/<disable_webhook>?user=${exec.result.user}

Ignore:
https://shuffler.io/api/v1/hooks/<ignore_webhook>
```

---

### HTTP Node Configuration

```text
Method: GET
URL: https://<ngrok-url>/?user=${trigger.query.user}
```

---

## 🌐 4. Ngrok Configuration

### Start Tunnel

```bash
ngrok http 8080
```

---

### Example Output

```text
Forwarding https://xxxx.ngrok-free.dev -> http://localhost:8080
```

---

## 🧠 5. Python API Server

Location:

```text
C:\scripts\server.py
```

Run server:

```bash
python server.py
```

Expected output:

```text
[START] Server running on 0.0.0.0:8080
```

---

## ⚡ 6. PowerShell Script

Location:

```text
C:\scripts\disable_user.ps1
```

Content:

```powershell
param(
    [string]$username
)

Disable-ADAccount -Identity $username
Write-Output "SUCCESS: User $username disabled"
```

---

## 🔔 7. Telegram Bot Configuration

* Create bot via BotFather
* Get bot token
* Configure in Shuffle Telegram node

---

## 📧 8. Email (User Action)

* Configure email integration in Shuffle
* Used for human approval (Disable / Ignore)

---

## 🔍 9. Verification

### Check if user is disabled:

```powershell
Get-ADUser TYunfa -Properties Enabled
```

Expected:

```text
Enabled : False
```

---

### Test RDP Login Again

```bash
xfreerdp /v:192.168.1.20 /u:TYunfa /p:Minin12345_ /d:MasterShifu
```

Expected:

```text
Login failed
```

---

## Final Result

After configuration, the system performs:

1. Detect RDP login
2. Send alert
3. Analyst decision
4. Disable user automatically
5. Confirm action
