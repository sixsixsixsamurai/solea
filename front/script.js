/* ---------------- NAV ---------------- */
const navButtons = document.querySelectorAll('.bText1');

navButtons.forEach(button => {
    button.addEventListener('click', () => {
        const link = button.getAttribute('data-link');
        window.location.href = link;
    });
});

const buttons = document.querySelectorAll('.button, .button2, .button3');

buttons.forEach(button => {
    button.addEventListener('click', () => {
        const link = button.getAttribute('data-link');
        window.location.href = link;
    });
});

/* ---------------- MODALS ---------------- */

const overlay = document.getElementById("overlay");

const loginModal = document.getElementById("loginModal");
const cartModal = document.getElementById("cartModal");
const sortModal = document.getElementById("sortModal");

const loginBtn = document.getElementById("openLogin");
const cartBtn = document.getElementById("openCart");
const sortBtn = document.querySelector(".buttonSort");

/* OPEN */

if (loginBtn) {
    loginBtn.onclick = () => {
        loginModal.classList.add("active");
        overlay.classList.add("active");
        document.body.style.overflow = "hidden";
    };
}

if (cartBtn) {
    cartBtn.onclick = () => {
        cartModal.classList.add("active");
        overlay.classList.add("active");
        document.body.style.overflow = "hidden";
    };
}

if (sortBtn) {
    sortBtn.onclick = () => {
        sortModal.classList.add("active");
        overlay.classList.add("active");
        document.body.style.overflow = "hidden";
    };
}

/* CLOSE FUNCTION */
function closeAllModals() {
    loginModal?.classList.remove("active");
    cartModal?.classList.remove("active");
    sortModal?.classList.remove("active");
    overlay?.classList.remove("active");

    document.body.style.overflow = "";
}

/* CLOSE BUTTONS */
document.querySelectorAll(".close").forEach(btn => {
    btn.onclick = closeAllModals;
});

/* CLICK OUTSIDE */
if (overlay) {
    overlay.onclick = closeAllModals;
}


/*cards */
document.addEventListener('click', (e) => {
    const card = e.target.closest('.card');
    
    if (card && !e.target.closest('.add-btn')) {
        const link = card.getAttribute('data-link');
        if (link) window.location.href = link;
    }
});
