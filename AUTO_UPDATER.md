# FRU Selector v2 - Automated Update System

## Overview

FRU Selector v2 maintains current data and binaries through a fully automated GitHub-based workflow that:

1. **Scrapes** Microsoft Learn service guides monthly for latest FRU/SKU data
2. **Validates** the scraped data against baseline data
3. **Recompiles** the Electron application with fresh data
4. **Publishes** releases to GitHub automatically

This ensures users always have access to the latest Surface device parts information without manual intervention.

## Architecture

### 1. Monthly Data Scraping & Build Workflow

**File**: `.github/workflows/monthly-update.yml`

The workflow runs on the 1st of every month (or manually via GitHub Actions UI) and performs:

```
GitHub Actions Workflow (ubuntu-latest)
  ↓
1. Python 3.12 Setup
  ↓
2. Scrape Microsoft Learn Service Guides
   └─ Uses scripts/scrape_service_guides.py
   └─ Fetches latest FRU parts from all Surface device service guides
   └─ Falls back to baseline_data.json if scraping fails
  ↓
3. Build & Validate HTML Reference
   └─ Uses scripts/build_and_validate.py
   └─ Extracts device data and parts information
   └─ Generates docs/index.html with embedded DATA catalog
  ↓
4. Check for Changes
   └─ Detects if any new data was scraped
  ↓
5. (If changed) Commit & Push
   └─ Creates commit with data update summary
   └─ Pushes to repository
  ↓
6. (If changed) Node.js Build
   └─ Sets up Node.js 18
   └─ Installs npm dependencies
   └─ Runs npm run build (TypeScript + React build)
  ↓
7. (If changed) Create GitHub Release
   └─ Tags release: v{run_number}-{attempt}
   └─ Publishes dist/** artifacts
   └─ Makes release available for download
```

### 2. Data Flow

```
Microsoft Learn Service Guides
  ↓
scrape_service_guides.py
  ↓
scraped_data.json (temporary)
  ↓
build_and_validate.py
  ↓
docs/index.html (includes DATA const)
  ↓
Git Commit
  ↓
npm run build (includes HTML → dist/)
  ↓
GitHub Release (dist/** artifacts)
```

### 3. Electron Application Updates

The Electron app (`src/main/index.ts` & `src/main/updater.ts`) is configured with `electron-updater` to:

- Check for new releases on startup
- Notify users when updates are available
- Download and install updates automatically
- Log all update events for troubleshooting

**Configuration** in `package.json`:
```json
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "microsoft",
      "repo": "fru-selector"  // Update to your repo
    }
  }
}
```

## How It Works

### Step 1: Monthly Trigger

The workflow is triggered automatically on the 1st of each month at 00:00 UTC, or manually:

```bash
# Trigger manually via GitHub UI Actions tab
# Or via GitHub CLI:
gh workflow run monthly-update.yml --repo owner/fru-selector
```

### Step 2: Web Scraping

The `scrape_service_guides.py` script:

- Connects to Microsoft Learn service guides
- Parses HTML tables for FRU/SKU parts data
- Extracts device-specific part information
- Combines data from 25+ Surface device pages
- Falls back to `scripts/baseline_data.json` if scraping fails

```python
# Example scraped structure:
{
  "devices": [
    {
      "name": "Surface Laptop 7",
      "parts": [
        {
          "part_number": "G8K-00001",
          "description": "Battery",
          "category": "Power Management",
          "substitute": "G8K-00002"
        }
      ]
    }
  ]
}
```

### Step 3: HTML Build & Validation

The `build_and_validate.py` script:

- Merges scraped data with known fixes
- Generates `docs/index.html` with embedded DATA
- Validates part numbers and descriptions
- Groups devices by family (Surface Laptop, Pro, etc.)
- Returns exit codes:
  - `0` = Success
  - `1` = Fatal error (stops workflow)
  - `2` = Warnings (continues to release)

### Step 4: Git Commit

If data changed, creates a signed commit:

```
Monthly FRU data update — April 2024

Automated refresh from Microsoft Learn service guides.
35 devices, 892 parts

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

### Step 5: Application Build

Node.js build process:

```bash
npm ci              # Install dependencies
npm run build       # Builds:
                    # - TypeScript main process (dist/main/*)
                    # - React app (build/*)
                    # - Electron dist includes docs/index.html
