/**
 * Gestion centralisée des interactions utilisateur (likes, retweets, follow)
 */

class SocialInteractions {
    constructor() {
        this.init();
    }

    init() {
        // Gestionnaire global pour toutes les interactions
        this.initGlobalClickHandler();
        this.initAccountDeletion();
        // Synchroniser l'état visuel des boutons
        this.syncButtonStates();
    }

    // Gestion des likes (maintenant dans le gestionnaire global)

    async handleLike(button) {
        console.log('handleLike called with:', button);
        if (!button || !button.dataset) {
            console.error('Button is undefined or has no dataset');
            return;
        }
        const tweetId = button.dataset.tweetId;
        console.log('Tweet ID:', tweetId);
        
        try {
            const response = await fetch(`/tweets/${tweetId}/like/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Mettre à jour tous les boutons like pour ce tweet original
                this.updateAllLikeButtons(tweetId, data.liked, data.likes_count);
            }
        } catch (error) {
            console.error('Erreur lors du like:', error);
        }
    }

    updateAllLikeButtons(tweetId, liked, count) {
        const likeButtons = document.querySelectorAll(`.like-btn[data-tweet-id="${tweetId}"]`);
        likeButtons.forEach(button => {
            this.updateLikeButton(button, liked, count);
        });
    }

    updateLikeButton(button, liked, count) {
        const likeCount = button.querySelector('.like-count');
        const svg = button.querySelector('svg path');
        
        if (liked) {
            button.classList.remove('text-x-gray', 'hover:text-red-500');
            button.classList.add('text-red-500');
            // Coeur plein
            if (svg) {
                svg.setAttribute('d', 'M12 21.638h-.014C9.403 21.59 1.95 14.856 1.95 8.478c0-3.064 2.525-5.754 5.403-5.754 2.29 0 3.83 1.58 4.646 2.73.814-1.148 2.354-2.73 4.645-2.73 2.88 0 5.404 2.69 5.404 5.755 0 6.376-7.454 13.11-10.037 13.157H12z');
            }
        } else {
            button.classList.remove('text-red-500');
            button.classList.add('text-x-gray', 'hover:text-red-500');
            // Coeur vide
            if (svg) {
                svg.setAttribute('d', 'M12 21.638h-.014C9.403 21.59 1.95 14.856 1.95 8.478c0-3.064 2.525-5.754 5.403-5.754 2.29 0 3.83 1.58 4.646 2.73.814-1.148 2.354-2.73 4.645-2.73 2.88 0 5.404 2.69 5.404 5.755 0 6.376-7.454 13.11-10.037 13.157H12zM7.354 4.225c-2.08 0-3.903 1.988-3.903 4.255 0 5.74 7.034 11.596 8.55 11.658 1.518-.062 8.55-5.917 8.55-11.658 0-2.267-1.822-4.255-3.902-4.255-2.528 0-3.94 2.936-3.952 2.965-.23.562-1.156.562-1.387 0-.014-.03-1.425-2.965-3.954-2.965z');
            }
        }
        
        if (likeCount) {
            likeCount.textContent = count;
        }
    }

    // Gestion des retweets (maintenant dans le gestionnaire global)

    async handleRetweet(button) {
        console.log('handleRetweet called with:', button);
        if (!button || !button.dataset) {
            console.error('Button is undefined or has no dataset');
            return;
        }
        const tweetId = button.dataset.tweetId;
        console.log('Tweet ID:', tweetId);
        
        try {
            const response = await fetch(`/tweets/${tweetId}/retweet/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Mettre à jour tous les boutons retweet pour ce tweet original
                this.updateAllRetweetButtons(tweetId, data.retweeted, data.retweets_count);
            }
        } catch (error) {
            console.error('Erreur lors du retweet:', error);
        }
    }

    updateAllRetweetButtons(tweetId, retweeted, count) {
        const retweetButtons = document.querySelectorAll(`.retweet-btn[data-tweet-id="${tweetId}"]`);
        retweetButtons.forEach(button => {
            this.updateRetweetButton(button, retweeted, count);
        });
    }

