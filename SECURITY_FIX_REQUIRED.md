# SECURITY ALERT - API Keys Exposed

## Issue Identified

**Real API keys were found hardcoded in `manage.py`** - This is a critical security vulnerability.

### Keys Found (EXPOSED)
1. **Claude API Key**: `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`
2. **Gemini API Key**: `AIzaSyBjDGtyntnQrMxPLZNiIGe3nZ6urQeb63s`

### Risk Level: **CRITICAL** 🔴
- Keys are in public git repository
- Anyone with git access can see the keys
- Keys can be used to incur unauthorized charges
- Keys should be considered **COMPROMISED**

---

## Fix Applied ✓

### Changes Made
1. **Removed hardcoded keys** from `manage.py`
2. **Updated to use environment variables** instead
3. **Created `.env.example`** template for setup
4. **Added error messages** to guide users

### New Approach
```python
# Before (INSECURE):
claude_api_key = "sk-ant-api03-..."

# After (SECURE):
claude_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
```

---

## How to Use Securely

### Step 1: Create `.env` File
```bash
cp .env.example .env
```

### Step 2: Add Your Real Keys
Edit `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_REAL_KEY_HERE
GOOGLE_API_KEY=AIzaSy-YOUR_REAL_KEY_HERE
```

### Step 3: Run manage.py
```bash
python manage.py start
```

The keys will be loaded from the `.env` file (which is **NOT** committed to git).

---

## Verification

### Check that .env is Protected
```bash
# .env should be in .gitignore:
grep "\.env" .gitignore
# Output: .env (if protected)

# .env should never be committed:
git status | grep .env
# Should show nothing - .env is ignored
```

### Check that manage.py is Safe
```bash
# Search for hardcoded API keys:
grep -E "sk-ant-api03|AIzaSy" manage.py
# Should show NO RESULTS - keys removed
```

---

## Recovery Steps (REQUIRED)

### 1. Revoke Exposed Keys Immediately
**Anthropic (Claude):**
- Go to https://console.anthropic.com/account/keys
- Find the exposed key
- Delete or revoke it
- Generate a new API key

**Google (Gemini):**
- Go to https://console.cloud.google.com/apis/credentials
- Find the exposed key
- Delete or disable it
- Generate a new API key

### 2. Update .env with New Keys
```bash
echo "ANTHROPIC_API_KEY=sk-ant-api03-your-new-key" >> .env
echo "GOOGLE_API_KEY=AIzaSy-your-new-key" >> .env
```

### 3. Force-Push Git History (OPTIONAL but RECOMMENDED)
If keys were already committed to git history:

```bash
# Remove all commits with exposed keys from history
git filter-branch --tree-filter 'rm -f manage.py' HEAD

# OR use git-filter-repo (recommended):
git filter-repo --path manage.py --invert-paths

# Force push (warning: rewrites history)
git push origin --force
```

---

## Best Practices Going Forward

### ✓ DO
- Load API keys from `.env` file (local, not committed)
- Use environment variables
- Create `.env.example` with placeholder values
- Add `.env` to `.gitignore`
- Keep `.env.example` in repo for reference

### ✗ DON'T
- Hardcode API keys in source files
- Commit `.env` file to git
- Store keys in comments
- Share keys in messages or documentation
- Use the same key for testing and production

### 🔐 For Production
```bash
# Use proper secret management:
# - AWS Secrets Manager
# - Azure Key Vault
# - HashiCorp Vault
# - Environment-specific .env files (never committed)
```

---

## Files Modified

| File | Change | Status |
|------|--------|--------|
| `manage.py` | Removed hardcoded keys | ✓ FIXED |
| `.env.example` | Created template | ✓ NEW |
| `.gitignore` | Already protects `.env` | ✓ OK |

---

## Testing

### Verify Fix Works
```bash
# Set your new keys
export ANTHROPIC_API_KEY="your-new-key"
export GOOGLE_API_KEY="your-new-key"

# Start services
python manage.py start

# Should work without errors
# (and use environment variables, not hardcoded)
```

---

## Summary

| Item | Status |
|------|--------|
| **Keys Exposed** | ✓ FOUND |
| **Keys Removed** | ✓ DONE |
| **Environment Variables** | ✓ IMPLEMENTED |
| **`.env` Protection** | ✓ IN PLACE |
| **Old Keys** | ⚠️ MUST BE REVOKED |
| **New Keys** | ⏳ MUST BE GENERATED |

---

## Action Required

**CRITICAL - Please do the following immediately:**

1. ✓ Revoke the exposed API keys in both Anthropic and Google consoles
2. ✓ Generate new API keys
3. ✓ Create `.env` file with new keys
4. ✓ Test with `python manage.py start`
5. ✓ Consider git history cleanup (filter-branch)

---

**Status**: Security fix applied
**Next Step**: Revoke exposed keys and generate new ones
**Timeline**: IMMEDIATELY - Do not delay
**Risk**: CRITICAL until old keys are revoked
