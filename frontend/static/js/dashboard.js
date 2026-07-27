// ==========================================
// DASHBOARD JAVASCRIPT
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    const greeting = document.getElementById("greeting");
    
    console.log(greeting.dataset.username);

    if (greeting) {

        const username = greeting.dataset.username;
        const hour = new Date().getHours();

        if (hour < 12) {

            greeting.innerHTML = `Good Morning, ${username}!`;

        }

        else if (hour < 17) {

            greeting.innerHTML = `Good Afternoon, ${username}!`;

        }

        else {

            greeting.innerHTML = `Good Evening, ${username}!`;

        }

    }

});