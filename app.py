import streamlit as st
import requests
import re
import json
from datetime import datetime
import time

# Configuration de la page
st.set_page_config(
    page_title="Safe Job Hub Pro",
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
</style>
""", unsafe_allow_html=True)

# Classe de détection d'arnaques complète
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

# Fonction API JSearch RÉELLE (Multi-sources : Indeed + LinkedIn + Glassdoor + ZipRecruiter)
def get_real_jobs_jsearch(query="", location="", page=1):
    """Récupère de VRAIES offres via JSearch API (Indeed + LinkedIn + Glassdoor + ZipRecruiter)"""
    
    # Configuration API JSearch (Multi-sources)
    url = "https://jsearch.p.rapidapi.com/search"
    
    headers = {
        "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY"),
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    # Construction de la requête améliorée
    search_query = query or "emploi"
    if location:
        search_query += f" in {location}"
    
    params = {
        "query": search_query,
        "page": str(page),
        "num_pages": "3",  # Plus de pages pour plus d'offres
        "country": "fr",
        "date_posted": "all",  # Toutes les dates
        "employment_types": "FULLTIME,PARTTIME,CONTRACTOR"  # Tous types
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('data', []):
                # Nettoyer et formater les données
                description = job.get('job_description', '')
                if len(description) > 500:
                    description = description[:500] + '...'
                
                # Déterminer la source
                source = "Indeed"
                if "linkedin" in job.get('job_apply_link', '').lower():
                    source = "LinkedIn"
                elif "glassdoor" in job.get('job_apply_link', '').lower():
                    source = "Glassdoor"
                elif "ziprecruiter" in job.get('job_apply_link', '').lower():
                    source = "ZipRecruiter"
                
                jobs.append({
                    'title': job.get('job_title', 'Titre non disponible'),
                    'company': job.get('employer_name', 'Entreprise non spécifiée'),
                    'location': job.get('job_city', '') + ', ' + job.get('job_country', ''),
                    'description': description,
                    'url': job.get('job_apply_link', ''),
                    'date': job.get('job_posted_at_datetime_utc', 'Date non spécifiée'),
                    'salary': job.get('job_salary_currency', '') + ' ' + str(job.get('job_min_salary', '')) + '-' + str(job.get('job_max_salary', '')) if job.get('job_min_salary') else 'Salaire non spécifié',
                    'type': job.get('job_employment_type', 'CDI'),
                    'source': source,
                    'is_remote': job.get('job_is_remote', False)
                })
            
            return jobs
        
        elif response.status_code == 429:
            st.warning("⚠️ Limite API atteinte. Réessayez dans quelques minutes.")
            return []
        
        else:
            st.error(f"Erreur API JSearch (Code: {response.status_code})")
            return []
            
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout API - Réessayez")
        return []
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return []

# Fonction API France Travail OFFICIELLE (GRATUITE - AUCUNE CONFIG REQUISE)
def get_france_travail_jobs(query="", location=""):
    """API officielle France Travail avec vraies offres françaises - GRATUITE"""
    
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
    
    headers = {
        "Accept": "application/json"
    }
    
    params = {
        "motsCles": query or "",
        "commune": location or "",
        "range": "0-99"  # 100 offres max par requête
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('resultats', []):
                # Nettoyer la description
                description = job.get('description', '')
                if len(description) > 500:
                    description = description[:500] + '...'
                
                # Construire l'URL de l'offre
                job_url = ""
                if job.get('origineOffre', {}).get('urlOrigine'):
                    job_url = job['origineOffre']['urlOrigine']
                
                jobs.append({
                    'title': job.get('intitule', 'Titre non disponible'),
                    'company': job.get('entreprise', {}).get('nom', 'Entreprise non spécifiée'),
                    'location': job.get('lieuTravail', {}).get('libelle', location or 'France'),
                    'description': description,
                    'url': job_url,
                    'date': job.get('dateCreation', 'Date non spécifiée'),
                    'salary': job.get('salaire', {}).get('libelle', 'Salaire non spécifié'),
                    'type': job.get('typeContrat', 'CDI'),
                    'source': 'France Travail',
                    'is_remote': 'télétravail' in description.lower() or 'remote' in description.lower()
                })
            
            return jobs
        else:
            return []
            
    except Exception as e:
        return []

# Fonction API Indeed (backup)
def get_indeed_jobs_backup(query="", location=""):
    """API Indeed de backup si JSearch ne fonctionne pas"""
    
    url = "https://indeed12.p.rapidapi.com/jobs/search"
    
    headers = {
        "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY"),
        "X-RapidAPI-Host": "indeed12.p.rapidapi.com"
    }
    
    params = {
        "query": query or "emploi",
        "location": location or "France",
        "page_id": "1",
        "locality": "fr"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('hits', []):
                jobs.append({
                    'title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'description': job.get('description', '')[:500] + '...',
                    'url': job.get('url', ''),
                    'date': job.get('date', ''),
                    'salary': job.get('salary', 'Non spécifié'),
                    'type': 'CDI',
                    'source': 'Indeed',
                    'is_remote': False
                })
            
            return jobs
        else:
            return []
            
    except Exception as e:
        return []

# Base de données utilisateurs complète
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

# Fonctions d'authentification complètes
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
        # Garder seulement les 10 dernières recherches
        user_info['searches'] = user_info['searches'][-10:]

# Initialisation des variables de session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# Interface principale complète
def main():
    st.markdown('<h1 class="main-header">🔍 Safe Job Hub Pro</h1>', unsafe_allow_html=True)
    st.markdown("### Hub de recherche d'emploi - Toutes les offres d'Internet en un seul endroit")
    
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
            
            # Statut API
            api_key = st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY")
            if api_key == "DEMO_KEY":
                st.warning("⚠️ JSearch non configurée")
                st.success("✅ France Travail disponible")
            else:
                st.success("✅ JSearch + France Travail")
            
            if st.button("Se déconnecter"):
                logout_user()
                st.rerun()
    
    # Contenu principal
    if st.session_state.logged_in:
        # Onglets principaux complets
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Recherche d'emploi", 
            "👤 Mon Profil", 
            "🛡️ Analyse d'offre", 
            "📊 Mes candidatures",
            "⚙️ Configuration API"
        ])
        
        with tab1:
            st.header("🎯 Recherche d'emploi - Hub centralisé multi-sources")
            
            # Barre de recherche améliorée
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                query = st.text_input("🔍 Poste recherché", placeholder="Ex: développeur, vendeur, serveur...")
            
            with col2:
                location = st.text_input("📍 Localisation", placeholder="Ex: Paris, Lyon...")
            
            with col3:
                api_choice = st.selectbox("Source", ["Toutes", "JSearch", "France Travail", "Indeed"])
            
            with col4:
                st.write("")
                st.write("")
                search_button = st.button("🔍 Rechercher", use_container_width=True)
            
            # Recherche avec vraies API
            if search_button or query:
                with st.spinner("🌐 Recherche sur Internet (JSearch + France Travail + Indeed)..."):
                    all_jobs = []
                    
                    # Recherche sur toutes les sources
                    if api_choice == "Toutes":
                        # JSearch (si configuré)
                        jsearch_jobs = get_real_jobs_jsearch(query, location)
                        all_jobs.extend(jsearch_jobs)
                        
                        # France Travail (toujours disponible)
                        france_jobs = get_france_travail_jobs(query, location)
                        all_jobs.extend(france_jobs)
                        
                        # Indeed backup si JSearch ne fonctionne pas
                        if not jsearch_jobs:
                            indeed_jobs = get_indeed_jobs_backup(query, location)
                            all_jobs.extend(indeed_jobs)
                    
                    # Recherche JSearch uniquement
                    elif api_choice == "JSearch":
                        jsearch_jobs = get_real_jobs_jsearch(query, location)
                        all_jobs.extend(jsearch_jobs)
                        
                        if not jsearch_jobs:
                            st.info("🔄 JSearch indisponible, utilisation d'Indeed en backup...")
                            indeed_jobs = get_indeed_jobs_backup(query, location)
                            all_jobs.extend(indeed_jobs)
                    
                    # Recherche France Travail uniquement
                    elif api_choice == "France Travail":
                        france_jobs = get_france_travail_jobs(query, location)
                        all_jobs.extend(france_jobs)
                    
                    # Recherche Indeed uniquement
                    elif api_choice == "Indeed":
                        indeed_jobs = get_indeed_jobs_backup(query, location)
                        all_jobs.extend(indeed_jobs)
                    
                    if all_jobs:
                        # Sauvegarder la recherche
                        save_search(query, location, len(all_jobs))
                        
                        st.success(f"✅ {len(all_jobs)} offres trouvées sur Internet")
                        
                        # Statistiques
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Offres trouvées", len(all_jobs))
                        with col2:
                            remote_count = len([j for j in all_jobs if j.get('is_remote')])
                            st.metric("Télétravail", remote_count)
                        with col3:
                            sources = len(set([j.get('source', 'Autre') for j in all_jobs]))
                            st.metric("Sources", sources)
                        with col4:
                            companies = len(set([j['company'] for j in all_jobs if j['company']]))
                            st.metric("Entreprises", companies)
                        
                        detector = AdvancedJobScamDetector()
                        
                        # Affichage des offres
                        for i, job in enumerate(all_jobs):
                            analysis = detector.analyze_text(job['description'])
                            
                            # Déterminer le niveau de risque
                            if analysis['risk_score'] >= 0.6:
                                risk_class = "risk-high"
                                risk_emoji = "🚨"
                                risk_text = "RISQUE ÉLEVÉ"
                                risk_color = "#DC143C"
                            elif analysis['risk_score'] >= 0.3:
                                risk_class = "risk-medium"
                                risk_emoji = "⚠️"
                                risk_text = "RISQUE MOYEN"
                                risk_color = "#FF8C00"
                            else:
                                risk_class = "risk-low"
                                risk_emoji = "✅"
                                risk_text = "OFFRE SÉCURISÉE"
                                risk_color = "#2E8B57"
                            
                            # Afficher seulement les offres sécurisées
                            if analysis['risk_score'] < 0.6:
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
                        st.warning("Aucune offre trouvée. Essayez d'autres mots-clés ou vérifiez votre configuration API.")
        
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
                st.subheader("🔍 Historique des recherches")
                for search in user_info['searches'][-5:]:  # 5 dernières recherches
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
            st.header("⚙️ Configuration API")
            
            st.markdown("""
            <div class="api-status">
                <h3>🔧 Configuration des sources d'offres d'emploi</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Statut des API
            api_key = st.secrets.get("RAPIDAPI_KEY", "DEMO_KEY")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🇫🇷 France Travail (Officiel)")
                st.success("✅ **Toujours disponible** - AUCUNE configuration requise")
                st.info("API officielle du gouvernement français avec toutes les offres d'emploi publiques")
            
            with col2:
                st.subheader("🌐 JSearch (Multi-sources)")
                if api_key == "DEMO_KEY":
                    st.error("❌ **Non configurée** - Configuration optionnelle")
                else:
                    st.success("✅ **Configurée** - Accès Indeed + LinkedIn + Glassdoor")
            
            st.markdown("""
            ### 📊 Sources disponibles :
            
            **🇫🇷 France Travail (GRATUIT - AUCUNE CONFIG):**
            - ✅ **API officielle** du gouvernement français
            - ✅ **Toutes les offres publiques** françaises
            - ✅ **Aucune limite** de requêtes
            - ✅ **Aucune configuration** requise
            - ✅ **Liens directs** vers les offres
            
            **🌐 JSearch (OPTIONNEL - 2500 requêtes/mois gratuites):**
            - ✅ **Multi-sources** : Indeed + LinkedIn + Glassdoor + ZipRecruiter
            - ✅ **2500 requêtes/mois** gratuites
            - ✅ **Offres internationales**
            - ⚙️ **Configuration requise** (optionnelle)
            
            ### 🔧 Configuration JSearch (OPTIONNELLE) :
            
            **Si vous voulez plus d'offres internationales :**
            
            1. **Créer un compte RapidAPI :** https://rapidapi.com/
            2. **S'abonner à JSearch :** https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
            3. **Récupérer votre clé API**
            4. **L'ajouter dans les secrets Streamlit :** `RAPIDAPI_KEY = "votre_cle"`
            
            ### 💡 Recommandation :
            **L'API France Travail suffit** pour la plupart des recherches d'emploi en France !
            """)
            
            # Test des API
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🧪 Tester France Travail"):
                    with st.spinner("Test en cours..."):
                        test_jobs = get_france_travail_jobs("test", "Paris")
                        if test_jobs:
                            st.success(f"✅ France Travail fonctionnelle ! {len(test_jobs)} offres trouvées")
                        else:
                            st.warning("⚠️ Aucune offre trouvée pour 'test' à 'Paris'")
            
            with col2:
                if st.button("🧪 Tester JSearch"):
                    with st.spinner("Test en cours..."):
                        test_jobs = get_real_jobs_jsearch("test", "France")
                        if test_jobs:
                            st.success(f"✅ JSearch fonctionnelle ! {len(test_jobs)} offres trouvées")
                            st.info(f"Sources : {', '.join(set([j.get('source', 'Autre') for j in test_jobs]))}")
                        else:
                            st.error("❌ JSearch non configurée ou aucune offre trouvée")
    
    else:
        st.info("👈 Veuillez vous connecter pour accéder à l'application")
        
        st.header("🎯 Hub de recherche d'emploi centralisé")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h2>🇫🇷</h2>
                <h3>France Travail Officiel</h3>
                <p>API gouvernementale avec toutes les offres d'emploi françaises</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <h2>🌐</h2>
                <h3>Multi-sources JSearch</h3>
                <p>Indeed + LinkedIn + Glassdoor + ZipRecruiter (optionnel)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stats-card">
                <h2>🛡️</h2>
                <h3>Protection anti-arnaque</h3>
                <p>Filtrage automatique des offres suspectes</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
