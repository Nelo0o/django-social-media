from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from tweets.models import Tweet, Hashtag, Comment, Like
from follows.models import Follow
import random
from django.utils import timezone
from datetime import timedelta
import requests
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io
import os


class Command(BaseCommand):
    help = 'Quick populate database with predefined users and tweets'
    
    def create_avatar_for_user(self, user_profile):
        """Crée un avatar pour l'utilisateur en utilisant différentes méthodes"""
        try:
            # Méthode 1: Télécharger depuis Robohash (avatars robots colorés)
            username = user_profile.user.username
            robohash_url = f"https://robohash.org/{username}.png?size=200x200&set=set1"
            
            response = requests.get(robohash_url, timeout=10)
            if response.status_code == 200:
                avatar_content = ContentFile(response.content)
                avatar_filename = f"{username}_avatar.png"
                user_profile.avatar.save(avatar_filename, avatar_content, save=True)
                return True
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Robohash failed for {username}: {e}"))
        
        try:
            # Méthode 2: Créer un avatar avec initiales si Robohash échoue
            return self.create_initials_avatar(user_profile)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Avatar creation failed for {username}: {e}"))
            return False
    
    def create_initials_avatar(self, user_profile):
        """Crée un avatar avec les initiales de l'utilisateur"""
        # Couleurs de fond variées inspirées du thème violet
        colors = [
            '#6366f1',  # indigo
            '#8b5cf6',  # violet
            '#a855f7',  # purple
            '#d946ef',  # fuchsia
            '#ec4899',  # pink
            '#f59e0b',  # amber
            '#10b981',  # emerald
            '#3b82f6',  # blue
        ]
        
        # Obtenir les initiales
        first_name = user_profile.user.first_name or user_profile.user.username[0]
        last_name = user_profile.user.last_name or user_profile.user.username[1:2]
        initials = (first_name[0] + last_name[0]).upper() if last_name else first_name[0].upper()
        
        # Choisir une couleur basée sur le username pour la cohérence
        color_index = hash(user_profile.user.username) % len(colors)
        bg_color = colors[color_index]
        
        # Créer l'image
        size = 200
        image = Image.new('RGB', (size, size), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Essayer d'utiliser une police système, sinon utiliser la police par défaut
        try:
            # Taille de police adaptée
            font_size = int(size * 0.4)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Calculer la position du texte pour le centrer
        if font:
            bbox = draw.textbbox((0, 0), initials, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(initials) * 20
            text_height = 30
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        # Dessiner le texte en blanc
        draw.text((x, y), initials, fill='white', font=font)
        
        # Sauvegarder l'image
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        
        avatar_content = ContentFile(img_io.getvalue())
        avatar_filename = f"{user_profile.user.username}_initials.png"
        user_profile.avatar.save(avatar_filename, avatar_content, save=True)
        
        return True

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Tweet.objects.all().delete()
            Follow.objects.all().delete()
            UserProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            Hashtag.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared successfully'))

        # Données prédéfinies pour les utilisateurs
        users_data = [
            {
                'username': 'alice_dev',
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Martin',
                'bio': 'Développeuse Python passionnée. J\'adore Django et l\'IA.',
                'city': 'Paris'
            },
            {
                'username': 'bob_designer',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Dupont',
                'bio': 'Designer UX/UI. Créateur d\'expériences numériques.',
                'city': 'Lyon'
            },
            {
                'username': 'charlie_data',
                'email': 'charlie@example.com',
                'first_name': 'Charlie',
                'last_name': 'Rousseau',
                'bio': 'Data Scientist. Passionné par le machine learning.',
                'city': 'Marseille'
            },
            {
                'username': 'diana_pm',
                'email': 'diana@example.com',
                'first_name': 'Diana',
                'last_name': 'Moreau',
                'bio': 'Product Manager. J\'aime transformer les idées en produits.',
                'city': 'Toulouse'
            },
            {
                'username': 'eve_frontend',
                'email': 'eve@example.com',
                'first_name': 'Eve',
                'last_name': 'Bernard',
                'bio': 'Développeuse Frontend. React et Vue.js sont mes amis.',
                'city': 'Nice'
            },
            {
                'username': 'frank_backend',
                'email': 'frank@example.com',
                'first_name': 'Frank',
                'last_name': 'Petit',
                'bio': 'Développeur Backend. APIs et microservices.',
                'city': 'Bordeaux'
            },
            {
                'username': 'grace_devops',
                'email': 'grace@example.com',
                'first_name': 'Grace',
                'last_name': 'Robert',
                'bio': 'DevOps Engineer. Docker, Kubernetes et CI/CD.',
                'city': 'Nantes'
            },
            {
                'username': 'henry_mobile',
                'email': 'henry@example.com',
                'first_name': 'Henry',
                'last_name': 'Richard',
                'bio': 'Développeur Mobile. Flutter et React Native.',
                'city': 'Strasbourg'
            },
            {
                'username': 'iris_security',
                'email': 'iris@example.com',
                'first_name': 'Iris',
                'last_name': 'Dubois',
                'bio': 'Expert en cybersécurité. Protection des données.',
                'city': 'Lille'
            },
            {
                'username': 'jack_fullstack',
                'email': 'jack@example.com',
                'first_name': 'Jack',
                'last_name': 'Leroy',
                'bio': 'Développeur Full-Stack. De la base de données à l\'interface.',
                'city': 'Montpellier'
            }
        ]

        # Tweets prédéfinis pour chaque utilisateur
        tweets_data = {
            'alice_dev': [
                "Nouveau projet Django en cours ! #django #python #webdev",
                "Les migrations Django peuvent parfois être délicates... #django #database #tips",
                "Café du matin et code Python ☕ #python #coding #morning",
                "Découverte d'une nouvelle librairie Python aujourd'hui #python #learning #opensource",
                "Weekend de code et de détente 🚀 #coding #weekend #productivity"
            ],
            'bob_designer': [
                "Nouveau design system en cours de création #design #ux #ui",
                "L'importance des couleurs dans l'UX #colors #ux #design",
                "Figma vs Sketch : mon retour d'expérience #figma #sketch #tools",
                "Inspiration design du jour ✨ #inspiration #creativity #design",
                "Prototype terminé ! Place aux tests utilisateurs #prototype #testing #ux"
            ],
            'charlie_data': [
                "Analyse de données passionnante aujourd'hui #datascience #analytics #python",
                "Machine Learning avec scikit-learn #ml #python #ai",
                "Visualisation de données avec matplotlib #dataviz #python #charts",
                "Nettoyage de données : 80% du travail d'un data scientist #datascience #cleaning #reality",
                "Nouveau modèle déployé en production 🎯 #ml #deployment #success"
            ],
            'diana_pm': [
                "Roadmap produit mise à jour #product #roadmap #planning",
                "Retour client très positif sur la dernière release #feedback #product #success",
                "Sprint planning de la semaine #agile #scrum #planning",
                "L'importance de l'écoute client #customer #feedback #product",
                "Nouvelle fonctionnalité en cours de spécification #feature #specs #product"
            ],
            'eve_frontend': [
                "React Hooks : une révolution pour le développement #react #hooks #javascript",
                "CSS Grid vs Flexbox : quand utiliser quoi ? #css #layout #frontend",
                "Performance web : optimisation en cours #performance #web #optimization",
                "Nouveau composant réutilisable créé #components #react #reusability",
                "Tests unitaires pour le frontend #testing #jest #frontend"
            ],
            'frank_backend': [
                "API REST bien documentée = développeurs heureux #api #rest #documentation",
                "Optimisation de base de données en cours #database #optimization #performance",
                "Microservices : avantages et inconvénients #microservices #architecture #backend",
                "Nouvelle route API déployée #api #deployment #backend",
                "Gestion des erreurs : crucial pour une bonne API #errorhandling #api #bestpractices"
            ],
            'grace_devops': [
                "Pipeline CI/CD optimisé ! #cicd #devops #automation",
                "Docker containers : isolation et portabilité #docker #containers #devops",
                "Kubernetes en production : retour d'expérience #kubernetes #production #devops",
                "Monitoring et alertes configurés #monitoring #alerts #devops",
                "Infrastructure as Code avec Terraform #iac #terraform #devops"
            ],
            'henry_mobile': [
                "Flutter : un framework, deux plateformes #flutter #mobile #crossplatform",
                "Optimisation des performances mobiles #mobile #performance #optimization",
                "Design responsive pour mobile #responsive #mobile #design",
                "Nouvelle app mobile en cours de développement #mobile #app #development",
                "Tests sur différents devices #testing #mobile #devices"
            ],
            'iris_security': [
                "Sécurité des APIs : bonnes pratiques #security #api #cybersecurity",
                "Authentification et autorisation #auth #security #backend",
                "Chiffrement des données sensibles #encryption #security #data",
                "Audit de sécurité terminé #audit #security #assessment",
                "Formation équipe sur les bonnes pratiques sécurité #training #security #team"
            ],
            'jack_fullstack': [
                "Full-stack : de la base de données à l'interface #fullstack #development #web",
                "Intégration frontend-backend réussie #integration #frontend #backend",
                "Architecture application complète #architecture #fullstack #design",
                "Déploiement complet de l'application #deployment #fullstack #production",
                "Code review : qualité et bonnes pratiques #codereview #quality #bestpractices"
            ]
        }

        created_users = []

        # Créer les utilisateurs
        for user_data in users_data:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password='password123',
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            profile = user.profile
            profile.bio = user_data['bio']
            profile.city = user_data['city']
            profile.save()
            
            # Créer un avatar pour l'utilisateur
            if self.create_avatar_for_user(profile):
                self.stdout.write(f'✅ Created user with avatar: {user_data["username"]}')
            else:
                self.stdout.write(f'⚠️  Created user without avatar: {user_data["username"]}')
            
            created_users.append(profile)

        # Créer des relations de suivi logiques
        follow_relationships = [
            ('alice_dev', ['bob_designer', 'charlie_data', 'eve_frontend', 'frank_backend']),
            ('bob_designer', ['alice_dev', 'eve_frontend', 'diana_pm', 'henry_mobile']),
            ('charlie_data', ['alice_dev', 'frank_backend', 'grace_devops', 'iris_security']),
            ('diana_pm', ['bob_designer', 'alice_dev', 'charlie_data', 'jack_fullstack']),
            ('eve_frontend', ['alice_dev', 'bob_designer', 'henry_mobile', 'jack_fullstack']),
            ('frank_backend', ['alice_dev', 'charlie_data', 'grace_devops', 'iris_security']),
            ('grace_devops', ['frank_backend', 'charlie_data', 'iris_security', 'jack_fullstack']),
            ('henry_mobile', ['bob_designer', 'eve_frontend', 'diana_pm', 'jack_fullstack']),
            ('iris_security', ['frank_backend', 'grace_devops', 'charlie_data', 'alice_dev']),
            ('jack_fullstack', ['alice_dev', 'eve_frontend', 'frank_backend', 'grace_devops'])
        ]

        for follower_username, following_usernames in follow_relationships:
            follower = UserProfile.objects.get(user__username=follower_username)
            for following_username in following_usernames:
                followed = UserProfile.objects.get(user__username=following_username)
                Follow.objects.get_or_create(
                    follower=follower,
                    followed=followed
                )

        # Créer les tweets
        for profile in created_users:
            username = profile.user.username
            if username in tweets_data:
                for i, content in enumerate(tweets_data[username]):
                    # Créer des tweets avec des dates différentes
                    days_ago = random.randint(0, 15)
                    hours_ago = random.randint(0, 23)
                    
                    created_at = timezone.now() - timedelta(
                        days=days_ago,
                        hours=hours_ago,
                        minutes=random.randint(0, 59)
                    )
                    
                    tweet = Tweet.objects.create(
                        author=profile,
                        content=content,
                        created_at=created_at
                    )
                    
                    self.stdout.write(f'Created tweet for {username}: {content[:50]}...')

        # Créer des likes et commentaires organiques
        self.stdout.write('Creating organic likes and comments...')
        
        all_tweets = Tweet.objects.all()
        all_profiles = list(created_users)
        
        # Commentaires spécifiques pour le contexte professionnel
        professional_comments = [
            "Excellente approche ! 👍",
            "Merci pour ce retour d'expérience",
            "Très instructif, j'ai appris quelque chose",
            "Bonne pratique à retenir",
            "Je suis d'accord avec cette vision",
            "Intéressant point de vue",
            "Merci pour le partage",
            "Sage conseil ! 💡",
            "J'ai eu une expérience similaire",
            "Très pertinent",
            "Continue comme ça !",
            "Bonne question, j'y réfléchis aussi",
            "Merci pour ces insights",
            "Parfaitement résumé",
            "J'adore cette approche"
        ]
        
        likes_created = 0
        comments_created = 0
        
        # Créer des interactions logiques entre collègues
        for tweet in all_tweets:
            author_username = tweet.author.user.username
            
            # Les développeurs s'entraident plus
            dev_users = ['alice_dev', 'eve_frontend', 'frank_backend', 'henry_mobile', 'jack_fullstack']
            tech_users = ['charlie_data', 'grace_devops', 'iris_security']
            creative_users = ['bob_designer', 'diana_pm']
            
            # Déterminer les groupes d'intérêt
            if author_username in dev_users:
                interested_users = dev_users + tech_users
            elif author_username in tech_users:
                interested_users = tech_users + dev_users
            elif author_username in creative_users:
                interested_users = creative_users + ['alice_dev', 'eve_frontend']
            else:
                interested_users = [u.user.username for u in all_profiles]
            
            # Supprimer l'auteur de la liste
            interested_users = [u for u in interested_users if u != author_username]
            
            # Créer des likes (70% de chance pour les tweets pertinents)
            if random.random() < 0.7:
                num_likes = random.randint(2, min(6, len(interested_users)))
                selected_usernames = random.sample(interested_users, min(num_likes, len(interested_users)))
                
                for username in selected_usernames:
                    liker = next((p for p in all_profiles if p.user.username == username), None)
                    if liker:
                        max_minutes = max(5, int((timezone.now() - tweet.created_at).total_seconds() / 60))
                        like_date = tweet.created_at + timedelta(
                            minutes=random.randint(5, max_minutes)
                        )
                        
                        Like.objects.get_or_create(
                            user=liker,
                            tweet=tweet,
                            defaults={'created_at': like_date}
                        )
                        likes_created += 1
            
            # Créer des commentaires (40% de chance)
            if random.random() < 0.4:
                num_comments = random.randint(1, min(3, len(interested_users)))
                selected_usernames = random.sample(interested_users, min(num_comments, len(interested_users)))
                
                for username in selected_usernames:
                    commenter = next((p for p in all_profiles if p.user.username == username), None)
                    if commenter:
                        comment_content = random.choice(professional_comments)
                        
                        # Personnaliser selon le domaine
                        if 'django' in tweet.content.lower() or 'python' in tweet.content.lower():
                            if commenter.user.username in dev_users:
                                comment_content = random.choice([
                                    "Django est vraiment puissant ! 🐍",
                                    "Python forever ! 🚀",
                                    "Excellente utilisation de Django",
                                    "J'adore cette stack technique"
                                ])
                        elif 'design' in tweet.content.lower() or 'ux' in tweet.content.lower():
                            if commenter.user.username in creative_users:
                                comment_content = random.choice([
                                    "Le design c'est la vie ! 🎨",
                                    "UX avant tout !",
                                    "Beau travail de design",
                                    "L'expérience utilisateur est cruciale"
                                ])
                        
                        max_minutes = max(10, int((timezone.now() - tweet.created_at).total_seconds() / 60))
                        comment_date = tweet.created_at + timedelta(
                            minutes=random.randint(10, max_minutes)
                        )
                        
                        Comment.objects.create(
                            tweet=tweet,
                            author=commenter,
                            content=comment_content,
                            created_at=comment_date
                        )
                        comments_created += 1
        
        self.stdout.write(f'Created {likes_created} likes and {comments_created} comments')

        # Statistiques finales
        total_users = User.objects.filter(is_superuser=False).count()
        total_tweets = Tweet.objects.count()
        total_hashtags = Hashtag.objects.count()
        total_follows = Follow.objects.count()
        total_likes = Like.objects.count()
        total_comments = Comment.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Database populated successfully!\n'
                f'📊 Statistics:\n'
                f'   - Users created: {total_users}\n'
                f'   - Tweets created: {total_tweets}\n'
                f'   - Hashtags created: {total_hashtags}\n'
                f'   - Follow relationships: {total_follows}\n'
                f'   - Likes created: {total_likes}\n'
                f'   - Comments created: {total_comments}\n'
                f'\n🔐 All users have password: "password123"\n'
                f'📝 Try logging in as: alice_dev, bob_designer, charlie_data, etc.\n'
                f'🚀 Your social media platform is ready to explore!\n'
                f'🎉 Professional network with organic interactions!'
            )
        )
