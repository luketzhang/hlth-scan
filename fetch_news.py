#!/usr/bin/env python3
"""Fetch public HLTH news pages and produce static data/news.json."""
import json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
import requests
from bs4 import BeautifulSoup

SOURCE = 'https://hlth.com/insights/news'
OUTPUT = Path(__file__).parent / 'data' / 'news.json'
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; HLTHNewsDashboard/2.0; public news aggregation)'}
DOMAINS = {
 'Patient Access and Engagement': ['patient access','patient engagement','patient portal','appointment','scheduling','navigation','patient experience','patient communication','consumer health','health literacy','patient outreach','patient journey','patient-facing','patient activation','patient intake','patient acquisition','access to care','benefits navigation','price transparency','patient support'],
 'Clinical Decision Support': ['clinical decision','clinical ai','diagnostic','diagnosis','decision support','clinical workflow ai','radiology ai','clinical documentation','precision medicine','treatment recommendation','clinical intelligence','physician copilot','medical imaging','clinical guidance','decision-making','clinical algorithm','clinical assistant','pathology ai','risk stratification','predictive analytics','ambient ai','ai scribe','clinical reasoning'],
 'Behavioral Health & Digital Therapeutics': ['behavioral health','mental health','psychiatr','psycholog','digital therapeutic','substance use','addiction','depression','anxiety','therapy app','cognitive behavioral','mental wellness','digital treatment','digital therapeutics','autism','adhd','behavior change','psychotherapy'],
 'Care Operations and Coordination': ['care coordination','care management','referral','discharge','hospital operations','workflow','staffing','revenue cycle','prior authorization','care team','administrative','population health','utilization management','clinical operations','hospital efficiency','provider productivity','ehr','electronic health record','interoperability','health information exchange','care transition','claims processing','healthcare workforce','patient flow','practice management','case management','care navigation'],
 'Virtual & Hybrid Care Delivery': ['telehealth','telemedicine','virtual care','virtual health','virtual-first','hybrid care','online consultation','digital clinic','virtual visit','virtual primary care','online care','digital-first','video consultation','virtual nursing','virtual hospital','hospital at home','home-based care','virtual specialty','online therapy'],
 'Remote Monitoring': ['remote patient monitoring','remote monitoring','wearable','connected device','continuous monitoring','home monitoring','sensor','digital biomarker','at-home monitoring','smartwatch','smart watch','connected health','biosensor','glucose monitor','blood pressure monitor','cardiac monitor','monitoring platform','patient monitoring','remote diagnostics','continuous glucose'],
}

DATE_RE = re.compile(r'\b(\d{1,2}\s+[A-Za-z]{3,9}\s+20\d{2})\b')
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def soup_for(url):
    resp = SESSION.get(url, timeout=22)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')

def clean(s): return re.sub(r'\s+', ' ', s or '').strip()

def extract_date(text):
    match = DATE_RE.search(text)
    if match:
        for fmt in ('%d %b %Y', '%d %B %Y'):
            try: return datetime.strptime(match.group(1), fmt).date().isoformat()
            except ValueError: pass
    return ''

def meta(soup, *pairs):
    for key, value in pairs:
        el = soup.find('meta', attrs={key: value})
        if el and el.get('content'): return clean(el['content'])
    return ''

def summary_for(soup):
    description = meta(soup, ('name','description'), ('property','og:description'))
    if len(description) >= 60: return description[:420]
    body = soup.find('article') or soup.find('main') or soup
    paragraphs = [clean(p.get_text(' ',strip=True)) for p in body.find_all('p')]
    paragraphs = [p for p in paragraphs if len(p)>70 and not re.search(r'cookie|privacy policy|subscribe to|sign up',p,re.I)]
    return clean(' '.join(paragraphs[:2]))[:420] or 'Open the original article for details.'

def classify(title, summary):
    title_text = title.lower()
    text = (title + ' ' + summary).lower()
    scored = []
    for domain, keywords in DOMAINS.items():
        score = sum((4 if phrase in title_text else 2) for phrase in keywords if phrase in text)
        if score: scored.append((score, domain))
    if not scored: return ['Uncategorized']
    scored.sort(reverse=True)
    best = scored[0][0]
    return [domain for score, domain in scored if score >= max(2, best * 0.35)][:3]

def candidates(soup):
    result, seen = [], set()
    for a in soup.select('a[href]'):
        href = urldefrag(urljoin(SOURCE, a['href']))[0]
        parsed = urlparse(href)
        if parsed.scheme not in ('http','https') or not (parsed.hostname or '').endswith('.hlth.com') and parsed.hostname != 'hlth.com': continue
        if href.rstrip('/') == SOURCE or href in seen: continue
        text = clean(a.get_text(' ',strip=True))
        date = extract_date(text)
        # Prefer article-shaped URLs or listings with dated link text.
        path = parsed.path.lower()
        if not date and not (('/insights/' in path or '/news/' in path) and len(text) >= 28): continue
        if len(text)<28: continue
        title = clean(DATE_RE.sub('',text))
        title = re.sub(r'\bAuthor\s*:\s*HLTH.*$', '', title, flags=re.I).strip(' -|:')
        if len(title)<18: continue
        seen.add(href)
        result.append((href,title,date))
    return result

def fetch():
    listing = soup_for(SOURCE)
    entries = candidates(listing)
    print(f'Found {len(entries)} candidate links', file=sys.stderr)
    articles = []
    for url, listing_title, listing_date in entries[:45]:
        try:
            page = soup_for(url)
            canonical = page.find('link', rel='canonical')
            canonical_url = urljoin(url, canonical['href']) if canonical and canonical.get('href') else url
            title = meta(page,('property','og:title')) or (clean(page.h1.get_text(' ',strip=True)) if page.h1 else listing_title)
            title = re.sub(r'\s*[|–-]\s*HLTH\s*$', '', title, flags=re.I)
            if not title or len(title)<18: title=listing_title
            description = summary_for(page)
            date = listing_date or extract_date(meta(page,('property','article:published_time')))
            if not date:
                time_el = page.find('time')
                if time_el: date = extract_date(time_el.get('datetime','') or time_el.get_text(' ',strip=True))
            if not date:
                published = meta(page,('property','article:published_time'),('name','date'))
                date = published[:10] if re.match(r'^\d{4}-\d{2}-\d{2}',published) else ''
            articles.append({'title':title,'date':date,'url':canonical_url,'summary':description,'domains':classify(title,description),'why_it_matters':'This development may affect healthcare technology adoption, care delivery, or industry strategy. Review the source for specifics.'})
            time.sleep(.15)
        except requests.RequestException as exc:
            print(f'Skipped {url}: {exc}',file=sys.stderr)
    deduped = {a['url']:a for a in articles}
    return sorted(deduped.values(),key=lambda a:a['date'],reverse=True)[:35]

def main():
    articles = fetch()
    if not articles:
        raise RuntimeError('No articles extracted; refusing to overwrite previously published news data.')
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    payload = {'source':SOURCE,'updated_at':datetime.now(timezone.utc).isoformat(),'articles':articles}
    tmp = OUTPUT.with_suffix('.tmp')
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(OUTPUT)
    print(f'Wrote {len(articles)} articles to {OUTPUT}')

if __name__=='__main__': main()
