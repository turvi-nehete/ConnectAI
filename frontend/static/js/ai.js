console.log("AI JS Loaded");

// ===========================
// CSRF Helper (Django)
// ===========================

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {

                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;

            }

        }

    }

    return cookieValue;

}

// ===========================
// Global State
// ===========================

let selectedRecipients = [];

// ===========================
// Generate Email
// ===========================

document.addEventListener("DOMContentLoaded", function () {

    const button = document.getElementById("generateBtn");
    const loading = document.getElementById("loadingSection");
    const result = document.getElementById("resultSection");

    if (!button) return;

    button.addEventListener("click", async function () {

        button.disabled = true;

        button.innerHTML =
            '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';

        loading.style.display = "block";

        result.style.display = "none";

        const promptInput = document.getElementById("promptInput");
        const prompt = promptInput ? promptInput.value.trim() : "";

        if (!prompt) {
            alert("Please enter a prompt.");

            loading.style.display = "none";
            button.disabled = false;
            button.innerHTML =
                '<i class="bi bi-stars me-2"></i>Generate';

            return;
        }

        try {

            const csrftoken = getCookie("csrftoken");

            const pdfPromptRadio = document.getElementById("pdfPrompt");
            const usePdf = pdfPromptRadio && pdfPromptRadio.checked;

            let response;

            if (usePdf) {

                const pdfFileInput = document.getElementById("pdfFile");
                const formData = new FormData();

                formData.append("prompt", prompt);

                if (pdfFileInput && pdfFileInput.files[0]) {
                    formData.append("pdf", pdfFileInput.files[0]);
                }

                response = await fetch("/generate-email-rag/", {

                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken
                    },
                    body: formData

                });

            } else {

                response = await fetch("/generate-email/", {

                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrftoken
                    },
                    body: JSON.stringify({ prompt })

                });

            }

            if (!response.ok) {
                throw new Error("Request failed with status " + response.status);
            }

            const data = await response.json();
            console.log(data);

            const subjectPreview = document.getElementById("subjectPreview");
            const emailPreview = document.getElementById("emailPreview");

            if (subjectPreview) {
                subjectPreview.value = data.subject;
            }

            if (emailPreview) {
                emailPreview.textContent = data.body;
            }

            loading.style.display = "none";

            result.style.display = "block";

            button.disabled = false;

            button.innerHTML =
                '<i class="bi bi-stars me-2"></i>Generate';

        } catch (error) {

            console.error("Error generating email:", error);

            alert("Something went wrong while generating the email. Please try again.");

            loading.style.display = "none";

            button.disabled = false;

            button.innerHTML =
                '<i class="bi bi-stars me-2"></i>Generate';

        }

    });

});

// ===========================
// Audience Selection
// ===========================

document.addEventListener("DOMContentLoaded", function () {

    const audienceMethod = document.getElementById("audienceMethod");
    const smartFilters = document.getElementById("smartFiltersSection");
    const manualSelection = document.getElementById("manualSelectionSection");

    if (!audienceMethod) return;

    function updateAudience() {

        if (audienceMethod.value === "smart") {

            smartFilters.style.display = "block";
            manualSelection.style.display = "none";

        } else {

            smartFilters.style.display = "none";
            manualSelection.style.display = "block";

        }

    }

    updateAudience();

    audienceMethod.addEventListener("change", updateAudience);

});

// ===========================
// Client Search (Manual Selection)
// ===========================

document.addEventListener("DOMContentLoaded", function () {

    const search = document.getElementById("clientSearch");

    if (!search) return;

    search.addEventListener("keyup", function () {

        const value = search.value.toLowerCase();

        document.querySelectorAll(".form-check").forEach(item => {

            const text = item.innerText.toLowerCase();

            item.style.display =
                text.includes(value)
                ? ""
                : "none";

        });

    });

});

// ===========================
// Edit Generated Email
// ===========================

document.addEventListener("DOMContentLoaded", function () {

    const editBtn = document.getElementById("editBtn");
    const subjectPreview = document.getElementById("subjectPreview");
    const emailPreview = document.getElementById("emailPreview");

    if (!editBtn || !subjectPreview || !emailPreview) return;

    editBtn.addEventListener("click", function () {

        subjectPreview.removeAttribute("readonly");
        emailPreview.removeAttribute("readonly");

        subjectPreview.focus();

        editBtn.innerHTML = '<i class="bi bi-pencil-square me-1"></i>Editing...';
        editBtn.disabled = true;

    });

});

