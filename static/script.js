const form = document.querySelector("form");

if (form) {

    form.addEventListener("submit", function () {

        const button = form.querySelector("button");

        button.innerHTML = "⏳ Loading...";

        button.disabled = true;

    });

}

const locationBtn = document.getElementById("locationBtn");

if (locationBtn) {

    locationBtn.addEventListener("click", () => {

        if (!navigator.geolocation) {

            alert("Geolocation is not supported.");

            return;

        }

        locationBtn.innerHTML = "📍 Detecting...";

        navigator.geolocation.getCurrentPosition((position) => {

            const lat = position.coords.latitude;

            const lon = position.coords.longitude;

            window.location.href = `/location?lat=${lat}&lon=${lon}`;

        });

    });

}