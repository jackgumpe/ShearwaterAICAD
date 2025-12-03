# CI/CD Pipeline Configuration

## Overview

Automated testing, building, and deployment pipeline using GitHub Actions. Two main workflows:
- **Test & Coverage** (`test.yml`) - Runs on every push/PR
- **Build & Deploy** (`deploy.yml`) - Runs on main branch push

---

## Test Workflow

**File:** `.github/workflows/test.yml`

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

### Jobs

#### 1. Test Job
Runs on `ubuntu-latest` with Node.js 18 and 20 (matrix strategy)

**Steps:**
1. Checkout code
2. Setup Node.js (cache npm packages)
3. Install dependencies
4. Run linting
5. Run unit tests
6. Generate coverage report
7. Upload coverage to Codecov
8. Archive test results as artifacts

**Outputs:**
- Coverage report (HTML)
- Test results
- Codecov integration

#### 2. E2E Job
Runs after test job passes

**Steps:**
1. Checkout code
2. Setup Node.js
3. Install dependencies
4. Install Playwright browsers
5. Build application
6. Start dev server
7. Wait for server to be ready
8. Run E2E tests
9. Upload Playwright report

**Outputs:**
- Playwright test report
- Screenshots/videos of failures

### Coverage Requirements
- Unit tests: 95%+ coverage
- Tests run in parallel for Node 18 and 20
- Codecov automatically tracks coverage over time

### Artifacts Retention
- Test results kept for 30 days
- Playwright reports kept for 30 days
- Enable download from workflow runs page

---

## Deploy Workflow

**File:** `.github/workflows/deploy.yml`

### Triggers
- Push to `main` branch
- Manual trigger (`workflow_dispatch`)

### Jobs

#### 1. Build Job
Creates production build

**Steps:**
1. Checkout code
2. Setup Node.js
3. Install dependencies
4. Build application with `npm run build`
5. Generate version/build info
6. Upload build artifacts
7. Create build summary in GitHub

**Build Info includes:**
- Git commit hash
- Build date/time
- Branch name

**Outputs:**
- `ui/dist/` directory
- Build artifacts (30 day retention)

#### 2. Test Build Job
Verifies build integrity

**Steps:**
1. Download build artifacts
2. Install dependencies
3. Verify `dist/` directory exists
4. Confirm build is valid

**Purpose:** Ensure build completed successfully before deploying

#### 3. Deploy to Staging
Deploys to staging environment (if build succeeds)

**Requirements:**
- `STAGING_DEPLOY_KEY` secret
- `STAGING_HOST` secret
- `STAGING_USER` secret

**Process:**
1. Download build artifacts
2. Setup SSH key
3. Scan host key
4. Rsync files to staging server
5. Log success/failure

**SSH Configuration:**
```
~/.ssh/deploy_key (chmod 600)
~/.ssh/known_hosts (auto-populated)
```

#### 4. Deploy to Production
Deploys to production (main branch only)

**Requirements:**
- `PROD_DEPLOY_KEY` secret
- `PROD_HOST` secret
- `PROD_USER` secret

**Process:**
1. Download build artifacts
2. Create GitHub release with tag `v{YYYYMMDD.HHMMSS}`
3. Setup SSH key
4. Rsync files to production server
5. Notify deployment completion

**Release Info:**
- Tag: `v2025.12.03.120000`
- Includes built artifacts
- Automatic versioning by timestamp

---

## GitHub Secrets Setup

Add these secrets to your repository (Settings > Secrets):

### Staging Secrets
```
STAGING_DEPLOY_KEY      - SSH private key (PEM format)
STAGING_HOST            - staging.example.com
STAGING_USER            - deploy_user
```

### Production Secrets
```
PROD_DEPLOY_KEY         - SSH private key (PEM format)
PROD_HOST               - prod.example.com
PROD_USER               - deploy_user
```

### Optional Secrets
```
CODECOV_TOKEN           - For codecov integration
SLACK_WEBHOOK           - For Slack notifications
```

---

## SSH Key Setup

### Generate Deployment Key
```bash
ssh-keygen -t rsa -b 4096 -f deploy_key -N ""
```

### Add to GitHub Secrets
1. Copy `deploy_key` contents
2. Paste into `STAGING_DEPLOY_KEY` or `PROD_DEPLOY_KEY` secret
3. Delete local `deploy_key` file

