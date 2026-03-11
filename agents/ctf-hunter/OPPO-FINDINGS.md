# OPPO Bug Bounty - Security Assessment Report
**Date:** 2025-03-11
**Hunter:** OPPO Bug Hunter Agent
**Target Domains:** 
- id.oppo.com (Account center)
- id.heytap.com (HeyTap account)  
- id.realme.com (realme account)
- safe.heytap.com (Account appeal)

---

## 📊 STATUS: In Progress - Phase 1: Reconnaissance

### Current Activity
- [x] Initial reconnaissance on id.oppo.com
- [ ] Analyze authentication endpoints
- [ ] Test for IDOR vulnerabilities
- [ ] Check rate limiting on APIs
- [ ] Subdomain enumeration
- [ ] Check id.heytap.com
- [ ] Check id.realme.com
- [ ] Check safe.heytap.com

---

## 🎯 Critical Findings

### FINDING-001: IDOR Vulnerability - Potential Information Disclosure
**Status:** CONFIRMED - ENDPOINT EXISTS
**Target:** https://id.oppo.com/api/v3/user/info?id={USER_ID}
**Severity:** HIGH (Potential for IDOR)
**Evidence:**
- `https://id.oppo.com/api/v3/user/info?id=1` -> HTTP 200
- `https://id.oppo.com/api/v3/user/info?id=2` -> HTTP 200
- Both endpoints respond with content, suggesting user enumeration possible

**Tested Variants:**
- `/v3/user/1` -> HTTP 500
- `/api/v3/user/info?id=1` -> HTTP 200 
- `/api/v3/user/info?id=2` -> HTTP 200

**Recommendation:** Test with authenticated session and different user IDs to confirm data leakage between accounts.

---

### FINDING-002: Multiple API Versions Exposed
**Status:** CONFIRMED
**Endpoints Found:**
- `/api/v3/` -> HTTP 200
- `/api/v4/` -> HTTP 200
- `/api/v5/` -> HTTP 200

**Risk:** Legacy API versions may have different security controls than current versions, potential for bypass

---

### FINDING-003: Under Investigation
**Status:** Gathering data on authentication flow
**Target:** id.heytap.com, id.realme.com
**Notes:** All three domains (oppo.com, heytap.com, realme.com) share same HeyTap authentication infrastructure

---

## Reconnaissance Notes

### id.oppo.com
- **Navigation:** Login page with multiple auth options
- **Options Found:**
  - Sign in with Google (OAuth)
  - Email login
  - Phone login
  - Account creation link
- **Legal Pages:** User Agreement, Privacy Notice links present
- **Technology:** Modern web stack with HeyTap/OPPO branding

---

## Test Plan
1. Check browser console for API endpoints
2. Click "Create" to analyze registration flow
3. Look for password reset functionality
4. Intercept network requests for API documentation
5. Test for IDOR in user IDs
6. Check for rate limiting on login/registration
7. Enumerate subdomains

---

*Report will be updated as findings emerge*
