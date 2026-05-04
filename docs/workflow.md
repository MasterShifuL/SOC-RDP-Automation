# 🔄 Workflow Explanation

This document explains how the Automated RDP Incident Response System works step-by-step, from detection to response.

---

## 🧠 Overview

This workflow simulates a real Security Operations Center (SOC) process by combining:

- Detection (Splunk SIEM)
- Automation (Shuffle SOAR)
- Human Decision (Email approval)
- Response (Active Directory user disable)

---

## 📊 Step 1: Event Generation (RDP Login)

A user performs a Remote Desktop Protocol (RDP) login to a Windows machine.

- Windows logs this event as:
```text
Event ID: 4624
Logon Type: 10 (Remote Interactive)
````

This event is recorded in the Windows Security Event Log.

---

## 📥 Step 2: Log Collection (Splunk)

* Splunk Universal Forwarder collects Windows Security logs
* Logs are sent to Splunk SIEM
* Splunk indexes the data in:

```text
index=MasterShifu-ad
```

---

## 🔍 Step 3: Detection (Splunk SPL)

Splunk runs a scheduled search using the following SPL:

```spl
index=MasterShifu-ad EventCode=4624 (Logon_Type=10 OR Logon_Type=7)
| eval user=coalesce(TargetUserName, Account_Name, user)
| eval user=mvfilter(NOT match(user, "\$"))
| search user!="ANONYMOUS LOGON" user!="SYSTEM"
| dedup user Source_Network_Address
| eval readable_time=strftime(_time, "%Y-%m-%d %H:%M:%S")
| stats count by ComputerName, Source_Network_Address, user, Logon_Type, readable_time
```

### Detection Logic:

* Detect successful logins (Event ID 4624)
* Focus on RDP sessions (Logon Type 10)
* Filter out:

  * Machine accounts (`$`)
  * SYSTEM accounts
  * Anonymous logons
* Convert timestamp into human-readable format

---

## 🚨 Step 4: Alert Trigger

When results are found:

* Splunk triggers an alert
* Alert sends data via webhook to Shuffle

Data sent includes:

```text
User
Source IP
Computer Name
Time
```

---

## 🔄 Step 5: Workflow Execution (Shuffle)

Shuffle receives the webhook and starts the automation workflow.

---

### 📢 5.1 Telegram Notification

Shuffle sends an alert message to Telegram:

```text
🚨 RDP ALERT 🚨
User: TYunfa
Time: 2026-05-03 22:23:48
Source IP: 192.168.1.5
```

Purpose:

* Provide real-time visibility
* Notify SOC analyst immediately

---

### 📧 5.2 Email with User Action

Shuffle sends an email containing:

* Alert details
* Two decision links:

  * Disable User
  * Ignore

Example:

```text
Disable:
https://shuffler.io/api/v1/hooks/.../?user=TYunfa

Ignore:
https://shuffler.io/api/v1/hooks/...
```

Purpose:

* Allow human decision (approval-based response)
* Prevent automatic false positives

---

## 👨‍💻 Step 6: Analyst Decision

The SOC analyst reviews the alert and chooses:

### Option 1: Ignore

* Workflow stops
* No action is taken

---

### Option 2: Disable User

* Shuffle triggers the "Disable Webhook"
* Workflow continues to response phase

---

## 🌐 Step 7: API Request (Ngrok + Python)

Shuffle sends a request to the API server:

```text
https://<ngrok-url>/?user=TYunfa
```

Flow:

```text
Shuffle → Ngrok → Python Server
```

---

## ⚙️ Step 8: PowerShell Execution

The Python server:

1. Receives the request
2. Extracts the username
3. Executes PowerShell:

```powershell
Disable-ADAccount -Identity TYunfa
```

---

## 🏢 Step 9: Active Directory Response

* Active Directory disables the user account
* The account can no longer log in

---

## 📢 Step 10: Confirmation Notification

Shuffle sends a confirmation message via Telegram:

```text
🚨 Account Information 🚨
User TYunfa has been DISABLED successfully
```

---

## 🔍 Step 11: Verification

The result can be verified using:

```powershell
Get-ADUser TYunfa -Properties Enabled
```

Expected output:

```text
Enabled : False
```

---

## 🔄 Complete Workflow Summary

```text
RDP Login
→ Windows Event Log (4624)
→ Splunk Detection
→ Shuffle Webhook Trigger

→ Telegram Alert
→ Email Decision (User Action)

→ Analyst Decision
    → Ignore → Stop
    → Disable → Continue

→ API Server (Python)
→ PowerShell Execution
→ Active Directory Disable User

→ Telegram Confirmation
→ Verification
```

---

## 🧠 Key Concepts Demonstrated

* SIEM-based detection (Splunk)
* SOAR automation (Shuffle)
* Human-in-the-loop decision making
* Active Directory response automation
* Secure API integration via ngrok
* End-to-end incident response pipeline

---

## 🎯 Conclusion

This workflow demonstrates how detection, alerting, decision-making, and response can be integrated into a single automated pipeline, closely simulating real-world SOC operations.

The system balances automation with human control, ensuring both efficiency and accuracy in handling security incidents.
