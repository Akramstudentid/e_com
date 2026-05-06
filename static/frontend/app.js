const API_ROOT = "/api";

const state = {
    courses: [],
    token: localStorage.getItem("accessToken") || "",
    refresh: localStorage.getItem("refreshToken") || "",
    username: localStorage.getItem("username") || "",
    isStaff: localStorage.getItem("isStaff") === "true"
};

const qs = (selector) => document.querySelector(selector);
const qsa = (selector) => Array.from(document.querySelectorAll(selector));

function money(value) {
    const amount = Number(value || 0);
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0
    }).format(amount);
}

function showToast(message) {
    const toast = qs("#toast");
    toast.textContent = message;
    toast.classList.remove("opacity-0", "translate-y-full");
    toast.classList.add("opacity-100", "translate-y-0");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => {
        toast.classList.add("opacity-0", "translate-y-full");
        toast.classList.remove("opacity-100", "translate-y-0");
    }, 3200);
}

function authHeaders() {
    return state.token ? { Authorization: `Bearer ${state.token}` } : {};
}

async function api(path, options = {}) {
    const response = await fetch(`${API_ROOT}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...authHeaders(),
            ...(options.headers || {})
        }
    });

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await response.json() : null;

    if (!response.ok) {
        const detail = data?.detail || data?.error || Object.values(data || {}).flat().join(" ");
        throw new Error(detail || `Request failed with status ${response.status}`);
    }

    return data;
}

function setSession(tokens, username) {
    state.token = tokens.access || tokens.access_token;
    state.refresh = tokens.refresh || tokens.refresh_token;
    state.username = tokens.username || username;
    state.isStaff = Boolean(tokens.is_staff);
    localStorage.setItem("accessToken", state.token);
    localStorage.setItem("refreshToken", state.refresh);
    localStorage.setItem("username", state.username);
    localStorage.setItem("isStaff", String(state.isStaff));
    renderSession();
}

function clearSession() {
    state.token = "";
    state.refresh = "";
    state.username = "";
    state.isStaff = false;
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("username");
    localStorage.removeItem("isStaff");
    renderSession();
}

function renderSession() {
    qs("#sessionLabel").textContent = state.username ? `Signed in: ${state.username}${state.isStaff ? " (admin)" : ""}` : "Guest";
    qs("#logoutButton").hidden = !state.token;
    qs('[data-view="admin"]').hidden = !state.isStaff;
}

function switchView(view) {
    qsa(".tab").forEach((tab) => tab.classList.toggle("is-active", tab.dataset.view === view));
    qsa(".view").forEach((section) => section.classList.remove("is-active"));
    qs(`#${view}View`).classList.add("is-active");

    if (view === "cart") loadCart();
    if (view === "admin") {
        if (!state.isStaff) {
            showToast("Admin tools require a staff account.");
            switchView("catalog");
            return;
        }
        loadDashboard();
    }
}

function courseDescription(text) {
    if (!text) return "No description added yet.";
    return text.length > 112 ? `${text.slice(0, 109)}...` : text;
}

function renderCourses() {
    const term = qs("#searchInput").value.trim().toLowerCase();
    const grid = qs("#courseGrid");
    const courses = state.courses.filter((course) => {
        const haystack = `${course.name} ${course.category_name || ""}`.toLowerCase();
        return !term || haystack.includes(term);
    });

    if (!courses.length) {
        grid.innerHTML = `<div class="col-span-full text-center py-12 text-gray-500">No courses found matching your search.</div>`;
        updateHeroStats();
        return;
    }

    grid.innerHTML = courses.map((course) => `
        <div class="bg-white rounded-lg shadow hover:shadow-xl transition-shadow overflow-hidden">
            <div class="bg-gradient-to-r from-purple-400 to-purple-600 h-40 flex items-center justify-center">
                <div class="text-center text-white">
                    <p class="text-sm opacity-75">#${course.id}</p>
                    <span class="inline-block px-3 py-1 bg-white/20 rounded-full text-sm mt-2">${course.available ? "Available" : "Closed"}</span>
                </div>
            </div>
            <div class="p-6">
                <p class="text-xs text-purple-600 font-semibold uppercase">${course.category_name || "Uncategorized"}</p>
                <h3 class="font-bold text-gray-900 mt-2 text-lg">${course.name}</h3>
                <p class="text-gray-600 text-sm mt-3 line-clamp-2">${course.description || "No description"}</p>
                
                <div class="mt-4 border-t pt-4">
                    <div class="flex items-center justify-between mb-3">
                        <div>
                            <strong class="text-purple-600 text-xl">${money(course.final_price)}</strong>
                            ${course.mrp != course.final_price ? `<del class="text-gray-400 ml-2">${money(course.mrp)}</del>` : ''}
                        </div>
                        <span class="text-sm text-gray-600">${course.stock} in stock</span>
                    </div>
                </div>

                <div class="mt-4 flex gap-2">
                    <button class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-900 font-semibold py-2 rounded-lg transition" data-buy="${course.id}">
                        Buy Now
                    </button>
                    <button class="flex-1 gradient-primary text-white font-semibold py-2 rounded-lg gradient-hover transition" data-cart="${course.id}">
                        Add to Cart
                    </button>
                </div>
            </div>
        </div>
    `).join("");

    updateHeroStats(courses);
}

function updateHeroStats(courses = state.courses) {
    const stock = courses.reduce((sum, course) => sum + Number(course.stock || 0), 0);
    const prices = courses.map((course) => Number(course.final_price || course.mrp || 0)).filter(Boolean);
    const bestPrice = prices.length ? Math.min(...prices) : 0;
    qs("#heroStock").textContent = stock || "--";
    qs("#heroPrice").textContent = bestPrice ? money(bestPrice) : "--";
}

async function loadCourses() {
    const category = qs("#categoryInput").value.trim();
    const path = category ? `/courses/filter/?category=${encodeURIComponent(category)}` : "/courses/";
    state.courses = await api(path);
    renderCourses();
}

async function addToCart(courseId) {
    if (!state.token) {
        switchView("account");
        showToast("Please login before adding to cart.");
        return;
    }

    await api("/cart/", {
        method: "POST",
        body: JSON.stringify({ product_id: Number(courseId), quantity: 1 })
    });
    showToast("Course added to cart.");
}

async function buyCourse(courseId) {
    if (!state.token) {
        switchView("account");
        showToast("Please login before placing a buy request.");
        return;
    }

    const quote = await api("/order/", {
        method: "POST",
        body: JSON.stringify({ Course_id: Number(courseId) })
    });

    showToast(`Final price ${money(quote["Final Price"])}. You saved ${money(quote["You Saved"])}.`);
}

async function loadCart() {
    const list = qs("#cartList");
    const summary = qs("#cartSummary");

    if (!state.token) {
        summary.innerHTML = "";
        list.innerHTML = `<div class="empty-state">Login to see your cart.</div>`;
        return;
    }

    const data = await api("/cart/");
    const items = data.items || [];
    const totalItems = items.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
    const totalPrice = items.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.quantity || 0), 0);
    
    summary.innerHTML = `
        <div class="space-y-4">
            <div class="flex justify-between items-center">
                <span class="text-gray-600">Total Items</span>
                <strong class="text-lg">${totalItems}</strong>
            </div>
            <div class="flex justify-between items-center border-t pt-4">
                <span class="text-gray-600">Total Price</span>
                <strong class="text-2xl text-purple-600">${money(totalPrice)}</strong>
            </div>
            <button id="placeOrderBtn" class="w-full gradient-primary text-white font-bold py-3 rounded-lg gradient-hover transition mt-6" ${items.length ? '' : 'disabled'}>
                Place Order
            </button>
        </div>
    `;

    if (!items.length) {
        list.innerHTML = `<div class="text-center py-12 text-gray-500">Your cart is empty. Add some courses to get started!</div>`;
        return;
    }

    list.innerHTML = items.map((item) => `
        <div class="border-b pb-4 mb-4 last:border-b-0">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <p class="text-xs text-gray-500">Course #${item.product}</p>
                    <h3 class="font-semibold text-gray-900">${item.product_name}</h3>
                    <p class="text-sm text-gray-600 mt-1">Quantity: <strong>${item.quantity}</strong></p>
                </div>
                <div class="text-right">
                    <strong class="text-lg text-purple-600">${money(Number(item.price) * Number(item.quantity))}</strong>
                </div>
            </div>
        </div>
    `).join("");

    // Add event listener to place order button
    const placeOrderBtn = qs("#placeOrderBtn");
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener("click", placeOrder);
    }
}

