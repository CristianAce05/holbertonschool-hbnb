document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const placesList = document.getElementById('places-list');

    if (loginForm) {
        setupLoginForm(loginForm);
    }

    if (placesList) {
        setupIndexPage(placesList);
    }
});

function setupLoginForm(loginForm) {
    const feedback = document.getElementById('login-feedback');
    const submitButton = document.getElementById('login-submit');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            showFeedback('Enter both email and password.', 'error');
            return;
        }

        setSubmitting(true);
        showFeedback('Signing you in...', 'success');

        try {
            const response = await fetch(getLoginUrl(), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const data = await parseResponse(response);

            if (!response.ok) {
                const message = typeof data.error === 'string' ? data.error : 'Login failed.';
                throw new Error(message);
            }

            if (!data.access_token) {
                throw new Error('Login succeeded but no token was returned.');
            }

            setCookie('token', data.access_token, 1);
            window.location.href = 'index.html';
        } catch (error) {
            showFeedback(error.message || 'Unable to log in right now.', 'error');
            setSubmitting(false);
        }
    });

    function setSubmitting(isSubmitting) {
        submitButton.disabled = isSubmitting;
        submitButton.textContent = isSubmitting ? 'Signing In...' : 'Sign In';
    }

    function showFeedback(message, type) {
        feedback.hidden = false;
        feedback.textContent = message;
        feedback.className = `form-feedback ${type === 'error' ? 'is-error' : 'is-success'}`;
    }
}

async function setupIndexPage(placesList) {
    const priceFilter = document.getElementById('price-filter');
    const feedback = document.getElementById('places-feedback');
    const token = getCookie('token');

    toggleLoginVisibility(Boolean(token));

    if (priceFilter) {
        priceFilter.addEventListener('change', () => {
            filterPlaces(placesList, priceFilter.value, feedback);
        });
    }

    try {
        const places = await fetchPlaces(token);
        renderPlaces(placesList, places);
        filterPlaces(placesList, priceFilter ? priceFilter.value : 'all', feedback);
    } catch (error) {
        placesList.innerHTML = '';
        feedback.hidden = false;
        feedback.textContent = error.message || 'Unable to load places right now.';
        feedback.className = 'form-feedback is-error';
    }
}

function toggleLoginVisibility(isAuthenticated) {
    const loginLink = document.getElementById('login-link');
    const loginButton = document.getElementById('login-button');

    [loginLink, loginButton].forEach((element) => {
        if (!element) {
            return;
        }

        element.classList.toggle('is-authenticated', isAuthenticated);
        element.setAttribute('aria-hidden', isAuthenticated ? 'true' : 'false');
    });
}

async function fetchPlaces(token) {
    const headers = {};
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${getApiBaseUrl()}/places`, { headers });
    const data = await parseResponse(response);

    if (!response.ok) {
        const message = typeof data.error === 'string' ? data.error : 'Failed to fetch places.';
        throw new Error(message);
    }

    if (!Array.isArray(data)) {
        throw new Error('Unexpected places response from the API.');
    }

    return data;
}

function renderPlaces(placesList, places) {
    placesList.innerHTML = '';

    if (!places.length) {
        return;
    }

    places.forEach((place, index) => {
        const card = document.createElement('article');
        const mediaClass = getMediaClass(index);
        const price = Number(place.price_by_night) || 0;
        const ownerEmail = place.owner && place.owner.email ? place.owner.email : 'Unknown host';
        const description = place.description || 'No description is available for this place yet.';

        card.className = 'place-card';
        card.dataset.price = String(price);
        card.innerHTML = `
            <div class="card-media ${mediaClass}" aria-hidden="true"></div>
            <div class="card-content">
                <h3>${escapeHtml(place.name || 'Unnamed place')}</h3>
                <p class="price-tag">$${price} / night</p>
                <div class="card-meta">
                    <span>Host: ${escapeHtml(ownerEmail)}</span>
                    <span>${Array.isArray(place.amenities) ? place.amenities.length : 0} amenities</span>
                </div>
                <p>${escapeHtml(description)}</p>
                <div class="card-actions">
                    <a href="place.html?id=${encodeURIComponent(place.id || '')}" class="details-button">View Details</a>
                </div>
            </div>
        `;

        placesList.appendChild(card);
    });
}

function filterPlaces(placesList, selectedPrice, feedback) {
    const cards = Array.from(placesList.querySelectorAll('.place-card'));
    const maxPrice = selectedPrice === 'all' ? Number.POSITIVE_INFINITY : Number(selectedPrice);

    let visibleCount = 0;

    cards.forEach((card) => {
        const nightlyPrice = Number(card.dataset.price) || 0;
        const shouldShow = nightlyPrice <= maxPrice;

        card.classList.toggle('is-hidden', !shouldShow);
        if (shouldShow) {
            visibleCount += 1;
        }
    });

    if (!feedback) {
        return;
    }

    feedback.hidden = false;

    if (!cards.length) {
        feedback.textContent = 'No places are available yet.';
        feedback.className = 'form-feedback';
        return;
    }

    if (!visibleCount) {
        feedback.textContent = 'No places match the selected price.';
        feedback.className = 'form-feedback is-error';
        return;
    }

    feedback.textContent = `Showing ${visibleCount} place${visibleCount === 1 ? '' : 's'}.`;
    feedback.className = 'form-feedback is-success';
}

function getMediaClass(index) {
    const mediaClasses = ['media-loft', 'media-courtyard', 'media-cliff'];
    return mediaClasses[index % mediaClasses.length];
}

function getCookie(name) {
    const cookieString = document.cookie || '';
    const cookies = cookieString.split('; ');

    for (const cookie of cookies) {
        if (!cookie) {
            continue;
        }

        const [key, ...valueParts] = cookie.split('=');
        if (key === name) {
            return decodeURIComponent(valueParts.join('='));
        }
    }

    return null;
}

function getLoginUrl() {
    const apiBaseUrl = getApiBaseUrl();
    return `${apiBaseUrl}/auth/login`;
}

function getApiBaseUrl() {
    const metaTag = document.querySelector('meta[name="api-base-url"]');
    if (metaTag && metaTag.content) {
        return metaTag.content.replace(/\/$/, '');
    }

    if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
        return `${window.location.origin}/api/v1`;
    }

    return 'http://127.0.0.1:5000/api/v1';
}

async function parseResponse(response) {
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
        return response.json();
    }

    const text = await response.text();
    return text ? { error: text } : {};
}

function setCookie(name, value, maxAgeDays) {
    const maxAge = maxAgeDays * 24 * 60 * 60;
    const encodedValue = encodeURIComponent(value);
    const secureFlag = window.location.protocol === 'https:' ? '; Secure' : '';
    document.cookie = `${name}=${encodedValue}; Max-Age=${maxAge}; Path=/; SameSite=Lax${secureFlag}`;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
