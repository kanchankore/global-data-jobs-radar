COUNTRIES = {
    "Netherlands": {"location": "Netherlands", "indeed_country": "Netherlands", "sites": ["indeed", "glassdoor", "linkedin"]},
    "Singapore": {"location": "Singapore", "indeed_country": "Singapore", "sites": ["indeed", "glassdoor", "linkedin"]},
    "Dubai / UAE": {"location": "Dubai, UAE", "indeed_country": "United Arab Emirates", "sites": ["indeed", "linkedin", "bayt"]},
}
SEARCH_TERMS = ["Data Engineer", "Data Analyst", "Business Intelligence Analyst", "Analytics Engineer", "Data Quality Analyst", "ETL Developer"]
COLUMNS = ["first_seen", "last_seen", "country", "search_term", "title", "company", "location", "site", "date_posted", "job_type", "min_amount", "max_amount", "is_remote", "job_url", "description", "key"]
REGIONAL_BOARDS = {
    "Netherlands": {
        "Nationale Vacaturebank": "https://www.nationalevacaturebank.nl/",
        "Intermediair": "https://www.intermediair.nl/vacatures",
        "Magnet.me": "https://magnet.me/en/",
        "Werk.nl": "https://www.werk.nl/",
    },
    "Singapore": {
        "MyCareersFuture": "https://www.mycareersfuture.gov.sg/",
        "JobStreet Singapore": "https://sg.jobstreet.com/",
        "JobsDB Singapore": "https://sg.jobsdb.com/",
    },
    "Dubai / UAE": {
        "GulfTalent": "https://www.gulftalent.com/uae/jobs",
        "Naukrigulf": "https://www.naukrigulf.com/",
        "Dubai Careers": "https://dubaicareers.ae/",
        "Bayt": "https://www.bayt.com/en/uae/jobs/",
    },
}
