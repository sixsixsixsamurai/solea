/* ---------------- MODALS ---------------- */
const overlay    = document.getElementById("overlay");
const loginModal = document.getElementById("loginModal");
const sortModal  = document.getElementById("sortModal");
const loginBtn   = document.getElementById("openLogin");
const cartBtn    = document.getElementById("openCart");
const sortBtn    = document.querySelector(".buttonSort");

function closeAllModals() {
    loginModal?.classList.remove("active");
    sortModal?.classList.remove("active");
    overlay?.classList.remove("active");
    document.body.style.overflow = "";
}

function openModal(modal) {
    modal?.classList.add("active");
    overlay?.classList.add("active");
    document.body.style.overflow = "hidden";
}

if (loginBtn) loginBtn.onclick = () => openModal(loginModal);
if (sortBtn)  sortBtn.onclick  = () => openModal(sortModal);

document.querySelectorAll(".close").forEach(btn => { btn.onclick = closeAllModals; });
if (overlay) overlay.onclick = () => { closeAllModals(); closeCartDrawer(); };

/* ---------------- CART DRAWER ---------------- */
const cartDrawer = document.getElementById("cartDrawer");
const cartDrawerBody   = document.getElementById("cartDrawerBody");
const cartDrawerFooter = document.getElementById("cartDrawerFooter");
const cartDrawerTotal  = document.getElementById("cartDrawerTotal");
const closeDrawerBtn   = document.getElementById("closeCartDrawer");

function getCsrf() {
    return document.cookie.split(';').map(c => c.trim())
        .find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
}

function updateBadge(count) {
    let badge = document.querySelector('.cart-badge');
    const cartLink = document.getElementById('openCart');
    if (count > 0) {
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'cart-badge';
            cartLink?.appendChild(badge);
        }
        badge.textContent = count;
    } else if (badge) {
        badge.remove();
    }
}

function renderCartItems(items, total) {
    cartDrawerBody.innerHTML = '';
    if (!items.length) {
        cartDrawerBody.innerHTML = `
            <div class="cart-drawer__empty">
                <p>Your cart is empty</p>
                <a href="/menu/">Browse menu</a>
            </div>`;
        cartDrawerFooter.style.display = 'none';
        return;
    }

    items.forEach(item => {
        const imgHtml = item.image
            ? `<img class="cart-drawer__item-img" src="${item.image}" alt="${item.title}">`
            : `<div class="cart-drawer__item-img-placeholder">🍽</div>`;

        const el = document.createElement('div');
        el.className = 'cart-drawer__item';
        el.dataset.itemId = item.id;
        el.innerHTML = `
            ${imgHtml}
            <div class="cart-drawer__item-info">
                <div class="cart-drawer__item-title">${item.title}</div>
                <div class="cart-drawer__item-price">$${item.unit_price} / pc</div>
            </div>
            <div class="cart-drawer__qty">
                <button class="qty-minus" data-id="${item.id}">−</button>
                <span class="cart-drawer__qty-value">${item.quantity}</span>
                <button class="qty-plus" data-id="${item.id}">+</button>
            </div>
            <div class="cart-drawer__item-subtotal">$${item.subtotal}</div>
            <button class="cart-drawer__item-remove" data-id="${item.id}" title="Remove">&#10006;</button>
        `;
        cartDrawerBody.appendChild(el);
    });

    cartDrawerTotal.textContent = `$${total}`;
    cartDrawerFooter.style.display = 'flex';
}

async function loadCartData() {
    cartDrawerBody.innerHTML = '<div class="cart-drawer__loading">Loading...</div>';
    cartDrawerFooter.style.display = 'none';
    try {
        const res = await fetch('/cart/data/');
        const data = await res.json();
        renderCartItems(data.items, data.total_price);
        updateBadge(data.cart_count);
    } catch {
        cartDrawerBody.innerHTML = '<div class="cart-drawer__loading">Failed to load cart</div>';
    }
}

function openCartDrawer() {
    cartDrawer?.classList.add("active");
    overlay?.classList.add("active");
    document.body.style.overflow = "hidden";
    loadCartData();
}

function closeCartDrawer() {
    cartDrawer?.classList.remove("active");
    overlay?.classList.remove("active");
    document.body.style.overflow = "";
}

if (cartBtn) cartBtn.onclick = (e) => { e.preventDefault(); openCartDrawer(); };
if (closeDrawerBtn) closeDrawerBtn.onclick = closeCartDrawer;

/* Qty +/- and remove — event delegation */
cartDrawerBody?.addEventListener('click', async (e) => {
    const csrf = getCsrf();

    if (e.target.classList.contains('qty-minus') || e.target.classList.contains('qty-plus')) {
        const id = e.target.dataset.id;
        const itemEl = cartDrawerBody.querySelector(`[data-item-id="${id}"]`);
        const qtyEl  = itemEl?.querySelector('.cart-drawer__qty-value');
        if (!qtyEl) return;

        let qty = parseInt(qtyEl.textContent);
        qty = e.target.classList.contains('qty-plus') ? qty + 1 : qty - 1;

        const res = await fetch(`/cart/update/${id}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest',
                       'Content-Type': 'application/x-www-form-urlencoded' },
            body: `quantity=${qty}`,
        });
        if (res.ok) {
            const data = await res.json();
            updateBadge(data.cart_count);
            cartDrawerTotal.textContent = `$${data.total_price}`;
            if (qty < 1) {
                itemEl?.remove();
                if (!cartDrawerBody.querySelector('.cart-drawer__item')) {
                    renderCartItems([], data.total_price);
                }
            } else {
                qtyEl.textContent = qty;
                const subtotalEl = itemEl?.querySelector('.cart-drawer__item-subtotal');
                if (subtotalEl) {
                    // recalculate subtotal locally
                    const unitEl = itemEl?.querySelector('.cart-drawer__item-price');
                    const unit = parseFloat(unitEl?.textContent?.replace('$','') || 0);
                    subtotalEl.textContent = `$${(unit * qty).toFixed(2)}`;
                }
            }
        }
    }

    if (e.target.classList.contains('cart-drawer__item-remove')) {
        const id = e.target.dataset.id;
        const itemEl = cartDrawerBody.querySelector(`[data-item-id="${id}"]`);
        const res = await fetch(`/cart/remove/${id}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest' },
        });
        if (res.ok) {
            const data = await res.json();
            updateBadge(data.cart_count);
            itemEl?.remove();
            cartDrawerTotal.textContent = `$${data.total_price}`;
            if (!cartDrawerBody.querySelector('.cart-drawer__item')) {
                renderCartItems([], data.total_price);
            }
        }
    }
});

/* ---------------- CART ADD AJAX ---------------- */
document.querySelectorAll('.add-btn-form, .detail-add-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const res = await fetch(form.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest',
            },
        });
        if (res.ok) {
            const data = await res.json();
            updateBadge(data.cart_count);
        }
    });
});

/* ---------------- AUTO-CLOSE MESSAGES ---------------- */
setTimeout(() => {
    document.querySelectorAll('.message').forEach(m => m.remove());
}, 4000);