// ===========================
// Recipient Card Helper
// (shared by Smart Filters + Manual Selection)
// ===========================

function updateRecipientCard(count, label) {

    const recipientCount = document.getElementById("recipientCount");
    document.getElementById("recipientCountTop").textContent = count;
    const recipientLabel = document.getElementById("recipientLabel");

    if (recipientCount) {
        recipientCount.innerText = count;
    }

    if (recipientLabel) {
        recipientLabel.innerText = label;
    }

}

// ===========================
// Dynamic Recipient Fetching (Smart Filters)
// ===========================

function getSmartFilterValues() {

    const customerType = document.getElementById("customerType");
    const companyType = document.getElementById("companyType");
    const country = document.getElementById("country");
    const state = document.getElementById("state");
    const city = document.getElementById("city");
    const status = document.getElementById("status")

    return {
        customer_type:
            customerType && customerType.value.toLowerCase() !== "all"
                ? customerType.value
                : "",

        company_type:
            companyType && companyType.value.toLowerCase() !== "all"
                ? companyType.value
                : "",

        country:
            country && country.value.toLowerCase() !== "all"
                ? country.value
                : "",

        state:
            state && state.value.toLowerCase() !== "all"
                ? state.value
                : "",

        city:
            city && city.value.toLowerCase() !== "all"
                ? city.value
                : "",
        status:
            status && status.value.toLowerCase() !== "all"
                ? status.value
                : ""
    };

}

async function fetchFilteredRecipients() {

    const filters = getSmartFilterValues();

    try {

        const csrftoken = getCookie("csrftoken");

        const response = await fetch("/clients/filter/", {

            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify(filters)

        });

        if (!response.ok) {
            throw new Error("Request failed with status " + response.status);
        }

        const data = await response.json();

        selectedRecipients = data.recipients || [];

        updateRecipientCard(data.count, data.count + " Clients Selected");

    } catch (error) {

        console.error("Error fetching filtered recipients:", error);

    }

}

document.addEventListener("DOMContentLoaded", function () {

    const filterIds = [
        "customerType",
        "companyType",
        "country",
        "state",
        "city",
        "status"
    ];

    filterIds.forEach(function (id) {

        const el = document.getElementById(id);

        if (el) {
            el.addEventListener("change", fetchFilteredRecipients);
        }

    });

});

// ===========================
// Manual Client Selection
// ===========================

// Enriches server-rendered checkboxes with data-name / data-company / data-email
// (read once from the existing label markup, no HTML redesign needed).
function enrichClientCheckboxes() {

    document.querySelectorAll(".client-checkbox").forEach(function (checkbox) {

        // Skip if already enriched
        if (checkbox.dataset.company && checkbox.dataset.email) {
            return;
        }

        const label = document.querySelector('label[for="' + checkbox.id + '"]');

        if (!label) return;

        const companyEl = label.querySelector("strong");
        const detailsEl = label.querySelector("small");

        const company = companyEl ? companyEl.textContent.trim() : "";

        let contactName = "";
        let email = "";

        if (detailsEl) {

            const parts = detailsEl.textContent.split("|");

            contactName = parts[0] ? parts[0].trim() : "";
            email = parts[1] ? parts[1].trim() : "";

        }

        checkbox.dataset.name = contactName;
        checkbox.dataset.company = company;
        checkbox.dataset.email = email;

    });

}

// Rebuilds selectedRecipients from every checked manual checkbox.
function updateManualSelection() {

    selectedRecipients = [];

    document.querySelectorAll(".client-checkbox:checked").forEach(function (checkbox) {

        selectedRecipients.push({
            id: checkbox.value,
            name: checkbox.dataset.name || "",
            company: checkbox.dataset.company || "",
            email: checkbox.dataset.email || ""
        });

    });

    updateRecipientCard(
        selectedRecipients.length,
        selectedRecipients.length + " Clients Selected"
    );

}

document.addEventListener("DOMContentLoaded", function () {

    enrichClientCheckboxes();

    const clientListContainer =
        document.getElementById("clientList") ||
        document.getElementById("manualSelectionSection");

    if (!clientListContainer) return;

    // Event delegation: one listener handles all current and future checkboxes
    clientListContainer.addEventListener("change", function (event) {

        if (event.target && event.target.classList.contains("client-checkbox")) {
            updateManualSelection();
        }

    });

});

// ===========================
// View Recipient List (Modal)
// ===========================

