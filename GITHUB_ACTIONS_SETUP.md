# GitHub Actions Setup Guide

This project includes a GitHub Actions workflow that runs the AI Discovery Monitor in the cloud on-demand or on a schedule.

## Features

✅ Run on-demand via GitHub UI (no local setup needed)
✅ Automatic Python environment setup
✅ Twitter API integration (with stored secrets)
✅ Upload recommendations as downloadable artifacts
✅ No database committed to repo (fresh runs each time)
✅ Detailed logs and error reporting

## Setup Instructions

### Step 1: Add Anthropic API Key as GitHub Secret

1. Go to your repo: https://github.com/brhannan/ai-discovery-monitor
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Fill in:
   - **Name**: `ANTHROPIC_API_KEY`
   - **Secret**: Paste your API key from https://console.anthropic.com/settings/keys
5. Click **Add secret**

### Step 2: Add Twitter API Token as GitHub Secret

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Fill in:
   - **Name**: `TWITTER_BEARER_TOKEN`
   - **Secret**: Paste your Twitter Bearer Token
4. Click **Add secret**

### Step 3: (Optional) Configure Schedule

To run automatically on a schedule, edit `.github/workflows/discover-sources.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

Cron format: `minute hour day month day-of-week`

Examples:
- `'0 9 * * *'` - Daily at 9 AM UTC
- `'0 */6 * * *'` - Every 6 hours
- `'0 9 * * 1'` - Every Monday at 9 AM UTC

### Step 3: Run the Workflow

#### Manual Run (On-Demand)

1. Go to your repo
2. Click **Actions** tab
3. Click **AI Discovery Monitor** workflow
4. Click **Run workflow** → **Run workflow**
5. Wait for it to complete
6. Download results from **Artifacts**

#### Automatic Run (If Scheduled)

If you configured a schedule, the workflow runs automatically at the specified time. You'll see results in the **Actions** tab.

## What Happens During a Run

1. **Checkout** - Pulls latest code
2. **Python Setup** - Installs Python 3.11
3. **Dependencies** - Installs requirements.txt
4. **Monitor Runs** - Executes `python monitor.py`
5. **Artifact Upload** - Saves recommendations.md and discovery.db
6. **Results Display** - Shows recommendations in logs
7. **Cleanup** - Artifacts retained for 30 days

## Viewing Results

### During Run
- Click the running workflow to see real-time logs
- Watch for the "Run AI Discovery Monitor" step output

### After Run
1. Go to **Actions** tab
2. Click the completed workflow run
3. Scroll to **Artifacts** section
4. Download `ai-discovery-recommendations`
5. Extract and view `recommendations.md`

## Troubleshooting

**"TWITTER_BEARER_TOKEN not provided"**
- Verify secret is added to GitHub (Settings → Secrets)
- Secret name must be exactly `TWITTER_BEARER_TOKEN`
- Workflow must reference it: `${{ secrets.TWITTER_BEARER_TOKEN }}`

**"No sources discovered"**
- Check config.yaml is correctly committed
- Verify primary sources URLs are accessible
- Check workflow logs for detailed errors

**"Python dependencies failed"**
- Check requirements.txt is in repo root
- Verify all packages are pip-installable

**"Artifact not uploaded"**
- Check that monitor.py ran without errors
- Verify recommendations.md was generated
- Check workflow logs for error messages

## Cost & Limits

GitHub Actions includes:
- **Free**: 2,000 minutes/month for private repos
- **Public repos**: Unlimited free minutes
- Each run takes ~1-2 minutes

This workflow easily fits within free limits (even if you run 10 times per day).

## Environment Variables

The workflow provides:
- `TWITTER_BEARER_TOKEN` - From GitHub Secrets
- `PYTHONUNBUFFERED=1` - Unbuffered output for live logs

You can add more secrets and reference them as needed.

## Customization

### Run on Multiple Schedules

```yaml
schedule:
  - cron: '0 9 * * 1'    # Monday at 9 AM
  - cron: '0 9 * * 4'    # Thursday at 9 AM
  - cron: '0 9 * * 0'    # Sunday at 9 AM
```

### Save Recommendations to Repo

Replace the artifact upload step with:

```yaml
- name: Commit recommendations
  run: |
    git config user.name "AI Discovery Bot"
    git config user.email "bot@example.com"
    git add recommendations.md
    git commit -m "Update AI discovery recommendations" || true
    git push
```

### Add Slack Notifications

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Change Python Version

```yaml
python-version: '3.12'  # Update version here
```

## Next Steps

1. ✅ Add TWITTER_BEARER_TOKEN secret (if using Twitter)
2. ✅ Test with manual run (Actions → Run workflow)
3. ✅ (Optional) Configure schedule in `.github/workflows/discover-sources.yml`
4. ✅ Download and review recommendations
5. ✅ Adjust config.yaml based on results

## Questions?

- Check GitHub Actions logs for detailed error messages
- Review workflow file: `.github/workflows/discover-sources.yml`
- See main README.md for project documentation
