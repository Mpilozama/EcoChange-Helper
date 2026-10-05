// Show feedback while the AI is working, so the page doesn't look frozen
const form = document.getElementById('check-form');
if (form) {
    form.addEventListener('submit', () => {
        const btn = document.getElementById('submit-btn');
        btn.disabled = true;
        btn.textContent = 'Checking your air…';
    });
}