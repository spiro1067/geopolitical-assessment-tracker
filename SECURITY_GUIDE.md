# Email Security Guide

This guide explains how to securely configure email notifications for the Assessment Tracker.

## ⚠️ Security Concerns with App Passwords

Google App Passwords have several security issues:
- **No granular permissions** - Full account access
- **No automatic expiration** - Valid indefinitely
- **No activity logging** - Hard to audit usage
- **Plain text storage** - Stored unencrypted in JSON files
- **Revocation required** - Must manually revoke if compromised

## ✅ Recommended Secure Methods

### **Option 1: SendGrid API (Most Secure - Recommended)**

**Why this is best:**
- ✅ No password storage required
- ✅ API keys can be instantly revoked
- ✅ Granular permissions (send-only access)
- ✅ Professional email infrastructure
- ✅ Better deliverability rates
- ✅ Free tier: 100 emails/day

**Setup Steps:**

1. **Sign up for SendGrid:**
   ```
   https://signup.sendgrid.com/
   ```

2. **Verify your sender email:**
   - Go to Settings → Sender Authentication
   - Verify a single sender email (for free tier)

3. **Create an API key:**
   - Go to Settings → API Keys
   - Click "Create API Key"
   - Choose "Restricted Access"
   - Enable only "Mail Send" permission
   - Copy the API key (you'll only see it once!)

4. **Install SendGrid library:**
   ```bash
   pip install sendgrid --break-system-packages
   ```

5. **Set environment variables:**
   ```bash
   export SENDGRID_API_KEY='your-api-key-here'
   export EMAIL_FROM='your-verified-email@example.com'
   ```

6. **Make it permanent (add to ~/.bashrc or ~/.zshrc):**
   ```bash
   echo 'export SENDGRID_API_KEY="your-api-key-here"' >> ~/.bashrc
   echo 'export EMAIL_FROM="your-verified-email@example.com"' >> ~/.bashrc
   source ~/.bashrc
   ```

7. **Test it:**
   ```bash
   python3 weekly_reminder.py
   ```

**Cost:** Free for up to 100 emails/day (more than enough for weekly reminders)

---

### **Option 2: Environment Variables (Better Security)**

Instead of storing passwords in files, use environment variables.

**Why this is better:**
- ✅ Credentials not in files (won't accidentally commit to git)
- ✅ Separate from code
- ✅ Can use different credentials per environment
- ❌ Still requires App Password

**Setup Steps:**

1. **Create Gmail App Password** (if using Gmail):
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Assessment Tracker"
   - Copy the 16-character password

2. **Set environment variables:**
   ```bash
   export EMAIL_SMTP_SERVER='smtp.gmail.com'
   export EMAIL_SMTP_PORT='587'
   export EMAIL_USER='your_email@gmail.com'
   export EMAIL_PASSWORD='your_app_password'
   export EMAIL_FROM='your_email@gmail.com'
   ```

3. **Make it permanent (add to ~/.bashrc or ~/.zshrc):**
   ```bash
   cat >> ~/.bashrc << 'EOF'
   # Assessment Tracker Email Config
   export EMAIL_SMTP_SERVER='smtp.gmail.com'
   export EMAIL_SMTP_PORT='587'
   export EMAIL_USER='your_email@gmail.com'
   export EMAIL_PASSWORD='your_app_password_here'
   export EMAIL_FROM='your_email@gmail.com'
   EOF

   source ~/.bashrc
   ```

4. **Test it:**
   ```bash
   python3 weekly_reminder.py
   ```

**Security Best Practices:**
- Use `.bashrc` instead of storing in files
- Set proper file permissions: `chmod 600 ~/.bashrc`
- Never commit `.bashrc` to version control
- Rotate App Passwords regularly (every 90 days)

---

### **Option 3: email_config.json (Least Secure - Not Recommended)**

**Why this is risky:**
- ❌ Password stored in plain text
- ❌ Easily committed to version control by mistake
- ❌ Visible to anyone with file access
- ❌ No automatic expiration

**Only use this for:**
- Local development/testing
- Non-production environments
- When other options aren't available

**If you must use this method:**

1. **Create email_config.json:**
   ```bash
   cp email_config.json.example email_config.json
   nano email_config.json
   ```

2. **Add to .gitignore:**
   ```bash
   echo "email_config.json" >> .gitignore
   ```

3. **Set restrictive permissions:**
   ```bash
   chmod 600 email_config.json
   ```

4. **Rotate password frequently**

---

## 🔍 How the System Chooses Email Method

The `secure_email.py` module tries methods in this order:

1. **SendGrid API** - Checks for `SENDGRID_API_KEY` environment variable
2. **Environment Variables** - Checks for `EMAIL_*` environment variables
3. **email_config.json** - Falls back to JSON file if it exists
4. **Fails gracefully** - Shows helpful error message if none configured

You can check which method is active:
```bash
python3 secure_email.py
```

---

## 🛡️ Additional Security Recommendations

### **1. Use App-Specific Passwords (Gmail)**
Never use your main Google password for SMTP.

### **2. Enable 2-Factor Authentication**
Required for creating App Passwords in Gmail.

### **3. Monitor Email Activity**
Regularly check your account's security activity:
- Gmail: https://myaccount.google.com/security

### **4. Rotate Credentials Regularly**
Change API keys and App Passwords every 90 days.

### **5. Use Separate Email Accounts**
Consider a dedicated email account just for automated notifications.

### **6. Limit Permissions**
If using SendGrid, create restricted API keys with only "Mail Send" permission.

### **7. Monitor for Suspicious Activity**
Check logs regularly for unexpected email sending.

---

## 🚀 Quick Setup Commands

### **For SendGrid (Recommended):**
```bash
# Install SendGrid
pip install sendgrid --break-system-packages

# Set environment variables
export SENDGRID_API_KEY='your-api-key'
export EMAIL_FROM='verified-sender@yourdomain.com'

# Test
python3 weekly_reminder.py
```

### **For Environment Variables:**
```bash
# Setup guide
python3 secure_email.py setup-env

# Follow the instructions to add variables to ~/.bashrc
```

### **Check Current Configuration:**
```bash
python3 secure_email.py
```

---

## 📧 Alternative Email Services

If you want even better security, consider these professional services:

| Service | Free Tier | Security | Ease of Use |
|---------|-----------|----------|-------------|
| **SendGrid** | 100/day | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Mailgun** | 100/day | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Amazon SES** | 62,000/month | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Postmark** | 100/month | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Gmail SMTP** | Unlimited* | ⭐⭐ | ⭐⭐⭐⭐⭐ |

*Gmail has sending limits (500/day for free accounts, 2000/day for Workspace)

---

## ❓ Frequently Asked Questions

**Q: Can I use my regular Gmail password?**
A: No. You must use an App Password or switch to SendGrid.

**Q: What if I accidentally commit email_config.json to GitHub?**
A:
1. Immediately revoke the App Password at https://myaccount.google.com/apppasswords
2. Remove the file from git history: `git filter-branch --index-filter 'git rm --cached --ignore-unmatch email_config.json' HEAD`
3. Force push: `git push --force`
4. Create a new App Password

**Q: How do I switch from email_config.json to SendGrid?**
A:
1. Sign up for SendGrid and get API key
2. Set environment variable: `export SENDGRID_API_KEY='your-key'`
3. Delete or rename email_config.json
4. The system will automatically use SendGrid

**Q: Can I use multiple email methods at once?**
A: The system uses only one method, prioritizing the most secure available.

---

## 🔗 Useful Links

- **SendGrid Signup:** https://signup.sendgrid.com/
- **SendGrid API Keys:** https://app.sendgrid.com/settings/api_keys
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Gmail Security Checkup:** https://myaccount.google.com/security
- **Mailgun (Alternative):** https://www.mailgun.com/
- **Amazon SES (Alternative):** https://aws.amazon.com/ses/

---

**Last Updated:** January 2026
**Recommended Method:** SendGrid API with environment variables
