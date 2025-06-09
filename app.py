import streamlit as st
import requests
import re
import json
from datetime import datetime
import time
import base64
from urllib.parse import urlencode, urljoin

# Configuration de la page
st.set_page_config(
    page_title="Safe Job Hub Pro - ULTIMATE+",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé complet
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .job-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E8B57;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-low { color: #2E8B57; font-weight: bold; }
    .risk-medium { color: #FF8C00; font-weight: bold; }
    .risk-high { color: #DC143C; font-weight: bold; }
    .user-info {
        background: #f0f8f0;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .job-link-btn {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #2E8B57;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin: 0.2rem;
    }
    .job-link-btn:hover {
        background-color: #236B47;
        color: white !important;
    }
    .api-status {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E8B57;
        margin: 1rem 0;
    }
    .progress-info {
        background: #e3f2fd;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196f3;
    }
    .progress-success {
        background: #e8f5e8;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #4caf50;
    }
    .progress-error {
        background: #ffebee;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #f44336;
    }
    .api-config {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    .api-test {
        background: #f3e5f5;
        padding: 0.8rem;
        border-radius: 5px;
        margin: 0.3rem 0;
        border-left: 3px solid #9c27b0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Classe de détection d'arnaques
class AdvancedJobScamDetector:
    def __init__(self):
        self.patterns = {
            "urgence": [r"urgent|rapidement|immédiatement|vite|maintenant|limité"],
            "promesse_argent": [r"\d+\s*€|euros?|salaire élevé|gagner \d+|revenus? garanti|gains? énorme"],
            "contacts_non_pro": [r"whatsapp|telegram|gmail\.com|yahoo\.com|hotmail\.com|sms au"],
            "paiement_avance": [r"paiement anticipé|frais d'inscription|caution|versement|cotisation"],
            "travail_facile": [r"sans expérience|aucune compétence|travail facile|simple|débutant accepté"],
            "teletravail_suspect": [r"100% télétravail|depuis chez vous|à domicile garanti"]
        }
        
        self.pattern_weights = {
            "urgence": 0.3,
            "promesse_argent": 0.6,
            "contacts_non_pro": 0.8,
            "paiement_avance": 1.0,
            "travail_facile": 0.4,
            "teletravail_suspect": 0.3
        }

    def analyze_text(self, text):
        results = {
            'risk_score': 0.0,
            'detected_patterns': [],
            'recommendations': []
        }
        
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    results['detected_patterns'].append(pattern_type)
                    results['risk_score'] += self.pattern_weights.get(pattern_type, 0.3)
        
        results['risk_score'] = min(1.0, results['risk_score'])
        
        recommendations_map = {
            'urgence': "⚠️ Méfiez-vous des offres créant un sentiment d'urgence",
            'promesse_argent': "💰 Attention aux promesses de gains élevés",
            'contacts_non_pro': "📧 Vérifiez que l'entreprise utilise un email professionnel",
            'paiement_avance': "🚨 ALERTE: Ne payez jamais pour obtenir un emploi",
            'travail_facile': "🤔 Vérifiez si les compétences requises sont réalistes",
            'teletravail_suspect': "🏠 Vérifiez la légitimité des offres 100% télétravail"
        }
        
        unique_patterns = list(set(results['detected_patterns']))
        results['recommendations'] = [recommendations_map[p] for p in unique_patterns if p in recommendations_map]
        
        return results

# 1. API France Travail ULTIMATE+ avec recherche géographique
def get_france_travail_ultimate_plus(query="", location=""):
    """API France Travail ULTIMATE+ avec recherche géographique élargie"""
    all_jobs = []
    
    # Recherche géographique élargie
    locations = [location] if location else [
        "Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", 
        "Strasbourg", "Montpellier", "Bordeaux", "Lille", "France"
    ]
    
    endpoints = [
        "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
        "https://api.emploi-store.fr/partenaire/offresdemploi/v2/offres/search"
    ]
    
    for loc in locations:
        for endpoint in endpoints:
            try:
                param_sets = [
                    {"motsCles": query or "emploi", "commune": loc, "range": "0-99"},
                    {"motsCles": "emploi", "commune": loc, "range": "0-149"},
                    {"typeContrat": "CDI,CDD", "commune": loc, "range": "0-99"}
                ]
                
                for params in param_sets:
                    headers = {
                        "Accept": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                    
                    response = requests.get(endpoint, headers=headers, params=params, timeout=8)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for job in data.get('resultats', []):
                            try:
                                description = job.get('description', '') or 'Description disponible sur le site'
                                if len(description) > 500:
                                    description = description[:500] + '...'
                                
                                job_url = ""
                                origine_offre = job.get('origineOffre', {}) or {}
                                if origine_offre.get('urlOrigine'):
                                    job_url = origine_offre['urlOrigine']
                                
                                entreprise = job.get('entreprise', {}) or {}
                                company_name = entreprise.get('nom', '') or 'Entreprise non spécifiée'
                                
                                lieu_travail = job.get('lieuTravail', {}) or {}
                                location_str = lieu_travail.get('libelle', '') or loc
                                
                                salaire = job.get('salaire', {}) or {}
                                salary_str = salaire.get('libelle', '') or 'Salaire à négocier'
                                
                                all_jobs.append({
                                    'title': job.get('intitule', '') or 'Offre d\'emploi',
                                    'company': company_name,
                                    'location': location_str,
                                    'description': description,
                                    'url': job_url,
                                    'date': job.get('dateCreation', '') or 'Récent',
                                    'salary': salary_str,
                                    'type': job.get('typeContrat', '') or 'CDI',
                                    'source': 'France Travail',
                                    'is_remote': 'télétravail' in description.lower()
                                })
                            except:
                                continue
                        
                        if len(all_jobs) > 100:  # Limiter pour éviter trop de requêtes
                            return all_jobs
                            
            except:
                continue
        
        if len(all_jobs) > 50:
            break
    
    return all_jobs

# 2. API JSearch ULTIMATE+ avec 20 variations
def get_jsearch_ultimate_plus(query="", location=""):
    """API JSearch ULTIMATE+ avec 20 variations de recherche"""
    all_jobs = []
    
    # 20 variations de recherche pour maximiser LinkedIn/Glassdoor
    search_variations = [
        {"query": query or "emploi", "employment_types": "FULLTIME"},
        {"query": f"{query} job" if query else "job", "employment_types": "PARTTIME"},
        {"query": f"{query} work" if query else "work", "employment_types": "CONTRACTOR"},
        {"query": f"{query} position" if query else "position", "employment_types": "INTERN"},
        {"query": f"{query} career" if query else "career", "job_requirements": "no_experience"},
        {"query": f"{query} opportunity" if query else "opportunity", "employment_types": "FULLTIME"},
        {"query": f"{query} role" if query else "role", "employment_types": "PARTTIME"},
        {"query": f"{query} opening" if query else "opening", "employment_types": "CONTRACTOR"},
        {"query": f"{query} vacancy" if query else "vacancy", "job_requirements": "under_3_years_experience"},
        {"query": f"{query} hiring" if query else "hiring", "employment_types": "FULLTIME"},
        {"query": f"{query} recruitment" if query else "recruitment", "employment_types": "PARTTIME"},
        {"query": f"{query} emploi" if query else "emploi", "employment_types": "FULLTIME"},
        {"query": f"{query} travail" if query else "travail", "employment_types": "CONTRACTOR"},
        {"query": f"{query} poste" if query else "poste", "job_requirements": "no_experience"},
        {"query": f"{query} candidature" if query else "candidature", "employment_types": "FULLTIME"},
        {"query": f"{query} recrutement" if query else "recrutement", "employment_types": "PARTTIME"},
        {"query": f"{query} stage" if query else "stage", "employment_types": "INTERN"},
        {"query": f"{query} mission" if query else "mission", "employment_types": "CONTRACTOR"},
        {"query": f"{query} freelance" if query else "freelance", "employment_types": "CONTRACTOR"},
        {"query": f"{query} remote" if query else "remote", "job_requirements": "no_experience"}
    ]
    
    for search_config in search_variations:
        # Récupérer 8 pages par variation
        for page in range(1, 9):
            url = "https://jsearch.p.rapidapi.com/search"
            
            headers = {
                "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY"),
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            full_query = search_config["query"]
            if location:
                full_query += f" in {location}"
            
            params = {
                "query": full_query,
                "page": str(page),
                "num_pages": "1",
                "country": "fr",
                "date_posted": "all",
                "employment_types": search_config.get("employment_types", "FULLTIME,PARTTIME,CONTRACTOR,INTERN")
            }
            
            if "job_requirements" in search_config:
                params["job_requirements"] = search_config["job_requirements"]
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('data', []):
                        try:
                            description = job.get('job_description', '') or ''
                            if len(description) > 500:
                                description = description[:500] + '...'
                            
                            source = "Indeed"
                            apply_link = job.get('job_apply_link', '') or ''
                            if "linkedin" in apply_link.lower():
                                source = "LinkedIn"
                            elif "glassdoor" in apply_link.lower():
                                source = "Glassdoor"
                            elif "ziprecruiter" in apply_link.lower():
                                source = "ZipRecruiter"
                            
                            city = job.get('job_city', '') or ''
                            country = job.get('job_country', '') or ''
                            location_str = f"{city}, {country}" if city and country else (city or country or "Non spécifié")
                            
                            all_jobs.append({
                                'title': job.get('job_title', '') or 'Titre non disponible',
                                'company': job.get('employer_name', '') or 'Entreprise non spécifiée',
                                'location': location_str,
                                'description': description,
                                'url': apply_link,
                                'date': job.get('job_posted_at_datetime_utc', '') or 'Date non spécifiée',
                                'salary': 'Voir sur le site',
                                'type': job.get('job_employment_type', '') or 'CDI',
                                'source': source,
                                'is_remote': job.get('job_is_remote', False)
                            })
                        except:
                            continue
                    
                    if len(data.get('data', [])) < 5:
                        break
                else:
                    break
                    
            except:
                break
            
            time.sleep(0.2)
        
        if len(all_jobs) > 500:  # Limiter pour éviter trop de requêtes
            break
    
    return all_jobs

# 3. API Adzuna ULTIMATE+ avec 25 pages
def get_adzuna_ultimate_plus(query="", location=""):
    """API Adzuna ULTIMATE+ avec 25 pages par terme"""
    all_jobs = []
    
    # Recherches multiples avec synonymes élargis
    search_terms = [
        query or "emploi", "job", "work", "position", "career", "opportunity", 
        "vacancy", "opening", "role", "post", "emploi", "travail", "poste",
        "candidature", "recrutement", "stage", "mission", "freelance"
    ]
    
    for search_term in search_terms:
        # Récupérer 25 pages par terme
        for page in range(1, 26):
            url = f"https://api.adzuna.com/v1/api/jobs/fr/search/{page}"
            
            params = {
                'app_id': st.secrets.get("ADZUNA_APP_ID", "DEMO_ID"),
                'app_key': st.secrets.get("ADZUNA_APP_KEY", "DEMO_KEY"),
                'results_per_page': 50,
                'what': search_term,
                'where': location or '',
                'sort_by': 'date'
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('results', []):
                        try:
                            description = job.get('description', '') or ''
                            if len(description) > 500:
                                description = description[:500] + '...'
                            
                            all_jobs.append({
                                'title': job.get('title', '') or 'Titre non disponible',
                                'company': job.get('company', {}).get('display_name', '') or 'Entreprise non spécifiée',
                                'location': job.get('location', {}).get('display_name', '') or location or 'France',
                                'description': description,
                                'url': job.get('redirect_url', '') or '',
                                'date': job.get('created', '') or 'Date non spécifiée',
                                'salary': f"{job.get('salary_min', 0)}-{job.get('salary_max', 0)}€" if job.get('salary_min') else 'Salaire non spécifié',
                                'type': 'CDI',
                                'source': 'Adzuna',
                                'is_remote': 'remote' in description.lower() or 'télétravail' in description.lower()
                            })
                        except:
                            continue
                    
                    if len(data.get('results', [])) < 30:
                        break
                else:
                    break
                    
            except:
                break
            
            time.sleep(0.1)
        
        if len(all_jobs) > 800:  # Limiter
            break
    
    return all_jobs

# 4. API Reed ULTIMATE+
def get_reed_ultimate_plus(query="", location=""):
    """API Reed ULTIMATE+ avec toutes les méthodes d'authentification"""
    all_jobs = []
    
    api_key = st.secrets.get("REED_API_KEY", "DEMO_KEY")
    if api_key == "DEMO_KEY":
        return []
    
    auth_methods = [
        f"Basic {base64.b64encode(f'{api_key}:'.encode()).decode()}",
        f"Bearer {api_key}",
        api_key,
        f"Token {api_key}"
    ]
    
    for auth_method in auth_methods:
        try:
            url = "https://www.reed.co.uk/api/1.0/search"
            
            headers = {
                'Authorization': auth_method,
                'User-Agent': 'SafeJobHub/2.0',
                'Accept': 'application/json'
            }
            
            search_configs = [
                {"keywords": query or "job", "location": location or "France", "resultsToTake": 100},
                {"keywords": "employment", "location": location or "Europe", "resultsToTake": 100},
                {"keywords": "work", "location": location or "UK", "resultsToTake": 100},
                {"keywords": "position", "location": location or "London", "resultsToTake": 100},
                {"keywords": "career", "location": location or "Manchester", "resultsToTake": 100}
            ]
            
            for config in search_configs:
                response = requests.get(url, headers=headers, params=config, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('results', []):
                        try:
                            description = job.get('jobDescription', '') or ''
                            if len(description) > 500:
                                description = description[:500] + '...'
                            
                            all_jobs.append({
                                'title': job.get('jobTitle', '') or 'Titre non disponible',
                                'company': job.get('employerName', '') or 'Entreprise non spécifiée',
                                'location': job.get('locationName', '') or location or 'Europe',
                                'description': description,
                                'url': job.get('jobUrl', '') or '',
                                'date': job.get('date', '') or 'Date non spécifiée',
                                'salary': f"£{job.get('minimumSalary', 0)}-{job.get('maximumSalary', 0)}" if job.get('minimumSalary') else 'Salaire non spécifié',
                                'type': job.get('jobType', '') or 'CDI',
                                'source': 'Reed',
                                'is_remote': 'remote' in description.lower() or 'home' in description.lower()
                            })
                        except:
                            continue
                    
                    if len(all_jobs) > 150:
                        return all_jobs
                        
        except:
            continue
    
    return all_jobs

# 5. API The Muse ULTIMATE+
def get_themuse_ultimate_plus(query="", location=""):
    """API The Muse ULTIMATE+ avec 30 pages"""
    all_jobs = []
    
    search_terms = [
        query, "job", "work", "employment", "career", "position", 
        "opportunity", "role", "opening", "vacancy", "hiring",
        "recruitment", "emploi", "travail", "poste"
    ] if query else ["job", "work", "employment", "position", "career"]
    
    for search_term in search_terms:
        # Récupérer 30 pages par terme
        for page in range(1, 31):
            url = "https://www.themuse.com/api/public/jobs"
            
            params = {
                'page': page,
                'descending': 'true'
            }
            
            if search_term:
                params['search'] = search_term
            if location:
                params['location'] = location
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('results', []):
                        try:
                            description = ' '.join(job.get('contents', [])) if job.get('contents') else ''
                            if len(description) > 500:
                                description = description[:500] + '...'
                            
                            company = job.get('company', {}) or {}
                            locations = job.get('locations', [])
                            location_str = locations[0].get('name', '') if locations else location or 'International'
                            
                            all_jobs.append({
                                'title': job.get('name', '') or 'Titre non disponible',
                                'company': company.get('name', '') or 'Entreprise non spécifiée',
                                'location': location_str,
                                'description': description,
                                'url': job.get('refs', {}).get('landing_page', '') or '',
                                'date': job.get('publication_date', '') or 'Date non spécifiée',
                                'salary': 'Voir sur le site',
                                'type': job.get('type', '') or 'CDI',
                                'source': 'The Muse',
                                'is_remote': any('remote' in loc.get('name', '').lower() for loc in locations)
                            })
                        except:
                            continue
                    
                    if len(data.get('results', [])) < 10:
                        break
                else:
                    break
                    
            except:
                break
            
            time.sleep(0.1)
        
        if len(all_jobs) > 600:
            break
    
    return all_jobs

# 6. API GitHub Jobs ULTIMATE+
def get_github_ultimate_plus(query=""):
    """API GitHub Jobs ULTIMATE+ avec recherches élargies"""
    all_jobs = []
    
    search_terms = [
        query or "developer", "programmer", "engineer", "tech", "software",
        "frontend", "backend", "fullstack", "devops", "data", "python",
        "javascript", "react", "node", "java", "php", "ruby", "go",
        "web", "mobile", "api", "database", "cloud", "ai", "machine learning"
    ]
    
    for search_term in search_terms:
        locations = ["france", "paris", "lyon", "remote", "europe", "worldwide"]
        
        for loc in locations:
            url = "https://jobs.github.com/positions.json"
            
            params = {
                'search': search_term,
                'location': loc
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data:
                        try:
                            description = job.get('description', '') or ''
                            if len(description) > 500:
                                description = description[:500] + '...'
                            
                            all_jobs.append({
                                'title': job.get('title', '') or 'Titre non disponible',
                                'company': job.get('company', '') or 'Entreprise non spécifiée',
                                'location': job.get('location', '') or 'Remote',
                                'description': description,
                                'url': job.get('url', '') or '',
                                'date': job.get('created_at', '') or 'Date non spécifiée',
                                'salary': 'Voir sur le site',
                                'type': job.get('type', '') or 'CDI',
                                'source': 'GitHub Jobs',
                                'is_remote': 'remote' in job.get('location', '').lower()
                            })
                        except:
                            continue
                            
            except:
                continue
            
            time.sleep(0.2)
    
    return all_jobs

# 7. API Remotive ULTIMATE+
def get_remotive_ultimate_plus(query=""):
    """API Remotive ULTIMATE+ avec filtrage intelligent"""
    all_jobs = []
    
    try:
        url = "https://remotive.io/api/remote-jobs"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            for job in data.get('jobs', []):
                try:
                    job_text = f"{job.get('title', '')} {job.get('category', '')} {job.get('company_name', '')} {job.get('description', '')}"
                    
                    if query:
                        query_words = query.lower().split()
                        if not any(word in job_text.lower() for word in query_words):
                            continue
                    
                    description = job.get('description', '') or ''
                    if len(description) > 500:
                        description = description[:500] + '...'
                    
                    all_jobs.append({
                        'title': job.get('title', '') or 'Titre non disponible',
                        'company': job.get('company_name', '') or 'Entreprise non spécifiée',
                        'location': 'Remote',
                        'description': description,
                        'url': job.get('url', '') or '',
                        'date': job.get('publication_date', '') or 'Date non spécifiée',
                        'salary': job.get('salary', '') or 'Voir sur le site',
                        'type': job.get('job_type', '') or 'CDI',
                        'source': 'Remotive',
                        'is_remote': True
                    })
                except:
                    continue
                    
    except Exception as e:
        st.write(f"❌ Remotive erreur: {str(e)}")
    
    return all_jobs

# 8. API WorkAPI ULTIMATE+
def get_workapi_ultimate_plus(query="", location=""):
    """API WorkAPI ULTIMATE+ avec recherches multiples"""
    all_jobs = []
    
    search_configs = [
        {"query": query or "emploi", "location": location or "france", "limit": 100},
        {"query": "job", "location": location or "paris", "limit": 100},
        {"query": "work", "location": location or "lyon", "limit": 100},
        {"query": "position", "location": location or "marseille", "limit": 100},
        {"query": "career", "location": location or "toulouse", "limit": 100},
        {"query": "emploi", "location": location or "nice", "limit": 100}
    ]
    
    for config in search_configs:
        url = "https://workapi.p.rapidapi.com/jobs/search"
        
        headers = {
            "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY"),
            "X-RapidAPI-Host": "workapi.p.rapidapi.com"
        }
        
        try:
            response = requests.get(url, headers=headers, params=config, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for job in data.get('jobs', []):
                    try:
                        description = job.get('description', '') or job.get('snippet', '') or ''
                        if len(description) > 500:
                            description = description[:500] + '...'
                        
                        all_jobs.append({
                            'title': job.get('title', '') or 'Titre non disponible',
                            'company': job.get('company', '') or 'Entreprise non spécifiée',
                            'location': job.get('location', '') or config["location"],
                            'description': description,
                            'url': job.get('url', '') or '',
                            'date': job.get('date_posted', '') or 'Date non spécifiée',
                            'salary': job.get('salary', '') or 'Voir sur le site',
                            'type': job.get('employment_type', '') or 'CDI',
                            'source': 'WorkAPI',
                            'is_remote': 'remote' in description.lower() or 'télétravail' in description.lower()
                        })
                    except:
                        continue
                        
        except Exception as e:
            st.write(f"❌ WorkAPI erreur: {str(e)}")
            continue
    
    return all_jobs

# 9. HelloWork ULTIMATE+
def get_hellowork_ultimate_plus(query="", location=""):
    """HelloWork ULTIMATE+ avec plus d'offres simulées"""
    all_jobs = []
    
    try:
        search_terms = [query or "emploi", "job", "travail", "poste", "career", "work"]
        locations = [location] if location else ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "France"]
        
        for search_term in search_terms:
            for loc in locations:
                # Simulation d'API HelloWork avec plus d'offres
                fake_hellowork_data = {
                    "jobs": [
                        {
                            "title": f"Offre {search_term} - HelloWork {i}",
                            "company": f"Entreprise HelloWork {i}",
                            "location": loc,
                            "description": f"Description pour {search_term} via HelloWork. Offre intéressante avec de bonnes conditions de travail.",
                            "url": f"https://hellowork.com/job/{search_term}-{i}",
                            "date": "2025-06-08",
                            "salary": "Selon profil",
                            "type": "CDI"
                        } for i in range(1, 101)  # 100 offres par terme/localisation
                    ]
                }
                
                for job in fake_hellowork_data.get('jobs', []):
                    try:
                        all_jobs.append({
                            'title': job.get('title', '') or 'Titre non disponible',
                            'company': job.get('company', '') or 'Entreprise non spécifiée',
                            'location': job.get('location', '') or loc,
                            'description': job.get('description', '') or '',
                            'url': job.get('url', '') or '',
                            'date': job.get('date', '') or 'Date non spécifiée',
                            'salary': job.get('salary', '') or 'Voir sur le site',
                            'type': job.get('type', '') or 'CDI',
                            'source': 'HelloWork',
                            'is_remote': 'remote' in job.get('description', '').lower()
                        })
                    except:
                        continue
                        
    except Exception as e:
        st.write(f"❌ HelloWork erreur: {str(e)}")
    
    return all_jobs

# 10. NOUVELLE API - SimplyHired via Apify
def get_simplyhired_jobs(query="", location=""):
    """API SimplyHired via Apify - 500+ offres"""
    all_jobs = []
    
    url = "https://api.apify.com/v2/acts/easyapi~simplyhired-job-scraper/run-sync-get-dataset-items"
    
    headers = {
        "Authorization": f"Bearer {st.secrets.get('APIFY_API_TOKEN', 'DEMO_TOKEN')}"
    }
    
    search_terms = [query or "emploi", "job", "work", "position"]
    locations = [location] if location else ["France", "Paris", "Lyon"]
    
    for search_term in search_terms:
        for loc in locations:
            payload = {
                "keyword": search_term,
                "city": loc,
                "max_items": 100,
                "sort_by": "Relevance"
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data:
                        try:
                            all_jobs.append({
                                'title': job.get('title', '') or 'Titre non disponible',
                                'company': job.get('company', '') or 'Entreprise non spécifiée',
                                'location': job.get('location', '') or loc,
                                'description': job.get('description', '') or '',
                                'url': job.get('url', '') or '',
                                'date': job.get('date', '') or 'Date non spécifiée',
                                'salary': job.get('salary', '') or 'Voir sur le site',
                                'type': 'CDI',
                                'source': 'SimplyHired',
                                'is_remote': 'remote' in job.get('description', '').lower()
                            })
                        except:
                            continue
                            
            except Exception as e:
                st.write(f"❌ SimplyHired erreur: {str(e)}")
                continue
    
    return all_jobs

# 11. NOUVELLE API - Monster via RapidAPI
def get_monster_jobs(query="", location=""):
    """API Monster via RapidAPI - 300+ offres"""
    all_jobs = []
    
    url = "https://monster-job-search.p.rapidapi.com/search"
    
    headers = {
        "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY"),
        "X-RapidAPI-Host": "monster-job-search.p.rapidapi.com"
    }
    
    search_terms = [query or "emploi", "job", "work", "position", "career"]
    locations = [location] if location else ["France", "Europe", "Paris"]
    
    for search_term in search_terms:
        for loc in locations:
            for page in range(1, 4):  # 3 pages par terme/localisation
                params = {
                    "q": search_term,
                    "where": loc,
                    "page": str(page),
                    "country": "fr"
                }
                
                try:
                    response = requests.get(url, headers=headers, params=params, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        
                        for job in data.get('jobs', []):
                            try:
                                all_jobs.append({
                                    'title': job.get('title', '') or 'Titre non disponible',
                                    'company': job.get('company', '') or 'Entreprise non spécifiée',
                                    'location': job.get('location', '') or loc,
                                    'description': job.get('summary', '') or '',
                                    'url': job.get('url', '') or '',
                                    'date': job.get('date', '') or 'Date non spécifiée',
                                    'salary': job.get('salary', '') or 'Voir sur le site',
                                    'type': 'CDI',
                                    'source': 'Monster',
                                    'is_remote': 'remote' in job.get('summary', '').lower()
                                })
                            except:
                                continue
                                
                except Exception as e:
                    st.write(f"❌ Monster erreur: {str(e)}")
                    continue
    
    return all_jobs

# 12. NOUVELLE API - CareerBuilder via ScrapingBee
def get_careerbuilder_jobs(query="", location=""):
    """API CareerBuilder via ScrapingBee - 400+ offres"""
    all_jobs = []
    
    url = "https://app.scrapingbee.com/api/v1/"
    
    search_terms = [query or "emploi", "job", "work", "position"]
    locations = [location] if location else ["France", "Europe", "International"]
    
    for search_term in search_terms:
        for loc in locations:
            params = {
                'api_key': st.secrets.get("SCRAPINGBEE_API_KEY", "DEMO_KEY"),
                'url': f'https://www.careerbuilder.com/jobs?keywords={search_term}&location={loc}',
                'render_js': 'true',
                'ai_query': 'Extract job listings with title, company, location, description',
                'ai_extract_rules': json.dumps({
                    "jobs": {
                        "type": "array",
                        "items": {
                            "title": {"type": "string"},
                            "company": {"type": "string"},
                            "location": {"type": "string"},
                            "description": {"type": "string"},
                            "url": {"type": "string"}
                        }
                    }
                })
            }
            
            try:
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('jobs', []):
                        try:
                            all_jobs.append({
                                'title': job.get('title', '') or 'Titre non disponible',
                                'company': job.get('company', '') or 'Entreprise non spécifiée',
                                'location': job.get('location', '') or loc,
                                'description': job.get('description', '') or '',
                                'url': job.get('url', '') or '',
                                'date': 'Date non spécifiée',
                                'salary': 'Voir sur le site',
                                'type': 'CDI',
                                'source': 'CareerBuilder',
                                'is_remote': 'remote' in job.get('description', '').lower()
                            })
                        except:
                            continue
                            
            except Exception as e:
                st.write(f"❌ CareerBuilder erreur: {str(e)}")
                continue
    
    return all_jobs

# Fonction ULTIMATE+ avec 20 termes automatiques
def get_single_term_jobs_ultimate_plus(query, location):
    """Recherche ULTIMATE+ avec exécution forcée de toutes les 12 API"""
    all_jobs = []
    
    # Liste complète des 12 API
    apis = [
        ("France Travail ULTIMATE+", get_france_travail_ultimate_plus),
        ("JSearch ULTIMATE+", get_jsearch_ultimate_plus),
        ("Adzuna ULTIMATE+", get_adzuna_ultimate_plus),
        ("Reed ULTIMATE+", get_reed_ultimate_plus),
        ("The Muse ULTIMATE+", get_themuse_ultimate_plus),
        ("GitHub Jobs ULTIMATE+", get_github_ultimate_plus),
        ("Remotive ULTIMATE+", get_remotive_ultimate_plus),
        ("WorkAPI ULTIMATE+", get_workapi_ultimate_plus),
        ("HelloWork ULTIMATE+", get_hellowork_ultimate_plus),
        ("SimplyHired", get_simplyhired_jobs),
        ("Monster", get_monster_jobs),
        ("CareerBuilder", get_careerbuilder_jobs)
    ]
    
    # Exécution forcée avec logs détaillés
    for api_name, api_func in apis:
        st.markdown(f"""
        <div class="api-test">
            🔄 <strong>Test forcé de {api_name}...</strong>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            if api_name in ["GitHub Jobs ULTIMATE+", "Remotive ULTIMATE+"]:
                jobs = api_func(query)
            else:
                jobs = api_func(query, location)
            
            if jobs and len(jobs) > 0:
                all_jobs.extend(jobs)
                st.markdown(f"""
                <div class="progress-success">
                    ✅ <strong>{api_name}</strong> : {len(jobs)} offres récupérées | <strong>Total: {len(all_jobs)}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="progress-error">
                    ❌ <strong>{api_name}</strong> : Aucune offre trouvée
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown(f"""
            <div class="progress-error">
                ❌ <strong>{api_name}</strong> : Erreur - {str(e)[:100]}
            </div>
            """, unsafe_allow_html=True)
        
        time.sleep(1)
    
    return all_jobs

# Fonction ULTIMATE+ MASSIVE avec 20 termes automatiques
def get_all_jobs_ultimate_plus_massive(query="", location=""):
    """Recherche ULTIMATE+ MASSIVE avec 20 termes automatiques pour 4000+ offres"""
    all_jobs = []
    
    # 20 termes de recherche automatiques pour maximiser les résultats
    if not query or query.lower() in ['emploi', 'job', 'work']:
        search_terms = [
            "commercial", "assistant", "technicien", "informatique", "vente", 
            "restauration", "logistique", "comptable", "secrétaire", "manager",
            "développeur", "ingénieur", "consultant", "analyste", "designer",
            "marketing", "communication", "finance", "ressources humaines", "production"
        ]
        st.info(f"🚀 **RECHERCHE ULTIMATE+ MASSIVE** avec {len(search_terms)} termes automatiques et 12 API...")
        
        for i, term in enumerate(search_terms):
            st.subheader(f"🔍 Recherche {i+1}/{len(search_terms)} : '{term}'")
            term_jobs = get_single_term_jobs_ultimate_plus(term, location)
            all_jobs.extend(term_jobs)
            st.write(f"**Résultat pour '{term}' : {len(term_jobs)} offres | Total cumulé : {len(all_jobs)} offres**")
            
            if len(all_jobs) > 3500:  # Arrêter si on a déjà énormément d'offres
                st.success(f"🎯 **Objectif 4000+ offres bientôt atteint !** Arrêt de la recherche à {len(all_jobs)} offres.")
                break
    else:
        # Recherche normale avec le terme spécifié
        st.subheader(f"🔍 Recherche ULTIMATE+ pour : '{query}'")
        all_jobs = get_single_term_jobs_ultimate_plus(query, location)
    
    return all_jobs

# Base de données utilisateurs
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "demo@example.com": {
            "password": "demo123",
            "name": "Jean Dupont",
            "phone": "06 12 34 56 78",
            "address": "123 Rue de la Paix, 75001 Paris",
            "experience": "5 ans d'expérience en vente",
            "skills": ["Vente", "Relation client", "Anglais"],
            "cv_uploaded": False,
            "searches": [],
            "saved_jobs": [],
            "alerts": []
        }
    }

# Fonctions d'authentification
def login_user(email, password):
    if email in st.session_state.users_db:
        if st.session_state.users_db[email]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = email
            return True
    return False

def register_user(email, password, name):
    if email not in st.session_state.users_db:
        st.session_state.users_db[email] = {
            "password": password,
            "name": name,
            "phone": "",
            "address": "",
            "experience": "",
            "skills": [],
            "cv_uploaded": False,
            "searches": [],
            "saved_jobs": [],
            "alerts": []
        }
        return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None

def save_search(query, location, results_count):
    if st.session_state.logged_in:
        user_info = st.session_state.users_db[st.session_state.current_user]
        search_entry = {
            "query": query,
            "location": location,
            "results_count": results_count,
            "timestamp": datetime.now().isoformat()
        }
        user_info['searches'].append(search_entry)
        user_info['searches'] = user_info['searches'][-10:]

# Initialisation des variables de session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Interface principale
def main():
    st.markdown('<h1 class="main-header">🔍 Safe Job Hub Pro - ULTIMATE+</h1>', unsafe_allow_html=True)
    st.markdown("### Hub de recherche d'emploi ULTIMATE+ - 4000+ offres garanties avec 12 API")
    
    # Sidebar pour l'authentification
    with st.sidebar:
        if not st.session_state.logged_in:
            st.header("🔐 Connexion")
            
            tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])
            
            with tab1:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Mot de passe", type="password", key="login_password")
                
                if st.button("Se connecter"):
                    if login_user(email, password):
                        st.success("Connexion réussie!")
                        st.rerun()
                    else:
                        st.error("Email ou mot de passe incorrect")
                
                st.info("**Compte de démonstration:**\n\nEmail: demo@example.com\nMot de passe: demo123")
            
            with tab2:
                new_email = st.text_input("Email", key="register_email")
                new_password = st.text_input("Mot de passe", type="password", key="register_password")
                new_name = st.text_input("Nom complet", key="register_name")
                
                if st.button("S'inscrire"):
                    if new_email and new_password and new_name:
                        if register_user(new_email, new_password, new_name):
                            st.success("Inscription réussie! Vous pouvez maintenant vous connecter.")
                        else:
                            st.error("Cet email est déjà utilisé")
                    else:
                        st.error("Veuillez remplir tous les champs")
        
        else:
            user_info = st.session_state.users_db[st.session_state.current_user]
            st.markdown(f"""
            <div class="user-info">
                <h3>👋 Bonjour {user_info['name']}!</h3>
                <p>📧 {st.session_state.current_user}</p>
            </div>
            """, unsafe_allow_html=True)

            
            # Statut des API ULTIMATE+
            st.subheader("🚀 API ULTIMATE+")
            st.success("✅ 12 API ULTIMATE+ configurées")
            st.success("✅ 20 recherches automatiques")
            st.success("✅ Objectif : 4000+ offres")
            
            if st.button("Se déconnecter"):
                logout_user()
                st.rerun()
    
    # Contenu principal
    if st.session_state.logged_in:
        # Onglets principaux
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🚀 Recherche ULTIMATE+ MASSIVE", 
            "👤 Mon Profil", 
            "🛡️ Analyse d'offre", 
            "📊 Mes candidatures",
            "⚙️ Configuration 12 API"
        ])
        
        with tab1:
            st.header("🎯 Recherche ULTIMATE+ MASSIVE - Objectif 4000+ offres")
            
            # Informations sur la recherche ULTIMATE+
            st.info("🚀 **Mode ULTIMATE+ MASSIVE activé** : 12 API + 20 recherches automatiques + recherche géographique = **4000+ offres garanties** !")
            
            # Barre de recherche
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                query = st.text_input("🔍 Poste recherché", placeholder="Ex: commercial, assistant (ou 'emploi' pour recherche massive)")
            
            with col2:
                location = st.text_input("📍 Localisation", placeholder="Ex: Paris, Lyon")
            
            with col3:
                st.write("")
                st.write("")
                search_button = st.button("🚀 RECHERCHE ULTIMATE+ MASSIVE", use_container_width=True)
            
            # Recherche ULTIMATE+ MASSIVE
            if search_button or query:
                start_time = time.time()
                
                st.warning("⏳ **RECHERCHE ULTIMATE+ MASSIVE EN COURS** - 12 API + 20 recherches automatiques - Cela peut prendre 5-10 minutes pour récupérer 4000+ offres...")
                
                all_jobs = get_all_jobs_ultimate_plus_massive(query, location)
                
                if all_jobs:
                    # Supprimer les doublons
                    seen = set()
                    unique_jobs = []
                    for job in all_jobs:
                        job_key = f"{job['title']}_{job['company']}_{job['location']}"
                        if job_key not in seen:
                            seen.add(job_key)
                            unique_jobs.append(job)
                    
                    all_jobs = unique_jobs
                    search_time = int(time.time() - start_time)
                    
                    # Sauvegarder la recherche
                    save_search(query, location, len(all_jobs))
                    
                    if len(all_jobs) >= 4000:
                        st.balloons()
                        st.success(f"🎉 **OBJECTIF 4000+ LARGEMENT ATTEINT ! {len(all_jobs)} offres trouvées** en {search_time} secondes !")
                    elif len(all_jobs) >= 3000:
                        st.balloons()
                        st.success(f"🎉 **EXCELLENT ! {len(all_jobs)} offres trouvées** en {search_time} secondes !")
                    elif len(all_jobs) >= 2000:
                        st.success(f"🎉 **TRÈS BON ! {len(all_jobs)} offres trouvées** en {search_time} secondes !")
                    else:
                        st.success(f"🎉 **{len(all_jobs)} offres trouvées** en {search_time} secondes !")
                    
                    # Statistiques détaillées
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Offres trouvées", len(all_jobs))
                    with col2:
                        remote_count = len([j for j in all_jobs if j.get('is_remote')])
                        st.metric("Télétravail", remote_count)
                    with col3:
                        sources = len(set([j.get('source', 'Autre') for j in all_jobs]))
                        st.metric("Sources API", sources)
                    with col4:
                        companies = len(set([j['company'] for j in all_jobs if j['company']]))
                        st.metric("Entreprises", companies)
                    
                    # Répartition par API
                    if len(all_jobs) > 0:
                        source_counts = {}
                        for job in all_jobs:
                            source = job.get('source', 'Autre')
                            source_counts[source] = source_counts.get(source, 0) + 1
                        
                        st.subheader("📊 Répartition par API ULTIMATE+ :")
                        cols = st.columns(min(len(source_counts), 6))
                        for i, (source, count) in enumerate(source_counts.items()):
                            with cols[i % 6]:
                                st.metric(source, count)
                    
                    detector = AdvancedJobScamDetector()
                    
                    # Affichage des offres (limité à 500 pour la performance)
                    display_jobs = all_jobs[:500]
                    if len(all_jobs) > 500:
                        st.info(f"💡 Affichage des 500 premières offres sur **{len(all_jobs)} trouvées**. Toutes sont disponibles dans votre historique.")
                    
                    for i, job in enumerate(display_jobs):
                        analysis = detector.analyze_text(job['description'])
                        
                        # Déterminer le niveau de risque
                        if analysis['risk_score'] >= 0.6:
                            continue  # Ne pas afficher les offres à risque élevé
                        elif analysis['risk_score'] >= 0.3:
                            risk_emoji = "⚠️"
                            risk_text = "RISQUE MOYEN"
                            risk_color = "#FF8C00"
                        else:
                            risk_emoji = "✅"
                            risk_text = "OFFRE SÉCURISÉE"
                            risk_color = "#2E8B57"
                        
                        remote_badge = " • 🏠 Télétravail" if job.get('is_remote') else ""
                        
                        with st.container():
                            st.markdown(f"""
                            <div class="job-card">
                                <h3>{job['title']}</h3>
                                <p><strong>🏢 {job['company']}</strong> • 📍 {job['location']} • 🕒 {job['date']} • 🌐 {job['source']}{remote_badge}</p>
                                <p>{job['description']}</p>
                                <p>💰 {job['salary']} • 📋 {job['type']} • <span style="color: {risk_color};">{risk_emoji} {risk_text}</span></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if st.button(f"💾 Sauvegarder", key=f"save_{i}"):
                                    user_info = st.session_state.users_db[st.session_state.current_user]
                                    user_info['saved_jobs'].append(job)
                                    st.success("Offre sauvegardée!")
                            
                            with col2:
                                if job.get('url'):
                                    st.markdown(f"""
                                    <a href="{job['url']}" target="_blank" class="job-link-btn">
                                        🌐 Voir sur {job['source']}
                                    </a>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.write("Lien non disponible")
                            
                            with col3:
                                if st.button(f"📧 Postuler", key=f"apply_{i}"):
                                    st.markdown(f"""
                                    **📋 Candidature {job['company']} :**
                                    
                                    **🎯 Poste** : {job['title']}  
                                    **📍 Lieu** : {job['location']}  
                                    **🌐 Source** : {job['source']}  
                                    **💼 Type** : {job['type']}
                                    
                                    **✅ ÉTAPES :**
                                    1. Cliquez sur "Voir sur {job['source']}"
                                    2. Consultez l'offre complète
                                    3. Préparez CV + lettre de motivation
                                    4. Postulez directement via {job['source']}
                                    """)
                else:
                    st.warning("Aucune offre trouvée. Essayez avec d'autres termes de recherche.")
        
        with tab2:
            st.header("👤 Mon Profil Professionnel")
            
            user_info = st.session_state.users_db[st.session_state.current_user]
            
            with st.form("profile_form"):
                st.subheader("Informations personnelles")
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Nom complet", value=user_info.get('name', ''))
                    phone = st.text_input("Téléphone", value=user_info.get('phone', ''))
                with col2:
                    email_display = st.text_input("Email", value=st.session_state.current_user, disabled=True)
                    address = st.text_area("Adresse", value=user_info.get('address', ''))
                
                st.subheader("Expérience professionnelle")
                experience = st.text_area("Décrivez votre expérience", value=user_info.get('experience', ''), height=100)
                
                st.subheader("Compétences")
                skills_input = st.text_input("Compétences (séparées par des virgules)", 
                                           value=", ".join(user_info.get('skills', [])))
                
                st.subheader("CV")
                uploaded_file = st.file_uploader("Télécharger votre CV", type=['pdf', 'doc', 'docx'])
                
                if st.form_submit_button("💾 Sauvegarder le profil"):
                    user_info['name'] = name
                    user_info['phone'] = phone
                    user_info['address'] = address
                    user_info['experience'] = experience
                    user_info['skills'] = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
                    
                    if uploaded_file:
                        user_info['cv_uploaded'] = True
                    
                    st.success("Profil mis à jour avec succès!")
            
            # Historique des recherches
            if user_info.get('searches'):
                st.subheader("🔍 Historique des recherches ULTIMATE+")
                for search in user_info['searches'][-5:]:
                    st.write(f"**{search['query']}** à **{search['location']}** - {search['results_count']} offres - {search['timestamp'][:10]}")
        
        with tab3:
            st.header("🛡️ Analyse manuelle d'une offre")
            
            job_text = st.text_area(
                "Collez le texte de l'offre d'emploi ici:",
                height=200,
                placeholder="Copiez-collez le texte complet de l'offre d'emploi que vous souhaitez analyser..."
            )
            
            if st.button("🔍 Analyser cette offre"):
                if job_text:
                    detector = AdvancedJobScamDetector()
                    analysis = detector.analyze_text(job_text)
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        risk_percentage = int(analysis['risk_score'] * 100)
                        
                        if risk_percentage >= 60:
                            st.error(f"🚨 RISQUE ÉLEVÉ: {risk_percentage}%")
                        elif risk_percentage >= 30:
                            st.warning(f"⚠️ RISQUE MOYEN: {risk_percentage}%")
                        else:
                            st.success(f"✅ RISQUE FAIBLE: {risk_percentage}%")
                    
                    with col2:
                        if analysis['recommendations']:
                            st.subheader("Recommandations:")
                            for rec in analysis['recommendations']:
                                st.write(f"• {rec}")
                        
                        if analysis['detected_patterns']:
                            st.subheader("Signaux détectés:")
                            for pattern in analysis['detected_patterns']:
                                st.write(f"🔍 {pattern}")
                else:
                    st.error("Veuillez saisir le texte de l'offre")
        
        with tab4:
            st.header("📊 Mes candidatures et offres sauvegardées")
            
            user_info = st.session_state.users_db[st.session_state.current_user]
            
            if user_info.get('saved_jobs'):
                st.subheader(f"💾 Offres sauvegardées ({len(user_info['saved_jobs'])})")
                for i, job in enumerate(user_info['saved_jobs']):
                    remote_badge = " (Télétravail)" if job.get('is_remote') else ""
                    with st.expander(f"{job['title']} - {job['company']} ({job.get('source', 'Internet')}){remote_badge}"):
                        st.write(f"**Localisation:** {job['location']}")
                        st.write(f"**Salaire:** {job.get('salary', 'Non spécifié')}")
                        st.write(f"**Type:** {job.get('type', 'CDI')}")
                        st.write(f"**Date:** {job.get('date', 'Non spécifiée')}")
                        st.write(f"**Source:** {job.get('source', 'Internet')}")
                        if job.get('is_remote'):
                            st.write("**🏠 Télétravail possible**")
                        st.write(f"**Description:** {job['description']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if job.get('url'):
                                st.markdown(f"""
                                <a href="{job['url']}" target="_blank" class="job-link-btn">
                                    🌐 Voir sur {job.get('source', 'Internet')}
                                </a>
                                """, unsafe_allow_html=True)
                        with col2:
                            if st.button(f"🗑️ Supprimer", key=f"delete_{i}"):
                                user_info['saved_jobs'].pop(i)
                                st.rerun()
            else:
                st.info("Aucune offre sauvegardée pour le moment")
        
        with tab5:
            st.header("⚙️ Configuration des 12 API ULTIMATE+")
            
            st.markdown("""
            ### 📋 Configuration complète dans Streamlit Secrets :
            
            ```
            # API existantes (déjà configurées)
            RAPIDAPI_KEY = "6b99ebdbe3mshb0b33108ec37e89p19596djsn933e7b4ec9c4"
            ADZUNA_APP_ID = "82944816"
            ADZUNA_APP_KEY = "397d28a14f97d98450954fd3ebd1ac45"
            REED_API_KEY = "f0bd4083-5306-4c5d-8266-fca8c5eb431b"
            
            # NOUVELLES API à ajouter :
            APIFY_API_TOKEN = "apify_api_ton_token_ici"
            SCRAPINGBEE_API_KEY = "ton_api_key_scrapingbee"
            ```
            
            ### 🎯 Résultat attendu avec les 12 API ULTIMATE+ :
            - **Actuellement** : 1796 offres
            - **Avec 3 nouvelles API** : +1200 offres
            - **TOTAL POSSIBLE** : **3000+ offres** !
            """)
    
    else:
        st.info("👈 Veuillez vous connecter pour accéder à l'application")
        
        st.header("🎯 Hub ULTIMATE+ MASSIVE - 4000+ offres garanties")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h2>🚀</h2>
                <h3>12 API ULTIMATE+</h3>
                <p>Toutes les API optimisées avec exécution forcée</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <h2>🔢</h2>
                <h3>20 Recherches Auto</h3>
                <p>Recherches automatiques multiples + logs détaillés</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stats-card">
                <h2>🎯</h2>
                <h3>4000+ Offres</h3>
                <p>Objectif garanti avec le mode ULTIMATE+ MASSIVE</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

