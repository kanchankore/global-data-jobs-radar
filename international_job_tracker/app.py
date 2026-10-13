from pathlib import Path
from datetime import datetime, timedelta, timezone
import pandas as pd
import streamlit as st
from config import COUNTRIES, REGIONAL_BOARDS, COLUMNS
from matching import classify, SKILL_PATTERNS

st.set_page_config(page_title='Global Data Jobs Radar', page_icon='🌍', layout='wide')
st.title('🌍 Global Data Jobs Radar')
st.caption('Jobs in Netherlands, Singapore and Dubai/UAE • ranked by your skills • sponsorship evidence clearly labelled')
path = Path(__file__).parent / 'data' / 'jobs.csv'
try:
    df = pd.read_csv(path, dtype=str, keep_default_na=False) if path.exists() else pd.DataFrame(columns=COLUMNS)
except Exception as exc:
    st.error(f'Unable to load job data: {exc}')
    st.stop()
for c in COLUMNS:
    if c not in df.columns: df[c] = ''

with st.sidebar:
    st.header('Your job preferences')
    countries = st.multiselect('Countries', list(COUNTRIES), default=list(COUNTRIES))
    roles = sorted(x for x in df['search_term'].unique() if x)
    terms = st.multiselect('Search roles', roles, default=roles)
    sites = sorted(x for x in df['site'].unique() if x)
    chosen_sites = st.multiselect('Collected sources', sites, default=sites)
    st.divider()
    minimum, maximum = st.slider('Preferred experience range (years)', 0, 15, (3, 6))
    strict_exp = st.checkbox('Hide jobs asking for more experience', value=True)
    visa_mode = st.selectbox('Visa / work permit', ['Show all (recommended)', 'Exclude explicitly unavailable', 'Explicit sponsorship wording only'], index=1)
    st.caption('“Not stated” means the listing does not provide enough evidence. It does not mean sponsorship is available.')
    language = st.selectbox('Language', ['Prefer English (rank only)', 'Hide explicit other-language requirements', 'All languages'])
    skills = st.multiselect('Prioritize skills', list(SKILL_PATTERNS), default=['SQL', 'Python', 'ETL', 'Airflow', 'Data Quality', 'Snowflake', 'Power BI'])
    min_score = st.slider('Minimum match score', 0, 100, 40, 5)
    hide_irrelevant = st.checkbox('Exclude unrelated job titles', value=True)
    keyword = st.text_input('Keyword across listings', placeholder='Banking, SSIS, Databricks...')
    days = st.select_slider('Last seen within', options=[1,3,7,14,30,90,365], value=30, format_func=lambda d:f'{d} days')
    new_only = st.checkbox('First discovered in last 7 days')

filtered = df[df['country'].isin(countries) & df['search_term'].isin(terms) & df['site'].isin(chosen_sites)].copy()
if keyword:
    combined = filtered[['title','company','location','description']].fillna('').agg(' '.join, axis=1)
    filtered = filtered[combined.str.contains(keyword, case=False, regex=False)]
cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
filtered = filtered[filtered['last_seen'] >= cutoff]
if new_only:
    fresh = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
    filtered = filtered[filtered['first_seen'] >= fresh]
if not filtered.empty:
    rows = filtered.apply(lambda r: classify(r, skills), axis=1).apply(pd.Series)
    filtered = pd.concat([filtered.reset_index(drop=True), rows.reset_index(drop=True)], axis=1)
    if hide_irrelevant: filtered = filtered[~filtered['Unrelated title']]
    if visa_mode == 'Exclude explicitly unavailable': filtered = filtered[filtered['Visa status'] != 'Explicitly unavailable']
    elif visa_mode == 'Explicit sponsorship wording only': filtered = filtered[filtered['Visa status'] == 'Explicitly offered (verify)']
    if language == 'Hide explicit other-language requirements': filtered = filtered[~filtered['Other language required']]
    if strict_exp: filtered = filtered[filtered['Years required (detected)'].isna() | (filtered['Years required (detected)'] <= maximum)]
    filtered = filtered[filtered['Match score'] >= min_score]
    filtered = filtered.sort_values(['Match score','last_seen'], ascending=[False,False])

cols = st.columns(4)
cols[0].metric('Matching jobs', len(filtered))
cols[1].metric('Companies', filtered['company'].nunique() if not filtered.empty else 0)
cols[2].metric('Sources collected', filtered['site'].nunique() if not filtered.empty else 0)
cols[3].metric('Last collection', df['last_seen'].max() if not df.empty else 'Not yet')
st.info('Sponsorship labels are based on wording in the collected listing, not a verified immigration decision. Experience requirements are estimated from explicit text only. Missing descriptions can lead to unknown status.')
if df.empty:
    st.warning('No jobs collected yet. Run the GitHub Actions workflow to populate the dashboard.')
else:
    show = ['Match score','country','title','company','location','Visa status','Years required (detected)','Skills matched','site','date_posted','job_url']
    st.dataframe(filtered[show].rename(columns={'job_url':'Apply / View job'}), column_config={'Apply / View job':st.column_config.LinkColumn('Apply / View job',display_text='Open job'), 'Match score':st.column_config.ProgressColumn('Match score', min_value=0,max_value=100)}, use_container_width=True, hide_index=True, height=620)
    st.download_button('⬇️ Export matching jobs',filtered.to_csv(index=False).encode(),'matching_jobs.csv','text/csv')

st.subheader('More country-specific job boards')
st.caption('Links below are additional search sources, NOT automatically ingested. Automated integrations require an allowed API/feed or individual permission.')
extra = {
 'Netherlands': {'JobThing – recognised sponsors':'https://jobthing.nl/','EURES':'https://eures.europa.eu/','Welcome to NL':'https://www.welcome-to-nl.nl/'},
 'Singapore': {'foundit Singapore':'https://www.foundit.sg/','eFinancialCareers Singapore':'https://www.efinancialcareers.sg/'},
 'Dubai / UAE': {'foundit Gulf':'https://www.founditgulf.com/','Laimoon':'https://www.laimoon.com/','Dubai Careers':'https://dubaicareers.ae/'}}
for country, links in REGIONAL_BOARDS.items():
    with st.expander(country):
        merged = {**links, **extra.get(country,{})}
        st.markdown(' · '.join(f'[{name}]({url})' for name,url in merged.items()))
st.caption('Never pay recruiters for a visa/job promise. Verify job details and sponsorship with the employer. The tracker does not apply on your behalf.')
