"""Conservative, explainable classification for job search listings."""
import re

NEGATIVE = re.compile(r'\b(no visa sponsorship|visa sponsorship (?:is )?not (?:available|provided)|cannot sponsor|unable to sponsor|must (?:already )?have (?:the )?right to work|must (?:already )?be authorized to work|no work permit sponsorship|no relocation support)\b', re.I)
POSITIVE = re.compile(r'\b(visa sponsorship (?:is )?(?:available|provided|offered)|we (?:will|can) sponsor|work visa sponsorship|sponsor (?:your|a) (?:work )?visa|relocation (?:and visa )?(?:support|package)|sponsorship (?:and|for) (?:work )?permit)\b', re.I)
LANGUAGE = re.compile(r'\b(dutch|nederlands|mandarin|arabic)\s+(?:language\s+)?(?:required|mandatory|fluency|proficiency|speaking)|(?:fluent|proficient)\s+in\s+(?:dutch|nederlands|mandarin|arabic)\b', re.I)
UNRELATED = re.compile(r'\b(data center|datacenter|data centre|scientist|machine learning researcher|sales engineer|network engineer|devops engineer)\b', re.I)
SENIOR = re.compile(r'\b(principal|staff|director|head of|lead|architect|senior manager)\b', re.I)
SKILL_PATTERNS = {'SQL':r'\bsql\b','Python':r'\bpython\b','ETL':r'\betl\b|\bdata pipeline','Airflow':r'\bairflow\b','Data Quality':r'\bdata quality\b|\bdata governance\b','Snowflake':r'\bsnowflake\b','Power BI':r'\bpower\s*bi\b','AWS':r'\baws\b','Azure':r'\bazure\b','Spark':r'\bspark\b|\bpyspark\b','Hadoop':r'\bhadoop\b|\bhive\b','Data Governance':r'\bdata governance\b','Collibra':r'\bcollibra\b'}

def extract_experience(text):
    """Returns numeric required years only on explicit evidence; otherwise None."""
    patterns = [r'\b(\d{1,2})\s*(?:[-–to]{1,3}\s*(\d{1,2}))?\s*\+?\s*years?\s+(?:of\s+)?(?:relevant\s+|professional\s+|work\s+)?experience\b', r'\b(?:experience of|minimum of|at least)\s+(\d{1,2})\s*\+?\s*years?\b']
    for pattern in patterns:
        found = re.search(pattern, text, re.I)
        if found:
            return int(found.group(1))
    return None

def classify(row, preferred_skills):
    title = str(row.get('title',''))
    description = str(row.get('description',''))
    text = title + ' ' + description
    if NEGATIVE.search(text):
        visa = 'Explicitly unavailable'
    elif POSITIVE.search(text):
        visa = 'Explicitly offered (verify)'
    else:
        visa = 'Not stated'
    hits = [skill for skill in preferred_skills if re.search(SKILL_PATTERNS[skill], text, re.I)]
    years = extract_experience(description)
    irrelevant = bool(UNRELATED.search(title))
    score = min(100, max(0, 50 + 7*len(hits) - (45 if irrelevant else 0) - (12 if SENIOR.search(title) else 0) + (10 if visa.startswith('Explicitly offered') else 0)))
    return {'Visa status': visa, 'Years required (detected)': years, 'Skills matched': ', '.join(hits), 'Match score': score, 'Other language required': bool(LANGUAGE.search(description)), 'Unrelated title': irrelevant}
