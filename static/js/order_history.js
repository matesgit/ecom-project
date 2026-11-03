const ordersContainer = document.getElementById('ordersContainer');
const token = localStorage.getItem('access_token');

if (!token) {
    ordersContainer.innerHTML = "<p>You must be logged in to view your orders.</p>";
} else {
    fetch('/api/orders/', {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed to fetch orders.");
        return res.json();
    })
    .then(data => {
        const orders = data.orders;
        if (!orders.length) {
            ordersContainer.innerHTML = "<p>You have no orders yet.</p>";
            return;
        }

        ordersContainer.innerHTML = '';
        orders.forEach(order => {
            const orderEl = document.createElement('div');
            orderEl.classList.add('order-card');

            // Build items HTML
            let itemsHtml = '<div class="order-items">';
            order.items.forEach(item => {
                itemsHtml += `<div class="order-item">
                    <div class="item-info">
                        <img src="${item.image || 'https://via.placeholder.com/50'}" alt="${item.perfume_name}">
                        <span class="item-name">${item.perfume_name} (x${item.quantity})</span>
                    </div>
                    <span>$${item.subtotal}</span>
                </div>`;
            });
            itemsHtml += '</div>';

            // Order card inner HTML
            orderEl.innerHTML = `
                <div class="order-header">
                    <span>Order #${order.id} - ${new Date(order.created_at).toLocaleString()}</span>
                    <span class="order-status ${order.completed ? 'completed' : 'pending'}">
                        ${order.completed ? 'Completed' : 'Pending'}
                    </span>
                </div>
                ${itemsHtml}
                <div class="order-total">Total: $${order.total}</div>
            `;

            // Toggle items visibility on header click
            const header = orderEl.querySelector('.order-header');
            const itemsDiv = orderEl.querySelector('.order-items');
            header.addEventListener('click', () => {
                itemsDiv.style.display = itemsDiv.style.display === 'flex' ? 'none' : 'flex';
            });

            ordersContainer.appendChild(orderEl);
        });
    })
    .catch(err => {
        console.error(err);
        ordersContainer.innerHTML = "<p>Error loading orders. Please try again later.</p>";
    });
}