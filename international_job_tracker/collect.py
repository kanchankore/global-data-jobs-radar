"""Daily job collector. Queries public job board search results via JobSpy.

Only use sources in ways permitted by their terms and local laws. This collector
has conservative limits, no proxies, no login automation, and no CAPTCHA bypass.
"""
from __future__ import annotations
import argparse
import hashlib
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import pandas as pd
from config import COUNTRIES, SEARCH_TERMS, COLUMNS

FILE = Path(__file__).parent / "data" / "jobs.csv"
LOG = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    if not url or url == 'nan':
        return ''
    try:
        parts = urlsplit(str(url).strip())
        params = [(k, v) for k,v in parse_qsl(parts.query) if not k.lower().startswith(('utm_', 'ref', 'trk', 'tracking'))]
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip('/'), urlencode(params), ''))
    except Exception:
        return str(url)


def get_key(row: dict) -> str:
    url = normalize_url(row.get('job_url', ''))
    if url:
        payload = url
    else:
        payload = '|'.join(str(row.get(c, '')).strip().casefold() for c in ('title','company','location'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:24]


def load_existing() -> pd.DataFrame:
    if FILE.exists():
        try:
            return pd.read_csv(FILE, dtype=str, keep_default_na=False).reindex(columns=COLUMNS, fill_value='')
        except Exception as exc:
            LOG.warning('Cannot read existing jobs: %s', exc)
    return pd.DataFrame(columns=COLUMNS)


def collect(results_wanted: int = 15, hours_old: int = 168, sites_override: list[str] | None = None):
    from jobspy import scrape_jobs
    today = datetime.now(timezone.utc).date().isoformat()
    records = []
    for country, opts in COUNTRIES.items():
        for term in SEARCH_TERMS:
            sites = sites_override or opts['sites']
            # Isolating each site ensures errors on one job board don't stop other searches.
            for site in sites:
                try:
                    LOG.info('Searching %s / %s / %s', country, term, site)
                    df = scrape_jobs(site_name=[site], search_term=term,
                        location=opts['location'], country_indeed=opts['indeed_country'],
                        results_wanted=results_wanted, hours_old=hours_old,
                        fetch_description=False, verbose=0)
                    if df is None or df.empty:
                        continue
                    for r in df.to_dict('records'):
                        record = {c: '' for c in COLUMNS}
                        record.update({
                            'first_seen': today, 'last_seen': today, 'country': country,
                            'search_term': term, 'title': str(r.get('title') or ''),
                            'company': str(r.get('company') or ''),
                            'location': str(r.get('location') or ''),
                            'site': str(r.get('site') or site),
                            'date_posted': str(r.get('date_posted') or ''),
                            'job_type': str(r.get('job_type') or ''),
                            'min_amount': str(r.get('min_amount') or ''),
                            'max_amount': str(r.get('max_amount') or ''),
                            'is_remote': str(r.get('is_remote') or ''),
                            'job_url': normalize_url(r.get('job_url') or ''),
                            'description': str(r.get('description') or '')[:3500],
                        })
                        record['key'] = get_key(record)
                        records.append(record)
                except Exception as exc:
                    LOG.warning('Source failed [%s / %s / %s]: %s', country, term, site, exc)
                time.sleep(1)
    incoming = pd.DataFrame(records, columns=COLUMNS)
    existing = load_existing()
    if incoming.empty:
        LOG.warning('No new results found; keeping historical records unchanged.')
        return len(existing), 0
    incoming = incoming.drop_duplicates(subset=['key'])
    old_keys = set(existing['key'])
    added = len(set(incoming['key']) - old_keys)
    # Update last-seen for revisited jobs; retain historical jobs for audit.
    existing_by_key = {r['key']:r for r in existing.to_dict('records') if r.get('key')}
    for r in incoming.to_dict('records'):
        if r['key'] in existing_by_key:
            r['first_seen'] = existing_by_key[r['key']].get('first_seen') or today
        existing_by_key[r['key']] = r
    combined = pd.DataFrame(list(existing_by_key.values()), columns=COLUMNS)
    combined = combined.sort_values(['last_seen','first_seen'], ascending=False)
    FILE.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(FILE, index=False)
    return len(combined), added

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--per-search', type=int, default=int(os.getenv('JOBS_PER_SEARCH', '15')))
    parser.add_argument('--hours-old', type=int, default=int(os.getenv('HOURS_OLD', '168')))
    parser.add_argument('--sites', nargs='*', default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    total, added = collect(args.per_search, args.hours_old, args.sites)
    print(f'Finished. {total} jobs saved, {added} new jobs.')
