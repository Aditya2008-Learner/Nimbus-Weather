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

        console.log("Location button clicked!");

        if (!navigator.geolocation) {
            alert("Geolocation is not supported.");
            return;
        }

        navigator.geolocation.getCurrentPosition(

            (position) => {

                console.log(position);

                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                window.location.href = `/location?lat=${lat}&lon=${lon}`;

            },

            (error) => {

                console.log(error);

                alert(error.message);

            }

        );

    });

}