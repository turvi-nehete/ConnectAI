console.log("clients.js loaded!");

document.addEventListener("DOMContentLoaded", function () {

    const editButtons = document.querySelectorAll(".edit-client");

    const form = document.getElementById("clientForm");
    const modalTitle = document.getElementById("clientModalLabel");
    const submitBtn = document.getElementById("clientSubmitBtn");


    editButtons.forEach(button => {

        button.addEventListener("click", function () {

            console.log("Edit clicked");
            console.log(this.dataset);


            document.getElementById("comp_name").value = this.dataset.company;

            document.getElementById("contactname").value = this.dataset.contact;

            document.getElementById("c_mail").value = this.dataset.email;

            document.getElementById("phone_no").value = this.dataset.phone;

            document.getElementById("city").value = this.dataset.city;

            document.getElementById("state").value = this.dataset.state;

            document.getElementById("country").value = this.dataset.country;


            document.getElementById("customer_type").value =
                this.dataset.customer;


            document.getElementById("comp_type").value =
                this.dataset.companytype;


            document.getElementById("is_active").checked =
                this.dataset.active === "True";


            modalTitle.innerText = "Edit Client";

            submitBtn.innerText = "Update Client";


            form.action = "/clients/edit/" + this.dataset.id + "/";

        });

    });


    // Reset modal when Add Client is clicked

    const addButton = document.getElementById("addClientBtn");


    if (addButton) {

        addButton.addEventListener("click", function () {

            form.reset();

            modalTitle.innerText = "Add Client";

            submitBtn.innerText = "Save Client";

            form.action = "/clients/";

        });

    }


});