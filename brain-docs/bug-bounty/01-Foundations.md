# 01 – Foundations (Hinglish)

## 1. Networking Basics (Quick Primer)
- **IP Address** – 4 octet decimal (e.g., `192.168.1.10`). IPv4 has 32 bits; IPv6 is 128‑bit hex notation (`2001:db8::1`).
- **Subnet Mask / CIDR** – network‑host division. `/24` means first 24 bits are network (`255.255.255.0`).
- **Ports** – 0‑65535. Common:
  - `80` – HTTP (unencrypted web)
  - `443` – HTTPS (encrypted web)
  - `22` – SSH (remote admin)
  - `3306` – MySQL database
  - `21` – FTP
- **TCP vs UDP** – TCP provides reliable ordered delivery (handshake), UDP is connection‑less and faster (used for DNS, VoIP).
- **Public vs Private IP** – Private ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) are not routable on the internet; useful for lab setups.

## 2. OSI Model & Security Relevance
| Layer | What it does | Typical bugs you see |
|-------|--------------|----------------------|
| 7 – Application | End‑user protocols (HTTP, FTP) | XSS, SQLi, SSRF |
| 6 – Presentation | Data formatting, encryption | MIME‑type mismatch |
| 5 – Session | Session management | Session fixation |
| 4 – Transport | TCP/UDP, ports | Rate‑limit bypass |
| 3 – Network | IP routing, subnets | IP‑based ACL flaws |
| 2 – Data Link | MAC addresses, switches | ARP spoofing (rare in web bounty) |
| 1 – Physical | Cables, hardware | Physical access (out of scope) |

## 3. HTTP Essentials (Hinglish)
- **Request Line** – `GET /path HTTP/1.1` (method, URI, version).
- **Headers** – key/value pairs, e.g., `User-Agent`, `Cookie`, `Referer`, `Host`.
- **Common Methods** – `GET` (read), `POST` (write), `PUT` (replace), `DELETE` (remove), `OPTIONS` (capabilities).
- **Status Codes** – `2xx` success, `3xx` redirect, `4xx` client error, `5xx` server error. Important ones:
  - `200 OK` – normal response
  - `302 Found` – redirect (often used in auth flows)
  - `403 Forbidden` – access denied (good for testing auth bypass)
  - `404 Not Found` – missing resource (useful for fuzzing)
  - `500 Internal Server Error` – server crashed (possible injection clue)
- **Common Mis‑configurations** – exposing `Server` header, `X-Powered-By`, missing `Content‑Security‑Policy` (CSP).

## 4. Linux Command‑Line Essentials for Hunters
```bash
# Navigation
ls -la                # list with permissions
cd /var/www/html        # go to web root

# Find interesting files (PHP, JS, config)
find . -type f \( -name "*.php" -o -name "*.js" -o -name "*.env" \) -print

# Quick HTTP request (curl)
curl -I https://target.com          # fetch headers only
curl -X POST -d "user=admin&pass=admin" https://target.com/login

# Netcat listener for reverse shells
nc -lvnp 4444
```
- **File permissions** – `chmod 644 file.php` (readable by web server), `chmod 755 script.sh` (executable).
- **Process monitoring** – `ps aux | grep php` to see running services.

## 5. Setting Up a Local Lab (Why & How)
1. **Why lab?** – Safe environment to practice without breaking any rules.
2. **Kali Linux** – pre‑installed pen‑test tools (`apt update && apt install <tool>`).
3. **Docker vulnerable apps** (quick spin‑up):
   - **OWASP Juice Shop** (full‑stack web app):
     ```bash
     docker run -d -p 3000:3000 bkimminich/juice-shop
     ```
   - **DVWA** (Deliberately Vulnerable Web App) – low/medium/high difficulty modes:
     ```bash
     docker run -d -p 80:80 vulnerables/web-dvwa
     ```
   - **WebGoat** (educational OWASP project):
     ```bash
     docker run -d -p 8080:8080 webgoat/webgoat-8.2
     ```
4. **Burp Suite Community** – intercepting proxy for modifying requests:
   ```bash
   java -jar burpsuite_community.jar
   ```
   Set your browser proxy to `127.0.0.1:8080`.

## 6. Legal & Ethical Basics (Never Forget)
- **Scope** – Test ONLY assets listed in program rules. Anything outside is *out‑of‑scope* and can be illegal.
- **No data exfiltration** – you may view data for proof, but never download large amounts or cause damage.
- **Responsible Disclosure** – submit via the platform, wait for triage, and do not publicize until the vendor fixes it.
- **Do not brute‑force login without explicit permission** – many platforms treat it as out‑of‑scope unless allowed.

---

### 📚 Recommended Reading / Videos (Beginner Friendly)
- *The Web Application Hacker's Handbook* – Chapters 1‑3 (HTTP basics & testing methodology).
- *LiveOverflow* – "Web Hacking Basics" (YouTube) – great visual intro.
- *PortSwigger Web Security Academy* – free labs for XSS, SQLi, SSRF, etc.
- *OWASP Juice Shop* walkthroughs – practice real‑world bugs.

Next module: **Recon Tools** – detailed guide on sub‑domain enumeration, port scanning, directory busting, and OSINT. 🚀