    updateRetweetButton(button, retweeted, count) {
        const retweetCount = button.querySelector('.retweet-count');
        
        if (retweeted) {
            button.classList.remove('text-x-gray', 'hover:text-green-500');
            button.classList.add('text-green-500');
        } else {
            button.classList.remove('text-green-500');
            button.classList.add('text-x-gray', 'hover:text-green-500');
        }
        
        if (retweetCount) {
            retweetCount.textContent = count;
        }
    }

    // Gestion du follow/unfollow (maintenant dans le gestionnaire global)

    async handleFollow(button) {
        try {
            const username = button.dataset.username;
            const isFollowing = button.dataset.following === 'true';
            const url = isFollowing ? `/unfollow/${username}/` : `/follow/${username}/`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateFollowButton(button, data.is_following, data.followers_count);
            } else {
                console.error('Erreur lors du follow/unfollow:', data.error);
            }
        } catch (error) {
            console.error('Erreur lors du follow/unfollow:', error);
        }
    }

    updateFollowButton(button, isFollowing, followersCount) {
        if (isFollowing) {
            button.textContent = 'Suivi';
            button.className = 'bg-x-gray text-white px-6 py-2 rounded-full font-medium hover:bg-red-600 hover:text-white transition-colors group';
            button.dataset.following = 'true';
            
            // Effet hover pour "Ne plus suivre"
            button.innerHTML = `
                <span class="group-hover:hidden">Suivi</span>
                <span class="hidden group-hover:inline">Ne plus suivre</span>
            `;
        } else {
            button.textContent = 'Suivre';
            button.className = 'bg-x-blue text-white px-6 py-2 rounded-full font-medium hover:bg-x-blue-hover transition-colors';
            button.dataset.following = 'false';
        }
        
        // Mettre à jour le compteur de followers si disponible
        if (followersCount !== undefined) {
            const followersCountElement = document.getElementById('followers-count');
            if (followersCountElement) {
                followersCountElement.textContent = followersCount;
            }
        }
    }

    // Gestion des menus de tweets (déplacé vers initGlobalClickHandler)
    initTweetMenus() {
        // Cette méthode est maintenant vide car la logique est dans initGlobalClickHandler
        // Conservée pour compatibilité
    }



    closeAllTweetMenus() {
        document.querySelectorAll('.tweet-menu').forEach(menu => {
            menu.classList.add('hidden');
        });
    }

    // Gestion de la suppression de tweets (déplacé vers initGlobalClickHandler)
    initDeleteButtons() {
        // Cette méthode est maintenant vide car la logique est dans initGlobalClickHandler
        // Conservée pour compatibilité
    }

    async handleDeleteTweet(e) {
        e.preventDefault();
        const button = e.target.closest('.delete-tweet-btn');
        const tweetId = button.dataset.tweetId;
        
        if (!confirm('Êtes-vous sûr de vouloir supprimer ce tweet ?')) {
            return;
        }
        
        try {
            const response = await fetch(`/tweets/${tweetId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Animation de suppression avec transition
                const tweetCard = button.closest('article');
                if (tweetCard) {
                    tweetCard.style.opacity = '0';
                    tweetCard.style.transform = 'translateX(-20px)';
                    tweetCard.style.transition = 'all 0.3s ease';
                    
                    setTimeout(() => {
                        tweetCard.remove();
                    }, 300);
                }
            } else {
                alert(data.message || 'Erreur lors de la suppression du tweet');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Erreur lors de la suppression du tweet');
        }
    }

    // Synchronisation de l'état visuel des boutons au chargement
    syncButtonStates() {
        // Synchroniser les boutons like
        document.querySelectorAll('.like-btn').forEach(button => {
            const isLiked = button.classList.contains('text-red-500');
            const svg = button.querySelector('svg path');
            
            // S'assurer que l'icône correspond à l'état
            if (isLiked && svg) {
                // Cœur plein pour les tweets likés
                svg.setAttribute('d', 'M12 21.638h-.014C9.403 21.59 1.95 14.856 1.95 8.478c0-3.064 2.525-5.754 5.403-5.754 2.29 0 3.83 1.58 4.646 2.73.814-1.148 2.354-2.73 4.645-2.73 2.88 0 5.404 2.69 5.404 5.755 0 6.376-7.454 13.11-10.037 13.157H12z');
            } else if (!isLiked && svg) {
                // Cœur vide pour les tweets non likés
                svg.setAttribute('d', 'M12 21.638h-.014C9.403 21.59 1.95 14.856 1.95 8.478c0-3.064 2.525-5.754 5.403-5.754 2.29 0 3.83 1.58 4.646 2.73.814-1.148 2.354-2.73 4.645-2.73 2.88 0 5.404 2.69 5.404 5.755 0 6.376-7.454 13.11-10.037 13.157H12zM7.354 4.225c-2.08 0-3.903 1.988-3.903 4.255 0 5.74 7.034 11.596 8.55 11.658 1.518-.062 8.55-5.917 8.55-11.658 0-2.267-1.822-4.255-3.902-4.255-2.528 0-3.94 2.936-3.952 2.965-.23.562-1.156.562-1.387 0-.014-.03-1.425-2.965-3.954-2.965z');
            }
        });
        
        // Les boutons retweet n'ont pas besoin de synchronisation d'icône
        // car l'icône reste la même, seule la couleur change
    }

    // Utilise les utilitaires globaux pour le token CSRF
    getCSRFToken() {
        return window.AjaxUtils ? window.AjaxUtils.getCSRFToken() : null;
    }

    // Gestionnaire global de clics pour centraliser toute la logique
    initGlobalClickHandler() {
        document.addEventListener('click', (e) => {
            // Gestion des likes
            const likeButton = e.target.closest('.like-btn');
            if (likeButton) {
                console.log('Like button found:', likeButton);
                e.preventDefault();
                e.stopPropagation();
                this.handleLike(likeButton);
                return;
            }

            // Gestion des retweets
            const retweetButton = e.target.closest('.retweet-btn');
            if (retweetButton) {
                e.preventDefault();
                e.stopPropagation();
                this.handleRetweet(retweetButton);
                return;
            }

            // Gestion du follow/unfollow
            const followButton = e.target.closest('#follow-btn');
            if (followButton) {
                e.preventDefault();
                e.stopPropagation();
                this.handleFollow(followButton);
                return;
            }

            // Gestion des menus de tweets
            const menuButton = e.target.closest('.tweet-menu-btn');
            if (menuButton) {
                e.preventDefault();
                e.stopPropagation();
                this.handleTweetMenuClick(menuButton);
                return;
            }

            // Gestion de la suppression de tweets
            const deleteButton = e.target.closest('.delete-tweet-btn');
            if (deleteButton) {
                e.preventDefault();
                e.stopPropagation();
                this.handleDeleteTweet(e);
                return;
            }

            // Fermer les menus ouverts si clic ailleurs
            if (!e.target.closest('.tweet-menu')) {
                this.closeAllTweetMenus();
            }
        });
    }

    // Gestion des clics sur les boutons de menu de tweets
    handleTweetMenuClick(menuButton) {
        const menu = menuButton.nextElementSibling;
        
        if (menu && menu.classList.contains('tweet-menu')) {
            // Fermer tous les autres menus
            document.querySelectorAll('.tweet-menu').forEach(m => {
                if (m !== menu) {
                    m.classList.add('hidden');
                }
            });
            
            // Basculer l'état du menu actuel
            const isHidden = menu.classList.contains('hidden');
            if (isHidden) {
                menu.classList.remove('hidden');
            } else {
                menu.classList.add('hidden');
            }
        }
    }

    // Gestion de la suppression de compte
    initAccountDeletion() {
        // Exposer la fonction globalement pour les boutons onclick
        window.confirmDeleteAccount = () => {
            const confirmation = confirm("Êtes-vous sûr(e) de vouloir supprimer votre compte ?");
            
            if (confirmation) {
                const deleteForm = document.getElementById('delete-form');
                if (deleteForm) {
                    deleteForm.submit();
                }
            }
        };
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    new SocialInteractions();
});

// Export pour utilisation modulaire
window.SocialInteractions = SocialInteractions;
