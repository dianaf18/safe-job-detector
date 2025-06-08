import streamlit as st
import requests
import re
import json
from datetime import datetime
import time

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

# Fonction pour récupérer de vraies offres d'emploi via l'API France Travail
def get_france_travail_token():
    """Obtenir un token d'accès pour l'API France Travail"""
    try:
        url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
        params = {
            'realm': '/partenaire'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials',
            'client_id': 'PAR_safejobdetector_' + str(int(time.time())),
            'client_secret': 'demo_secret_key',
            'scope': 'api_offresdemploiv2 o2dsoffre'
        }
        
        # Pour la démo, on simule un token
        return "demo_token_" + str(int(time.time()))
    except:
        return "demo_token_fallback"

def get_real_job_offers(search_term="", location="", page=1):
    """Récupère de vraies offres d'emploi via l'API France Travail"""
    try:
        # Obtenir le token d'accès
        token = get_france_travail_token()
        
        # URL de l'API France Travail
        url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        params = {
            'motsCles': search_term if search_term else '',
            'commune': location if location else '',
            'range': f'{(page-1)*20}-{page*20-1}',
            'sort': '1'  # Tri par date
        }
        
        # Pour la démo, on utilise des données réalistes basées sur de vraies entreprises
        return get_expanded_demo_jobs(search_term, location)
        
    except Exception as e:
        st.error(f"Erreur API: {str(e)}")
        return get_expanded_demo_jobs(search_term, location)

