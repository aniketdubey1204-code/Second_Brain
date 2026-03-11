# 02 – Recon Tools (Hinglish)

**Recon** target ko locate aur map karne ka pehla kadam hai. Yahan aap sub‑domains, hidden endpoints, open ports, aur technology stack discover karte ho – jo aage ke vulnerability testing ko focused banata hai.

## 2.1 Sub‑domain Enumeration
| Tool | Command | When to use |
|------|---------|-------------|
| **Sublist3r** | `sublist3r -d target.com -o subdomains.txt` | Quick list from many public sources |
| **Amass** | `amass enum -d target.com -o amass.txt` | Deep passive + active enumeration |
| **Assetfinder** | `assetfinder --subs-only target.com > assets.txt` | Very fast, simple |
| **MassDNS** | `massdns -r resolvers.txt -t A -q subdomains.txt -o S > results.txt` | Bulk DNS resolution for large lists |

## 2.2 Wayback Machine & Archive.org
- **waybackurls** – gathers historic URLs:
  ```bash
  waybackurls target.com > wayback.txt
  ```
- **gau** – pulls from Wayback, CommonCrawl, etc.:
  ```bash
  gau --providers wayback,commoncrawl target.com > gau.txt
  ```

## 2.3 Port Scanning & Service Fingerprinting
| Tool | Command | What you get |
|------|---------|-------------|
| **Nmap** | `nmap -sS -sV -p- -T4 target.com -oN nmap.txt` | Open ports + service versions |
| **Masscan** | `masscan -p1-65535 target.com --rate=1000 -oX masscan.xml` | Super‑fast port list (feed to Nmap) |
| **Rustscan** | `rustscan -a target.com -b 5000 -- -sV -oN rustscan.txt` | Fast discovery + version info |

## 2.4 Directory & File Brute‑Forcing
| Tool | Command |
|------|---------|
| **Dirsearch** | `python3 dirsearch.py -u https://target.com -e php,js,html -x 403,404` |
| **Gobuster** | `gobuster dir -u https://target.com -w /usr/share/wordlists/dirb/common.txt -x php,js,txt` |
| **FFUF** | `ffuf -u https://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,302` |

## 2.5 Technology Fingerprinting
- **Wappalyzer** – browser extension for quick UI view.
- **WhatWeb** – CLI:
  ```bash
  whatweb -v https://target.com > whatweb.txt
  ```
- **BuiltWith** – web lookup for deeper stack info.

## 2.6 Open‑Source Intelligence (OSINT)
- **Google Dorking** – e.g., `site:target.com inurl:admin`.
- **Shodan** – `shodan host <IP>` for device‑level data.
- **hakrawler** – crawl internal links:
  ```bash
  hakrawler -url https://target.com -depth 3 -plain -output urls.txt
  ```

## 2.7 Automation Snippet (Bash)
```bash
#!/usr/bin/env bash
TARGET=$1
sublist3r -d $TARGET -o subdomains.txt
amass enum -d $TARGET -o amass.txt
cat subdomains.txt amass.txt | sort -u > all_subs.txt
nmap -sS -sV -iL all_subs.txt -oN nmap.txt
```

---

**Tip:** Always store results in a `recon/` folder (e.g., `recon/subdomains.txt`, `recon/ports.txt`) – easier to reference later when writing reports.

Next module: **Vulnerability Types** – where we dive into XSS, SQLi, SSRF, और बहुत कुछ! 🚀