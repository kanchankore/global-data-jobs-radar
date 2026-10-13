# Global Data Jobs Radar

An MVP for daily searches across the Netherlands, Singapore and Dubai/UAE for Data Engineer, Data Analyst, BI Analyst, Analytics Engineer, Data Quality Analyst and ETL Developer jobs.

## Setup

Requires Python 3.11, Git and a GitHub account.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python collect.py --per-search 10
streamlit run app.py
```

Your local dashboard opens at `http://localhost:8501`. Initial data collection may take several minutes and some sites may return no results or fail. These failures are logged and do not stop other searches.

## Daily unattended run

1. Create your own GitHub repository, upload these files including `.github/workflows/daily-jobs.yml`.
2. In your repository, select **Actions → Refresh data jobs → Run workflow** to test.
3. In **Settings → Actions → General**, allow GitHub Actions to have **Read and write permissions** if the repository permissions permit it.
4. The workflow is scheduled for **08:00 India time every day** (02:30 UTC). GitHub scheduled runs may be delayed and can be disabled after prolonged repository inactivity.
5. Optionally deploy the repository's `app.py` to **Streamlit Community Cloud** for a shareable dashboard. Changes committed to `data/jobs.csv` will be picked up on app rerun/redeployment; live-refresh behavior depends on the hosting platform.

**Privacy:** The sample CSV is committed to the GitHub repository. Use a private repo if you don't want the collected data public. Check that your chosen dashboard hosting supports access to private repos.

## Supported automation in this MVP

- Indeed and LinkedIn in all three places, Glassdoor in Netherlands and Singapore, and Bayt for UAE, via JobSpy.
- Country-specific portal links are supplied for manual browsing. This starter does **not** automatically scrape MyCareersFuture, JobStreet, GulfTalent, Naukrigulf, Nationale Vacaturebank, etc.
- Each board has different access rules and automated collection may be unreliable or disallowed under its terms. Verify permission for sources before collecting from them. Never use this project to bypass CAPTCHAs, logins, or access restrictions.
- Jobs are deduplicated primarily by normalized URL. Cross-posted copies with different URLs can remain. Dates, salaries and visa-sponsorship information may be incomplete.
- The source may not find all available jobs, and it does not automatically submit applications.

## Next improvements

- Use authorized ATS job APIs (e.g., Greenhouse/Lever boards) and feeds for company-direct opportunities.
- Add permissions-based integrations for regional boards and country-specific portals.
- Add notifications, visa sponsorship and language filters, and individual application tracking.
- Replace committed CSV with a hosted database (e.g., Supabase) before large-scale use.

## Adjust searches

Edit `SEARCH_TERMS` and `COUNTRIES` in `config.py`.