### Server Configuration
Add public key to server:
```bash
# On deployment server
mkdir -p ~/.ssh
echo "$(cat public_key)" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

---

## Environment Variables

### Build Time
Add to workflow or `.env.build`:
```
VITE_API_URL=ws://api.example.com
VITE_ENV=production
VITE_VERSION=${GIT_COMMIT}
```

### Runtime
Set on deployment servers:
```bash
export REACT_APP_API_URL="ws://api.example.com"
export REACT_APP_ENV="production"
```

---

## Monitoring & Notifications

### GitHub Workflow Status
- Check Actions tab for workflow runs
- Click on failed workflow for details
- View logs for each step

### Email Notifications
GitHub sends automatic emails for:
- Workflow failures
- Re-run triggers
- Deployment status

### Slack Integration (Optional)
```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Build failed: ${{ github.repository }}"
      }
```

### Codecov Integration
- Automatically posts coverage comments on PRs
- Tracks coverage trends over time
- Alerts on coverage drops

---

## Rollback Procedure

### Staging Rollback
```bash
# SSH to staging server
ssh deploy_user@staging.example.com

# View recent deployments
ls -la /var/www/staging/

# Restore previous version
rsync -avz /var/www/staging_backup/ /var/www/staging/
```

### Production Rollback
```bash
# Use GitHub releases to identify previous version
# Download previous release artifacts
# Deploy manually or trigger workflow with specific commit

git checkout previous_commit
git push --force-with-lease
```

---

## Deployment Checklist

- [ ] All tests passing (100+ tests)
- [ ] Coverage at 95%+
- [ ] Build completes without warnings
- [ ] No console errors in build
- [ ] Staging deployment succeeds
- [ ] Smoke tests pass on staging
- [ ] Performance metrics acceptable
- [ ] Security scan passes
- [ ] Code review approved
- [ ] Ready for production

---

## Performance Metrics

### Build Time Target
- < 2 minutes total
- Test phase: < 1 minute
- Build phase: < 1 minute

### Deployment Time Target
- Staging: < 5 minutes
- Production: < 10 minutes

### Uptime Target
- 99.9% deployment success rate
- Automatic rollback on deployment failure

---

## Advanced Configuration

### Conditional Steps
```yaml
- name: Deploy production
  if: github.ref == 'refs/heads/main' && success()
  run: ./deploy.sh
```

### Custom Environment per Job
```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://example.com
```

### Artifact Dependencies
```yaml
- name: Download artifacts
  uses: actions/download-artifact@v3
  with:
    name: build-artifacts
    path: ./dist
```

---

## Troubleshooting

### Workflow Not Triggering
- Check branch protection rules
- Verify workflow is not disabled
- Check file path filters (if configured)
- Look for syntax errors in workflow file

### Deploy Fails
- Check SSH key permissions (must be 600)
- Verify secrets are set correctly
- Check server disk space
- Review deploy user permissions

### Coverage Not Uploading
- Verify Codecov token in secrets
- Check coverage report format
- Review Codecov configuration

### Tests Timing Out
- Increase timeout values
- Check if server is responding
- Review browser resource limits

---

## Best Practices

1. **Run tests locally before pushing**
   ```bash
   npm test:unit
   npm run test:e2e
   ```

2. **Keep workflow files small and focused**
   - Separate test and deploy workflows
   - Use reusable workflows for common tasks

3. **Monitor artifact storage**
   - Set appropriate retention periods
   - Clean up old artifacts regularly

4. **Version your deployments**
   - Use semantic versioning (v1.0.0)
   - Tag releases in git
   - Document breaking changes

5. **Test deployment process**
   - Dry-run deployments
   - Test rollback procedures
   - Verify disaster recovery

6. **Secure secrets properly**
   - Rotate SSH keys regularly
   - Use short-lived tokens when possible
   - Limit secret scope to required workflows

---

## Commands Reference

### Manually Trigger Workflow
```bash
# Requires GitHub CLI
gh workflow run deploy.yml --ref main
```

### View Workflow Runs
```bash
gh run list --workflow test.yml
gh run view <run_id> --log
```

### Download Artifacts
```bash
gh run download <run_id> --name build-artifacts
```

### Force Rerun
```bash
gh run rerun <run_id>
```

---

## Integration Points

### Pre-Deployment Checks
- Linting (ESLint)
- Type checking (TypeScript)
- Unit tests (Vitest)
- E2E tests (Playwright)
- Security scanning (OWASP)

### Post-Deployment
- Health checks
- Smoke tests
- Performance monitoring
- Error tracking (Sentry)
- User analytics

---

## Support & Documentation

- GitHub Actions Docs: https://docs.github.com/en/actions
- Workflow Syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- Codecov: https://codecov.io/docs
- Playwright: https://playwright.dev/docs/ci
