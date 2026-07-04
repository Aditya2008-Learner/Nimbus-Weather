const form = document.querySelector("form");

if (form) {
    form.addEventListener("submit", function () {
        const button = form.querySelector("button");

        button.innerHTML = "⏳ Loading...";
        button.disabled = true;
    });
}

const searchForm = document.getElementById("searchForm");

if (searchForm) {

    searchForm.addEventListener("submit", function (e) {

        e.preventDefault();

        const city = searchForm.city.value.trim();

        if (city) {
            window.location.href = `/weather/${encodeURIComponent(city)}`;
        }

    });

}

const locationBtn = document.getElementById("locationBtn");

if (locationBtn) {

    locationBtn.addEventListener("click", () => {

        console.log("Location button clicked!");

        if (!navigator.geolocation) {
            alert("Geolocation is not supported.");
            return;
        }

        navigator.geolocation.getCurrentPosition(

            // Success
            (position) => {

                console.log(position);

                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                window.location.href = `/location?lat=${lat}&lon=${lon}`;

            },

            // Error
            (error) => {

                console.error(error);

                let message = "";

                switch (error.code) {

                    case error.PERMISSION_DENIED:
                        message = "Location permission was denied. Please allow location access for your browser.";
                        break;

                    case error.POSITION_UNAVAILABLE:
                        message = "Your device couldn't determine your location. Please turn on GPS and try again.";
                        break;

                    case error.TIMEOUT:
                        message = "Location request timed out. Please try again.";
                        break;

                    default:
                        message = "Location is unavailable on this device.";
                }

                alert(message);

            },

            // Options
            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 0
            }

        );

    });

}
