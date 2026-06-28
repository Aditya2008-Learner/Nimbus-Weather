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
            alert("Geolocation is not supported by your browser.");
            return;
        }

        locationBtn.innerHTML = "📍 Detecting...";
        locationBtn.disabled = true;

        navigator.geolocation.getCurrentPosition(

            // Success
            (position) => {

                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                console.log("Latitude:", lat);
                console.log("Longitude:", lon);
                console.log("Accuracy:", position.coords.accuracy + " meters");

                window.location.href = `/location?lat=${lat}&lon=${lon}`;

            },

            // Error
            (error) => {

                console.error(error);

                let message = "Unable to retrieve your location.";

                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        message = "Location permission was denied.";
                        break;

                    case error.POSITION_UNAVAILABLE:
                        message = "Location information is unavailable.";
                        break;

                    case error.TIMEOUT:
                        message = "Location request timed out. Please try again.";
                        break;
                }

                alert(message);

                locationBtn.innerHTML = "📍 Use My Current Location";
                locationBtn.disabled = false;
            },

            // Options
            {
                timeout: 10000,
                maximumAge: 60000
            }

        );

    });

}