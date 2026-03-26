document.querySelector('form').addEventListener('submit', function() {
    const btn = document.querySelector('.btn-submit');
    // Change the button text so it feels like AI is working
    btn.innerHTML = "Consulting Climate Sensors... 📡";
    btn.disabled = true; // Prevent double-clicking
    btn.style.opacity = "0.8";
});

function shareResult() {
    const text = `I just checked my climate impact for 2030 with EcoChange AI! My footprint is ${document.querySelector('h2').innerText}. Can you beat my score? #2030AIChallenge #ClimateAction`;
    alert("Copied to clipboard: " + text);
    // In a real app, this would open a Twitter/WhatsApp share link
}