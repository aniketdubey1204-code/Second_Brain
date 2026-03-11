# 05 – Reporting Templates (Hinglish)

A **well‑structured report** is the key to getting paid fast and getting your bug accepted. नीचे ready‑to‑use markdown templates दिए गए हैं – बस अपने target‑specific details fill करो और platform ke report box में paste करो.

---

## 📄 How to Use These Templates
1. **Copy the entire template** you need (RCE, XSS, SQLi, etc.).
2. **Replace placeholders** (`<TARGET_URL>`, `<PAYLOAD>`, `<SHELL>`, etc.) with your actual values.
3. **Add screenshots** (use Burp's "Copy as PNG" or take a screenshot with Snipping Tool) – attach them in the platform UI.
4. **Optional video** – 30‑sec proof of exploit (use `ffmpeg -f x11grab -i :0.0 -t 30 -c:v libx264 out.mp4`).
5. **Submit** via the platform’s “New Report” form, select appropriate severity, and hit submit.

---

## 📄 Template 1 – Remote Code Execution (RCE) via Unauthenticated File Upload
```markdown
**Title:** Remote Code Execution via Unauthenticated File Upload
**Severity:** Critical (Remote Code Execution)

**Summary:**
A vulnerable file‑upload endpoint allows an attacker to upload a malicious PHP web‑shell without authentication. The uploaded shell can be accessed at `<TARGET_URL>/uploads/<SHELL>.php` and provides full command execution on the server.

**Steps to Reproduce:**
1. Send a POST request to `<TARGET_URL>/api/upload` with `multipart/form-data` containing the file `shell.php` (see PoC below).
2. Receive HTTP 200 response containing the file path.
3. Access `<TARGET_URL>/uploads/<SHELL>.php?cmd=id` – server returns system user info.

**Proof‑of‑Concept (cURL):**
```bash
curl -X POST "<TARGET_URL>/api/upload" \
  -F "file=@shell.php"
```
**shell.php** (simple web‑shell):
```php
<?php system($_GET['cmd']); ?>
```

**Technical Details:**
- **Endpoint:** `<TARGET_URL>/api/upload`
- **Method:** POST (multipart/form-data)
- **Response:** `{ "status": "success", "path": "/uploads/<SHELL>.php" }`
- **Impact:** Full server control – attacker can read/write files, pivot to internal network, steal credentials.

**Remediation:**
- Enforce whitelist of allowed file types (e.g., only image MIME types).
- Store uploads outside web root or rename them using a random hash.
- Require authentication and rate‑limit on upload endpoint.
- Validate file content (use `getimagesize()` for images).

**References:**
- OWASP File Upload Cheat Sheet – https://owasp.org/www-project-cheat-sheets/cheatsheets/File_Upload_Cheat_Sheet.html
```
---

## 📄 Template 2 – Reflected XSS in Search Parameter
```markdown
**Title:** Reflected XSS in Search Parameter
**Severity:** Medium (XSS)

**Summary:**
The `q` parameter of the search page reflects user input without proper encoding, leading to a reflected XSS that can steal session cookies of logged‑in users.

**Steps to Reproduce:**
1. Visit `<TARGET_URL>/search?q=<script>alert('XSS')</script>`.
2. The alert dialog appears, confirming script execution.

**Proof‑of‑Concept (Burp Repeater):**
```
GET /search?q=%3Cscript%3Ealert('XSS')%3C/script%3E HTTP/1.1
Host: <TARGET_HOST>
User-Agent: Mozilla/5.0
```

**Technical Details:**
- **Vulnerable parameter:** `q`
- **Response snippet:** `<div class="result">Search results for <script>alert('XSS')</script></div>`
- **Impact:** Can steal cookies (`document.cookie`) and perform actions on behalf of the victim.

**Remediation:**
- Encode output using `htmlspecialchars()` or equivalent.
- Implement a strong Content‑Security‑Policy (`Content‑Security‑Policy: default-src 'self'; script-src 'self'`).
- Validate and sanitize input on server side.

**References:**
- OWASP XSS – https://owasp.org/www-community/attacks/xss/
```
---

## 📄 Template 3 – Union‑Based SQL Injection in `id` Parameter
```markdown
**Title:** Union‑Based SQL Injection in `id` Parameter
**Severity:** High (SQLi)

**Summary:**
The `id` GET parameter is concatenated directly into an SQL query, allowing a union‑based injection that extracts the `users` table (`username` & `password` hashes).

**Steps to Reproduce:**
1. Request `<TARGET_URL>/profile?id=1 UNION SELECT username,password FROM users-- `.
2. Application returns a table with all usernames and password hashes.

**Proof‑of‑Concept (sqlmap):**
```bash
sqlmap -u "<TARGET_URL>/profile?id=1" --dump -D <DB_NAME> -T users
```

**Technical Details:**
- **Vulnerable query (approx):** `SELECT * FROM profiles WHERE id = $GET[id];`
- **Injected payload:** `1 UNION SELECT username,password FROM users--`
- **Impact:** Exposure of all user credentials; potential credential reuse.

**Remediation:**
- Use prepared statements / parameterized queries (`PDO`, `mysqli` with bound params).
- Apply least‑privilege principle to DB user (no `SELECT *` on `users`).
- Validate numeric parameters (`is_numeric()`).

**References:**
- OWASP SQL Injection Prevention Cheat Sheet – https://owasp.org/www-project-cheat-sheets/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
```
---

## 📄 Template 4 – Server‑Side Request Forgery (SSRF) via Image Preview
```markdown
**Title:** SSRF via Image URL Parameter
**Severity:** High (SSRF)

**Summary:**
The `img` parameter of the image preview endpoint fetches external URLs without any validation, allowing internal network probing and potential access to cloud metadata services.

**Steps to Reproduce:**
1. Request `<TARGET_URL>/preview?img=http://127.0.0.1:3306`.
2. Server returns MySQL error page, confirming internal request.
3. Using a DNS‑logging service (e.g., `burpcollaborator`), send `<TARGET_URL>/preview?img=http://<COLLAB_SUBDOMAIN>.burpcollaborator.net` and see inbound request.

**Proof‑of‑Concept (curl):**
```bash
curl "<TARGET_URL>/preview?img=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
```

**Technical Details:**
- **Vulnerable parameter:** `img`
- **Server side request:** `file_get_contents($_GET['img'])`
- **Impact:** Can access internal services (databases, admin panels) or cloud metadata (AWS IAM credentials).

**Remediation:**
- Whitelist allowed domains (e.g., only `images.cdn.com`).
- Validate URL schema (allow only `https`).
- Use an outbound proxy with domain allowlist.

**References:**
- OWASP SSRF – https://owasp.org/www-project-web-security-testing-guide/v41/4-Web_Application_Security_Testing/12-Server_Side_Request_Forgery.html
```
---

## 📄 Template 5 – Insecure Direct Object Reference (IDOR) in Profile Endpoint
```markdown
**Title:** IDOR – User Profile Enumeration via `id` Parameter
**Severity:** Medium (IDOR)

**Summary:**
Changing the numeric `id` parameter in `/profile?id=12345` returns another user's private profile data without any authorization check.

**Steps to Reproduce:**
1. Authenticate as a normal user and note your own profile URL (`/profile?id=56789`).
2. Increment the ID to `56790`, `56791`, etc., and observe that other users' emails and phone numbers are exposed.

**Proof‑of‑Concept (Burp Intruder):**
- Set payload list: `56790-56820`
- Run Intruder against the `id` parameter – many responses contain full user details.

**Technical Details:**
- **Vulnerable endpoint:** `/profile?id=<USER_ID>`
- **Missing check:** No server‑side verification that the logged‑in user owns the requested ID.
- **Impact:** Disclosure of personal data (PHI, PII) – could be GDPR violation.

**Remediation:**
- Enforce strict access control: compare authenticated user ID with requested resource ID.
- Return generic error (`403 Forbidden`) for unauthorized access.

**References:**
- OWASP IDOR – https://owasp.org/www-project-web-security-testing-guide/v41/4-Web_Application_Security_Testing/09-Access_Control_Testing/03-Testing_for_Insecure_Direct_Object_Reference.html
```
---

## 📄 Template 6 – Cross‑Site Request Forgery (CSRF) on Money Transfer
```markdown
**Title:** CSRF on Money Transfer Endpoint
**Severity:** Medium (CSRF)

**Summary:**
The `/transfer` endpoint processes POST requests without verifying a CSRF token, allowing an attacker to force a logged‑in user to transfer funds to the attacker’s account.

**Steps to Reproduce:**
1. Log in as a victim user and capture the POST request for a legitimate transfer using Burp.
2. Remove the CSRF token from the request and replace the `to_account` value with `attacker_account`.
3. Host a malicious HTML page with an auto‑submitting form:
```html
<html>
<body onload="document.forms[0].submit()">
<form action="https://<TARGET_HOST>/transfer" method="POST">
<input type="hidden" name="amount" value="1000"/>
<input type="hidden" name="to_account" value="ATTACKER_ACC"/>
</form>
</body>
</html>
```
4. When the victim visits the page while logged in, the transfer is executed.

**Technical Details:**
- **Missing protection:** No `SameSite` cookie flag, no anti‑CSRF token.
- **Impact:** Unauthorized fund transfer.

**Remediation:**
- Implement anti‑CSRF tokens (synchronizer token pattern).
- Set cookies with `SameSite=Strict` or `Lax`.
- Validate request origin header.

**References:**
- OWASP CSRF – https://owasp.org/www-community/attacks/csrf
```
---

## 📚 Using the Templates Effectively
- **Copy‑Paste** the whole block into the platform’s markdown editor – most platforms (HackerOne, Bugcrowd) support markdown.
- **Replace placeholders** (`<TARGET_URL>`, `<SHELL>`, `<COLLAB_SUBDOMAIN>`) with actual values.
- **Attach screenshots** right after the relevant step (most platforms let you drag‑and‑drop).
- **Add a short video** (optional) – platforms often have a “Upload file” button.
- **Select correct severity** based on impact and platform guidelines.

---

### 📖 Additional Resources
- *PortSwigger Academy – “Writing Effective Bug Reports”* (free).
- *John Hammond – “Bug Bounty Report Writing”* (YouTube).
- *OWASP Bug Bounty Cheat Sheet* – checklist before submission.

Follow these templates, keep them tidy, और payouts आसानी से मिलेंगे! 🚀