async function placeOrder() {
    if (!state.token) {
        showToast("Please login first");
        return;
    }

    try {
        const result = await api("/cart/place-order/", {
            method: "POST",
            body: JSON.stringify({})
        });
        
        showToast(`Order placed successfully! Order ID: ${result.order_id}`);
        await loadCart();
        switchView("catalog");
    } catch (error) {
        showToast(error.message);
    }
}

async function loadDashboard() {
    const wrap = qs("#dashboardCards");

    if (!state.token || !state.isStaff) {
        wrap.innerHTML = `<div class="col-span-full text-center py-12 text-gray-500">Login as an admin to load dashboard metrics.</div>`;
        return;
    }

    try {
        const data = await api("/dashboard/");
        const labels = {
            total_payment: "Total Revenue",
            refund_amount: "Refund Amount",
            buy_request: "Total Orders",
            delivery: "Delivered",
            active_users: "Active Users",
            inactive_users: "Inactive Users"
        };
        wrap.innerHTML = Object.entries(labels).map(([key, label]) => `
            <div class="bg-white rounded-lg shadow p-6">
                <p class="text-gray-600 text-sm font-medium">${label}</p>
                <strong class="text-3xl text-purple-600 mt-2 block">${key.includes("amount") || key.includes("payment") ? money(data[key]) : data[key]}</strong>
            </div>
        `).join("");
    } catch (error) {
        wrap.innerHTML = `<div class="col-span-full bg-red-50 text-red-800 rounded-lg p-6 text-center">${error.message}</div>`;
    }
}

