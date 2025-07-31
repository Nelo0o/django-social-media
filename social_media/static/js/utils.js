// Utilitaires pour les requêtes AJAX
const AjaxUtils = {
    /**
     * Récupère le token CSRF de différentes sources
     */
    getCSRFToken() {
        // Essayer d'abord le champ de formulaire
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) return token.value;
        
        // Essayer le meta tag
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) return metaToken.getAttribute('content');
        
        // Essayer les cookies en dernier recours
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') return value;
        }
        return null;
    },

    /**
     * Effectue une requête POST avec gestion d'erreurs
     */
    async post(url, data = {}) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erreur AJAX:', error);
            throw error;
        }
    }
};

// Utilitaires pour les animations
const AnimationUtils = {
    /**
     * Animation de suppression avec slide
     */
    slideOut(element, callback) {
        element.style.opacity = '0';
        element.style.transform = 'translateX(-20px)';
        element.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            if (callback) callback();
        }, 300);
    },

    /**
     * Animation de "pop" pour les interactions
     */
    pop(element, scale = 1.3, duration = 200) {
        const originalTransform = element.style.transform;
        element.style.transform = `scale(${scale})`;
        
        setTimeout(() => {
            element.style.transform = originalTransform;
        }, duration);
    },

    /**
     * Animation de feedback pour les boutons
     */
    buttonFeedback(button, callback) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
            if (callback) callback();
        }, 150);
    }
};

// Utilitaires pour le DOM
const DOMUtils = {
    /**
     * Trouve l'élément parent le plus proche avec la classe spécifiée
     */
    closest(element, selector) {
        return element.closest(selector);
    },

    /**
     * Met à jour le texte d'un élément par son ID
     */
    updateTextById(id, text) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
        }
    },

    /**
     * Bascule la visibilité d'un élément
     */
    toggleVisibility(element, show) {
        if (show) {
            element.classList.remove('hidden');
        } else {
            element.classList.add('hidden');
        }
    },

    /**
     * Ferme tous les éléments avec une classe donnée
     */
    closeAll(selector) {
        document.querySelectorAll(selector).forEach(element => {
            element.classList.add('hidden');
        });
    }
};

// Utilitaires pour les formulaires
const FormUtils = {
    /**
     * Valide un formulaire
     */
    validate(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('border-red-500');
                isValid = false;
            } else {
                field.classList.remove('border-red-500');
            }
        });
        
        return isValid;
    },

    /**
     * Réinitialise un formulaire
     */
    reset(form) {
        form.reset();
        // Supprimer les classes d'erreur
        form.querySelectorAll('.border-red-500').forEach(field => {
            field.classList.remove('border-red-500');
        });
    }
};

// Utilitaires pour les notifications
const NotificationUtils = {
    /**
     * Affiche une notification toast
     */
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-x-full`;
        
        // Couleurs selon le type
        const colors = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-black',
            info: 'bg-blue-500 text-white'
        };
        
        toast.className += ` ${colors[type] || colors.info}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Animation d'entrée
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Suppression automatique
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, duration);
    }
};

// Utilitaires pour le formatage
const FormatUtils = {
    /**
     * Formate un nombre (1.2K, 1.5M, etc.)
     */
    formatCount(value) {
        try {
            value = parseInt(value);
        } catch {
            return 0;
        }
        
        if (value >= 1000000) {
            return `${(value/1000000).toFixed(1)}M`;
        } else if (value >= 1000) {
            return `${(value/1000).toFixed(1)}K`;
        }
        return value.toString();
    },

    /**
     * Formate une date relative
     */
    timeAgo(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days}j`;
        if (hours > 0) return `${hours}h`;
        if (minutes > 0) return `${minutes}m`;
        return `${seconds}s`;
    }
};

// Export global des utilitaires
window.AjaxUtils = AjaxUtils;
window.AnimationUtils = AnimationUtils;
window.DOMUtils = DOMUtils;
window.FormUtils = FormUtils;
window.NotificationUtils = NotificationUtils;
window.FormatUtils = FormatUtils;
