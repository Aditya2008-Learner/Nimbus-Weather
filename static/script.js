const loadingScreen = document.getElementById("loading-screen");

const searchForm = document.getElementById("searchForm");

if (searchForm) {

    searchForm.addEventListener("submit", function () {

        loadingScreen.classList.remove("hidden");

        const button = this.querySelector('button[type="submit"]');

        button.innerHTML = "⏳ Loading...";

        button.disabled = true;

    });

}

const locationBtn = document.getElementById("locationBtn");

if (locationBtn) {

    locationBtn.addEventListener("click", () => {

        if (!navigator.geolocation) {

            alert("Geolocation isn't supported.");

            return;

        }

        navigator.geolocation.getCurrentPosition(

            (position) => {

                loadingScreen.classList.remove("hidden");
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                setTimeout(() => {

                    window.location.href =
                        `/location?lat=${lat}&lon=${lon}`;

                }, 150);

            },

            (error) => {

                loadingScreen.classList.add("hidden");
                switch (error.code) {

                    case error.PERMISSION_DENIED:
                        alert("Location permission denied.");
                        break;

                    case error.POSITION_UNAVAILABLE:
                        alert("Unable to determine your location.");
                        break;

                    case error.TIMEOUT:
                        alert("Location request timed out.");
                        break;

                    default:
                        alert("Unknown location error.");

                }

            },

            {

                enableHighAccuracy: true,

                timeout: 15000,

                maximumAge: 0

            }

        );

    });

}

/* ==========================================================
   PREMIUM LOADING SCREEN
========================================================== */

window.addEventListener('load', () => {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 400); // Matches the 0.4s CSS transition
    }
});

// ==========================================================================
// NIMBUS 60FPS GRAPHICS CANVAS ENGINE
// ==========================================================================
(function() {
    const canvas = document.getElementById('nimbus-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const weatherCondition = canvas.getAttribute('data-weather') || 'default';
    let particles = [];
    let animationFrameId;

    // Fast-resize handler
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initParticles();
    }

    // Ultra-light particle generator pooling mechanism
    function initParticles() {
        particles = [];
        let count = 40; // Low count keeps CPU overhead at zero
        
        if (weatherCondition.includes('rain')) count = 60;
        else if (weatherCondition.includes('clear')) count = 25;

        for (let i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 2 + 1,
                speedY: weatherCondition.includes('rain') ? Math.random() * 4 + 4 : Math.random() * 0.4 + 0.1,
                speedX: weatherCondition.includes('wind') ? Math.random() * 2 + 1 : Math.random() * 0.2 - 0.1,
                opacity: Math.random() * 0.5 + 0.2
            });
        }
    }

    // Hardware Accelerated Render Loop
    function renderLoop() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Match drawing styles directly to the weather state
        if (weatherCondition.includes('rain')) {
            ctx.strokeStyle = 'rgba(174, 219, 255, 0.4)';
            ctx.lineWidth = 1.5;
        } else {
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        }

        const len = particles.length;
        for (let i = 0; i < len; i++) {
            const p = particles[i];
            
            if (weatherCondition.includes('rain')) {
                // Renders high-tech falling precipitation streaks
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p.x + p.speedX * 2, p.y + p.speedY * 2);
                ctx.stroke();
            } else {
                // Renders glowing, drifting atmospheric solar dust
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.random() * Math.PI * 2);
                ctx.fill();
            }

            // Recycle positions seamlessly to keep memory allocation static
            p.y += p.speedY;
            p.x += p.speedX;

            if (p.y > canvas.height) { p.y = -10; p.x = Math.random() * canvas.width; }
            if (p.x > canvas.width) p.x = 0;
            if (p.x < 0) p.x = canvas.width;
        }

        // Native GPU Sync hook
        animationFrameId = requestAnimationFrame(renderLoop);
    }

    // Launch Engine safely without interrupting DOM parsing
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    renderLoop();
})();