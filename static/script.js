const loadingScreen = document.getElementById("loading-screen");

const searchForm = document.getElementById("searchForm");

if (searchForm) {

    searchForm.addEventListener("submit", function () {

        loadingScreen.classList.add("active");

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

                loadingScreen.classList.add("active");

                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                setTimeout(() => {

                    window.location.href =
                        `/location?lat=${lat}&lon=${lon}`;

                }, 150);

            },

            (error) => {

                loadingScreen.classList.remove("active");

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