// Assessment Tracker Dashboard JavaScript

// Auto-refresh functionality (optional)
let autoRefreshInterval = null;

function enableAutoRefresh(intervalMinutes = 5) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }

    autoRefreshInterval = setInterval(() => {
        console.log('Auto-refreshing data...');
        location.reload();
    }, intervalMinutes * 60 * 1000);

    console.log(`Auto-refresh enabled: every ${intervalMinutes} minutes`);
}

function disableAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('Auto-refresh disabled');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // R key to refresh
    if (e.key === 'r' && !e.ctrlKey && !e.metaKey) {
        location.reload();
    }

    // H key to go home
    if (e.key === 'h' && !e.ctrlKey && !e.metaKey) {
        window.location.href = '/';
    }
});

// Show loading indicator on page navigation
window.addEventListener('beforeunload', () => {
    const body = document.body;
    body.style.opacity = '0.6';
    body.style.pointerEvents = 'none';
});

// Smooth scroll to sections
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Assessment Tracker Dashboard loaded');

    // Optionally enable auto-refresh (uncomment to enable)
    // enableAutoRefresh(5); // Refresh every 5 minutes
});