function renderRecipientList() {

    const listEl = document.getElementById("recipientListItems");

    if (!listEl) return;

    listEl.innerHTML = "";

    if (!selectedRecipients.length) {

        const emptyItem = document.createElement("li");
        emptyItem.className = "list-group-item text-muted";
        emptyItem.textContent = "No recipients found.";
        listEl.appendChild(emptyItem);

        return;

    }

    selectedRecipients.forEach(function (recipient) {

        const li = document.createElement("li");
        li.className = "list-group-item";

        const companyName =
            recipient.comp_name || recipient.company_name || recipient.company || "";

        const contactName =
            recipient.contactname || recipient.contact_name || recipient.name || "";

        const email =
            recipient.c_mail || recipient.email || "";

        li.innerHTML =
            "<strong>" + companyName + "</strong><br>" +
            "<small class=\"text-muted\">" + contactName + " | " + email + "</small>";

        listEl.appendChild(li);

    });

}

document.addEventListener("DOMContentLoaded", function () {

    // The modal markup lives inside a `.card` (see ai_chat.html). That card
    // has `transform: translateY(-4px)` on :hover, and a CSS transform on any
    // ancestor re-anchors a `position: fixed` element to that ancestor instead
    // of the viewport. Because the modal is a descendant of the card, hovering
    // the open modal keeps toggling the card's :hover transform, which makes the
    // fixed modal slide/flicker while the backdrop (attached to <body>) stays
    // put. Reparenting the modal to <body> removes it from the card entirely.
    const modalEl = document.getElementById("recipientListModal");
    if (modalEl && modalEl.parentElement !== document.body) {
        document.body.appendChild(modalEl);
    }

    const viewListBtn = document.getElementById("viewListBtn");

    if (!viewListBtn) return;

    viewListBtn.addEventListener("click", function () {

        renderRecipientList();

        if (modalEl && window.bootstrap) {
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl, {
                backdrop: "static",
                keyboard: false
            });
            modal.show();
        }

    });

});

document.getElementById("viewListBtnTop").addEventListener("click", function () {
    console.log("Top button clicked");
    document.getElementById("viewListBtn").click();
});


// ===========================
// Approve & Send (Gmail)
// ===========================

async function sendEmails() {

    const approveBtn = document.getElementById("approveSendBtn");
    const subjectPreview = document.getElementById("subjectPreview");
    const emailPreview = document.getElementById("emailPreview");

    if (!approveBtn) return;

    const subject = subjectPreview
        ? (subjectPreview.value !== undefined && subjectPreview.value !== ""
            ? subjectPreview.value
            : subjectPreview.textContent)
        : "";

    const body = emailPreview
        ? (emailPreview.value !== undefined && emailPreview.value !== ""
            ? emailPreview.value
            : emailPreview.textContent)
        : "";

    if (!subject || !body) {
        alert("Subject and email body are required before sending.");
        return;
    }

    if (!selectedRecipients.length) {
        alert("Please select at least one recipient before sending.");
        return;
    }

    const originalBtnHtml = approveBtn.innerHTML;

    approveBtn.disabled = true;
    approveBtn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-2"></span>Sending...';

    try {

        const csrftoken = getCookie("csrftoken");

        const response = await fetch("/send-gmail/", {

            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                subject: subject,
                body: body,
                recipients: selectedRecipients
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Request failed with status " + response.status);
        }

        alert(
            "🎉 Campaign Sent Successfully!\n\n" +
            "✅ Sent: " + data.result.total_sent + "\n" +
            "❌ Failed: " + data.result.total_failed
        );

    } catch (error) {

        console.error("Error sending emails:", error);

        alert("Failed to send campaign: " + error.message);

    } finally {

        approveBtn.disabled = false;
        approveBtn.innerHTML = originalBtnHtml;

    }

}

document.addEventListener("DOMContentLoaded", function () {

    const approveBtn = document.getElementById("approveSendBtn");

    if (!approveBtn) return;

    approveBtn.addEventListener("click", sendEmails);

});

const promptOnly = document.getElementById("promptOnly");
const pdfPrompt = document.getElementById("pdfPrompt");
const pdfUploadSection = document.getElementById("pdfUploadSection");

function togglePDFUpload() {
    pdfUploadSection.style.display = pdfPrompt.checked ? "block" : "none";
}

promptOnly.addEventListener("change", togglePDFUpload);
pdfPrompt.addEventListener("change", togglePDFUpload);

// Initialize on page load
togglePDFUpload();


