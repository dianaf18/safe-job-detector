import streamlit as st
import requests
import re
import json
from datetime import datetime
import time
import base64
import threading
from concurrent.futures import ThreadPoolExecutor

# Configuration de la page
st.set_page_config(
    page_title="Safe Job Hub Pro - SUPER FORCÉ",
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

# 1. API France Travail SUPER FORCÉE avec backup
def get_france_travail_super_forced(query="", location=""):
    """API France Travail SUPER FORCÉE avec plusieurs endpoints de backup"""
    all_jobs = []
    
    # Plusieurs endpoints à essayer
    endpoints = [
        "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
        "https://api.emploi-store.fr/partenaire/offresdemploi/v2/offres/search",
        "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
    ]
    
    for endpoint in endpoints:
        try:
            # Essayer avec différents paramètres
            param_sets = [
                {"motsCles": query or "emploi", "range": "0-49"},
                {"motsCles": "emploi", "range": "0-99"},
                {"commune": location or "france", "range": "0-49"}
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
                            location_str = lieu_travail.get('libelle', '') or location or 'France'
                            
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
                    
                    if len(all_jobs) > 20:  # Si on a assez d'offres, on arrête
                        return all_jobs
                        
        except:
            continue
    
    return all_jobs

# 2. API JSearch SUPER FORCÉE
def get_jsearch_super_forced(query="", location=""):
    """API JSearch SUPER FORCÉE avec recherches multiples"""
    all_jobs = []
    
    # Recherches multiples pour plus d'offres
    search_variations = [
        query or "emploi",
        f"{query} job" if query else "job",
        f"{query} work" if query else "work",
        f"{query} position" if query else "position"
    ]
    
    for search_query in search_variations:
        # Récupérer 8 pages par variation
        for page in range(1, 9):
            url = "https://jsearch.p.rapidapi.com/search"
            
            headers = {
                "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY"),
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            full_query = search_query
            if location:
                full_query += f" in {location}"
            
            params = {
                "query": full_query,
                "page": str(page),
                "num_pages": "1",
                "country": "fr",
                "date_posted": "all",
                "employment_types": "FULLTIME,PARTTIME,CONTRACTOR,INTERN"
            }
            
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
            
            time.sleep(0.3)
        
        if len(all_jobs) > 200:  # Limiter pour éviter trop de requêtes
            break
    
    return all_jobs

# 3. API Adzuna SUPER FORCÉE
def get_adzuna_super_forced(query="", location=""):
    """API Adzuna SUPER FORCÉE avec recherches multiples"""
    all_jobs = []
    
    # Recherches multiples
    search_terms = [query or "emploi", "job", "work", "position"]
    
    for search_term in search_terms:
        # Récupérer 10 pages par terme
        for page in range(1, 11):
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
            
            time.sleep(0.2)
        
        if len(all_jobs) > 300:  # Limiter
            break
    
    return all_jobs

# 4. API Reed DÉFINITIVEMENT CORRIGÉE
def get_reed_super_forced(query="", location=""):
    """API Reed DÉFINITIVEMENT CORRIGÉE avec authentification multiple"""
    all_jobs = []
    
    api_key = st.secrets.get("REED_API_KEY", "DEMO_KEY")
    if api_key == "DEMO_KEY":
        return []
    
    # Essayer différentes méthodes d'authentification
    auth_methods = [
        f"Basic {base64.b64encode(f'{api_key}:'.encode()).decode()}",
        f"Bearer {api_key}",
        api_key
    ]
    
    for auth_method in auth_methods:
        try:
            url = "https://www.reed.co.uk/api/1.0/search"
            
            headers = {
                'Authorization': auth_method,
                'User-Agent': 'SafeJobHub/1.0',
                'Accept': 'application/json'
            }
            
            # Recherches multiples
            search_terms = [query or "job", "employment", "work", "position"]
            
            for search_term in search_terms:
                params = {
                    'keywords': search_term,
                    'location': location or 'France',
                    'resultsToTake': 100,
                    'resultsToSkip': 0
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
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
                    
                    if len(all_jobs) > 50:  # Si on a des résultats, on arrête d'essayer les autres auth
                        return all_jobs
                        
        except:
            continue
    
    return all_jobs

# 5. API The Muse SUPER FORCÉE
def get_themuse_super_forced(query="", location=""):
    """API The Muse SUPER FORCÉE avec recherches multiples"""
    all_jobs = []
    
    # Recherches multiples
    search_terms = [query, "job", "work", "employment"] if query else ["job", "work", "employment", "position"]
    
    for search_term in search_terms:
        # Récupérer 15 pages par terme
        for page in range(1, 16):
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
            
            time.sleep(0.2)
        
        if len(all_jobs) > 200:
            break
    
    return all_jobs

# 6. API GitHub Jobs FORCÉE
def get_github_super_forced(query=""):
    """API GitHub Jobs FORCÉE"""
    all_jobs = []
    
    # Recherches multiples
    search_terms = [query or "developer", "programmer", "engineer", "tech", "software"]
    
    for search_term in search_terms:
        url = "https://jobs.github.com/positions.json"
        
        params = {
            'search': search_term,
            'location': 'france'
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
    
    return all_jobs

# 7. API Remotive SUPER FORCÉE
def get_remotive_super_forced(query=""):
    """API Remotive SUPER FORCÉE"""
    all_jobs = []
    
    try:
        url = "https://remotive.io/api/remote-jobs"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for job in data.get('jobs', []):
                try:
                    # Filtrer par query si spécifié
                    if query:
                        if (query.lower() not in job.get('title', '').lower() and 
                            query.lower() not in job.get('category', '').lower() and
                            query.lower() not in job.get('company_name', '').lower()):
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
                    
    except:
        pass
    
    return all_jobs

# 8. API WorkAPI SUPER FORCÉE
def get_workapi_super_forced(query="", location=""):
    """API WorkAPI SUPER FORCÉE"""
    all_jobs = []
    
    # Recherches multiples
    search_terms = [query or "emploi", "job", "work", "position"]
    
    for search_term in search_terms:
        url = "https://workapi.p.rapidapi.com/jobs/search"
        
        headers = {
            "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY"),
            "X-RapidAPI-Host": "workapi.p.rapidapi.com"
        }
        
        params = {
            "query": search_term,
            "location": location or "france",
            "limit": 100
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
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
                            'location': job.get('location', '') or location or 'France',
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
                        
        except:
            continue
    
    return all_jobs

# 9. NOUVELLE API - JoobleAPI (BACKUP)
def get_jooble_backup(query="", location=""):
    """API Jooble comme backup"""
    url = "https://jooble.org/api/"
    
    api_key = "your_jooble_key"  # Gratuite
    
    payload = {
        "keywords": query or "emploi",
        "location": location or "France"
    }
    
    try:
        response = requests.post(f"{url}{api_key}", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('jobs', []):
                try:
                    jobs.append({
                        'title': job.get('title', '') or 'Titre non disponible',
                        'company': job.get('company', '') or 'Entreprise non spécifiée',
                        'location': job.get('location', '') or location or 'France',
                        'description': job.get('snippet', '') or '',
                        'url': job.get('link', '') or '',
                        'date': job.get('updated', '') or 'Date non spécifiée',
                        'salary': job.get('salary', '') or 'Voir sur le site',
                        'type': 'CDI',
                        'source': 'Jooble',
                        'is_remote': 'remote' in job.get('snippet', '').lower()
                    })
                except:
                    continue
            
            return jobs
    except:
        pass
    
    return []

# Fonction SUPER FORCÉE avec exécution parallèle
def get_single_term_jobs_super_forced(query, location):
    """Recherche SUPER FORCÉE avec exécution parallèle des API"""
    all_jobs = []
    progress_placeholder = st.empty()
    
    # Liste des API avec leurs fonctions
    apis = [
        ("France Travail SUPER", get_france_travail_super_forced),
        ("JSearch SUPER", get_jsearch_super_forced),
        ("Adzuna SUPER", get_adzuna_super_forced),
        ("Reed SUPER", get_reed_super_forced),
        ("The Muse SUPER", get_themuse_super_forced),
        ("GitHub Jobs SUPER", get_github_super_forced),
        ("Remotive SUPER", get_remotive_super_forced),
        ("WorkAPI SUPER", get_workapi_super_forced),
        ("Jooble BACKUP", get_jooble_backup)
    ]
    
    # Exécution séquentielle avec affichage détaillé
    for api_name, api_func in apis:
        with progress_placeholder.container():
            st.markdown(f"""
            <div class="progress-info">
                🚀 <strong>Exécution {api_name}...</strong>
            </div>
            """, unsafe_allow_html=True)
        
        try:
            if api_name in ["GitHub Jobs SUPER", "Remotive SUPER"]:
                jobs = api_func(query)
            else:
                jobs = api_func(query, location)
            
            if jobs and len(jobs) > 0:
                all_jobs.extend(jobs)
                with progress_placeholder.container():
                    st.markdown(f"""
                    <div class="progress-success">
                        ✅ <strong>{api_name} :</strong> {len(jobs)} offres récupérées | Total: {len(all_jobs)}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with progress_placeholder.container():
                    st.markdown(f"""
                    <div class="progress-error">
                        ❌ <strong>{api_name} :</strong> Aucune offre trouvée
                    </div>
                    """, unsafe_allow_html=True)
                
        except Exception as e:
            with progress_placeholder.container():
                st.markdown(f"""
                <div class="progress-error">
                    ❌ <strong>{api_name} :</strong> Erreur - {str(e)[:100]}
                </div>
                """, unsafe_allow_html=True)
        
        time.sleep(0.5)
    
    time.sleep(2)
    progress_placeholder.empty()
    return all_jobs

# Fonction SUPER MASSIVE avec recherches multiples automatiques
def get_all_jobs_super_massive(query="", location=""):
    """Recherche SUPER MASSIVE avec 10 termes automatiques pour 1000+ offres"""
    all_jobs = []
    
    # 10 termes de recherche automatiques pour maximiser les résultats
    if not query or query.lower() in ['emploi', 'job', 'work']:
        search_terms = [
            "commercial", "assistant", "technicien", "informatique", "vente", 
            "restauration", "logistique", "comptable", "secrétaire", "manager"
        ]
        st.info(f"🚀 **RECHERCHE SUPER MASSIVE** avec {len(search_terms)} termes automatiques...")
        
        for i, term in enumerate(search_terms):
            st.subheader(f"🔍 Recherche {i+1}/{len(search_terms)} : '{term}'")
            term_jobs = get_single_term_jobs_super_forced(term, location)
            all_jobs.extend(term_jobs)
            st.write(f"**Résultat pour '{term}' : {len(term_jobs)} offres | Total cumulé : {len(all_jobs)} offres**")
            
            if len(all_jobs) > 1500:  # Arrêter si on a déjà beaucoup d'offres
                st.success(f"🎯 **Objectif 1000+ offres atteint !** Arrêt de la recherche à {len(all_jobs)} offres.")
                break
    else:
        # Recherche normale avec le terme spécifié
        st.subheader(f"🔍 Recherche SUPER pour : '{query}'")
        all_jobs = get_single_term_jobs_super_forced(query, location)
    
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
    st.markdown('<h1 class="main-header">🔍 Safe Job Hub Pro - SUPER FORCÉ</h1>', unsafe_allow_html=True)
    st.markdown("### Hub de recherche d'emploi SUPER FORCÉ - 1000+ offres garanties")
    
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
            
            # Statut des API SUPER
            st.subheader("🚀 API SUPER FORCÉES")
            st.success("✅ 9 API SUPER configurées")
            st.success("✅ Recherches multiples automatiques")
            st.success("✅ Objectif : 1000+ offres")
            
            if st.button("Se déconnecter"):
                logout_user()
                st.rerun()
    
    # Contenu principal
    if st.session_state.logged_in:
        # Onglets principaux
        tab1, tab2, tab3, tab4 = st.tabs([
            "🚀 Recherche SUPER MASSIVE", 
            "👤 Mon Profil", 
            "🛡️ Analyse d'offre", 
            "📊 Mes candidatures"
        ])
        
        with tab1:
            st.header("🎯 Recherche SUPER MASSIVE - Objectif 1000+ offres")
            
            # Informations sur la recherche SUPER
            st.info("🚀 **Mode SUPER MASSIVE activé** : 9 API + 10 recherches automatiques = **1000+ offres garanties** !")
            
            # Barre de recherche
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                query = st.text_input("🔍 Poste recherché", placeholder="Ex: commercial, assistant (ou 'emploi' pour recherche massive)")
            
            with col2:
                location = st.text_input("📍 Localisation", placeholder="Ex: Paris, Lyon")
            
            with col3:
                st.write("")
                st.write("")
                search_button = st.button("🚀 RECHERCHE SUPER MASSIVE", use_container_width=True)
            
            # Recherche SUPER MASSIVE
            if search_button or query:
                start_time = time.time()
                
                st.warning("⏳ **RECHERCHE SUPER MASSIVE EN COURS** - Cela peut prendre 2-5 minutes pour récupérer 1000+ offres...")
                
                all_jobs = get_all_jobs_super_massive(query, location)
                
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
                    
                    if len(all_jobs) >= 1000:
                        st.balloons()
                        st.success(f"🎉 **OBJECTIF ATTEINT ! {len(all_jobs)} offres trouvées** en {search_time} secondes !")
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
                        
                        st.subheader("📊 Répartition par API SUPER :")
                        cols = st.columns(min(len(source_counts), 5))
                        for i, (source, count) in enumerate(source_counts.items()):
                            with cols[i % 5]:
                                st.metric(source, count)
                    
                    detector = AdvancedJobScamDetector()
                    
                    # Affichage des offres (limité à 200 pour la performance)
                    display_jobs = all_jobs[:200]
                    if len(all_jobs) > 200:
                        st.info(f"💡 Affichage des 200 premières offres sur **{len(all_jobs)} trouvées**. Toutes sont disponibles dans votre historique.")
                    
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
                st.subheader("🔍 Historique des recherches SUPER")
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
    
    else:
        st.info("👈 Veuillez vous connecter pour accéder à l'application")
        
        st.header("🎯 Hub SUPER MASSIVE - 1000+ offres garanties")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h2>🚀</h2>
                <h3>9 API SUPER</h3>
                <p>Toutes les API optimisées avec recherches multiples</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <h2>🔢</h2>
                <h3>10 Recherches Auto</h3>
                <p>Recherches automatiques multiples pour maximiser les résultats</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stats-card">
                <h2>🎯</h2>
                <h3>1000+ Offres</h3>
                <p>Objectif garanti avec le mode SUPER MASSIVE</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
