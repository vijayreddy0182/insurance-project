// -----------------------------
// Load Policies from Backend
// -----------------------------
async function fetchPolicies() {
    const sel = document.getElementById('policySelect');
    try {
        const res = await fetch('/api/policies');
        const policies = await res.json();

        sel.innerHTML =
            '<option value="">(Optional) Choose a policy</option>' +
            policies
                .map(
                    p =>
                        `<option value="${p.PolicyID}">
                            ${p.PolicyName} — ₹${p.Premium}
                        </option>`
                )
                .join('');
    } catch (e) {
        sel.innerHTML = '<option value="">Failed to load</option>';
    }
}


// -----------------------------
// Submit Insurance Application
// -----------------------------
window.addEventListener('DOMContentLoaded', () => {
    fetchPolicies();

    const form = document.getElementById('insForm');

    form.addEventListener('submit', async (ev) => {
        ev.preventDefault();

        const fd = new FormData(form);
        const payload = Object.fromEntries(fd.entries());

        // Convert numeric fields
        if (payload.coverage) payload.coverage = Number(payload.coverage);

        // If policy empty → set NULL
        if (!payload.policyId) {
            payload.policyId = null;
        } else {
            payload.policyId = Number(payload.policyId);
        }

        const msg = document.getElementById('message');
        msg.textContent = 'Submitting...';

        try {
            const res = await fetch('/api/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const j = await res.json();

            if (res.ok) {
                msg.textContent = 'Submitted successfully! Application created.';
                msg.style.color = 'green';
                form.reset();
            } else {
                msg.style.color = 'red';
                msg.textContent = 'Error: ' + (j.error || 'Unknown');
            }
        } catch (err) {
            msg.style.color = 'red';
            msg.textContent = 'Network or server error.';
        }
    });
});
