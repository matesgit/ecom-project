const csrftoken = document.querySelector('meta[name="csrf-token"]').content;

// Helper to get auth headers
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    };
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }
    return headers;
}

// ------------------ CART LOGIC ------------------
async function updateCartCount() {
    try {
        const res = await fetch('/api/cart/', {
            method: 'GET',
            headers: getAuthHeaders()
        });
        if(res.ok){
            const data = await res.json();
            document.getElementById('cartCount').textContent = data.total_items || 0;
        }
    } catch (err) { 
        console.error('Cart count error:', err);
        document.getElementById('cartCount').textContent = '0';
    }
}

async function addToCart(perfumeId) {
    try {
        const res = await fetch(`/api/cart/add/${perfumeId}/`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        if(res.ok){
            const data = await res.json();
            document.getElementById('cartCount').textContent = data.total_items || 0;
            alert('Added to cart!');
        } else {
            const data = await res.json();
            alert('Failed to add: ' + JSON.stringify(data));
        }
    } catch(err){
        console.error('Add to cart error:', err);
        alert('Error adding to cart.');
    }
}


function openCart() {
    window.location.href = '/api/cart/';
}

// ------------------ PERFUME DETAIL MODAL ------------------
function viewPerfume(perfume) {
    document.getElementById('perfumeDetailTitle').textContent = perfume.name;
    document.getElementById('perfumeDetailName').textContent = perfume.name;
    document.getElementById('perfumeDetailBrand').textContent = perfume.brand.name;
    document.getElementById('perfumeDetailPrice').textContent = `$${perfume.price}`;
    document.getElementById('perfumeDetailType').textContent = perfume.perfume_type_display;
    document.getElementById('perfumeDetailDescription').textContent = perfume.description || 'No description available.';
    document.getElementById('perfumeDetailImage').src = perfume.image || 'https://via.placeholder.com/400x400';
    document.getElementById('perfumeDetailImage').alt = perfume.name;

    const addCartBtn = document.getElementById('perfumeDetailAddCart');

    if (perfume.in_stock) {
        addCartBtn.disabled = false;
        addCartBtn.textContent = "Add to Cart";
        addCartBtn.onclick = function() {
            addToCart(perfume.id);
        };
    } else {
        addCartBtn.disabled = true;
        addCartBtn.textContent = "Out of Stock";
        addCartBtn.onclick = null; // disable click
    }

    const modal = new bootstrap.Modal(document.getElementById('perfumeDetailModal'));
    modal.show();
}


// ------------------ USER LOGIC ------------------
async function updateWelcomeMessage() {
    const token = localStorage.getItem('access_token');
    const welcomeEl = document.getElementById('welcomeMessage');
    const registerBtn = document.getElementById('registerBtn');
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const ordersBtn = document.getElementById('ordersBtn'); // My Orders button

    if (!token) {
        // Guest user view
        welcomeEl.textContent = "Welcome, Guest!";
        registerBtn.classList.remove('d-none');
        loginBtn.classList.remove('d-none');
        logoutBtn.classList.add('d-none');
        if (ordersBtn) ordersBtn.classList.add('d-none'); // hide orders for guests
        // Update cart for guest user
        updateCartCount();
        return;
    }

    try {
        // Fetch authenticated user info
        const res = await fetch('/api/whoami/', {
            headers: { "Authorization": "Bearer " + token }
        });

        if (!res.ok) {
            // Token invalid or expired
            localStorage.removeItem('access_token');
            welcomeEl.textContent = "Welcome, Guest!";
            registerBtn.classList.remove('d-none');
            loginBtn.classList.remove('d-none');
            logoutBtn.classList.add('d-none');
            if (ordersBtn) ordersBtn.classList.add('d-none'); // hide orders for guests
            updateCartCount();
            return;
        }

        const user = await res.json();
        // Authenticated user view
        welcomeEl.textContent = `Welcome, ${user.username}!`;
        registerBtn.classList.add('d-none');
        loginBtn.classList.add('d-none');
        logoutBtn.classList.remove('d-none');
        if (ordersBtn) ordersBtn.classList.remove('d-none'); // show orders button
        // Update cart for authenticated user
        updateCartCount();

    } catch (error) {
        console.error("WHOAMI error:", error);
        // fallback to guest view
        welcomeEl.textContent = "Welcome, Guest!";
        registerBtn.classList.remove('d-none');
        loginBtn.classList.remove('d-none');
        logoutBtn.classList.add('d-none');
        if (ordersBtn) ordersBtn.classList.add('d-none');
        updateCartCount();
    }
}


function logoutUser() {
    localStorage.removeItem('access_token');
    // Clear guest cart by removing guest_id cookie
    document.cookie = 'guest_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    updateWelcomeMessage();
    alert('Logged out successfully!');
    location.reload(); // Reload to start fresh guest session
}

// ------------------ REGISTER ------------------
async function registerUser() {
    const data = {
        username: document.getElementById('regUsername').value,
        first_name: document.getElementById('regFirstName').value,
        last_name: document.getElementById('regLastName').value,
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value,
        password2: document.getElementById('regPassword2').value
    };

    const res = await fetch('/api/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify(data)
    });

    const result = await res.json();
    if(res.ok){ 
        localStorage.setItem('access_token', result.user.access || result.tokens?.access);
        // Clear guest cart cookie
        document.cookie = 'guest_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        updateWelcomeMessage();
        alert('Registered successfully!');
        bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
        location.reload(); // Reload to fetch user's cart
    } else { 
        alert(JSON.stringify(result)); 
    }
}

