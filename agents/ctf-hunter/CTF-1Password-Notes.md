# $1 Million 1Password CTF Challenge

## 🎯 Goal
Capture the "bad poetry" secure note from bugbounty-ctf.1password.com

## Status
- [x] Email `bugbounty@agilebits.com` for CTF account access (HackerOne username ke saath)
- [x] Access received ✅ 2026-03-11
- [ ] Initial recon started
- [ ] First breakthrough
- [ ] Flag captured 💰

## 📚 Learning Resources

### Phase 1: Basics (Week 1-2)
1. **What is Bug Bounty?** - Platforms find karne ke program mein companies hack hone se bachane ke liye hackers ko pay karti hain
2. **What is CTF?** - Capture The Flag = Hidden "flag" (secret data) find karna hai
3. **Web Security Basics:**
   - HTTP/HTTPS
   - Cookies/Sessions
   - Authentication vs Authorization
   - Common vulnerabilities (OWASP Top 10)

### Phase 2: 1Password Specific (Week 3-4)
1. Read: 1Password Security Design White Paper
   - **CRITICAL**: Section "Beware of the Leopard" (Page 68)
2. Understand 1Password architecture
3. Study their API/tooling

### Phase 3: Advanced (Ongoing)
- Cryptography concepts
- Authentication bypass techniques
- Secure storage vulnerabilities

## 🗺️ Strategy

### Reconnaissance (After Access)
- [ ] Account features explore karna
- [ ] API endpoints identify karna
- [ ] Account permissions check karna
- [ ] "Flag" location clues dhoondhna

### Attack Surface
1. Web App (1Password.com interface)
2. API endpoints
3. Account sharing/collaboration features
4. Secure notes functionality
5. Import/export features

### Tools to Learn
- Burp Suite (Web proxy/debugger)
- Browser DevTools
- curl/httpie (API testing)
- 1Password CLI (if applicable)

## 💡 Key Insights from Program Page
- **Flag format**: "Bad poetry" in secure note
- **Starting point**: NONE (they said "no known vulnerabilities")
- **Approach**: Think outside the box
- **Help**: `bugbounty@agilebits.com` (but they won't give direct hints)

## 📝 Research Notes

### Day 1 - BREAKTHROUGH: API Discovery (2026-03-11)
🔥 **CRITICAL DISCOVERY: API Endpoints Exposed!**
✅ Account accessed via browser relay
⚠️ **CRITICAL FINDING: Vault is COMPLETELY EMPTY**

| Section | Status | Notes |
|---------|--------|-------|
| All Items | EMPTY ❌ | "Add an item to get started" |
| Favorites | EMPTY ❌ | No favorites |
| Watchtower | EMPTY ❌ | "Try adding a new item first" |
| Archive | EMPTY ❌ | Nothing archived |
| Recently Deleted | EMPTY ❌ | No deleted items |
| Shared Vaults | EMPTY ❌ | "You don't have access to any shared vaults yet" |

**🔍 Key Observations:**
1. **"New Item" button is DISABLED** - Intentionally locked!
2. **Vault name**: "1Password Bug Bounty CTF"
3. **No shared vault access** mentioned
4. **Unlike normal 1Password accounts** - Can't add items

**📊 Technical Data Extracted:**
```
Account UUID: OMT2FPMPQFAOXO2MI4NXJ7JCFM
User ID: XHE54NLJXFCDVA327HYLYAK4IQ
Email: duhitsaniket@wearehackerone.com
Session Cookie: _tsession
Secret Key: Encrypted (kid: 3tnqywhecddkhvl375l6yu7qri)
Autolock: 480 minutes (8 hours)
```

**💡 What this means:**
- Flag is NOT in regular vault items (obviously)
- Solution requires OUTSIDE-THE-BOX thinking
- Likely involves: API manipulation, shared vault hacking, or permission escalation
- They said "no starting point" - TRUE! Nothing visible.

**🎯 Immediate Action Plan:**

#### Step 1: Network Monitor (Tu abhi karega)
- DevTools → Network tab
- "Preserve log" ON karna
- Page refresh (F5)
- Check for API calls to endpoints like:
  - `/api/v1/vaults`
  - `/api/v1/accounts`
  - `/api/v1/items`
  - `/api/v1/invitations`
  - `/api/v1/sharing`

#### Step 2: Check Email
- Check `duhitsaniket@wearehackerone.com` inbox
- Might have invitation/access emails
- Look for any shared vault invites

#### Step 3: API Investigation
- Use extracted Account UUID to probe endpoints
- Check if any shared vaults accessible via API

#### Step 4: Invite/Share Features
- Look for "Invite" or "Share" options
- Maybe flag is in a vault that needs invitation

### Day 2
[Next: Network analysis results]

---
*Created: 2026-03-11*
*Target: $1,000,000*
