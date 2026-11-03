// Auth headers
function getAuthHeaders() {
    const token = localStorage.getItem("access_token");
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = "Bearer " + token;
    return headers;
}

// LOAD CHECKOUT DATA
async function loadCheckout() {
    const res = await fetch("/api/checkout/", {
        method: "GET",
        headers: getAuthHeaders()
    });

    const data = await res.json();

    if (data.error) {
        document.getElementById("order-items").innerHTML = `<p>${data.error}</p>`;
        return;
    }

    let html = `
        <table class="table align-middle text-center">
            <thead>
                <tr>
                    <th class="text-start">Product</th>
                    <th>Image</th>
                    <th>Qty</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>
    `;

    data.items.forEach(i => {
        html += `
            <tr>
                <td class="text-start product-name">${i.perfume.name}</td>
                <td>
                    <img src="${i.perfume.image}" width="70" class="rounded">
                </td>
                <td>${i.quantity}</td>
                <td><strong>${i.subtotal} GEL</strong></td>
            </tr>
        `;
    });

    html += "</tbody></table>";

    document.getElementById("order-items").innerHTML = html;
    document.getElementById("order-total").textContent = data.total;

    document.getElementById("full_name").value = data.user.full_name || "";
    document.getElementById("email").value = data.user.email || "";
}

// PLACE ORDER
document.getElementById("order-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        full_name: document.getElementById("full_name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
        address: document.getElementById("address").value,
    };

    const res = await fetch("/api/order/place/", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.ok) {
        alert("Order placed successfully! Order ID: " + data.order_id);
        window.location.href = "/";
    } else {
        alert(data.error || "Failed to place order");
    }
});

// INITIAL LOAD
loadCheckout();