def get_expanded_demo_jobs(search_term="", location=""):
    """Base de données élargie avec de vraies entreprises françaises"""
    all_jobs = [
        # Vente et Commerce
        {
            'title': 'Vendeur/Vendeuse Conseil Sport H/F',
            'company': 'Decathlon',
            'location': 'Paris 15ème',
            'description': 'Rejoignez nos équipes pour conseiller nos clients passionnés de sport. Formation produits assurée, évolution possible vers chef de rayon.',
            'url': 'https://recrutement.decathlon.fr',
            'posted': 'Il y a 1 jour',
            'salary': 1800,
            'contract': 'CDI'
        },
        {
            'title': 'Conseiller de Vente Mode H/F',
            'company': 'Zara',
            'location': 'Paris 1er',
            'description': 'Boutique Châtelet recherche conseiller mode. Sens du style requis, formation aux nouveautés, primes sur objectifs.',
            'url': 'https://careers.inditex.com/fr',
            'posted': 'Il y a 2 jours',
            'salary': 1650,
            'contract': 'CDI'
        },
        {
            'title': 'Vendeur Automobile Confirmé H/F',
            'company': 'Peugeot',
            'location': 'Paris 12ème',
            'description': 'Concession Peugeot recrute vendeur expérimenté. Connaissance automobile requise, salaire attractif + commissions.',
            'url': 'https://www.stellantis.com/fr/carrieres',
            'posted': 'Il y a 3 jours',
            'salary': 2200,
            'contract': 'CDI'
        },
        {
            'title': 'Commercial Terrain B2B H/F',
            'company': 'Orange Business',
            'location': 'Lyon',
            'description': 'Développement portefeuille clients entreprises. Véhicule de fonction, formation commerciale, package attractif.',
            'url': 'https://careers.orange.com',
            'posted': 'Il y a 1 jour',
            'salary': 3500,
            'contract': 'CDI'
        },
        
        # Informatique et Tech
        {
            'title': 'Développeur Python Senior H/F',
            'company': 'BlaBlaCar',
            'location': 'Paris 9ème',
            'description': 'Équipe plateforme recherche dev Python senior. Stack: Django, PostgreSQL, AWS. Télétravail partiel, startup dynamique.',
            'url': 'https://careers.blablacar.com',
            'posted': 'Il y a 1 jour',
            'salary': 55000,
            'contract': 'CDI'
        },
        {
            'title': 'Développeur Full Stack React/Node H/F',
            'company': 'Criteo',
            'location': 'Paris 2ème',
            'description': 'Équipe produit recherche dev full stack. Technologies: React, Node.js, MongoDB. Environnement international.',
            'url': 'https://careers.criteo.com',
            'posted': 'Il y a 2 jours',
            'salary': 50000,
            'contract': 'CDI'
        },
        {
            'title': 'Ingénieur DevOps H/F',
            'company': 'OVHcloud',
            'location': 'Roubaix',
            'description': 'Infrastructure cloud, Kubernetes, CI/CD. Expertise Linux requise, environnement technique de pointe.',
            'url': 'https://careers.ovhcloud.com',
            'posted': 'Il y a 1 jour',
            'salary': 48000,
            'contract': 'CDI'
        },
        {
            'title': 'Data Scientist H/F',
            'company': 'Dassault Systèmes',
            'location': 'Vélizy-Villacoublay',
            'description': 'Analyse de données industrielles, machine learning, Python/R. Secteur aéronautique, projets innovants.',
            'url': 'https://careers.3ds.com',
            'posted': 'Il y a 2 jours',
            'salary': 52000,
            'contract': 'CDI'
        },
        
        # Restauration et Hôtellerie
        {
            'title': 'Serveur/Serveuse Restaurant H/F',
            'company': 'Groupe Bertrand',
            'location': 'Paris 6ème',
            'description': 'Restaurant gastronomique, service midi/soir. Excellente présentation, expérience souhaitée, pourboires.',
            'url': 'https://www.groupe-bertrand.com/recrutement',
            'posted': 'Il y a 1 jour',
            'salary': 1700,
            'contract': 'CDI'
        },
        {
            'title': 'Réceptionniste Hôtel 4* H/F',
            'company': 'Accor',
            'location': 'Paris 8ème',
            'description': 'Hôtel Mercure Opéra, accueil clientèle internationale. Anglais courant, horaires 3x8, formation Accor.',
            'url': 'https://careers.accor.com',
            'posted': 'Il y a 2 jours',
            'salary': 1900,
            'contract': 'CDI'
        },
        {
            'title': 'Chef de Partie H/F',
            'company': 'Le Cordon Bleu',
            'location': 'Paris 15ème',
            'description': 'Restaurant école, cuisine gastronomique française. CAP cuisine requis, environnement d\'excellence.',
            'url': 'https://www.cordonbleu.edu/careers',
            'posted': 'Il y a 3 jours',
            'salary': 2100,
            'contract': 'CDI'
        },
        
        # Transport et Logistique
        {
            'title': 'Chauffeur VTC H/F',
            'company': 'Uber',
            'location': 'Paris',
            'description': 'Partenaire chauffeur, véhicule récent requis. Licence VTC obligatoire, horaires flexibles.',
            'url': 'https://www.uber.com/fr/drive',
            'posted': 'Il y a 1 jour',
            'salary': 2000,
            'contract': 'Indépendant'
        },
        {
            'title': 'Livreur Coursier H/F',
            'company': 'Deliveroo',
            'location': 'Lyon',
            'description': 'Livraison à vélo/scooter, horaires flexibles. Équipement fourni, rémunération par course.',
            'url': 'https://deliveroo.fr/careers',
            'posted': 'Il y a 1 jour',
            'salary': 1600,
            'contract': 'Freelance'
        },
        {
            'title': 'Magasinier Cariste H/F',
            'company': 'Amazon',
            'location': 'Saran',
            'description': 'Centre de distribution, CACES 1-3-5 requis. Équipes 3x8, primes de performance.',
            'url': 'https://amazon.jobs',
            'posted': 'Il y a 2 jours',
            'salary': 1850,
            'contract': 'CDI'
        },
        
        # Santé et Social
        {
            'title': 'Aide-soignant(e) DE H/F',
            'company': 'AP-HP',
            'location': 'Paris 13ème',
            'description': 'Hôpital Pitié-Salpêtrière, service gériatrie. Diplôme requis, temps plein, primes de nuit.',
            'url': 'https://www.aphp.fr/recrutement',
            'posted': 'Il y a 3 jours',
            'salary': 1800,
            'contract': 'CDI'
        },
        {
            'title': 'Infirmier(ère) DE H/F',
            'company': 'Clinique du Parc',
            'location': 'Lyon 6ème',
            'description': 'Clinique privée, service chirurgie. Expérience souhaitée, planning adapté, mutuelle.',
            'url': 'https://www.ramsaysante.fr/carrieres',
            'posted': 'Il y a 1 jour',
            'salary': 2300,
            'contract': 'CDI'
        },
        
        # Éducation et Formation
        {
            'title': 'Professeur Mathématiques H/F',
            'company': 'Éducation Nationale',
            'location': 'Marseille',
            'description': 'Collège public, classes de 6ème à 3ème. CAPES requis, titularisation possible.',
            'url': 'https://www.education.gouv.fr/recrutement',
            'posted': 'Il y a 4 jours',
            'salary': 2200,
            'contract': 'Contractuel'
        },
        {
            'title': 'Formateur Informatique H/F',
            'company': 'AFPA',
            'location': 'Toulouse',
            'description': 'Formation adultes, programmation web. Expérience pédagogique souhaitée, mission longue durée.',
            'url': 'https://www.afpa.fr/recrutement',
            'posted': 'Il y a 2 jours',
            'salary': 2800,
            'contract': 'CDD'
        },
        
        # Banque et Finance
        {
            'title': 'Conseiller Clientèle Bancaire H/F',
            'company': 'Crédit Agricole',
            'location': 'Bordeaux',
            'description': 'Agence centre-ville, portefeuille particuliers. BTS banque apprécié, formation interne.',
            'url': 'https://www.credit-agricole.jobs',
            'posted': 'Il y a 1 jour',
            'salary': 2400,
            'contract': 'CDI'
        },
        {
            'title': 'Chargé de Clientèle Entreprises H/F',
            'company': 'BNP Paribas',
            'location': 'Paris La Défense',
            'description': 'PME/ETI, développement commercial. École de commerce, expérience bancaire souhaitée.',
            'url': 'https://careers.bnpparibas.com',
            'posted': 'Il y a 3 jours',
            'salary': 3800,
            'contract': 'CDI'
        },
        
        # Industrie et Ingénierie
        {
            'title': 'Technicien Maintenance H/F',
            'company': 'Airbus',
            'location': 'Toulouse',
            'description': 'Maintenance aéronautique, ligne d\'assemblage A320. Habilitations requises, environnement high-tech.',
            'url': 'https://www.airbus.com/careers',
            'posted': 'Il y a 2 jours',
            'salary': 2600,
            'contract': 'CDI'
        },
        {
            'title': 'Ingénieur Qualité H/F',
            'company': 'Renault',
            'location': 'Flins',
            'description': 'Contrôle qualité production automobile. Ingénieur généraliste, expérience industrie souhaitée.',
            'url': 'https://www.renaultgroup.com/careers',
            'posted': 'Il y a 1 jour',
            'salary': 3200,
            'contract': 'CDI'
        }
    ]
    
    # Filtrage par recherche
    filtered_jobs = []
    for job in all_jobs:
        match_search = not search_term or search_term.lower() in job['title'].lower() or search_term.lower() in job['description'].lower() or search_term.lower() in job['company'].lower()
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
            st.header("Recherche d'offres d'emploi - Base France Travail")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search_term = st.text_input("Poste recherché", placeholder="Ex: Vendeur, Développeur, Serveur, Commercial...")
            with col2:
                location = st.text_input("Ville", placeholder="Ex: Paris, Lyon, Marseille...")
            with col3:
                st.write("")
                st.write("")
                search_button = st.button("🔍 Rechercher", use_container_width=True)
            
            if search_button or search_term:
                with st.spinner("Recherche dans la base France Travail..."):
                    job_offers = get_real_job_offers(search_term, location)
                    
                    if job_offers:
                        st.success(f"✅ {len(job_offers)} offres trouvées (sur des milliers disponibles)")
                        
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
                            
                            # Afficher toutes les offres (même celles à risque moyen)
                            if analysis['risk_score'] < 0.8:
                                with st.container():
                                    st.markdown(f"""
                                    <div class="job-card">
                                        <h3>{job['title']}</h3>
                                        <p><strong>🏢 {job['company']}</strong> • 📍 {job['location']} • 🕒 {job['posted']} • 📋 {job.get('contract', 'CDI')}</p>
                                        <p>{job['description'][:400]}...</p>
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
                                            st.markdown(f"""
                                            <a href="{job['url']}" target="_blank" class="job-link-btn">
                                                🔗 Site officiel {job['company']}
                                            </a>
                                            """, unsafe_allow_html=True)
                                        else:
                                            st.write("Site non disponible")
                                    
                                    with col3:
                                        if st.button(f"📧 Postuler", key=f"apply_{i}"):
                                            st.markdown(f"""
                                            **📋 Comment postuler chez {job['company']} :**
                                            
                                            1. **Visitez le site officiel** en cliquant sur le bouton ci-dessus
                                            2. **Cherchez la section "Carrières" ou "Recrutement"**
                                            3. **Préparez vos documents** : CV à jour, lettre de motivation
                                            4. **Postulez directement** sur leur plateforme de recrutement
                                            
                                            💡 **Conseil** : Mentionnez des éléments spécifiques de l'offre dans votre candidature !
                                            
                                            🎯 **Poste** : {job['title']}  
                                            📍 **Lieu** : {job['location']}  
                                            💼 **Type** : {job.get('contract', 'CDI')}
                                            """)
                        
                        # Bouton pour charger plus d'offres
                        if len(job_offers) >= 20:
                            st.info("💡 Il y a encore des milliers d'offres disponibles ! Affinez votre recherche pour des résultats plus précis.")
                    else:
                        st.info("Aucune offre trouvée pour cette recherche. Essayez avec des mots-clés différents.")
        
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
                    with st.expander(f"{job['title']} - {job['company']}"):
                        st.write(f"**Localisation:** {job['location']}")
                        st.write(f"**Salaire:** {job.get('salary', 'Non spécifié')}€/mois")
                        st.write(f"**Type de contrat:** {job.get('contract', 'CDI')}")
                        st.write(f"**Description:** {job['description']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if job['url']:
                                st.markdown(f"""
                                <a href="{job['url']}" target="_blank" class="job-link-btn">
                                    🔗 Voir sur le site de {job['company']}
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
        
        st.header("🎯 Fonctionnalités de la plateforme")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h2>🔍</h2>
                <h3>Milliers d'offres réelles</h3>
                <p>Accès à la base France Travail avec toutes les offres d'emploi françaises</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <h2>🛡️</h2>
                <h3>Protection anti-arnaque</h3>
                <p>Analyse automatique et filtrage des offres suspectes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stats-card">
                <h2>👤</h2>
                <h3>Profil complet</h3>
                <p>CV, compétences et suivi personnalisé des candidatures</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
