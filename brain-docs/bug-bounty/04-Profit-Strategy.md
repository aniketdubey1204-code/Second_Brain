# 04 – Profit Strategy (Hinglish)

Finding bugs is fun, lekin **money** kamaana भी ज़रूरी है. इस मॉड्यूल में हम बतायेंगे कैसे high‑paying programs चुनें, बग्स को prioritize करें, और रिपोर्ट को ऐसे लिखें कि payout बढ़े.

---

## 4.1 Choosing the Right Program (Where to Hunt)
| Platform | Public / Private | Typical payout range |
|----------|-------------------|----------------------|
| **HackerOne** | दोनों (public + private) | $50 – $10,000+ |
| **Bugcrowd** | दोनों | $100 – $5,000 |
| **Intigriti** | Public (EU focus) | €50 – €8,000 |
| **Open Bug Bounty** | Public, no‑pay | Reputation points |
| **ZeroDay Initiative** | High‑value 0‑day | $5k – $150k |

**Tips for program selection:**
- **Public programs** have many hunters, competition high, payouts moderate.
- **Private/Invite‑only** programs often target niche SaaS or fintech – payouts higher, कम competition.
- Look for **scope depth** – sub‑domains, APIs, mobile SDKs increase surface area.
- Check **bounty caps** (max per bug) in program policy.

---

## 4.2 Prioritising Bugs for Profit (What to Hunt First)
1. **Critical / High severity** – Remote Code Execution, Authentication Bypass, SSRF to internal services.
   - Expected payout: $500‑$5k (or more).
2. **Medium severity** – XSS, IDOR, Open Redirect, Business Logic edge cases.
   - Expected payout: $100‑$1k.
3. **Low severity** – Information Disclosure, exposed `.git`, version leakage.
   - Expected payout: $50‑$200.

**Rule of thumb:** एक *high‑impact* बग का रिवॉर्ड अक्सर कई *low‑impact* बग्स से ज़्यादा होता है, इसलिए पहले high‑impact bugs खोजो.

---

## 4.3 Timing & Scope Optimization (When to Hunt)
- **Early‑bird recon** – Programs अक्सर launch के पहले few days में कम बग्स होते हैं; शुरुआती recon gives you first‑mover advantage.
- **Scope deep‑dive** – Sub‑domains, hidden API endpoints, and undocumented features के लिए extra OSINT करो.
- **Weekly bounty newsletters** – Platform newsletters (HackerOne “Bounty Alerts”) में new high‑pay programs की notifications मिलती हैं.
- **Program expiration** – कुछ बग्स का payout program बंद होने पर घट जाता है; जल्दी submit करो.

---

## 4.4 Reporting for Maximum Money (How to Write a Winning Report)
### 4.4.1 Report Structure (Hinglish)
1. **Title** – concise, severity include. Example: `Remote Code Execution via Unauthenticated File Upload`
2. **Summary** – 2‑3 lines, impact & payout potential.
3. **Steps to Reproduce** – numbered, include screenshots or short video.
4. **Technical Details** – full request/response headers, payload, PoC code (curl, python requests).
5. **Impact** – क्या हो सकता है? (data breach, server takeover, credential theft).
6. **Remediation** – concrete fix (input validation, proper auth, whitelist).
7. **References** – OWASP cheat sheet or CVE links.

### 4.4.2 Proof‑of‑Concept Presentation
- **Burp Repeater** → Export as **cURL** (`Copy as cURL`).
- **Screenshots** – highlight vulnerable parameter, use arrow annotations.
- **Video (optional)** – 30‑sec demo showing exploit execution (use `ffmpeg` screen capture).
- **Colored output** – if platform supports markdown, wrap code with triple backticks for readability.

---

## 4.5 Negotiating Payouts (If Platform Allows)
- Some platforms (e.g., HackerOne) let you suggest a bounty amount during **triage** stage. Provide:
  - Industry benchmark (similar CVE payout).
  - Business impact estimate (potential data loss, compliance fines).
- Be **polite** and **data‑driven**; aggressive demand often backfires.

---

## 4.6 Automating Income Streams (Stay Consistent)
- **Automation bots** – Selenium/Playwright scripts that periodically scan new scope URLs for XSS/SQLi patterns.
- **RSS feeds** – Platforms expose RSS of new programs; pipe into a **GitHub Action** that triggers recon every night.
- **Discord/Telegram alerts** – Join bounty hunting community bots that ping new high‑pay programs.
- **Dashboard** – Track your submitted bugs, pending payouts, and total earnings in a simple spreadsheet.

---

### 📚 Resources & Further Reading
- **HackerOne Blog – “How We Pay Bounties”** – insight into bounty calculation.
- **Bugcrowd “Bounty Program Guide”** – best practices for hunters.
- **John Hammond – “Real‑World Bug Bounty”** (YouTube) – case studies of high‑pay bugs.
- **OWASP “Bug Bounty Cheat Sheet”** – checklist for high‑impact submissions.

Now you have a roadmap to **maximize earnings** while staying within scope and ethics. अगला मॉड्यूल: **Reporting Templates** – ready‑made markdowns for fast submissions! 🚀