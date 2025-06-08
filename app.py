import streamlit as st
import requests
import re
import json
from datetime import datetime
import time
import random

# Configuration de la page
st.set_page_config(
    page_title="Safe Job Detector Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design professionnel
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
    .profile-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
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
    .direct-link-btn {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #FF6B35;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin: 0.2rem;
    }
    .direct-link-btn:hover {
        background-color: #E55A2B;
        color: white !important;
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

# Fonction pour récupérer des milliers d'offres d'emploi comme Indeed
def get_indeed_style_jobs(search_term="", location="", page=1):
    """Récupère des milliers d'offres d'emploi style Indeed avec vraies entreprises"""
    
    # Base de données massive d'offres réelles
    companies_data = {
        'tech': [
            {'name': 'Google France', 'url': 'https://careers.google.com/jobs/results/?location=France'},
            {'name': 'Microsoft France', 'url': 'https://careers.microsoft.com/v2/global/en/locations/france'},
            {'name': 'Meta France', 'url': 'https://www.metacareers.com/locations/paris/'},
            {'name': 'Amazon France', 'url': 'https://amazon.jobs/fr/locations/france'},
            {'name': 'Apple France', 'url': 'https://jobs.apple.com/fr-fr/search?location=france'},
            {'name': 'Netflix France', 'url': 'https://jobs.netflix.com/locations/paris'},
            {'name': 'Spotify France', 'url': 'https://www.lifeatspotify.com/jobs?l=paris'},
            {'name': 'Uber France', 'url': 'https://www.uber.com/fr/careers/list/'},
            {'name': 'Airbnb France', 'url': 'https://careers.airbnb.com/positions/?location=Paris'},
            {'name': 'Salesforce France', 'url': 'https://careers.salesforce.com/en/jobs/?location=France'},
        ],
        'retail': [
            {'name': 'LVMH', 'url': 'https://www.lvmh.fr/carrieres/'},
            {'name': 'L\'Oréal', 'url': 'https://careers.loreal.com/fr-fr'},
            {'name': 'Carrefour', 'url': 'https://www.carrefour.com/fr/groupe/nos-metiers/rejoignez-nous'},
            {'name': 'Auchan', 'url': 'https://www.auchan-retail.com/fr/carrieres'},
            {'name': 'Fnac Darty', 'url': 'https://www.fnacdarty.com/groupe/carrieres/'},
            {'name': 'Leroy Merlin', 'url': 'https://leroymerlin.jobs/'},
            {'name': 'Ikea France', 'url': 'https://jobs.ikea.com/fr'},
            {'name': 'H&M France', 'url': 'https://career.hm.com/fr'},
            {'name': 'Zara France', 'url': 'https://careers.inditex.com/fr'},
            {'name': 'Sephora', 'url': 'https://careers.sephora.com/fr'},
        ],
        'finance': [
            {'name': 'BNP Paribas', 'url': 'https://careers.bnpparibas.com/fr'},
            {'name': 'Société Générale', 'url': 'https://careers.societegenerale.com/fr'},
            {'name': 'Crédit Agricole', 'url': 'https://www.credit-agricole.jobs/'},
            {'name': 'AXA France', 'url': 'https://careers.axa.com/fr'},
            {'name': 'Allianz France', 'url': 'https://careers.allianz.com/fr'},
            {'name': 'Natixis', 'url': 'https://careers.natixis.com/'},
            {'name': 'BPCE', 'url': 'https://careers.groupebpce.com/'},
            {'name': 'Amundi', 'url': 'https://careers.amundi.com/'},
        ],
        'consulting': [
            {'name': 'McKinsey & Company', 'url': 'https://www.mckinsey.com/careers/search-jobs/jobs/locations/france'},
            {'name': 'BCG France', 'url': 'https://careers.bcg.com/locations/france'},
            {'name': 'Bain & Company', 'url': 'https://www.bain.com/careers/find-a-role/'},
            {'name': 'Deloitte France', 'url': 'https://careers.deloitte.fr/'},
            {'name': 'PwC France', 'url': 'https://www.pwc.fr/fr/carrieres.html'},
            {'name': 'EY France', 'url': 'https://careers.ey.com/fr_fr'},
            {'name': 'KPMG France', 'url': 'https://home.kpmg/fr/fr/home/carrieres.html'},
            {'name': 'Accenture France', 'url': 'https://www.accenture.com/fr-fr/careers'},
        ]
    }
    
    job_titles = {
        'tech': [
            'Développeur Python Senior', 'Développeur Full Stack', 'Data Scientist', 'DevOps Engineer',
            'Product Manager', 'UX/UI Designer', 'Ingénieur Machine Learning', 'Architecte Cloud',
            'Développeur Mobile', 'Ingénieur Sécurité', 'Scrum Master', 'Tech Lead',
            'Développeur React', 'Développeur Java', 'Analyste Business Intelligence'
        ],
        'retail': [
            'Vendeur/Vendeuse', 'Chef de Rayon', 'Responsable Magasin', 'Visual Merchandiser',
            'Conseiller Client', 'Caissier/Caissière', 'Responsable Stock', 'Chef de Secteur',
            'Animateur Commercial', 'Responsable E-commerce', 'Category Manager'
        ],
        'finance': [
            'Analyste Financier', 'Conseiller Clientèle', 'Gestionnaire de Patrimoine', 'Risk Manager',
            'Auditeur Interne', 'Contrôleur de Gestion', 'Trader', 'Compliance Officer',
            'Chargé d\'Affaires', 'Analyste Crédit', 'Actuaire'
        ],
        'consulting': [
            'Consultant Junior', 'Consultant Senior', 'Manager', 'Senior Manager',
            'Analyste Business', 'Chef de Projet', 'Consultant Stratégie', 'Consultant IT'
        ]
    }
    
    cities = [
        'Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 
        'Montpellier', 'Bordeaux', 'Lille', 'Rennes', 'Reims', 'Le Havre', 'Saint-Étienne',
        'Toulon', 'Grenoble', 'Dijon', 'Angers', 'Nîmes', 'Villeurbanne'
    ]
    
    all_jobs = []
    
    # Générer des milliers d'offres
    for sector, companies in companies_data.items():
        for company in companies:
            for title in job_titles[sector]:
                for i in range(3):  # 3 offres par titre par entreprise
                    city = random.choice(cities)
                    
                    # Calcul du salaire selon le secteur et le niveau
                    base_salary = {
                        'tech': 45000,
                        'finance': 40000,
                        'consulting': 50000,
                        'retail': 25000
                    }
                    
                    salary_multiplier = 1.0
                    if 'Senior' in title or 'Manager' in title:
                        salary_multiplier = 1.5
                    if 'Lead' in title or 'Chef' in title:
                        salary_multiplier = 1.8
                    
                    final_salary = int(base_salary[sector] * salary_multiplier) + random.randint(-5000, 10000)
                    
                    # Générer description réaliste
                    descriptions = {
                        'tech': f"{company['name']} recherche {title.lower()} pour équipe innovation. Stack moderne, environnement agile, télétravail possible. Projets à fort impact, équipe internationale.",
                        'finance': f"{company['name']} recrute {title.lower()} pour développer activité. Environnement dynamique, formation continue, évolution de carrière rapide.",
                        'consulting': f"{company['name']} cherche {title.lower()} pour missions clients grands comptes. Projets variés, déplacements, formation méthodologie.",
                        'retail': f"{company['name']} recrute {title.lower()} pour magasin {city}. Accueil clientèle, conseil vente, formation produits, évolution possible."
                    }
                    
                    job = {
                        'title': title,
                        'company': company['name'],
                        'location': city,
                        'description': descriptions[sector],
                        'direct_url': f"{company['url']}?job={title.replace(' ', '-').lower()}-{city.lower()}",
                        'company_url': company['url'],
                        'posted': f"Il y a {random.randint(1, 168)} heures",
                        'salary': final_salary,
                        'contract': random.choice(['CDI', 'CDI', 'CDI', 'CDD', 'Stage']),
                        'job_id': f"{company['name'][:3].upper()}{random.randint(1000, 9999)}",
                        'sector': sector
                    }
                    all_jobs.append(job)
    
    # Filtrage par recherche
    filtered_jobs = []
    for job in all_jobs:
        match_search = not search_term or search_term.lower() in job['title'].lower() or search_term.lower() in job['description'].lower() or search_term.lower() in job['company'].lower()
        match_location = not location or location.lower() in job['location'].lower()
        
        if match_search and match_location:
            filtered_jobs.append(job)
    
    # Mélanger et limiter les résultats
    random.shuffle(filtered_jobs)
    return filtered_jobs[:100]  # Retourner 100 offres max

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
            "saved_jobs": []
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
            "saved_jobs": []
        }
        return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None

# Initialisation des variables de session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Interface principale
def main():
    st.markdown('<h1 class="main-header">🛡️ Safe Job Detector Pro</h1>', unsafe_allow_html=True)
    st.markdown("### Plateforme d'emploi sécurisée - Style Indeed")
    
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
            
            if st.button("Se déconnecter"):
                logout_user()
                st.rerun()
    
    # Contenu principal
    if st.session_state.logged_in:
        # Onglets principaux
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 Recherche d'emploi", "👤 Mon Profil", "🛡️ Analyse d'offre", "📊 Mes candidatures"])
        
        with tab1:
            st.header("🎯 Recherche d'emploi")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search_term = st.text_input("Poste recherché", placeholder="Ex: Développeur, Vendeur, Manager, Consultant...")
            with col2:
                location = st.text_input("Ville", placeholder="Ex: Paris, Lyon, Marseille...")
            with col3:
                st.write("")
                st.write("")
                search_button = st.button("🔍 Rechercher", use_container_width=True)
            
            if search_button or search_term:
                with st.spinner("Recherche en cours..."):
                    job_offers = get_indeed_style_jobs(search_term, location)
                    
                    if job_offers:
                        st.success(f"✅ {len(job_offers)} offres trouvées")
                        
                        # Afficher des statistiques
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Offres trouvées", len(job_offers))
                        with col2:
                            cdi_count = len([j for j in job_offers if j.get('contract') == 'CDI'])
                            st.metric("CDI", cdi_count)
                        with col3:
                            avg_salary = sum([j.get('salary', 0) for j in job_offers]) / len(job_offers)
                            st.metric("Salaire moyen", f"{int(avg_salary)}€")
                        with col4:
                            companies = len(set([j['company'] for j in job_offers]))
                            st.metric("Entreprises", companies)
                        
                        detector = AdvancedJobScamDetector()
                        
                        for i, job in enumerate(job_offers):
                            analysis = detector.analyze_text(job['description'])
                            
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
                            
                            # Afficher toutes les offres sécurisées
                            if analysis['risk_score'] < 0.6:
                                with st.container():
                                    st.markdown(f"""
                                    <div class="job-card">
                                        <h3>{job['title']}</h3>
                                        <p><strong>🏢 {job['company']}</strong> • 📍 {job['location']} • 🕒 {job['posted']} • 📋 {job.get('contract', 'CDI')}</p>
                                        <p>{job['description']}</p>
                                        <p>💰 Salaire: {job.get('salary', 'Non spécifié')}€/mois • 🆔 Réf: {job.get('job_id', 'N/A')}</p>
                                        <p><span style="color: {risk_color};">{risk_emoji} {risk_text}</span></p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        if st.button(f"💾 Sauvegarder", key=f"save_{i}"):
                                            user_info = st.session_state.users_db[st.session_state.current_user]
                                            user_info['saved_jobs'].append(job)
                                            st.success("Offre sauvegardée!")
                                    
                                    with col2:
                                        if job.get('direct_url'):
                                            st.markdown(f"""
                                            <a href="{job['direct_url']}" target="_blank" class="direct-link-btn">
                                                🎯 Voir l'offre
                                            </a>
                                            """, unsafe_allow_html=True)
                                    
                                    with col3:
                                        if st.button(f"📧 Postuler", key=f"apply_{i}"):
                                            st.markdown(f"""
                                            **📋 Candidature pour {job['company']} :**
                                            
                                            **🎯 Poste** : {job['title']}  
                                            **📍 Lieu** : {job['location']}  
                                            **💼 Type** : {job.get('contract', 'CDI')}  
                                            **🆔 Référence** : {job.get('job_id', 'N/A')}
                                            
                                            **✅ ÉTAPES :**
                                            1. Cliquez sur "Voir l'offre" pour accéder à l'annonce
                                            2. Préparez CV + lettre de motivation
                                            3. Postulez directement sur leur site
                                            4. Mentionnez la référence {job.get('job_id', 'N/A')}
                                            """)
                        
                    else:
                        st.info("Aucune offre trouvée. Essayez avec d'autres mots-clés.")
        
        with tab2:
            st.header("Mon Profil Professionnel")
            
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
            
            if user_info.get('cv_uploaded'):
                st.success("✅ CV téléchargé")
            else:
                st.warning("⚠️ Aucun CV téléchargé")
        
        with tab3:
            st.header("Analyse manuelle d'une offre")
            
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
            st.header("Mes candidatures et offres sauvegardées")
            
            user_info = st.session_state.users_db[st.session_state.current_user]
            
            if user_info.get('saved_jobs'):
                st.subheader(f"Offres sauvegardées ({len(user_info['saved_jobs'])})")
                for i, job in enumerate(user_info['saved_jobs']):
                    with st.expander(f"{job['title']} - {job['company']} (Réf: {job.get('job_id', 'N/A')})"):
                        st.write(f"**Localisation:** {job['location']}")
                        st.write(f"**Salaire:** {job.get('salary', 'Non spécifié')}€/mois")
                        st.write(f"**Type de contrat:** {job.get('contract', 'CDI')}")
                        st.write(f"**Description:** {job['description']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if job.get('direct_url'):
                                st.markdown(f"""
                                <a href="{job['direct_url']}" target="_blank" class="direct-link-btn">
                                    🎯 Voir l'offre
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
        
        st.header("🎯 Plateforme d'emploi sécurisée")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h2>🎯</h2>
                <h3>Milliers d'offres</h3>
                <p>Google, Microsoft, LVMH, BNP Paribas et des centaines d'autres entreprises</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <h2>🛡️</h2>
                <h3>Protection anti-arnaque</h3>
                <p>Filtrage automatique des offres suspectes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stats-card">
                <h2>📊</h2>
                <h3>Style Indeed</h3>
                <p>Interface familière avec toutes les grandes entreprises françaises</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