```

### Step 6: GitHub Release

Creates a release with:

- **Tag**: `v{run_number}-{attempt}` (e.g., `v123-1`)
- **Name**: "FRU Selector v2 - Monthly Release"
- **Assets**: All files in `dist/`
- **Description**: Data update summary

Users can download the built application directly from releases page.

## File Structure

```
FRUSelector-v2-local/
├── .github/
│   └── workflows/
│       └── monthly-update.yml          ← Main automation workflow
├── scripts/
│   ├── scrape_service_guides.py        ← Web scraper
│   ├── build_and_validate.py           ← HTML builder
│   ├── baseline_data.json              ← Fallback data
│   └── merge_sku_data.py               ← Helper script
├── src/
│   └── main/
│       ├── updater.ts                  ← Electron update handler
│       └── index.ts                    ← App entry point
├── docs/
│   └── index.html                      ← Generated with DATA const
├── dist/                               ← Built Electron app
├── package.json                        ← Build config + publish
├── UPDATE_AT_LAUNCH.md                 ← Electron updater docs
└── AUTO_UPDATER.md                     ← This file
```

## Customization

### Change Update Schedule

Edit `.github/workflows/monthly-update.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 1 * *'  # 1st of month, midnight UTC
    # To weekly:
    # - cron: '0 0 * * 0' # Every Sunday
    # To daily:
    # - cron: '0 0 * * *' # Every day
```

### Change Release Provider

Update `package.json`:

```json
{
  "build": {
    "publish": {
      "provider": "s3",              // or "azure", "spaces", etc.
      "bucket": "my-bucket",
      "region": "us-east-1"
    }
  }
}
```

### Change Service Guides List

Edit `scripts/scrape_service_guides.py`:

```python
SERVICE_GUIDE_SLUGS = [
    ("Device Name", "url-slug", "alternate-slug"),
    # Add or remove devices here
]
```

### Disable Auto-Updates in App

Edit `src/main/index.ts`:

```typescript
// Comment out to disable:
if (!isDev) {
  initializeUpdater();
}
```

## Monitoring & Troubleshooting

### View Workflow Runs

Go to **GitHub → Actions → Monthly FRU Data Update & Release**

Check:
- ✅ Scrape step succeeded
- ✅ Validation passed
- ✅ Data changes detected
- ✅ Build completed
- ✅ Release published

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Scrape failed | Microsoft Learn page structure changed | Update `scrape_service_guides.py` parser |
| No changes detected | Data already current | Manual trigger to test workflow |
| Build failed | Node.js dependency issue | Check `npm ci` logs |
| Release failed | GitHub token permissions | Verify workflow permissions in settings |

### View Logs

```bash
# Workflow run logs (GitHub UI)
Actions → Monthly FRU Data Update & Release → [Run number] → [Step name] → Logs

# Download artifacts
Actions → [Run] → Artifacts → Download
```

### Manual Trigger

```bash
# Via GitHub CLI
gh workflow run monthly-update.yml -r main

# Via GitHub UI
Actions → Monthly FRU Data Update & Release → Run workflow → Run workflow
```

## Release Cycle

```
Month 1          Month 2          Month 3
↓                ↓                ↓
01:00 UTC → Scrape, Build, Release
- v1-1           - v2-1           - v3-1

Users:
↓
Download v1-1
↓
Launch Electron app
↓
electron-updater checks for updates
↓
If v2-1 released: "Update Available"
↓
User clicks "Install Now" or defers
↓
App restarts with v2-1
```

## Next Steps

1. **Repository Setup**:
   - Fork/clone this repository
   - Update `owner`/`repo` in `package.json` build.publish

2. **GitHub Token**:
   - Workflow uses default `${{ secrets.GITHUB_TOKEN }}`
   - No additional secrets needed if using GitHub releases

3. **Manual Test**:
   - Go to Actions tab
   - Run "Monthly FRU Data Update & Release" workflow
   - Verify release is created with artifacts

4. **User Distribution**:
   - Share GitHub releases page with users
   - Or automate download via your distribution platform
   - Users can also rely on app auto-update feature

5. **Monitor**:
   - Check workflow runs monthly
   - Review release notes for data quality
   - Monitor electron-updater logs for adoption

## Security Considerations

- ✅ Scraping uses standard HTTP requests (no credentials)
- ✅ Python scripts are sandboxed in GitHub Actions
- ✅ Commits are made by `github-actions[bot]`
- ✅ Releases use GitHub's native authentication
- ✅ No secrets or credentials in workflows

**Warning**: If adding external data sources, never commit API keys or secrets. Use GitHub Secrets instead.

## Performance Notes

- **Scraping**: ~2-5 minutes (depends on Microsoft Learn availability)
- **Validation**: ~30 seconds
- **Build**: ~3-5 minutes (Node.js compilation)
- **Release**: ~1 minute (GitHub API)
- **Total**: ~10 minutes per run

## Version History

- **v1.0** - Initial automated monthly update setup
- **v2.0** - Added Electron app build and GitHub releases
- **v2.1** - Improved fallback to baseline data

## Support

For issues:
1. Check workflow logs in GitHub Actions
2. Review `scripts/` directory for scraper health
3. Test `npm run build` locally
4. Check electron-updater logs: `~/.config/FRU Selector/logs/main.log`

---

**Last Updated**: April 2024
**Maintains**: FRU Selector v2 (the current production version)
