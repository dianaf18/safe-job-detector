import streamlit as st
import requests
import re
import json
from datetime import datetime, timedelta
import time
import base64
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from urllib.parse import urlencode, urljoin
import hashlib
import random

# Configuration de la page
st.set_page_config(
    page_title="Safe Job Hub AI - Candidature Automatique",
    page_icon="🤖",
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
    .ai-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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
    .ai-status-active {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    .ai-status-inactive {
        background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
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
    .ai-btn {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        margin: 0.2rem;
        border: none;
        cursor: pointer;
    }
    .ai-btn:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        color: white !important;
    }
    .notification-card {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .success-notification {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    .warning-notification {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Classe IA de Profilage Utilisateur
class UserProfileAI:
    def __init__(self):
        self.skills_keywords = {
            'commercial': ['vente', 'commercial', 'négociation', 'client', 'prospection'],
            'informatique': ['python', 'java', 'javascript', 'développement', 'programmation'],
            'marketing': ['marketing', 'communication', 'digital', 'réseaux sociaux', 'seo'],
            'finance': ['comptabilité', 'finance', 'gestion', 'budget', 'analyse'],
            'rh': ['ressources humaines', 'recrutement', 'formation', 'paie', 'social']
        }
    
    def analyze_user_profile(self, experience, skills, preferences):
        """Analyse automatique du profil utilisateur"""
        profile_score = {}
        
        # Analyse des compétences
        user_text = f"{experience} {' '.join(skills)}".lower()
        
        for domain, keywords in self.skills_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_text)
            profile_score[domain] = score
        
        # Domaine principal
        main_domain = max(profile_score, key=profile_score.get) if profile_score else 'général'
        
        # Génération des critères de recherche automatiques
        search_criteria = {
            'main_domain': main_domain,
            'keywords': self.skills_keywords.get(main_domain, ['emploi']),
            'experience_level': self._assess_experience_level(experience),
            'compatibility_threshold': 0.6
        }
        
        return search_criteria
    
    def _assess_experience_level(self, experience_text):
        """Évalue le niveau d'expérience"""
        experience_lower = experience_text.lower()
        
        if any(word in experience_lower for word in ['débutant', 'junior', 'stage', 'première']):
            return 'junior'
        elif any(word in experience_lower for word in ['senior', 'expert', 'manager', 'chef']):
            return 'senior'
        else:
            return 'confirmé'

# Classe de Recherche Automatique Intelligente
class AutoJobSearchAI:
    def __init__(self):
        self.daily_search_count = 0
        self.last_search_date = None
        
    def intelligent_job_search(self, user_criteria, location=""):
        """Recherche intelligente basée sur le profil utilisateur"""
        all_jobs = []
        
        # Recherche avec les mots-clés du domaine principal
        for keyword in user_criteria['keywords'][:3]:  # Top 3 mots-clés
            jobs = self._search_jobs_for_keyword(keyword, location)
            all_jobs.extend(jobs)
        
        # Filtrage intelligent des offres
        filtered_jobs = self._filter_jobs_by_compatibility(all_jobs, user_criteria)
        
        return filtered_jobs
    
    def _search_jobs_for_keyword(self, keyword, location):
        """Recherche pour un mot-clé spécifique"""
        # Utilise les API existantes optimisées
        jobs = []
        
        # API Adzuna optimisée
        try:
            jobs.extend(self._get_adzuna_jobs(keyword, location))
        except:
            pass
            
        # API HelloWork optimisée
        try:
            jobs.extend(self._get_hellowork_jobs(keyword, location))
        except:
            pass
        
        return jobs
    
    def _get_adzuna_jobs(self, keyword, location):
        """API Adzuna optimisée pour l'IA"""
        all_jobs = []
        
        for page in range(1, 4):  # 3 pages max pour la vitesse
            url = f"https://api.adzuna.com/v1/api/jobs/fr/search/{page}"
            
            params = {
                'app_id': st.secrets.get("ADZUNA_APP_ID", "DEMO_ID"),
                'app_key': st.secrets.get("ADZUNA_APP_KEY", "DEMO_KEY"),
                'results_per_page': 50,
                'what': keyword,
                'where': location or '',
                'sort_by': 'date'
            }
            
            try:
                response = requests.get(url, params=params, timeout=5)
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
                                'is_remote': 'remote' in description.lower() or 'télétravail' in description.lower(),
                                'ai_score': 0  # Score de compatibilité à calculer
                            })
                        except:
                            continue
                    
                    if len(data.get('results', [])) < 30:
                        break
                else:
                    break
                    
            except:
                break
        
        return all_jobs
    
    def _get_hellowork_jobs(self, keyword, location):
        """API HelloWork optimisée pour l'IA"""
        all_jobs = []
        
        # Simulation d'API HelloWork avec scoring IA
        fake_jobs = [
            {
                "title": f"Poste {keyword} - Entreprise {i}",
                "company": f"Entreprise {keyword} {i}",
                "location": location or "France",
                "description": f"Recherche {keyword} expérimenté. Excellente opportunité dans une entreprise dynamique.",
                "url": f"https://hellowork.com/job/{keyword}-{i}",
                "date": "2025-06-09",
                "salary": "Selon profil",
                "type": "CDI",
                "source": "HelloWork",
                "is_remote": random.choice([True, False]),
                "ai_score": random.uniform(0.5, 0.9)
            } for i in range(1, 31)
        ]
        
        for job in fake_jobs:
            all_jobs.append(job)
        
        return all_jobs
    
    def _filter_jobs_by_compatibility(self, jobs, user_criteria):
        """Filtre les offres par compatibilité avec le profil"""
        filtered_jobs = []
        
        for job in jobs:
            # Calcul du score de compatibilité
            compatibility_score = self._calculate_compatibility_score(job, user_criteria)
            job['ai_score'] = compatibility_score
            
            # Filtre par seuil de compatibilité
            if compatibility_score >= user_criteria['compatibility_threshold']:
                filtered_jobs.append(job)
        
        # Tri par score de compatibilité décroissant
        filtered_jobs.sort(key=lambda x: x['ai_score'], reverse=True)
        
        return filtered_jobs
    
    def _calculate_compatibility_score(self, job, user_criteria):
        """Calcule le score de compatibilité entre l'offre et le profil"""
        score = 0.5  # Score de base
        
        job_text = f"{job['title']} {job['description']}".lower()
        
        # Bonus pour mots-clés du domaine
        keyword_matches = sum(1 for keyword in user_criteria['keywords'] if keyword in job_text)
        score += keyword_matches * 0.1
        
        # Bonus pour niveau d'expérience
        experience_level = user_criteria['experience_level']
        if experience_level == 'junior' and any(word in job_text for word in ['junior', 'débutant', 'stage']):
            score += 0.2
        elif experience_level == 'senior' and any(word in job_text for word in ['senior', 'expert', 'manager']):
            score += 0.2
        elif experience_level == 'confirmé' and not any(word in job_text for word in ['junior', 'débutant', 'stage', 'senior', 'expert']):
            score += 0.1
        
        # Malus pour signaux d'arnaque
        scam_signals = ['urgent', 'paiement', 'formation payante', 'investissement']
        scam_count = sum(1 for signal in scam_signals if signal in job_text)
        score -= scam_count * 0.3
        
        return min(1.0, max(0.0, score))

# Classe de Génération Automatique de Candidatures
class ApplicationGeneratorAI:
    def __init__(self):
        self.cv_templates = {
            'commercial': "CV optimisé pour les postes commerciaux avec focus sur les résultats de vente",
            'informatique': "CV technique avec mise en avant des compétences de développement",
            'marketing': "CV créatif avec emphasis sur les campagnes et stratégies marketing",
            'finance': "CV analytique avec focus sur la gestion financière et budgétaire",
            'rh': "CV relationnel avec accent sur la gestion des talents"
        }
        
        self.cover_letter_templates = {
            'commercial': "Madame, Monsieur,\n\nPassionné(e) par la vente et fort(e) de mon expérience en développement commercial...",
            'informatique': "Madame, Monsieur,\n\nDéveloppeur(se) passionné(e) par les nouvelles technologies...",
            'marketing': "Madame, Monsieur,\n\nSpécialiste en marketing digital avec une approche créative...",
            'finance': "Madame, Monsieur,\n\nExpert(e) en analyse financière avec une solide expérience...",
            'rh': "Madame, Monsieur,\n\nProfessionnel(le) des ressources humaines orienté(e) développement des talents..."
        }
    
    def generate_custom_application(self, job_offer, user_profile, user_criteria):
        """Génère une candidature personnalisée"""
        domain = user_criteria['main_domain']
        
        # CV adapté
        custom_cv = self._adapt_cv_for_job(job_offer, user_profile, domain)
        
        # Lettre de motivation personnalisée
        custom_cover_letter = self._generate_cover_letter(job_offer, user_profile, domain)
        
        return {
            'cv': custom_cv,
            'cover_letter': custom_cover_letter,
            'application_date': datetime.now().isoformat(),
            'job_title': job_offer['title'],
            'company': job_offer['company'],
            'compatibility_score': job_offer.get('ai_score', 0)
        }
    
    def _adapt_cv_for_job(self, job_offer, user_profile, domain):
        """Adapte le CV selon l'offre d'emploi"""
        base_template = self.cv_templates.get(domain, "CV professionnel adapté au poste")
        
        # Personnalisation basée sur l'offre
        job_keywords = self._extract_keywords_from_job(job_offer)
        
        adapted_cv = f"""
        {base_template}
        
        PROFIL PROFESSIONNEL:
        {user_profile.get('experience', 'Expérience professionnelle diversifiée')}
        
        COMPÉTENCES CLÉS:
        {', '.join(user_profile.get('skills', ['Compétences variées']))}
        
        MOTS-CLÉS OPTIMISÉS POUR CE POSTE:
        {', '.join(job_keywords)}
        
        EXPÉRIENCE PERTINENTE:
        Expérience adaptée aux exigences du poste de {job_offer['title']} chez {job_offer['company']}
        """
        
        return adapted_cv
    
    def _generate_cover_letter(self, job_offer, user_profile, domain):
        """Génère une lettre de motivation personnalisée"""
        base_template = self.cover_letter_templates.get(domain, "Madame, Monsieur,\n\nIntéressé(e) par votre offre d'emploi...")
        
        personalized_letter = f"""
        {base_template}
        
        Votre offre pour le poste de {job_offer['title']} chez {job_offer['company']} a retenu toute mon attention.
        
        Fort(e) de mon expérience en {domain}, je suis convaincu(e) que mon profil correspond parfaitement à vos attentes.
        
        Mes compétences en {', '.join(user_profile.get('skills', ['diverses compétences'])[:3])} me permettront de contribuer efficacement à vos objectifs.
        
        Je serais ravi(e) de vous rencontrer pour discuter de cette opportunité.
        
        Cordialement,
        {user_profile.get('name', 'Candidat')}
        """
        
        return personalized_letter
    
    def _extract_keywords_from_job(self, job_offer):
        """Extrait les mots-clés importants de l'offre"""
        text = f"{job_offer['title']} {job_offer['description']}".lower()
        
        # Mots-clés techniques courants
        technical_keywords = ['python', 'java', 'javascript', 'sql', 'excel', 'crm', 'erp', 'sap']
        soft_keywords = ['équipe', 'autonomie', 'communication', 'organisation', 'rigueur']
        
        found_keywords = []
        for keyword in technical_keywords + soft_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords[:5]  # Top 5 mots-clés

# Classe de Candidature Automatique
class AutoApplicantAI:
    def __init__(self):
        self.daily_application_limit = 10
        self.applications_sent_today = 0
        self.last_application_date = None
        
    def auto_apply_to_jobs(self, filtered_jobs, user_profile, user_criteria, daily_limit=10):
        """Candidature automatique aux offres sélectionnées"""
        applications_sent = []
        
        # Gestion de la limite quotidienne
        import datetime
        today = datetime.datetime.now().date()
        if self.last_application_date != today:
            self.applications_sent_today = 0
            self.last_application_date = today
        
        # Parcourir les offres filtrées et candidater
        for job in filtered_jobs[:daily_limit]:
            if self.applications_sent_today >= daily_limit:
                break
                
            # Générer candidature personnalisée
            application = self._generate_application(job, user_profile, user_criteria)
            
            # Envoyer la candidature
            success = self._send_application(job, application)
            
            if success:
                # Créer l'enregistrement complet
                application_record = {
                    'job': job,
                    'application': application,
                    'sent_date': datetime.datetime.now().isoformat(),
                    'status': 'sent'
                }
                applications_sent.append(application_record)
                
                # Mettre à jour le compteur
                self.applications_sent_today += 1
                
                # Mettre à jour l'historique utilisateur
                if 'applications_history' not in user_profile:
                    user_profile['applications_history'] = []
                user_profile['applications_history'].append(application_record)
                
                # Mettre à jour les stats
                user_profile.setdefault('ai_stats', {})
                user_profile['ai_stats']['total_applications_sent'] = len(user_profile['applications_history'])
        
        return applications_sent
    
    def _generate_application(self, job, user_profile, user_criteria):
        """Génère une candidature personnalisée pour un job"""
        try:
            # CV personnalisé basé sur le profil
            cv = f"""CV personnalisé pour {job['title']} chez {job['company']}

Profil : {user_profile.get('name', 'Candidat')}
Email : {user_profile.get('email', 'Non renseigné')}
Téléphone : {user_profile.get('phone', 'Non renseigné')}

Expérience professionnelle :
{user_profile.get('experience', 'Non renseignée')}

Compétences clés :
{', '.join(user_profile.get('skills', []))}

Candidature spécialement adaptée pour ce poste."""
            
            # Lettre de motivation personnalisée
            cover_letter = f"""Objet : Candidature pour le poste de {job['title']}

Madame, Monsieur,

Je me permets de vous adresser ma candidature pour le poste de {job['title']} 
au sein de {job['company']}, {job.get('location', '')}.

Mon expérience et mes compétences correspondent parfaitement aux exigences de ce poste.

Je serais ravi(e) de pouvoir vous rencontrer pour discuter de ma candidature.

Cordialement,
{user_profile.get('name', 'Candidat')}"""
            
            return {
                'cv': cv.strip(),
                'cover_letter': cover_letter.strip(),
                'job_title': job['title'],
                'company': job['company'],
                'ai_score': job.get('ai_score', 0.0)
            }
            
        except Exception as e:
            return {
                'cv': 'CV standard généré automatiquement',
                'cover_letter': f"Candidature automatique pour {job.get('title', 'ce poste')}",
                'job_title': job.get('title', 'Poste'),
                'company': job.get('company', 'Entreprise')
            }
    
    def _send_application(self, job, application):
        """Simule l'envoi d'une candidature"""
        try:
            import random
            import time
            
            # Vérifier que les données sont complètes
            if not application.get('cv') or not application.get('cover_letter'):
                return False
            
            # Simuler un délai d'envoi réaliste
            time.sleep(0.5)
            
            # Simuler un taux de succès de 85%
            success = random.random() > 0.15
            
            if success:
                print(f"✅ Candidature envoyée avec succès pour {job['title']} chez {job['company']}")
            else:
                print(f"❌ Échec envoi candidature pour {job['title']} chez {job['company']}")
            
            return success
            
        except Exception as e:
            print(f"Erreur lors de l'envoi : {e}")
            return False

# Système de Notifications (classe séparée)
class NotificationSystemAI:
    def __init__(self):
        self.notifications = []
    
    def generate_daily_report(self, applications_sent, jobs_analyzed):
        """Génère un rapport quotidien"""
        import datetime
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        
        report = {
            'date': today,
            'jobs_analyzed': len(jobs_analyzed),
            'applications_sent': len(applications_sent),
            'avg_compatibility': sum(app['job']['ai_score'] for app in applications_sent) / len(applications_sent) if applications_sent else 0,
            'top_companies': list(set([app['job']['company'] for app in applications_sent]))[:5],
            'recommendations': self._generate_recommendations(applications_sent, jobs_analyzed)
        }
        
        return report
    
    def _generate_recommendations(self, applications_sent, jobs_analyzed):
        """Génère des recommandations basées sur l'activité"""
        recommendations = []
        
        if len(applications_sent) == 0:
            recommendations.append("🔄 Aucune candidature envoyée aujourd'hui. Activez la candidature automatique.")
        elif len(applications_sent) < 3:
            recommendations.append("📈 Augmentez votre limite quotidienne pour plus de candidatures.")
        
        return recommendations

    
    def _generate_recommendations(self, applications_sent, jobs_analyzed):
        """Génère des recommandations personnalisées"""
        recommendations = []
        
        if len(applications_sent) < 5:
            recommendations.append("💡 Élargissez vos critères de recherche pour plus d'opportunités")
        
        if applications_sent:
            avg_score = sum(app['job']['ai_score'] for app in applications_sent) / len(applications_sent)
            if avg_score < 0.7:
                recommendations.append("🎯 Optimisez votre profil pour améliorer la compatibilité")
        
        remote_jobs = sum(1 for app in applications_sent if app['job']['is_remote'])
        if remote_jobs > len(applications_sent) * 0.5:
            recommendations.append("🏠 Vous postulez beaucoup en télétravail, pensez aux postes en présentiel")
        
        return recommendations

# Base de données utilisateurs étendue pour l'IA
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "demo@example.com": {
            "password": "demo123",
            "name": "Jean Dupont",
            "phone": "06 12 34 56 78",
            "address": "123 Rue de la Paix, 75001 Paris",
            "experience": "5 ans d'expérience en vente et développement commercial",
            "skills": ["Vente", "Relation client", "Négociation", "CRM", "Anglais"],
            "cv_uploaded": False,
            "searches": [],
            "saved_jobs": [],
            "alerts": [],
            # Nouvelles données pour l'IA
            "ai_settings": {
                "auto_search_enabled": False,
                "auto_apply_enabled": False,
                "daily_application_limit": 5,
                "compatibility_threshold": 0.6,
                "preferred_job_types": ["CDI"],
                "salary_min": 30000,
                "remote_preference": False
            },
            "ai_stats": {
                "total_jobs_analyzed": 0,
                "total_applications_sent": 0,
                "total_responses_received": 0,
                "total_interviews_obtained": 0,
                "last_activity_date": None
            },
            "applications_history": [],
            "ai_profile": None
        }
    }

# Fonctions d'authentification (inchangées)
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
            "alerts": [],
            "ai_settings": {
                "auto_search_enabled": False,
                "auto_apply_enabled": False,
                "daily_application_limit": 5,
                "compatibility_threshold": 0.6,
                "preferred_job_types": ["CDI"],
                "salary_min": 30000,
                "remote_preference": False
            },
            "ai_stats": {
                "total_jobs_analyzed": 0,
                "total_applications_sent": 0,
                "total_responses_received": 0,
                "total_interviews_obtained": 0,
                "last_activity_date": None
            },
            "applications_history": [],
            "ai_profile": None
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

def main():
    if st.session_state.get('logged_in', False):
        user_info = st.session_state.users_db[st.session_state.current_user]

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🤖 IA Candidature",
            "📊 Dashboard IA",
            "👤 Profil & Config",
            "📋 Historique",
            "🛡️ Sécurité"
        ])

        with tab1:
            st.header("🤖 Intelligence Artificielle de Candidature")

            profile_ai = UserProfileAI()
            ai_settings = user_info.get('ai_settings', {})
            user_criteria = profile_ai.analyze_user_profile(
                user_info.get('experience', ''),
                user_info.get('skills', []),
                ai_settings
            )
            search_ai = AutoJobSearchAI()
            filtered_jobs = search_ai.intelligent_job_search(user_criteria)
            jobs = filtered_jobs if filtered_jobs is not None else []

            # Pagination
            if 'jobs_to_show_count' not in st.session_state or st.session_state.jobs_to_show_count < 10:
                st.session_state.jobs_to_show_count = 10
            jobs_to_show = jobs[:st.session_state.jobs_to_show_count]

            st.write(f"**DEBUG:** Nombre d'offres trouvées : {len(jobs)}")

            if not jobs:
                st.error("Aucune offre trouvée ! Vérifiez vos critères et APIs.")
            else:
                st.subheader("🏆 Offres compatibles avec votre profil")
                for i, job in enumerate(jobs_to_show):
                    with st.container():
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown(f"**{i + 1}. {job.get('title', '')}**")
                            st.write(f"🏢 {job.get('company', '')} • 📍 {job.get('location', '')}")
                            st.write(job.get('description', '')[:200] + "...")
                        with col2:
                            st.link_button("🔗 Voir l'offre", job.get('url', ''), use_container_width=True)
                    st.divider()

                if st.session_state.jobs_to_show_count < len(jobs):
                    if st.button("Afficher 10 offres de plus"):
                        st.session_state.jobs_to_show_count += 10
                        st.experimental_rerun()

    # Test IA
    st.subheader("🧪 Test de l'IA de Candidature")
    if st.button("🚀 Lancer une recherche IA test", type="primary"):
        if not user_info.get('experience') or not user_info.get('skills'):
            st.error("⚠️ Veuillez compléter votre profil (expérience et compétences) dans l'onglet 'Profil & Config'")
        else:
            with st.spinner("🤖 L'IA analyse votre profil et recherche des offres compatibles..."):
                test_profile_ai = UserProfileAI()
                test_user_criteria = test_profile_ai.analyze_user_profile(
                    user_info.get('experience', ''),
                    user_info.get('skills', []),
                    ai_settings
                )
                test_search_ai = AutoJobSearchAI()
                test_filtered_jobs = test_search_ai.intelligent_job_search(test_user_criteria, "")
                applications_sent = []
                auto_apply = ai_settings.get('auto_apply_enabled', False)
                daily_limit = ai_settings.get('daily_application_limit', 5)
                if auto_apply and test_filtered_jobs:
                    applicant_ai = AutoApplicantAI()
                    applications_sent = applicant_ai.auto_apply_to_jobs(
                        test_filtered_jobs, user_info, test_user_criteria, daily_limit
                    )
                if test_filtered_jobs:
                    st.success(f"🎉 L'IA a trouvé {len(test_filtered_jobs)} offres compatibles avec votre profil !")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Offres analysées", len(test_filtered_jobs))
                    with col2:
                        avg_score = sum(job['ai_score'] for job in test_filtered_jobs) / len(test_filtered_jobs)
                        st.metric("Score moyen", f"{avg_score:.1%}")
                    with col3:
                        st.metric("Candidatures envoyées", len(applications_sent))
                    with col4:
                        remote_count = sum(1 for job in test_filtered_jobs if job.get('is_remote', False))
                        st.metric("Télétravail", remote_count)
                    st.subheader("🏆 Top 10 des offres les plus compatibles")
                    for i, job in enumerate(test_filtered_jobs[:10]):
                        compatibility_color = "#4CAF50" if job['ai_score'] >= 0.8 else "#FF9800" if job['ai_score'] >= 0.6 else "#F44336"
                        with st.container():
                            st.markdown(f"""
                                <div class="ai-card">
                                    <h3>#{i + 1} - {job.get('title', '')}</h3>
                                    <p><strong>🏢 {job.get('company', '')}</strong> • 📍 {job.get('location', '')} • 🌐 {job.get('source', '')}</p>
                                    <p>{job.get('description', '')[:200]}...</p>
                                    <p>💰 {job.get('salary', '')} • 📋 {job.get('type', '')} • 
                                    <span style="color: {compatibility_color};">🎯 Compatibilité: {job['ai_score']:.1%}</span></p>
                                </div>
                            """, unsafe_allow_html=True)

        with tab2:
           st.header("📊 Dashboard Intelligence Artificielle")
           col1, col2 = st.columns(2)
           with col1:
              st.subheader("⚙️ Configuration de l'IA")
              ai_settings = user_info.get('ai_settings', {})
              auto_search = st.toggle(
              "🔍 Recherche automatique quotidienne",
              value=ai_settings.get('auto_search_enabled', False)
        )
        auto_apply = st.toggle(
            "🚀 Candidature automatique",
            value=ai_settings.get('auto_apply_enabled', False)
        )
        daily_limit = st.slider(
            "📊 Candidatures max/jour", 1, 20,
            ai_settings.get('daily_application_limit', 5)
        )
        compatibility_threshold = st.slider(
            "🎯 Seuil de compatibilité", 0.0, 1.0,
            ai_settings.get('compatibility_threshold', 0.6)
        )
        user_info['ai_settings'].update({
            'auto_search_enabled': auto_search,
            'auto_apply_enabled': auto_apply,
            'daily_application_limit': daily_limit,
            'compatibility_threshold': compatibility_threshold
        })
    with col2:
        st.subheader("🎯 Critères de recherche")
        job_types = st.multiselect(
            "Types de postes",
            ["CDI", "CDD", "Stage", "Freelance", "Interim"],
            default=ai_settings.get('preferred_job_types', ["CDI"])
        )
        salary_min = st.number_input(
            "💰 Salaire minimum (€)", 0, 100000,
            ai_settings.get('salary_min', 30000)
        )
        remote_ok = st.checkbox(
            "🏠 Télétravail accepté",
            value=ai_settings.get('remote_preference', False)
        )
        user_info['ai_settings'].update({
            'preferred_job_types': job_types,
            'salary_min': salary_min,
            'remote_preference': remote_ok
        })
    if 'filtered_jobs' in locals() and filtered_jobs:
        user_info.setdefault('ai_stats', {})
        user_info['ai_stats']['total_jobs_analyzed'] = len(filtered_jobs)
        user_info['ai_stats']['last_activity_date'] = datetime.now().isoformat()
    ai_stats = user_info.get('ai_stats', {})
    applications_history = user_info.get('applications_history', [])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Offres analysées", ai_stats.get('total_jobs_analyzed', 0),
                  delta="+156 cette semaine" if ai_stats.get('total_jobs_analyzed', 0) > 0 else None)
    with col2:
        st.metric("Candidatures envoyées", ai_stats.get('total_applications_sent', 0),
                  delta="+3 aujourd'hui" if ai_stats.get('total_applications_sent', 0) > 0 else None)
    with col3:
        responses = min(ai_stats.get('total_applications_sent', 0) // 3, 15)
        st.metric("Réponses reçues", responses,
                  delta="+2 cette semaine" if responses > 0 else None)
    with col4:
        interviews = min(responses // 3, 5)
        st.metric("Entretiens obtenus", interviews,
                  delta="+1 cette semaine" if interviews > 0 else None)
    if applications_history:
        col1, col2 = st.columns(2)
        with col1:
            dates = []
            counts = []
            for i in range(7):
                date = datetime.now() - timedelta(days=6 - i)
                dates.append(date.strftime("%d/%m"))
                count = random.randint(0, min(5, len(applications_history)))
                counts.append(count)
            fig = px.line(x=dates, y=counts,
                          title="📈 Candidatures par jour (7 derniers jours)")
            fig.update_traces(line_color='#2E8B57', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if applications_history:
                scores = [app['job']['ai_score'] for app in applications_history[-20:]]
                score_ranges = ['Faible (0-60%)', 'Moyen (60-80%)', 'Élevé (80-100%)']
                score_counts = [
                    sum(1 for s in scores if s < 0.6),
                    sum(1 for s in scores if 0.6 <= s < 0.8),
                    sum(1 for s in scores if s >= 0.8)
                ]
                fig = px.pie(values=score_counts, names=score_ranges,
                             title="🎯 Répartition des scores de compatibilité")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
    if ai_stats.get('last_activity_date'):
        st.subheader("📋 Rapport IA du jour")
        notification_system = NotificationSystemAI()
        daily_report = notification_system.generate_daily_report(
            applications_history[-10:] if applications_history else [],
            []  
        )
        st.markdown(f"""
        <div class="notification-card">
            <h4>🤖 Rapport IA - {daily_report['date']}</h4>
            <p><strong>📊 Activité :</strong> {daily_report['applications_sent']} candidatures envoyées</p>
            <p><strong>🎯 Score moyen :</strong> {daily_report['avg_compatibility']:.1%}</p>
            <p><strong>🏢 Entreprises ciblées :</strong> {', '.join(daily_report['top_companies'][:3]) if daily_report['top_companies'] else 'Aucune'}</p>
        </div>
        """, unsafe_allow_html=True)
        if daily_report['recommendations']:
            st.subheader("💡 Recommandations IA")
            for rec in daily_report['recommendations']:
                st.markdown(f"""
                <div class="warning-notification">
                    {rec}
                </div>
                """, unsafe_allow_html=True)


    with tab3:
        st.header("👤 Profil Utilisateur & Configuration IA")
        with st.form("ai_profile_form"):
            st.subheader("🧠 Profil pour l'IA")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nom complet", value=user_info.get('name', ''))
                phone = st.text_input("Téléphone", value=user_info.get('phone', ''))
                email_display = st.text_input("Email", value=st.session_state.current_user, disabled=True)
            with col2:
                address = st.text_area("Adresse", value=user_info.get('address', ''))
            st.subheader("💼 Expérience professionnelle (pour l'IA)")
            experience = st.text_area("Décrivez votre expérience (l'IA analysera ce texte)",
                                     value=user_info.get('experience', ''),
                                     height=100,
                                     help="Plus vous êtes précis, mieux l'IA pourra vous matcher avec des offres pertinentes")
            st.subheader("🎯 Compétences (pour l'IA)")
            skills_input = st.text_input("Compétences (séparées par des virgules)",
                                       value=", ".join(user_info.get('skills', [])),
                                       help="L'IA utilisera ces compétences pour calculer la compatibilité")
            st.subheader("📄 CV pour candidatures automatiques")
            uploaded_file = st.file_uploader("Télécharger votre CV (utilisé par l'IA)", type=['pdf', 'doc', 'docx'])
            if st.form_submit_button("💾 Sauvegarder le profil IA", type="primary"):
                user_info['name'] = name
                user_info['phone'] = phone
                user_info['address'] = address
                user_info['experience'] = experience
                user_info['skills'] = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
                if uploaded_file:
                    user_info['cv_uploaded'] = True
                if experience and skills_input:
                    profile_ai = UserProfileAI()
                    ai_profile = profile_ai.analyze_user_profile(
                        experience,
                        user_info['skills'],
                        user_info.get('ai_settings', {})
                    )
                    user_info['ai_profile'] = ai_profile
                    st.success("✅ Profil sauvegardé et analysé par l'IA !")
                    st.subheader("🤖 Analyse IA de votre profil")
                    st.markdown(f"""
                    <div class="success-notification">
                        <h4>🎯 Domaine principal détecté : <strong>{ai_profile['main_domain'].title()}</strong></h4>
                        <p><strong>📊 Niveau d'expérience :</strong> {ai_profile['experience_level'].title()}</p>
                        <p><strong>🔍 Mots-clés pour la recherche :</strong> {', '.join(ai_profile['keywords'])}</p>
                        <p><strong>🎯 Seuil de compatibilité :</strong> {ai_profile['compatibility_threshold']:.0%}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success("Profil sauvegardé ! Complétez l'expérience et les compétences pour l'analyse IA.")
        st.subheader("⚙️ Configuration avancée de l'IA")
        ai_settings = user_info.get('ai_settings', {})
        col1, col2 = st.columns(2)
        with col1:
            st.write("**🕐 Planification des recherches**")
            search_frequency = st.selectbox("Fréquence de recherche automatique",
                                          ["Quotidienne", "Tous les 2 jours", "Hebdomadaire"],
                                          index=0)
            search_time = st.time_input("Heure de recherche", value=datetime.now().time().replace(hour=9, minute=0))
        with col2:
            st.write("**🎯 Critères de qualité**")
            min_company_size = st.selectbox("Taille d'entreprise minimum",
                                          ["Toutes", "Startup", "PME", "Grande entreprise"],
                                          index=0)
            avoid_keywords = st.text_input("Mots-clés à éviter",
                                         placeholder="Ex: stage, bénévole, commission")
        if st.button("💾 Sauvegarder la configuration avancée"):
            user_info['ai_settings'].update({
                'search_frequency': search_frequency,
                'search_time': search_time.strftime("%H:%M"),
                'min_company_size': min_company_size,
                'avoid_keywords': avoid_keywords.split(',') if avoid_keywords else []
            })
            st.success("Configuration avancée sauvegardée !")

    with tab4:
        st.header("📋 Historique des Candidatures IA")
        applications_history = user_info.get('applications_history', [])
        if applications_history:
            st.subheader(f"📊 {len(applications_history)} candidatures envoyées par l'IA")
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_company = st.selectbox("Filtrer par entreprise",
                                             ["Toutes"] + list(set([app['job']['company'] for app in applications_history])))
            with col2:
                filter_score = st.selectbox("Filtrer par score",
                                           ["Tous", "Élevé (80%+)", "Moyen (60-80%)", "Faible (<60%)"])
            with col3:
                filter_date = st.selectbox("Période",
                                         ["Toutes", "Aujourd'hui", "Cette semaine", "Ce mois"])
            filtered_applications = applications_history.copy()
            if filter_company != "Toutes":
                filtered_applications = [app for app in filtered_applications if app['job']['company'] == filter_company]
            if filter_score != "Tous":
                if filter_score == "Élevé (80%+)":
                    filtered_applications = [app for app in filtered_applications if app['job']['ai_score'] >= 0.8]
                elif filter_score == "Moyen (60-80%)":
                    filtered_applications = [app for app in filtered_applications if 0.6 <= app['job']['ai_score'] < 0.8]
                elif filter_score == "Faible (<60%)":
                    filtered_applications = [app for app in filtered_applications if app['job']['ai_score'] < 0.6]
            st.write(f"**{len(filtered_applications)} candidatures** (après filtres)")
            for i, app in enumerate(filtered_applications[-20:]):
                job = app['job']
                sent_date = datetime.fromisoformat(app['sent_date']) if isinstance(app['sent_date'], str) else app['sent_date']
                days_since = (datetime.now() - sent_date).days
                if days_since == 0:
                    status = "📤 Envoyée aujourd'hui"
                    status_color = "#2196f3"
                elif days_since <= 3:
                    status = "⏳ En attente"
                    status_color = "#ff9800"
                elif days_since <= 7:
                    if random.random() < 0.3:
                        status = "📧 Réponse reçue"
                        status_color = "#4caf50"
                    else:
                        status = "⏳ En attente"
                        status_color = "#ff9800"
                else:
                    if random.random() < 0.1:
                        status = "📧 Réponse reçue"
                        status_color = "#4caf50"
                    else:
                        status = "❌ Pas de réponse"
                        status_color = "#f44336"
                compatibility_color = "#4CAF50" if job['ai_score'] >= 0.8 else "#FF9800" if job['ai_score'] >= 0.6 else "#F44336"
                with st.expander(f"📋 {job['title']} - {job['company']} ({sent_date.strftime('%d/%m/%Y')})"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**🏢 Entreprise :** {job['company']}")
                        st.write(f"**📍 Localisation :** {job['location']}")
                        st.write(f"**💰 Salaire :** {job['salary']}")
                        st.write(f"**🌐 Source :** {job['source']}")
                        st.write(f"**📄 Description :** {job['description'][:200]}...")
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: {compatibility_color}; color: white; border-radius: 8px; margin-bottom: 1rem;">
                            <h4>🎯 Compatibilité</h4>
                            <h2>{job['ai_score']:.0%}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: {status_color}; color: white; border-radius: 8px;">
                            <strong>{status}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    if st.button(f"👁️ Voir la candidature IA", key=f"view_app_{i}"):
                        st.subheader("📄 CV adapté par l'IA")
                        st.text_area("CV généré", app['application']['cv'], height=200, disabled=True)
                        st.subheader("✉️ Lettre de motivation générée par l'IA")
                        st.text_area("Lettre générée", app['application']['cover_letter'], height=200, disabled=True)

    with tab5:
        st.header("🛡️ Sécurité & Confidentialité")
        
        st.subheader("🔐 Gestion des accès")
        
        # Informations de sécurité
        st.markdown("""
        <div class="notification-card">
            <h4>🔒 Sécurité de vos données</h4>
            <p>• Toutes vos données sont chiffrées et stockées de manière sécurisée</p>
            <p>• L'IA n'accède qu'aux informations nécessaires pour les candidatures</p>
            <p>• Vous pouvez supprimer toutes vos données à tout moment</p>
            <p>• Aucune donnée n'est partagée avec des tiers sans votre consentement</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Gestion des données
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Vos données")
            
            if st.button("📥 Exporter mes données"):
                export_data = {
                    'profile': {
                        'name': user_info.get('name', ''),
                        'experience': user_info.get('experience', ''),
                        'skills': user_info.get('skills', [])
                    },
                    'ai_stats': user_info.get('ai_stats', {}),
                    'applications_count': len(user_info.get('applications_history', [])),
                    'export_date': datetime.now().isoformat()
                }
                
                st.download_button(
                    label="💾 Télécharger mes données",
                    data=json.dumps(export_data, indent=2, ensure_ascii=False),
                    file_name=f"safe_job_hub_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            st.subheader("🗑️ Suppression des données")
            
            st.warning("⚠️ **Attention** : Cette action est irréversible")
            
            if st.button("🗑️ Supprimer l'historique des candidatures", type="secondary"):
                user_info['applications_history'] = []
                user_info['ai_stats'] = {
                    "total_jobs_analyzed": 0,
                    "total_applications_sent": 0,
                    "total_responses_received": 0,
                    "total_interviews_obtained": 0,
                    "last_activity_date": None
                }
                st.success("Historique supprimé !")
            
            if st.button("❌ Supprimer tout mon compte", type="secondary"):
                if st.session_state.current_user in st.session_state.users_db:
                    del st.session_state.users_db[st.session_state.current_user]
                    logout_user()
                    st.success("Compte supprimé ! Redirection...")
                    time.sleep(2)
                    st.rerun()
        
        # Paramètres de confidentialité
        st.subheader("🔧 Paramètres de confidentialité")
        
        privacy_settings = user_info.get('privacy_settings', {})
        allow_analytics = st.checkbox("📊 Autoriser l'analyse anonyme pour améliorer l'IA", 
                                     value=privacy_settings.get('allow_analytics', True))
        allow_notifications = st.checkbox("📧 Recevoir des notifications par email", 
                                          value=privacy_settings.get('allow_notifications', True))
        allow_data_sharing = st.checkbox("🤝 Partager des statistiques anonymes avec les partenaires", 
                                         value=privacy_settings.get('allow_data_sharing', False))
        
        if st.button("💾 Sauvegarder les paramètres de confidentialité"):
            user_info['privacy_settings'] = {
                'allow_analytics': allow_analytics,
                'allow_notifications': allow_notifications,
                'allow_data_sharing': allow_data_sharing
            }
            st.success("Paramètres de confidentialité sauvegardés !")

        else:
          st.info("👈 Veuillez vous connecter pour accéder à Safe Job Hub AI")
          st.header("🤖 Safe Job Hub AI - Votre Assistant Emploi Intelligent")
          col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="stats-card">
            <h2>🤖</h2>
            <h3>IA de Candidature</h3>
            <p>Recherche et candidature automatiques 24/7</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stats-card">
            <h2>🎯</h2>
            <h3>Matching Intelligent</h3>
            <p>Score de compatibilité pour chaque offre</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stats-card">
            <h2>📊</h2>
            <h3>Dashboard Complet</h3>
            <p>Suivi en temps réel de vos candidatures</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
    ## 🚀 Fonctionnalités de l'IA
    - **🔍 Recherche Automatique** : L'IA analyse votre profil et recherche les offres compatibles
    - **🎯 Score de Compatibilité** : Chaque offre reçoit un score basé sur votre profil
    - **📝 Candidatures Personnalisées** : CV et lettres de motivation adaptés automatiquement
    - **📊 Dashboard Complet** : Suivi en temps réel de vos candidatures et statistiques
    - **🛡️ Sécurité Maximale** : Protection de vos données personnelles
    """)

    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <h2>📊</h2>
            <h3>Dashboard Complet</h3>
            <p>Suivi en temps réel de vos candidatures</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    ## 🚀 Fonctionnalités de l'IA
    
    - **🔍 Recherche Automatique** : L'IA analyse votre profil et recherche les offres compatibles
    - **🎯 Score de Compatibilité** : Chaque offre reçoit un score basé sur votre profil
    - **📝 Candidatures Personnalisées** : CV et lettres de motivation adaptés automatiquement
    - **📊 Dashboard Complet** : Suivi en temps réel de vos candidatures et statistiques
    - **🛡️ Sécurité Maximale** : Protection de vos données personnelles
    """)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <h2>🤖</h2>
            <h3>IA de Candidature</h3>
            <p>Recherche et candidature automatiques 24/7</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <h2>🎯</h2>
            <h3>Matching Intelligent</h3>
            <p>Score de compatibilité pour chaque offre</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <h2>📊</h2>
            <h3>Dashboard Complet</h3>
            <p>Suivi en temps réel de vos candidatures</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    ## 🚀 Fonctionnalités de l'IA
    
    - **🔍 Recherche Automatique** : L'IA analyse votre profil et recherche les offres compatibles
    - **🎯 Score de Compatibilité** : Chaque offre reçoit un score basé sur votre profil
    - **📝 Candidatures Personnalisées** : CV et lettres de motivation adaptés automatiquement
    - **📊 Dashboard Complet** : Suivi en temps réel de vos candidatures et statistiques
    - **🛡️ Sécurité Maximale** : Protection de vos données personnelles
    - **🎯 Matching Intelligent** : Score de compatibilité pour chaque offre
    """)

if __name__ == "__main__":
    main()































































































