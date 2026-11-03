function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = "Bearer " + token;
    return headers;
}

// LOAD CART ITEMS
async function loadCart() {
    try {
        const res = await fetch('/api/cart/', {
            method: 'GET',
            headers: getAuthHeaders()
        });

        const data = await res.json();

        const container = document.getElementById('cart-items');
        const table = document.getElementById('cart-table');
        const emptyMsg = document.getElementById('empty-message');
        const totalEl = document.getElementById('total-price');

        container.innerHTML = '';
        let total = 0;

        if (!data.items || data.items.length === 0) {
            table.style.display = 'none';
            emptyMsg.innerHTML = '🛍️ Your cart is empty';
            totalEl.textContent = '0';
            return;
        }

        table.style.display = 'table';
        emptyMsg.style.display = 'none';

        data.items.forEach(item => {
            total += item.subtotal;

            container.innerHTML += `
                <tr>
                    <td>
                        <img src="${item.perfume.image}" class="perfume-img">
                    </td>
                    <td class="text-start">${item.perfume.name}</td>
                    <td>${item.perfume.price} GEL</td>
                    <td>
                        <input type="number"
                               id="qty-${item.id}"
                               class="form-control qty-input"
                               value="${item.quantity}"
                               min="1">
                    </td>
                    <td><strong>${item.subtotal} GEL</strong></td>
                    <td>
                        <button class="btn btn-update btn-sm mb-1" onclick="updateItem(${item.id})">
                            Update
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteItem(${item.id})">
                            Remove
                        </button>
                    </td>
                </tr>
            `;
        });

        totalEl.textContent = total;

    } catch (err) {
        console.error(err);
        document.getElementById('empty-message').textContent = 'Failed to load cart.';
    }
}

// UPDATE ITEM
async function updateItem(itemId) {
    const qty = document.getElementById(`qty-${itemId}`).value;

    try {
        const res = await fetch(`/api/cart/update/${itemId}/`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({ quantity: qty })
        });

        if (res.ok) loadCart();
        else alert("Failed to update item");

    } catch (error) {
        console.error(error);
    }
}

// DELETE ITEM
async function deleteItem(itemId) {
    try {
        const res = await fetch(`/api/cart/remove/${itemId}/`, {
            method: "DELETE",
            headers: getAuthHeaders()
        });

        if (res.ok) loadCart();
        else alert("Failed to delete");

    } catch (error) {
        console.error(error);
    }
}

// INITIAL LOAD
loadCart();