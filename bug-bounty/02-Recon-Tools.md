# 🛠️ Phase 2: Reconnaissance (Finding the Target)

Recon is 90% of Bug Bounty. If you find something others missed, you find the bug.

### 1. Subdomain Discovery
- **Passive Recon:** Searching without touching the target's servers.
  - Tools: `subfinder`, `assetfinder`, `crt.sh`.
- **Active Recon:** Brute-forcing subdomains.
  - Tools: `ffuf`, `gobuster`, `amass`.

### 2. Directory Brute-forcing
- Finding hidden folders like `/admin`, `/.git`, `/.env`, `/backup`.
- Tool: `dirsearch -u <url> -e php,html,js,json`.

### 3. Port Scanning
- Finding open services that shouldn't be public.
- Tool: `nmap -sV <ip>`.

### 4. Visual Recon
- Taking screenshots of hundreds of subdomains to find interesting login pages.
- Tool: `httpx`, `aquatone`.

---
**Next Step:** Learn about different bug types in [03-Vulnerability-Types.md](./03-Vulnerability-Types.md).
