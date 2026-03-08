# 📝 Phase 5: Professional Reporting

A good bug with a bad report = $0.
A good bug with a great report = $$$ + Critical Impact.

### Structure of a Quality Report
1. **Summary:** Brief description of the bug.
2. **Steps to Reproduce (STR):** Clear, numbered steps that a 5-year-old could follow.
3. **Impact:** Why should the company care? (e.g., "I can steal all user passwords").
4. **Mitigation:** How they can fix it.

### Template
**Title:** IDOR on [Endpoint] leads to User Data Leak
**Description:** I found that by changing the `user_id` parameter, I can access private profiles...
**Steps:**
1. Login to account A.
2. Go to /profile/edit.
3. Capture request and change ID to account B.
4. Observe account B's data.
**Impact:** Personal Identifiable Information (PII) leak of all users.
