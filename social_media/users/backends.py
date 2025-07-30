from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailBackend(ModelBackend):
    """
    Backend d'authentification personnalisé qui permet la connexion avec email OU username
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authentifie un utilisateur avec son email ou son username
        """
        if username is None or password is None:
            return None
            
        try:
            # Chercher l'utilisateur par email OU par username
            user = User.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
            
            # Vérifier le mot de passe
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        except User.DoesNotExist:
            User().set_password(password)
            return None
        
        return None
