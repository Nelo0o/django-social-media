from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from users.models import UserProfile
from follows.models import Follow, FollowManager


class FollowManagerTestCase(TestCase):
    """Tests pour le FollowManager"""
    
    def setUp(self):
        """Configuration des données de test"""
        # Créer des utilisateurs de test
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            username='charlie',
            email='charlie@example.com',
            password='testpass123'
        )
        
        # Les profils sont créés automatiquement via le signal
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.profile3 = self.user3.profile
        
        # Gestionnaire de follow pour profile1
        self.follow_manager = FollowManager(self.profile1)
    
    def test_follow_user_success(self):
        """Test : suivre un utilisateur avec succès"""
        # Alice suit Bob
        result = self.follow_manager.follow(self.profile2)
        
        # Vérifications
        self.assertTrue(result)
        self.assertTrue(self.follow_manager.is_following(self.profile2))
        self.assertEqual(self.follow_manager.following_count, 1)
        self.assertEqual(self.profile2.follow_manager.followers_count, 1)
        
        # Vérifier que la relation existe en base
        follow_relation = Follow.objects.get(
            follower=self.profile1,
            followed=self.profile2
        )
        self.assertFalse(follow_relation.blocked)
    
    def test_follow_self_raises_validation_error(self):
        """Test : impossible de se suivre soi-même"""
        with self.assertRaises(ValidationError) as context:
            self.follow_manager.follow(self.profile1)
        
        self.assertIn("vous-même", str(context.exception))
    
    def test_follow_already_following_returns_false(self):
        """Test : suivre quelqu'un qu'on suit déjà retourne False"""
        # Alice suit Bob
        self.follow_manager.follow(self.profile2)
        
        # Essayer de suivre à nouveau
        result = self.follow_manager.follow(self.profile2)
        
        self.assertFalse(result)
        self.assertEqual(self.follow_manager.following_count, 1)
    
    def test_unfollow_user_success(self):
        """Test : ne plus suivre un utilisateur"""
        # Alice suit Bob
        self.follow_manager.follow(self.profile2)
        self.assertTrue(self.follow_manager.is_following(self.profile2))
        
        # Alice ne suit plus Bob
        result = self.follow_manager.unfollow(self.profile2)
        
        # Vérifications
        self.assertTrue(result)
        self.assertFalse(self.follow_manager.is_following(self.profile2))
        self.assertEqual(self.follow_manager.following_count, 0)
        self.assertEqual(self.profile2.follow_manager.followers_count, 0)
        
        # Vérifier que la relation n'existe plus
        self.assertFalse(
            Follow.objects.filter(
                follower=self.profile1,
                followed=self.profile2
            ).exists()
        )
    
    def test_unfollow_not_following_returns_false(self):
        """Test : ne plus suivre quelqu'un qu'on ne suit pas retourne False"""
        result = self.follow_manager.unfollow(self.profile2)
        self.assertFalse(result)


class FollowBlockingTestCase(TestCase):
    """Tests pour les fonctionnalités de blocage de followers"""
    
    def setUp(self):
        """Configuration des données de test"""
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='testpass123'
        )
        
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        
        # Bob suit Alice
        self.profile2.follow(self.profile1)
        
        # Gestionnaire de follow pour Alice
        self.follow_manager = FollowManager(self.profile1)
    
    def test_block_follower_success(self):
        """Test : bloquer un follower avec succès"""
        # Alice bloque Bob
        result = self.follow_manager.block_follower(self.profile2)
        
        # Vérifications
        self.assertTrue(result)
        self.assertTrue(self.follow_manager.is_follower_blocked(self.profile2))
        
        # Le follower bloqué ne compte plus dans les statistiques
        self.assertEqual(self.follow_manager.followers_count, 0)
        self.assertEqual(self.profile2.follow_manager.following_count, 0)
        
        # Vérifier que la relation existe mais est bloquée
        follow_relation = Follow.objects.get(
            follower=self.profile2,
            followed=self.profile1
        )
        self.assertTrue(follow_relation.blocked)
    
    def test_unblock_follower_success(self):
        """Test : débloquer un follower avec succès"""
        # Alice bloque puis débloque Bob
        self.follow_manager.block_follower(self.profile2)
        result = self.follow_manager.unblock_follower(self.profile2)
        
        # Vérifications
        self.assertTrue(result)
        self.assertFalse(self.follow_manager.is_follower_blocked(self.profile2))
        
        # Le follower débloqué compte à nouveau dans les statistiques
        self.assertEqual(self.follow_manager.followers_count, 1)
        self.assertEqual(self.profile2.follow_manager.following_count, 1)
        
        # Vérifier que la relation n'est plus bloquée
        follow_relation = Follow.objects.get(
            follower=self.profile2,
            followed=self.profile1
        )
        self.assertFalse(follow_relation.blocked)
    
    def test_block_non_follower_returns_false(self):
        """Test : bloquer quelqu'un qui n'est pas follower retourne False"""
        # Créer un troisième utilisateur qui ne suit pas Alice
        user3 = User.objects.create_user(
            username='charlie',
            email='charlie@example.com',
            password='testpass123'
        )
        profile3 = user3.profile
        
        result = self.follow_manager.block_follower(profile3)
        self.assertFalse(result)
    
    def test_follow_unblocks_blocked_relation(self):
        """Test : suivre quelqu'un débloque automatiquement une relation bloquée"""
        # Alice bloque Bob
        self.follow_manager.block_follower(self.profile2)
        self.assertTrue(self.follow_manager.is_follower_blocked(self.profile2))
        
        # Bob essaie de suivre Alice à nouveau
        result = self.profile2.follow(self.profile1)
        
        # La relation devrait être débloquée
        self.assertTrue(result)
        self.assertFalse(self.follow_manager.is_follower_blocked(self.profile2))
        self.assertEqual(self.follow_manager.followers_count, 1)