// ------------------ LOGIN ------------------
async function loginUser() {
    const data = {
        username: document.getElementById('loginUsername').value,
        password: document.getElementById('loginPassword').value
    };

    const res = await fetch('/api/login/', {
        method: 'POST',
        headers: { 'Content-Type':'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify(data)
    });

    const result = await res.json();
    if(res.ok){ 
        localStorage.setItem('access_token', result.access || result.tokens?.access);
        // Clear guest cart cookie
        document.cookie = 'guest_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        updateWelcomeMessage();
        alert('Logged in successfully!');
        bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
        location.reload(); // Reload to fetch user's cart
    } else { 
        alert(JSON.stringify(result)); 
    }
}

// ------------------ WHOAMI DEBUG ------------------
async function debugWhoAmI() {
    const token = localStorage.getItem('access_token');
    if(!token){ alert('No token found!'); return; }

    const res = await fetch('/api/whoami/', {
        headers: { "Authorization": "Bearer " + token }
    });
    const data = await res.json();
    console.log("WHOAMI RESULT:", data);
    alert(JSON.stringify(data, null, 2));
}

// ------------------ PERFUMES & BRANDS ------------------
let currentType = '';
let currentSearch = '';
let currentBrand = '';

async function loadPerfumes(url = '/api/perfumes/') {
    try {
        const params = new URL(url, window.location.origin);
        if (currentType) params.searchParams.set('perfume_type', currentType);
        if (currentSearch) params.searchParams.set('search', currentSearch);
        if (currentBrand) params.searchParams.set('brand', currentBrand);

        const response = await fetch(params.toString());
        const data = await response.json();
        const perfumes = data.results;
        const container = document.getElementById('perfumes-container');
        container.innerHTML = '';
        perfumes.forEach(perfume => {
    container.innerHTML += `
    <div class="col-md-3 col-sm-6">
        <div class="product-card text-center">
            <img src="${perfume.image ? perfume.image : 'https://via.placeholder.com/260x260'}" alt="${perfume.name}">
            <h5 class="mt-2">${perfume.name}</h5>
            <p class="text-muted">${perfume.brand.name}</p>
            <p class="price">$${perfume.price}</p>
            <p>Type: ${perfume.perfume_type_display}</p>
            
            <button class="btn btn-outline-dark btn-sm mb-3" onclick='viewPerfume(${JSON.stringify(perfume).replace(/'/g, "&#39;")})'>View</button>
            <button class="btn btn-dark btn-sm mb-3" 
                onclick="addToCart(${perfume.id}); return false;" 
                ${!perfume.in_stock ? 'disabled' : ''}>
                ${!perfume.in_stock ? 'Out of Stock' : 'Add to Cart'}
            </button>
        </div>
    </div>`;
});


        const pagination = document.getElementById('perfume-pagination');
        pagination.innerHTML = '';
        if (data.previous) {
            let prevURL = new URL(data.previous).pathname + new URL(data.previous).search;
            pagination.innerHTML += `<button class="btn btn-outline-primary" onclick="loadPerfumes('${prevURL}')">Previous</button>`;
        }
        if (data.next) {
            let nextURL = new URL(data.next).pathname + new URL(data.next).search;
            pagination.innerHTML += `<button class="btn btn-outline-primary" onclick="loadPerfumes('${nextURL}')">Next</button>`;
        }

    } catch (error) {
        console.error('Error loading perfumes:', error);
    }
}

async function loadBrands() {
    try {
        const response = await fetch('/api/brands/');
        const brands = await response.json();
        const container = document.getElementById('brands-container');
        container.innerHTML = '';
        brands.forEach(brand => {
            container.innerHTML += `
            <div class="col-md-4 col-sm-6">
                <div class="brand-card">
                    <img src="${brand.image ? brand.image : 'https://via.placeholder.com/120x120'}" alt="${brand.name}">
                    <h4>${brand.name}</h4>
                    <button class="btn btn-dark btn-sm mt-3" onclick="filterByBrand(${brand.id})">View Brand</button>
                </div>
            </div>`;
        });
    } catch (error) {
        console.error('Error loading brands:', error);
    }
}

function filterPerfumes(type) { currentType = type; currentSearch = ''; currentBrand = ''; document.getElementById('search-name').value=''; loadPerfumes(); }
function searchPerfumes() { currentSearch=document.getElementById('search-name').value.trim(); currentType=''; currentBrand=''; loadPerfumes(); }
function filterByBrand(brandId) { currentBrand=brandId; currentType=''; currentSearch=''; document.getElementById('search-name').value=''; loadPerfumes(); }

// ------------------ INITIAL LOAD ------------------
updateWelcomeMessage();
loadPerfumes();
loadBrands();