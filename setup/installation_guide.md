# 🛠️ Installation Guide

This guide explains how to set up the environment required to run the Automated RDP Incident Response System.

---

## 🧩 Lab Environment Overview

The setup consists of:

- 1 Domain Controller (Windows Server)
- 1 Client Machine (Windows 10 Pro)
- 1 Attacker Machine (Ubuntu)
- Splunk Server
- Shuffle (Cloud)
- Ngrok (Tunnel)
- Telegram Bot

---

## 🖥️ 1. Virtual Machine Setup

### Required Machines

| Machine | OS | Purpose |
|--------|----|--------|
| Domain Controller | Windows Server | Active Directory |
| Client Machine | Windows 10 Pro | RDP Target |
| Attacker Machine | Ubuntu | Simulate RDP Login |
| Splunk Server | Ubuntu / Windows | SIEM |

---

## 🌐 2. Network Configuration

- All machines must be in the same network
- Recommended:
  - Adapter 1: NAT
  - Adapter 2: Internal Network / Bridged

Example IPs:
```text
DC:      192.168.1.12
Client:  192.168.1.20
Attacker:192.168.1.5
````

---

## 🏢 3. Active Directory Setup (Domain Controller)

### Install AD DS

```powershell
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
```

---

### Promote to Domain Controller

```powershell
Install-ADDSForest -DomainName "MasterShifu.local"
```

---

### Create User

```powershell
New-ADUser -Name "Tamala Yunfa" `
-SamAccountName TYunfa `
-UserPrincipalName TYunfa@MasterShifu.local `
-AccountPassword (ConvertTo-SecureString "Password" -AsPlainText -Force) `
-Enabled $true
```

---

## 🖥️ 4. Client Machine Setup

### Join Domain

* Go to:

```text
System → Change Settings → Domain
```

* Enter:

```text
MasterShifu.local
```

---

### Enable RDP

```powershell
Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
```

---

### Add User to RDP Group

```powershell
Add-LocalGroupMember -Group "Remote Desktop Users" -Member "MasterShifu\TYunfa"
```

---

## 📊 5. Splunk Installation

### Install Splunk

Download from:

```text
https://www.splunk.com/download
```

---

### Install Splunk Universal Forwarder (Client)

* Install on Windows Client
* Configure to send logs to Splunk Server

---

### Configure Inputs

Monitor Windows Event Logs:

```text
Security Logs
```

---

## 🔄 6. Shuffle Setup

* Register account:

```text
https://shuffler.io
```

---

### Create Workflow

* Add Webhook node
* Add Telegram node
* Add User Action (Email)
* Add HTTP node
* Add Confirmation Telegram node

---

## 🌐 7. Ngrok Setup

### Install ngrok

Download:

```text
https://ngrok.com/download
```

---

### Authenticate

```bash
ngrok config add-authtoken <your_token>
```

---

### Start Tunnel

```bash
ngrok http 8080
```

---

## 🧠 8. Python API Server Setup

### Install Python

```bash
python --version
```

---

### Run Server

```bash
cd C:\scripts
python server.py
```

---

## ⚡ 9. PowerShell Script Setup

Create file:

```text
C:\scripts\disable_user.ps1
```

---

### Content:

```powershell
param(
    [string]$username
)

Disable-ADAccount -Identity $username
Write-Output "SUCCESS: User $username disabled"
```

---

## 🔔 10. Telegram Bot Setup

1. Open Telegram → search **BotFather**
2. Create bot
3. Get API token
4. Use token in Shuffle

---

## 🧪 11. Testing Setup

### Perform RDP Login

From Ubuntu:

```bash
xfreerdp /v:192.168.1.20 /u:TYunfa /p:Password /d:MasterShifu
```

---

### Expected Result

* Splunk detects login
* Shuffle triggers alert
* Telegram message appears
* Email sent for decision

---

## 🔍 12. Verification

Check AD:

```powershell
Get-ADUser TYunfa -Properties Enabled
```

---

## Final Outcome

After setup, the system will:

1. Detect RDP login
2. Send alert
3. Request analyst decision
4. Disable user automatically
5. Confirm via Telegram

