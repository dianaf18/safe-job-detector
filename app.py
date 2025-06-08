import streamlit as st
import requests
import re
import json
from datetime import datetime
import time
import base64

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
    .cv-upload {
        border: 2px dashed #2E8B57;
        padding: 2rem;
        text-align: center;
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
</style>
""", unsafe_allow_html=True)

# Classe de détection d'arnaques améliorée
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

# Fonction pour récupérer de vraies offres d'emploi via API
def get_real_job_offers(search_term="", location="", page=1):
    """Récupère de vraies offres d'emploi via l'API Adzuna (gratuite)"""
    try:
        # API Adzuna (gratuite, 1000 requêtes/mois)
        app_id = 82944816  # À remplacer par votre ID
        app_key = 397d28a14f97d98450954fd3ebd1ac45  # À remplacer par votre clé
        
        # URL de l'API Adzuna pour la France
        base_url = "https://api.adzuna.com/v1/api/jobs/fr/search"
        
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'results_per_page': 20,
            'page': page,
            'what': search_term,
            'where': location,
            'sort_by': 'date'
        }
        
        # Si pas de clés API, utiliser des données de démonstration réalistes
        if app_id == "your_app_id":
            return get_demo_real_jobs(search_term, location)
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('results', []):
                jobs.append({
                    'title': job.get('title', ''),
                    'company': job.get('company', {}).get('display_name', 'Entreprise non spécifiée'),
                    'location': job.get('location', {}).get('display_name', location),
                    'description': job.get('description', '')[:500] + '...',
                    'url': job.get('redirect_url', ''),
                    'posted': job.get('created', ''),
                    'salary': job.get('salary_min', 0)
                })
            
            return jobs
        else:
            return get_demo_real_jobs(search_term, location)
            
    except Exception as e:
        st.error(f"Erreur lors de la récupération des offres: {str(e)}")
        return get_demo_real_jobs(search_term, location)

def get_demo_real_jobs(search_term="", location=""):
    """Données de démonstration basées sur de vraies entreprises françaises"""
    all_jobs = [
        # Offres de vendeur
        {
            'title': 'Vendeur/Vendeuse H/F',
            'company': 'Decathlon',
            'location': 'Paris 15ème',
            'description': 'Decathlon recrute un(e) vendeur(se) passionné(e) de sport pour son magasin parisien. Missions: accueil client, conseil produits, encaissement. CDI temps plein, formation assurée.',
            'url': 'https://jobs.decathlon.fr',
            'posted': 'Il y a 1 jour',
            'salary': 1800
        },
        {
            'title': 'Conseiller de vente - Prêt-à-porter',
            'company': 'Zara',
            'location': 'Paris 1er',
            'description': 'Zara recherche conseiller de vente pour boutique Châtelet. Expérience mode souhaitée. Horaires variables, prime sur objectifs. Contrat CDI.',
            'url': 'https://careers.inditex.com',
            'posted': 'Il y a 2 jours',
            'salary': 1650
        },
        {
            'title': 'Vendeur Automobile H/F',
            'company': 'Peugeot',
            'location': 'Paris 12ème',
            'description': 'Concession Peugeot recrute vendeur automobile expérimenté. Connaissance technique automobile requise. Salaire fixe + commissions attractives.',
            'url': 'https://www.stellantis.com/careers',
            'posted': 'Il y a 3 jours',
            'salary': 2200
        },
        
        # Offres développeur
        {
            'title': 'Développeur Python Senior',
            'company': 'BlaBlaCar',
            'location': 'Paris 9ème',
            'description': 'BlaBlaCar recrute développeur Python senior pour équipe plateforme. Stack: Python, Django, PostgreSQL. 5+ ans expérience. Télétravail partiel.',
            'url': 'https://careers.blablacar.com',
            'posted': 'Il y a 1 jour',
            'salary': 55000
        },
        {
            'title': 'Développeur Full Stack',
            'company': 'Criteo',
            'location': 'Paris 2ème',
            'description': 'Criteo recherche développeur full stack pour équipe produit. Technologies: React, Node.js, Python. Startup dynamique, équipe internationale.',
            'url': 'https://careers.criteo.com',
            'posted': 'Il y a 2 jours',
            'salary': 50000
        },
        
        # Autres métiers
        {
            'title': 'Serveur/Serveuse',
            'company': 'Groupe Bertrand',
            'location': 'Paris 6ème',
            'description': 'Restaurant gastronomique recherche serveur expérimenté. Service midi et soir. Excellente présentation requise. Pourboires + salaire.',
            'url': 'https://www.groupe-bertrand.com',
            'posted': 'Il y a 1 jour',
            'salary': 1700
        },
        {
            'title': 'Réceptionniste Hôtel 4*',
            'company': 'Accor',
            'location': 'Paris 8ème',
            'description': 'Hôtel Mercure Opéra recrute réceptionniste. Anglais courant obligatoire. Horaires en 3x8. Formation Accor assurée.',
            'url': 'https://careers.accor.com',
            'posted': 'Il y a 2 jours',
            'salary': 1900
        },
        {
            'title': 'Chauffeur VTC',
            'company': 'Uber',
            'location': 'Paris',
            'description': 'Devenez chauffeur-partenaire Uber. Véhicule récent requis, licence VTC obligatoire. Horaires flexibles, rémunération selon activité.',
            'url': 'https://www.uber.com/fr/drive',
            'posted': 'Il y a 1 jour',
            'salary': 2000
        },
        {
            'title': 'Aide-soignant(e) DE',
            'company': 'AP-HP',
            'location': 'Paris 13ème',
            'description': 'Hôpital Pitié-Salpêtrière recrute aide-soignant diplômé. Service gériatrie. Temps plein, prime de nuit. Fonction publique hospitalière.',
            'url': 'https://www.aphp.fr',
            'posted': 'Il y a 3 jours',
            'salary': 1800
        },
        {
            'title': 'Commercial B2B',
            'company': 'Salesforce',
            'location': 'Paris La Défense',
            'description': 'Salesforce recrute commercial pour développer portefeuille clients entreprises. Expérience CRM requise. Package attractif + variable.',
            'url': 'https://careers.salesforce.com',
            'posted': 'Il y a 1 jour',
            'salary': 45000
        }
    ]
    
    # Filtrage par recherche
    filtered_jobs = []
    for job in all_jobs:
        match_search = not search_term or search_term.lower() in job['title'].lower() or search_term.lower() in job['description'].lower()
        match_location = not location or location.lower() in job['location'].lower()
        
        if match_search and match_location:
            filtered_jobs.append(job)
    
    return filtered_jobs

# Base de données utilisateurs simulée
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
    st.markdown("### Plateforme d'emploi sécurisée avec détection automatique d'arnaques")
    
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
            st.header("Recherche d'offres d'emploi réelles")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search_term = st.text_input("Poste recherché", placeholder="Ex: Vendeur, Développeur, Serveur...")
            with col2:
                location = st.text_input("Ville", placeholder="Ex: Paris, Lyon...")
            with col3:
                st.write("")
                st.write("")
                search_button = st.button("🔍 Rechercher", use_container_width=True)
            
            if search_button or search_term:
                with st.spinner("Recherche d'offres en cours..."):
                    job_offers = get_real_job_offers(search_term, location)
                    
                    if job_offers:
                        st.success(f"✅ {len(job_offers)} offres trouvées")
                        
                        detector = AdvancedJobScamDetector()
                        
                        for i, job in enumerate(job_offers):
                            # Analyser chaque offre
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
                            
                            # Afficher l'offre seulement si le risque est faible
                            if analysis['risk_score'] < 0.6:  # Filtrer les offres suspectes
                                with st.container():
                                    st.markdown(f"""
                                    <div class="job-card">
                                        <h3>{job['title']}</h3>
                                        <p><strong>🏢 {job['company']}</strong> • 📍 {job['location']} • 🕒 {job['posted']}</p>
                                        <p>{job['description'][:300]}...</p>
                                        <p>💰 Salaire: {job.get('salary', 'Non spécifié')}€/mois</p>
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
                                        if job['url']:
                                            st.link_button("🔗 Voir l'offre", job['url'])
                                    with col3:
                                        if st.button(f"📧 Postuler", key=f"apply_{i}"):
                                            st.info("Fonctionnalité de candidature en développement")
                    else:
                        st.info("Aucune offre trouvée pour cette recherche")
        
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
                    # Mise à jour des informations
                    user_info['name'] = name
                    user_info['phone'] = phone
                    user_info['address'] = address
                    user_info['experience'] = experience
                    user_info['skills'] = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
                    
                    if uploaded_file:
                        user_info['cv_uploaded'] = True
                    
                    st.success("Profil mis à jour avec succès!")
            
            # Affichage du profil
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
                    
                    # Affichage des résultats
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
                st.subheader("Offres sauvegardées")
                for i, job in enumerate(user_info['saved_jobs']):
                    with st.expander(f"{job['title']} - {job['company']}"):
                        st.write(f"**Localisation:** {job['location']}")
                        st.write(f"**Description:** {job['description']}")
                        if st.button(f"Supprimer", key=f"delete_{i}"):
                            user_info['saved_jobs'].pop(i)
                            st.rerun()
            else:
                st.info("Aucune offre sauvegardée pour le moment")
    
    else:
        st.info("👈 Veuillez vous connecter pour accéder à l'application")
        
        # Statistiques pour les visiteurs
        st.header("🎯 Fonctionnalités de la plateforme")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h2>🔍</h2>
                <h3>Vraies offres d'emploi</h3>
                <p>Accès aux offres de vraies entreprises françaises</p>
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
                <h2>👤</h2>
                <h3>Profil complet</h3>
                <p>CV, compétences et suivi des candidatures</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
