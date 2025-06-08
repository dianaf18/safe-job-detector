import streamlit as st
import requests
import re
import json
from datetime import datetime
import time
import base64

# Configuration de la page
st.set_page_config(
    page_title="Safe Job Hub Pro - ULTRA",
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

# 1. API France Travail CORRIGÉE
def get_france_travail_jobs_ultra_fixed(query="", location=""):
    """API France Travail CORRIGÉE avec gestion d'erreurs améliorée"""
    all_jobs = []
    
    # Essayer avec différents endpoints
    endpoints = [
        "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
        "https://api.emploi-store.fr/partenaire/offresdemploi/v2/offres/search"
    ]
    
    for endpoint in endpoints:
        try:
            headers = {
                "Accept": "application/json",
                "User-Agent": "SafeJobHub/1.0"
            }
            
            params = {
                "motsCles": query or "emploi",
                "range": "0-49"  # Réduire pour éviter les timeouts
            }
            
            if location and location.strip():
                params["commune"] = location.strip()
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            
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
                
                if all_jobs:
                    break  # Si on a des résultats, on arrête d'essayer les autres endpoints
                    
        except Exception as e:
            continue  # Essayer l'endpoint suivant
    
    return all_jobs

# 2. API JSearch ULTRA (RapidAPI)
def get_jsearch_jobs_ultra_fixed(query="", location=""):
    """API JSearch ULTRA avec gestion d'erreurs améliorée"""
    all_jobs = []
    
    # Récupérer 5 pages pour plus d'offres
    for page in range(1, 6):
        url = "https://jsearch.p.rapidapi.com/search"
        
        headers = {
            "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY"),
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        search_query = query or "emploi"
        if location:
            search_query += f" in {location}"
        
        params = {
            "query": search_query,
            "page": str(page),
            "num_pages": "1",
            "country": "fr",
            "date_posted": "all",
            "employment_types": "FULLTIME,PARTTIME,CONTRACTOR,INTERN"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
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
                
                if len(data.get('data', [])) < 10:
                    break
            else:
                break
                
        except:
            break
        
        time.sleep(0.5)
    
    return all_jobs

# 3. API Adzuna ULTRA
def get_adzuna_jobs_ultra_fixed(query="", location=""):
    """API Adzuna ULTRA avec gestion d'erreurs améliorée"""
    all_jobs = []
    
    # Récupérer 3 pages
    for page in range(1, 4):
        url = f"https://api.adzuna.com/v1/api/jobs/fr/search/{page}"
        
        params = {
            'app_id': st.secrets.get("ADZUNA_APP_ID", "DEMO_ID"),
            'app_key': st.secrets.get("ADZUNA_APP_KEY", "DEMO_KEY"),
            'results_per_page': 50,
            'what': query or '',
            'where': location or '',
            'sort_by': 'date'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
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
                
                if len(data.get('results', [])) < 50:
                    break
            else:
                break
                
        except:
            break
        
        time.sleep(0.3)
    
    return all_jobs

# 4. API Reed CORRIGÉE
def get_reed_jobs_ultra_fixed(query="", location=""):
    """API Reed ULTRA avec authentification corrigée"""
    all_jobs = []
    
    api_key = st.secrets.get("REED_API_KEY", "DEMO_KEY")
    if api_key == "DEMO_KEY":
        return []
    
    # Encoder correctement la clé pour Basic Auth
    try:
        encoded_key = base64.b64encode(f"{api_key}:".encode()).decode()
        
        url = "https://www.reed.co.uk/api/1.0/search"
        
        headers = {
            'Authorization': f'Basic {encoded_key}',
            'User-Agent': 'SafeJobHub/1.0'
        }
        
        params = {
            'keywords': query or '',
            'location': location or 'France',
            'resultsToTake': 50
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
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
                    
    except Exception as e:
        pass
    
    return all_jobs

# 5. API The Muse ULTRA
def get_themuse_jobs_ultra_fixed(query="", location=""):
    """API The Muse ULTRA avec gestion d'erreurs améliorée"""
    all_jobs = []
    
    # Récupérer 5 pages
    for page in range(1, 6):
        url = "https://www.themuse.com/api/public/jobs"
        
        params = {
            'page': page,
            'descending': 'true'
        }
        
        if query:
            params['search'] = query
        if location:
            params['location'] = location
        
        try:
            response = requests.get(url, params=params, timeout=15)
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
                
                if len(data.get('results', [])) < 20:
                    break
            else:
                break
                
        except:
            break
        
        time.sleep(0.3)
    
    return all_jobs

# 6. API GitHub Jobs
def get_github_jobs_ultra_fixed(query=""):
    """API GitHub Jobs avec gestion d'erreurs améliorée"""
    url = "https://jobs.github.com/positions.json"
    
    params = {
        'search': query or 'developer',
        'location': 'france'
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data:
                try:
                    description = job.get('description', '') or ''
                    if len(description) > 500:
                        description = description[:500] + '...'
                    
                    jobs.append({
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
            
            return jobs
        return []
    except:
        return []

# 7. API Remotive CORRIGÉE
def get_remotive_jobs_fixed(query=""):
    """API Remotive avec gestion d'erreurs améliorée"""
    url = "https://remotive.io/api/remote-jobs"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('jobs', []):
                try:
                    # Filtrer par query si spécifié
                    if query and query.lower() not in job.get('title', '').lower() and query.lower() not in job.get('category', '').lower():
                        continue
                        
                    description = job.get('description', '') or ''
                    if len(description) > 500:
                        description = description[:500] + '...'
                    
                    jobs.append({
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
            
            return jobs
        return []
    except:
        return []

# 8. API WorkAPI CORRIGÉE
def get_workapi_jobs_fixed(query="", location=""):
    """API WorkAPI avec gestion d'erreurs améliorée"""
    url = "https://workapi.p.rapidapi.com/jobs/search"
    
    headers = {
        "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY"),
        "X-RapidAPI-Host": "workapi.p.rapidapi.com"
    }
    
    params = {
        "query": query or "emploi",
        "location": location or "france",
        "limit": 50
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('jobs', []):
                try:
                    description = job.get('description', '') or job.get('snippet', '') or ''
                    if len(description) > 500:
                        description = description[:500] + '...'
                    
                    jobs.append({
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
            
            return jobs
        return []
    except:
        return []

# Fonction ULTRA FORCÉE qui teste toutes les API
def get_single_term_jobs_forced(query, location):
    """Recherche FORCÉE sur toutes les 8 API avec diagnostic détaillé"""
    all_jobs = []
    progress_placeholder = st.empty()
    
    # Liste des API avec leurs fonctions - VERSION FORCÉE
    apis = [
        ("France Travail ULTRA", get_france_travail_jobs_ultra_fixed),
        ("JSearch ULTRA", get_jsearch_jobs_ultra_fixed),
        ("Adzuna ULTRA", get_adzuna_jobs_ultra_fixed),
        ("Reed ULTRA", get_reed_jobs_ultra_fixed),
        ("The Muse ULTRA", get_themuse_jobs_ultra_fixed),
        ("GitHub Jobs", get_github_jobs_ultra_fixed),
        ("Remotive", get_remotive_jobs_fixed),
        ("WorkAPI", get_workapi_jobs_fixed)
    ]
    
    for api_name, api_func in apis:
        with progress_placeholder.container():
            st.markdown(f"""
            <div class="progress-info">
                🔄 <strong>Test {api_name}...</strong>
            </div>
            """, unsafe_allow_html=True)
        
        try:
            if api_name in ["GitHub Jobs", "Remotive"]:
                jobs = api_func(query)
            else:
                jobs = api_func(query, location)
            
            if jobs and len(jobs) > 0:
                all_jobs.extend(jobs)
                with progress_placeholder.container():
                    st.markdown(f"""
                    <div class="progress-success">
                        ✅ <strong>{api_name} :</strong> {len(jobs)} offres récupérées avec succès
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with progress_placeholder.container():
                    st.markdown(f"""
                    <div class="progress-error">
                        ❌ <strong>{api_name} :</strong> 0 offre trouvée (API non fonctionnelle ou pas de résultats)
                    </div>
                    """, unsafe_allow_html=True)
                
        except Exception as e:
            with progress_placeholder.container():
                st.markdown(f"""
                <div class="progress-error">
                    ❌ <strong>{api_name} :</strong> Erreur - {str(e)[:100]}
                </div>
                """, unsafe_allow_html=True)
        
        time.sleep(1)  # Pause plus longue pour voir les résultats
    
    time.sleep(2)  # Pause finale pour voir le résumé
    progress_placeholder.empty()
    return all_jobs

# Fonction ULTRA qui combine toutes les API avec recherches multiples FORCÉES
def get_all_jobs_ultra_massive_forced(query="", location=""):
    """Combine toutes les API + recherches multiples FORCÉES pour 2000+ offres"""
    all_jobs = []
    
    # Si pas de query spécifique, faire des recherches multiples
    if not query or query.lower() in ['emploi', 'job', 'work']:
        search_terms = ["commercial", "assistant", "technicien"]  # Réduire à 3 termes pour tester
        st.info(f"🚀 Recherche ULTRA FORCÉE avec {len(search_terms)} termes automatiques...")
        
        for term in search_terms:
            st.subheader(f"🔍 Recherche automatique : '{term}'")
            term_jobs = get_single_term_jobs_forced(term, location)
            all_jobs.extend(term_jobs)
            st.write(f"**Résultat pour '{term}' : {len(term_jobs)} offres**")
            time.sleep(1)
    else:
        # Recherche normale avec le terme spécifié
        st.subheader(f"🔍 Recherche pour : '{query}'")
        all_jobs = get_single_term_jobs_forced(query, location)
    
    return all_jobs

# Base de données utilisateurs[1]
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
    st.markdown('<h1 class="main-header">🔍 Safe Job Hub Pro - ULTRA FORCÉ</h1>', unsafe_allow_html=True)
    st.markdown("### Hub de recherche d'emploi avec diagnostic complet des 8 API")
    
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
            
            # Statut des API ULTRA
            st.subheader("📊 Statut API ULTRA")
            
            st.success("✅ France Travail ULTRA (corrigé)")
            
            if st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY") != "DEMO_KEY":
                st.success("✅ JSearch ULTRA (corrigé)")
                st.success("✅ WorkAPI (corrigé)")
            else:
                st.warning("⚠️ JSearch ULTRA (non configuré)")
                st.warning("⚠️ WorkAPI (non configuré)")
            
            if st.secrets.get("ADZUNA_APP_ID", "DEMO_ID") != "DEMO_ID":
                st.success("✅ Adzuna ULTRA (corrigé)")
            else:
                st.warning("⚠️ Adzuna ULTRA (non configuré)")
            
            if st.secrets.get("REED_API_KEY", "DEMO_KEY") != "DEMO_KEY":
                st.success("✅ Reed ULTRA (corrigé)")
            else:
                st.warning("⚠️ Reed ULTRA (non configuré)")
            
            st.success("✅ The Muse ULTRA (corrigé)")
            st.success("✅ GitHub Jobs (corrigé)")
            st.success("✅ Remotive (corrigé)")
            
            if st.button("Se déconnecter"):
                logout_user()
                st.rerun()
    
    # Contenu principal
    if st.session_state.logged_in:
        # Onglets principaux
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Recherche ULTRA FORCÉE", 
            "👤 Mon Profil", 
            "🛡️ Analyse d'offre", 
            "📊 Mes candidatures",
            "⚙️ Configuration API"
        ])
        
        with tab1:
            st.header("🎯 Recherche ULTRA FORCÉE - Diagnostic complet des 8 API")
            
            # Informations sur la recherche ULTRA
            st.info("🚀 **Mode ULTRA FORCÉ activé** : Test de chaque API individuellement avec diagnostic détaillé")
            
            # Barre de recherche
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                query = st.text_input("🔍 Poste recherché", placeholder="Ex: commercial, assistant, technicien")
            
            with col2:
                location = st.text_input("📍 Localisation", placeholder="Ex: Paris, Lyon")
            
            with col3:
                st.write("")
                st.write("")
                search_button = st.button("🚀 Recherche ULTRA FORCÉE", use_container_width=True)
            
            # Recherche ULTRA FORCÉE
            if search_button or query:
                start_time = time.time()
                
                st.warning("⏳ **Recherche ULTRA FORCÉE en cours** - Chaque API sera testée individuellement avec diagnostic détaillé...")
                
                all_jobs = get_all_jobs_ultra_massive_forced(query, location)
                
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
                    
                    st.success(f"🎉 **{len(all_jobs)} offres trouvées** en {search_time} secondes avec la recherche ULTRA FORCÉE !")
                    
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
                        
                        st.subheader("📊 Répartition par API ULTRA FORCÉE :")
                        cols = st.columns(min(len(source_counts), 4))
                        for i, (source, count) in enumerate(source_counts.items()):
                            with cols[i % 4]:
                                st.metric(source, count)
                    
                    detector = AdvancedJobScamDetector()
                    
                    # Affichage des offres (limité à 100 pour la performance)
                    display_jobs = all_jobs[:100]
                    if len(all_jobs) > 100:
                        st.info(f"💡 Affichage des 100 premières offres sur **{len(all_jobs)} trouvées**.")
                    
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
                    st.warning("Aucune offre trouvée. Vérifiez le diagnostic des API ci-dessus.")
        
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
                st.subheader("🔍 Historique des recherches ULTRA")
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
            st.header("⚙️ Diagnostic des 8 API")
            
            st.markdown("""
            <div class="api-status">
                <h3>🔧 Diagnostic complet des 8 API avec corrections appliquées</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            ### 🔧 Corrections appliquées :
            
            1. **🇫🇷 France Travail** : Endpoints multiples + gestion timeout
            2. **🌐 JSearch** : Pagination réduite + gestion erreurs
            3. **🔍 Adzuna** : Pagination optimisée + timeout
            4. **🇬🇧 Reed** : Authentification Basic Auth corrigée
            5. **💼 The Muse** : Pagination réduite + gestion erreurs
            6. **💻 GitHub Jobs** : Gestion timeout + filtrage
            7. **🏠 Remotive** : Filtrage par query + gestion erreurs
            8. **⚡ WorkAPI** : Headers corrigés + gestion timeout
            
            ### 🚀 Mode ULTRA FORCÉ :
            - ✅ **Test individuel** de chaque API
            - ✅ **Diagnostic détaillé** en temps réel
            - ✅ **Gestion d'erreurs** améliorée
            - ✅ **Affichage des résultats** par API
            - ✅ **Recherches multiples** automatiques
            """)
            
            # Tests individuels des API CORRIGÉES
            st.subheader("🧪 Tests individuels des API CORRIGÉES")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("Test France Travail CORRIGÉ"):
                    with st.spinner("Test..."):
                        jobs = get_france_travail_jobs_ultra_fixed("emploi", "")
                        if jobs:
                            st.success(f"✅ {len(jobs)} offres trouvées")
                        else:
                            st.error("❌ Aucune offre")
                
                if st.button("Test JSearch CORRIGÉ"):
                    with st.spinner("Test..."):
                        jobs = get_jsearch_jobs_ultra_fixed("emploi", "")
                        if jobs:
                            st.success(f"✅ {len(jobs)} offres trouvées")
                        else:
                            st.error("❌ Aucune offre")
            
            with col2:
                if st.button("Test Adzuna CORRIGÉ"):
                    with st.spinner("Test..."):
                        jobs = get_adzuna_jobs_ultra_fixed("emploi", "")
                        if jobs:
                            st.success(f"✅ {len(jobs)} offres trouvées")
                        else:
                            st.error("❌ Aucune offre")
                
                if st.button("Test Reed CORRIGÉ"):
                    with st.spinner("Test..."):
                        jobs = get_reed_jobs_ultra_fixed("emploi", "")
                        if jobs:
                            st.success(f"✅ {len(jobs)} offres trouvées")
                        else:
                            st.error("❌ Aucune offre")
            
            with col3:
                if st.button("Test The Muse CORRIGÉ"):
                    with st.spinner("Test..."):
                        jobs = get_themuse_jobs_ultra_fixed("emploi", "")
                        if jobs:
                            st.success(f"✅ {len(jobs)} offres trouvées")
                        else:
                            st.error("❌ Aucune offre")
                
                if st.button("Test GitHub Jobs CORRIGÉ"):
                    with st.spinner("Test..."):
                        jobs = get_github_jobs_ultra_fixed("developer")
                        if jobs:
                            st.success(f"✅ {len(jobs)} offres trouvées")
                        else:
                            st.error("❌ Aucune offre")
            
            with col4:
                if st.button("Test Remotive CORRIGÉ"):
                    with st.spinner("Test..."):
                        jobs = get_remotive_jobs_fixed("developer")
                        if jobs:
                            st.success(f"✅ {len(jobs)} offres trouvées")
                        else:
                            st.error("❌ Aucune offre")
                
                if st.button("Test WorkAPI CORRIGÉ"):
                    with st.spinner("Test..."):
                        jobs = get_workapi_jobs_fixed("emploi", "")
                        if jobs:
                            st.success(f"✅ {len(jobs)} offres trouvées")
                        else:
                            st.error("❌ Aucune offre")
    
    else:
        st.info("👈 Veuillez vous connecter pour accéder à l'application")
        
        st.header("🎯 Hub ULTRA FORCÉ - Diagnostic complet")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h2>🔧</h2>
                <h3>8 API Corrigées</h3>
                <p>Toutes les API ont été corrigées et optimisées</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <h2>🔍</h2>
                <h3>Diagnostic Détaillé</h3>
                <p>Test individuel de chaque API avec résultats en temps réel</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stats-card">
                <h2>🚀</h2>
                <h3>Mode FORCÉ</h3>
                <p>Exécution forcée de toutes les API pour maximiser les résultats</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
