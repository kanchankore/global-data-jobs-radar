import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta, timezone
from config import COUNTRIES, REGIONAL_BOARDS, COLUMNS

st.set_page_config(page_title='Global Data Jobs Radar', page_icon='🌍', layout='wide')
st.title('🌍 Global Data Jobs Radar')
st.caption('Daily discovery for Data Engineering, Analytics and BI | Netherlands • Singapore • Dubai')
path = Path(__file__).parent / 'data' / 'jobs.csv'
if path.exists():
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
else:
    df = pd.DataFrame(columns=COLUMNS)
for c in COLUMNS:
    if c not in df.columns:
        df[c] = ''
with st.sidebar:
    st.header('Search filters')
    countries = st.multiselect('Countries', list(COUNTRIES), default=list(COUNTRIES))
    roles = sorted(x for x in df['search_term'].unique() if x)
    terms = st.multiselect('Roles', roles, default=roles)
    sites = sorted(x for x in df['site'].unique() if x)
    selected_sites = st.multiselect('Sources', sites, default=sites)
    keyword = st.text_input('Keyword in title/company/location', placeholder='SQL, Python, Airflow, Snowflake...')
    days = st.select_slider('Last seen within', options=[1,3,7,14,30,90,365], value=30, format_func=lambda x: f'{x} days')
    only_new = st.checkbox('First discovered in last 7 days')
filtered = df[df['country'].isin(countries) & df['search_term'].isin(terms) & df['site'].isin(selected_sites)].copy()
if keyword:
    m = filtered[['title','company','location','description']].fillna('').agg(' '.join, axis=1).str.contains(keyword, case=False, regex=False)
    filtered = filtered[m]
cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
filtered = filtered[filtered['last_seen'] >= cutoff]
if only_new:
    fresh = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
    filtered = filtered[filtered['first_seen'] >= fresh]
stats = st.columns(4)
stats[0].metric('Matching jobs', f'{len(filtered):,}')
stats[1].metric('Companies', filtered['company'].nunique() if len(filtered) else 0)
stats[2].metric('Sources', filtered['site'].nunique() if len(filtered) else 0)
stats[3].metric('Last collection', df['last_seen'].max() if len(df) else 'Not run yet')
if df.empty:
    st.info('No jobs collected yet. Run `python collect.py` locally or trigger the GitHub Actions workflow. The dashboard will populate afterward.')
else:
    filtered = filtered.sort_values(['last_seen', 'first_seen'], ascending=False)
    st.dataframe(filtered[['first_seen','country','title','company','location','site','date_posted','job_url']].rename(columns={'job_url':'Apply / View job', 'first_seen':'Discovered'}),
                 column_config={'Apply / View job':st.column_config.LinkColumn('Apply / View job', display_text='Open job')},
                 hide_index=True, use_container_width=True, height=590)
    st.download_button('⬇️ Export filtered jobs as CSV', filtered.to_csv(index=False).encode('utf-8'), 'filtered_jobs.csv','text/csv')
st.subheader('Regional sites to explore')
st.caption('These are direct portal links. They are not yet automatically ingested by the collector unless supported by its selected sources.')
for country, links in REGIONAL_BOARDS.items():
    with st.expander(country):
        st.markdown(' · '.join(f'[{name}]({url})' for name, url in links.items()))
st.caption('Coverage is partial: search engines and job boards may rate-limit, change pages, or block automation. Check the original listing before applying. This app does not auto-apply.')