function formData(form) {
    return Object.fromEntries(new FormData(form).entries());
}

function isoDateFromNow(days) {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date.toISOString().slice(0, 10);
}

function bindEvents() {
    qsa("[data-view]").forEach((button) => {
        button.addEventListener("click", () => switchView(button.dataset.view));
    });

    qsa("[data-view-target]").forEach((button) => {
        button.addEventListener("click", () => switchView(button.dataset.viewTarget));
    });

    qs("#logoutButton").addEventListener("click", () => {
        clearSession();
        showToast("Logged out.");
    });

    qs("#filterButton").addEventListener("click", () => loadCourses().catch((error) => showToast(error.message)));
    qs("#searchInput").addEventListener("input", renderCourses);

    qsa("[data-refresh]").forEach((button) => {
        button.addEventListener("click", () => {
            const target = button.dataset.refresh;
            const loaders = { courses: loadCourses, cart: loadCart, admin: loadDashboard };
            loaders[target]().catch((error) => showToast(error.message));
        });
    });

    qs("#courseGrid").addEventListener("click", (event) => {
        const cartButton = event.target.closest("[data-cart]");
        const buyButton = event.target.closest("[data-buy]");
        if (cartButton) addToCart(cartButton.dataset.cart).catch((error) => showToast(error.message));
        if (buyButton) buyCourse(buyButton.dataset.buy).catch((error) => showToast(error.message));
    });

    qs("#loginForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            const payload = formData(event.currentTarget);
            const tokens = await api("/login/", {
                method: "POST",
                body: JSON.stringify(payload)
            });
            setSession(tokens, payload.username);
            showToast("Login successful.");
            switchView("catalog");
        } catch (error) {
            showToast(error.message);
        }
    });

    qs("#registerForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            const payload = formData(event.currentTarget);
            await api("/accounts/register/", {
                method: "POST",
                body: JSON.stringify(payload)
            });
            event.currentTarget.reset();
            showToast("Account created. You can login now.");
        } catch (error) {
            showToast(error.message);
        }
    });

    qs("#courseForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            const payload = formData(event.currentTarget);
            payload.mrp = Number(payload.mrp);
            payload.offer_price = Number(payload.offer_price || 0);
            payload.stock = Number(payload.stock || 0);
            payload.available = event.currentTarget.available.checked;
            if (payload.offer_price <= 0) delete payload.offer_price;

            await api("/courses/", {
                method: "POST",
                body: JSON.stringify(payload)
            });
            event.currentTarget.reset();
            event.currentTarget.available.checked = true;
            await loadCourses();
            showToast("Course created.");
        } catch (error) {
            showToast(error.message);
        }
    });

    qs("#offerForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            const payload = formData(event.currentTarget);
            payload.course = Number(payload.course);
            payload.title = `Course #${payload.course} offer`;
            payload.discount_percentage = Number(payload.percentage);
            if (payload.offer_type === "festival") payload.offer_type = "occasional";
            payload.start_date = payload.start_date || isoDateFromNow(0);
            payload.end_date = payload.end_date || isoDateFromNow(30);
            delete payload.course;
            delete payload.percentage;

            await api("/offers/", {
                method: "POST",
                body: JSON.stringify(payload)
            });
            event.currentTarget.reset();
            await loadCourses();
            showToast("Offer created.");
        } catch (error) {
            showToast(error.message);
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    renderSession();
    bindEvents();
    loadCourses().catch((error) => showToast(error.message));
});
