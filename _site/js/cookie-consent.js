/**
 * Cookie Consent Manager
 * Handles cookie consent banner and conditional Google Analytics loading
 */

(function() {
    'use strict';

    // Configuration
    const GA_TRACKING_ID = 'G-NGBZSX1L7Z';
    const CONSENT_KEY = 'cookieConsent';
    const SESSION_SHOWN_KEY = 'cookieBannerShown';
    const BANNER_ID = 'cookie-consent-banner';
    const ACCEPT_BUTTON_ID = 'cookie-accept';
    const DENY_BUTTON_ID = 'cookie-deny';

    /**
     * Check if user has already given consent
     */
    function getConsentStatus() {
        try {
            return localStorage.getItem(CONSENT_KEY);
        } catch (e) {
            console.error('Error accessing localStorage:', e);
            return null;
        }
    }

    /**
     * Save consent status to localStorage
     */
    function setConsentStatus(status) {
        try {
            localStorage.setItem(CONSENT_KEY, status);
        } catch (e) {
            console.error('Error saving to localStorage:', e);
        }
    }

    /**
     * Check if banner has been shown in this session
     */
    function hasBannerBeenShown() {
        try {
            return sessionStorage.getItem(SESSION_SHOWN_KEY) === 'true';
        } catch (e) {
            console.error('Error accessing sessionStorage:', e);
            return false;
        }
    }

    /**
     * Mark banner as shown in this session
     */
    function markBannerAsShown() {
        try {
            sessionStorage.setItem(SESSION_SHOWN_KEY, 'true');
        } catch (e) {
            console.error('Error saving to sessionStorage:', e);
        }
    }

    /**
     * Load Google Analytics script dynamically
     */
    function loadGoogleAnalytics() {
        // Check if GA is already loaded
        if (window.gtag && window.dataLayer) {
            return;
        }

        // Initialize dataLayer
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        window.gtag = gtag;
        gtag('js', new Date());
        gtag('config', GA_TRACKING_ID);

        // Load the GA script
        const script = document.createElement('script');
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_TRACKING_ID}`;
        document.head.appendChild(script);
    }

    /**
     * Show the cookie consent banner
     */
    function showBanner() {
        const banner = document.getElementById(BANNER_ID);
        if (banner) {
            banner.style.display = 'block';
            // Trigger animation by adding class after a brief delay
            setTimeout(() => {
                banner.classList.add('show');
            }, 10);
        }
    }

    /**
     * Hide the cookie consent banner
     */
    function hideBanner() {
        const banner = document.getElementById(BANNER_ID);
        if (banner) {
            banner.classList.remove('show');
            // Wait for animation to complete before hiding
            setTimeout(() => {
                banner.style.display = 'none';
            }, 300);
        }
    }

    /**
     * Handle accept button click
     */
    function handleAccept() {
        setConsentStatus('accepted');
        markBannerAsShown();
        loadGoogleAnalytics();
        hideBanner();
    }

    /**
     * Handle deny button click
     */
    function handleDeny() {
        setConsentStatus('denied');
        markBannerAsShown();
        hideBanner();
        // Don't load GA
    }

    /**
     * Initialize cookie consent on page load
     */
    function init() {
        const consentStatus = getConsentStatus();
        const bannerShown = hasBannerBeenShown();

        // Show banner only if it hasn't been shown in this session
        if (!bannerShown) {
            showBanner();
        }

        // If user previously accepted, load GA immediately (regardless of banner visibility)
        if (consentStatus === 'accepted') {
            loadGoogleAnalytics();
        }

        // Attach event listeners to buttons
        const acceptButton = document.getElementById(ACCEPT_BUTTON_ID);
        const denyButton = document.getElementById(DENY_BUTTON_ID);

        if (acceptButton) {
            acceptButton.addEventListener('click', handleAccept);
        }

        if (denyButton) {
            denyButton.addEventListener('click', handleDeny);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // DOM is already ready
        init();
    }
})();

