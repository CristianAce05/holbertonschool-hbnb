const APP_VERSION = '20260331c';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const placesList = document.getElementById('places-list');
    const placeDetails = document.getElementById('place-details');
    const reviewForm = document.getElementById('review-form');
    const token = getCookie('token');

    initializeAuthUI(token);
    updateNavigationLinks();
    bindNavigationHandlers();

    if (loginForm) {
        setupLoginForm(loginForm, token);
    }

    if (placesList) {
        setupIndexPage(placesList, token);
    }

    if (placeDetails) {
        setupPlacePage(token);
    }

    if (reviewForm) {
        setupReviewPage(reviewForm, token);
    }
});

function initializeAuthUI(token) {
    toggleLoginVisibility(Boolean(token));

    const logoutButton = document.getElementById('logout-button');
    if (!logoutButton) {
        return;
    }

    logoutButton.hidden = !token;

    if (logoutButton.dataset.bound === 'true') {
        return;
    }

    logoutButton.dataset.bound = 'true';
    logoutButton.addEventListener('click', () => {
        clearCookie('token');
        window.location.href = buildPageUrl('index.html');
    });
}

function toggleLoginVisibility(isAuthenticated) {
    const loginLink = document.getElementById('login-link');
    const loginButton = document.getElementById('login-button');
    const logoutButton = document.getElementById('logout-button');

    [loginLink, loginButton].forEach((element) => {
        if (!element) {
            return;
        }

        element.hidden = isAuthenticated;
        element.setAttribute('aria-hidden', isAuthenticated ? 'true' : 'false');
    });

    if (logoutButton) {
        logoutButton.hidden = !isAuthenticated;
        logoutButton.setAttribute('aria-hidden', isAuthenticated ? 'false' : 'true');
    }
}

function setupLoginForm(loginForm, token) {
    if (token) {
        window.location.href = getPostLoginDestination();
        return;
    }

    const feedback = document.getElementById('login-feedback');
    const submitButton = document.getElementById('login-submit');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            showFormFeedback(feedback, 'Enter both email and password.', 'error');
            return;
        }

        setButtonSubmitting(submitButton, true, 'Signing In...');
        showFormFeedback(feedback, 'Signing you in...', 'success');

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
            window.location.href = getPostLoginDestination();
        } catch (error) {
            showFormFeedback(feedback, error.message || 'Unable to log in right now.', 'error');
            setButtonSubmitting(submitButton, false, 'Sign In');
        }
    });
}

async function setupIndexPage(placesList, token) {
    token = requireAuthentication(token, buildLoginRedirectUrl(buildPageUrl('index.html')));
    if (!token) {
        return;
    }

    const countryFilter = document.getElementById('country-filter');
    const feedback = document.getElementById('places-feedback');

    if (countryFilter) {
        countryFilter.addEventListener('change', () => {
            filterPlaces(placesList, countryFilter.value, feedback);
        });
    }

    try {
        const places = await fetchPlaces(token);
        renderPlaces(placesList, places);
        populateCountryFilter(countryFilter, places);
        filterPlaces(placesList, countryFilter ? countryFilter.value : 'all', feedback);
    } catch (error) {
        placesList.innerHTML = '';
        showFormFeedback(feedback, error.message || 'Unable to load places right now.', 'error');
    }
}

async function setupPlacePage(token) {
    let placeId = getPlaceIdFromURL() || getStoredPlaceId();
    const feedback = document.getElementById('place-feedback');
    const addReviewSection = document.getElementById('add-review');
    const addReviewLink = document.getElementById('add-review-link');

    if (addReviewSection) {
        addReviewSection.hidden = !token;
    }

    if (!placeId) {
        try {
            const places = await fetchPlaces(token);
            if (places.length) {
                placeId = places[0].id;
                window.location.replace(buildPageUrl('place.html', { id: placeId }));
                return;
            }
        } catch (error) {
            showFormFeedback(feedback, error.message || 'Unable to load place details right now.', 'error');
            return;
        }

        showFormFeedback(feedback, 'No places are available yet.', 'error');
        return;
    }

    if (addReviewLink) {
        addReviewLink.href = buildPageUrl('add_review.html', { id: placeId });
    }

    try {
        const place = await fetchPlaceDetails(token, placeId);
        renderPlaceDetails(place);
        showFormFeedback(feedback, 'Place details loaded.', 'success');
    } catch (error) {
        showFormFeedback(feedback, error.message || 'Unable to load place details right now.', 'error');
    }
}

async function setupReviewPage(reviewForm, token) {
    token = requireAuthentication(token, buildLoginRedirectUrl(getCurrentPageTarget()));
    if (!token) {
        return;
    }

    let placeId = getPlaceIdFromURL() || getStoredPlaceId();
    const feedback = document.getElementById('review-feedback');
    const placeSelect = document.getElementById('place');
    const reviewHeading = document.getElementById('review-form-heading');
    const supportingCopy = document.getElementById('review-supporting-copy');
    const submitButton = document.getElementById('review-submit');
    const reviewInput = document.getElementById('review');

    const userId = getUserIdFromToken(token);
    if (!userId) {
        window.location.href = buildLoginRedirectUrl(getCurrentPageTarget());
        return;
    }

    try {
        const places = await fetchPlaces(token);
        if (!places.length) {
            throw new Error('No places are available to review yet.');
        }

        if (!placeId || !places.some((place) => place.id === placeId)) {
            placeId = places[0].id;
        }

        populateReviewPlaceOptions(placeSelect, places, placeId);
        updateReviewSelection(placeSelect, reviewHeading, supportingCopy);

        placeSelect.addEventListener('change', () => {
            placeId = placeSelect.value;
            storePlaceId(placeId);
            updateNavigationLinks();
            updateReviewSelection(placeSelect, reviewHeading, supportingCopy);
            updateCurrentPagePlaceId(placeId);
        });

        showFormFeedback(feedback, 'Ready to submit your review.', 'success');
    } catch (error) {
        showFormFeedback(feedback, error.message || 'Unable to load available places.', 'error');
        if (placeSelect) {
            placeSelect.innerHTML = '<option value="">Unable to load place</option>';
        }
        setButtonSubmitting(submitButton, true, 'Unavailable');
        return;
    }

    reviewForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const reviewText = reviewInput ? reviewInput.value.trim() : '';
        if (!reviewText) {
            showFormFeedback(feedback, 'Enter your review before submitting.', 'error');
            return;
        }

        setButtonSubmitting(submitButton, true, 'Submitting...');
        showFormFeedback(feedback, 'Submitting your review...', 'success');

        try {
            await submitReview(token, {
                placeId: placeSelect ? placeSelect.value : placeId,
                userId,
                text: reviewText
            });

            reviewForm.reset();
            if (placeSelect) {
                placeSelect.value = placeId;
            }
            showFormFeedback(feedback, 'Review submitted successfully.', 'success');
        } catch (error) {
            showFormFeedback(feedback, error.message || 'Failed to submit review.', 'error');
        } finally {
            setButtonSubmitting(submitButton, false, 'Submit Review');
        }
    });
}

async function fetchPlaces(token) {
    const headers = buildAuthHeaders(token);
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

async function fetchPlaceDetails(token, placeId) {
    const headers = buildAuthHeaders(token);
    const response = await fetch(`${getApiBaseUrl()}/places/${encodeURIComponent(placeId)}`, { headers });
    const data = await parseResponse(response);

    if (!response.ok) {
        const message = typeof data.error === 'string' ? data.error : 'Failed to fetch place details.';
        throw new Error(message);
    }

    if (!data || typeof data !== 'object' || Array.isArray(data)) {
        throw new Error('Unexpected place response from the API.');
    }

    return data;
}

async function submitReview(token, payload) {
    const response = await fetch(`${getApiBaseUrl()}/reviews`, {
        method: 'POST',
        headers: {
            ...buildAuthHeaders(token),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            place_id: payload.placeId,
            user_id: payload.userId,
            text: payload.text
        })
    });

    const data = await parseResponse(response);

    if (!response.ok) {
        const message = typeof data.error === 'string' ? data.error : 'Failed to submit review.';
        throw new Error(message);
    }

    return data;
}

function buildAuthHeaders(token) {
    const headers = {};
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    return headers;
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
        const country = getPlaceCountry(place);
        const ownerEmail = place.owner && place.owner.email ? place.owner.email : 'Unknown host';
        const description = place.description || 'No description is available for this place yet.';

        card.className = 'place-card';
        card.dataset.country = normalizeCountry(country);
        card.innerHTML = `
            <div class="card-media ${mediaClass}" aria-hidden="true"></div>
            <div class="card-content">
                <h3>${escapeHtml(place.name || 'Unnamed place')}</h3>
                <p class="price-tag">$${price} / night</p>
                <div class="card-meta">
                    <span>Host: ${escapeHtml(ownerEmail)}</span>
                    <span>Country: ${escapeHtml(country)}</span>
                    <span>${Array.isArray(place.amenities) ? place.amenities.length : 0} amenities</span>
                </div>
                <p>${escapeHtml(description)}</p>
                <div class="card-actions">
                    <a href="${escapeHtml(buildPageUrl('place.html', { id: place.id || '' }))}" class="details-button">View Details</a>
                </div>
            </div>
        `;

        placesList.appendChild(card);
    });
}

function renderPlaceDetails(place) {
    const placeName = document.getElementById('place-name');
    const placeHost = document.getElementById('place-host');
    const placePrice = document.getElementById('place-price');
    const placeDescription = document.getElementById('place-description');
    const placeFacts = document.getElementById('place-facts');
    const placeAmenities = document.getElementById('place-amenities');
    const reviewsList = document.getElementById('reviews-list');
    const placeHero = document.getElementById('place-hero');

    const ownerEmail = place.owner && place.owner.email ? place.owner.email : 'Unknown host';
    const country = getPlaceCountry(place);
    const price = Number(place.price_by_night) || 0;
    const facts = buildPlaceFacts(place);
    const amenities = Array.isArray(place.amenities) ? place.amenities : [];
    const reviews = Array.isArray(place.reviews) ? place.reviews : [];

    storePlaceId(place.id || '');
    updateNavigationLinks();

    document.title = `HBNB | ${place.name || 'Place Details'}`;

    if (placeName) {
        placeName.textContent = place.name || 'Unnamed place';
    }

    if (placeHost) {
        placeHost.textContent = `Hosted by ${ownerEmail}${country !== 'Unknown' ? ` in ${country}` : ''}`;
    }

    if (placePrice) {
        placePrice.textContent = `$${price} / night`;
    }

    if (placeDescription) {
        const descriptionText = place.description || 'No description is available for this place yet.';
        placeDescription.innerHTML = `<div class="detail-stack"><p>${escapeHtml(descriptionText)}</p></div>`;
    }

    if (placeFacts) {
        placeFacts.innerHTML = facts.map((fact) => `<li>${escapeHtml(fact)}</li>`).join('');
        placeFacts.classList.toggle('is-empty', !facts.length);
    }

    if (placeAmenities) {
        if (amenities.length) {
            placeAmenities.innerHTML = amenities.map((amenity) => `<li>${escapeHtml(amenity.name || 'Unnamed amenity')}</li>`).join('');
            placeAmenities.classList.remove('is-empty');
        } else {
            placeAmenities.innerHTML = '<li>No amenities listed.</li>';
            placeAmenities.classList.add('is-empty');
        }
    }

    if (reviewsList) {
        if (reviews.length) {
            reviewsList.classList.remove('is-empty');
            reviewsList.innerHTML = reviews.map((review) => {
                const author = review.user_name || review.user || review.user_id || 'Guest';
                const text = review.text || review.comment || 'No review text provided.';
                return `
                    <article class="review-card">
                        <h3>${escapeHtml(author)}</h3>
                        <p>${escapeHtml(text)}</p>
                    </article>
                `;
            }).join('');
        } else {
            reviewsList.classList.add('is-empty');
            reviewsList.innerHTML = '<p>No reviews yet for this place.</p>';
        }
    }

    if (placeHero) {
        placeHero.className = `place-hero ${getMediaClassFromSeed(place.id || place.name || '0')}`;
    }
}

function filterPlaces(placesList, selectedCountry, feedback) {
    const cards = Array.from(placesList.querySelectorAll('.place-card'));
    const normalizedCountry = normalizeCountry(selectedCountry);

    let visibleCount = 0;

    cards.forEach((card) => {
        const cardCountry = normalizeCountry(card.dataset.country || 'unknown');
        const shouldShow = normalizedCountry === 'all' || cardCountry === normalizedCountry;

        card.classList.toggle('is-hidden', !shouldShow);
        if (shouldShow) {
            visibleCount += 1;
        }
    });

    if (!feedback) {
        return;
    }

    if (!cards.length) {
        showFormFeedback(feedback, 'No places are available yet.', 'success');
        return;
    }

    if (!visibleCount) {
        showFormFeedback(feedback, 'No places match the selected country.', 'error');
        return;
    }

    showFormFeedback(feedback, `Showing ${visibleCount} place${visibleCount === 1 ? '' : 's'}.`, 'success');
}

function populateCountryFilter(countryFilter, places) {
    if (!countryFilter) {
        return;
    }

    const countries = Array.from(
        new Set(
            places
                .map((place) => getPlaceCountry(place))
                .filter((country) => country && country !== 'Unknown')
                .sort((left, right) => left.localeCompare(right))
        )
    );

    countryFilter.innerHTML = '<option value="all">All</option>';

    countries.forEach((country) => {
        const option = document.createElement('option');
        option.value = country;
        option.textContent = country;
        countryFilter.appendChild(option);
    });
}

function getMediaClass(index) {
    const mediaClasses = ['media-loft', 'media-courtyard', 'media-cliff'];
    return mediaClasses[index % mediaClasses.length];
}

function getMediaClassFromSeed(seed) {
    let total = 0;
    const value = String(seed);

    for (let index = 0; index < value.length; index += 1) {
        total += value.charCodeAt(index);
    }

    return getMediaClass(total);
}

function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

function buildPlaceFacts(place) {
    const facts = [];
    const country = getPlaceCountry(place);

    if (place.owner && place.owner.id) {
        facts.push(`Host ID: ${place.owner.id}`);
    }

    if (place.id) {
        facts.push(`Place ID: ${place.id}`);
    }

    if (country !== 'Unknown') {
        facts.push(`Country: ${country}`);
    }

    if (Array.isArray(place.reviews)) {
        facts.push(`${place.reviews.length} review${place.reviews.length === 1 ? '' : 's'}`);
    }

    if (Array.isArray(place.amenities)) {
        facts.push(`${place.amenities.length} amenit${place.amenities.length === 1 ? 'y' : 'ies'}`);
    }

    if (!facts.length) {
        facts.push('No additional facts are available for this place.');
    }

    return facts;
}

function requireAuthentication(token, redirectTarget) {
    token = token || getCookie('token');

    if (!token) {
        window.location.href = redirectTarget || 'index.html';
        return null;
    }

    return token;
}

function getPlaceCountry(place) {
    if (!place || typeof place !== 'object') {
        return 'Unknown';
    }

    const country = place.country
        || (place.location && place.location.country)
        || (place.address && place.address.country);

    if (typeof country !== 'string' || !country.trim()) {
        return 'Unknown';
    }

    return country.trim();
}

function normalizeCountry(value) {
    const normalized = String(value || 'all').trim().toLowerCase();
    return normalized || 'all';
}

function getUserIdFromToken(token) {
    const payload = decodeJwtPayload(token);
    if (!payload || typeof payload !== 'object') {
        return null;
    }

    return payload.sub || payload.identity || null;
}

function decodeJwtPayload(token) {
    const parts = String(token || '').split('.');
    if (parts.length < 2) {
        return null;
    }

    try {
        const normalized = parts[1].replace(/-/g, '+').replace(/_/g, '/');
        const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=');
        const decoded = atob(padded);
        return JSON.parse(decoded);
    } catch (error) {
        return null;
    }
}

function populateReviewPlaceOptions(placeSelect, places, selectedPlaceId) {
    if (!placeSelect) {
        return;
    }

    placeSelect.disabled = false;
    placeSelect.innerHTML = places.map((place) => {
        const isSelected = place.id === selectedPlaceId ? ' selected' : '';
        return `<option value="${escapeHtml(place.id || '')}"${isSelected}>${escapeHtml(place.name || 'Unnamed place')}</option>`;
    }).join('');
    placeSelect.value = selectedPlaceId || (places[0] && places[0].id) || '';
    storePlaceId(placeSelect.value);
    updateNavigationLinks();
    updateCurrentPagePlaceId(placeSelect.value);
}

function updateReviewSelection(placeSelect, reviewHeading, supportingCopy) {
    if (!placeSelect) {
        return;
    }

    const selectedOption = placeSelect.options[placeSelect.selectedIndex];
    const placeName = selectedOption ? selectedOption.textContent : 'this place';

    if (reviewHeading) {
        reviewHeading.textContent = `Add your review for ${placeName}.`;
    }

    if (supportingCopy) {
        supportingCopy.textContent = 'Only authenticated users can submit reviews. Select a place, share what mattered during the stay, and your review will be posted to the API.';
    }
}

function buildLoginRedirectUrl(target) {
    return buildPageUrl('login.html', { next: target || getCurrentPageTarget() });
}

function getPostLoginDestination() {
    const params = new URLSearchParams(window.location.search);
    const next = params.get('next');

    if (!next || /^(https?:)?\/\//i.test(next)) {
        return buildPageUrl('index.html');
    }

    return next;
}

function getCurrentPageTarget() {
    const path = window.location.pathname.split('/').pop() || 'index.html';
    const params = new URLSearchParams(window.location.search);
    params.delete('v');
    const query = params.toString();
    return `${path}${query ? `?${query}` : ''}`;
}

function getStoredPlaceId() {
    try {
        return window.localStorage.getItem('lastPlaceId');
    } catch (error) {
        return null;
    }
}

function storePlaceId(placeId) {
    if (!placeId) {
        return;
    }

    try {
        window.localStorage.setItem('lastPlaceId', placeId);
    } catch (error) {
        // Ignore storage failures and continue using the current page state.
    }
}

function updateNavigationLinks() {
    const currentOrStoredPlaceId = getPlaceIdFromURL() || getStoredPlaceId();
    const placeLink = document.querySelector('.main-nav a[href="place.html"], .main-nav a[href^="place.html?id="], .main-nav a[href^="place.html?v="]');
    const reviewLink = document.querySelector('.main-nav a[href="add_review.html"], .main-nav a[href^="add_review.html?id="], .main-nav a[href^="add_review.html?v="]');
    const placesLink = document.querySelector('.main-nav a[href="index.html"], .main-nav a[href^="index.html?v="]');
    const brandLink = document.querySelector('.brand-link');
    const loginButton = document.getElementById('login-button');
    const loginLink = document.getElementById('login-link');

    if (placesLink) {
        placesLink.href = buildPageUrl('index.html');
    }

    if (brandLink) {
        brandLink.href = buildPageUrl('index.html');
    }

    if (loginButton) {
        loginButton.href = buildPageUrl('login.html');
    }

    if (loginLink) {
        loginLink.href = buildPageUrl('login.html');
    }

    if (placeLink && currentOrStoredPlaceId) {
        placeLink.href = buildPageUrl('place.html', { id: currentOrStoredPlaceId });
    } else if (placeLink) {
        placeLink.href = buildPageUrl('place.html');
    }

    if (reviewLink && currentOrStoredPlaceId) {
        reviewLink.href = buildPageUrl('add_review.html', { id: currentOrStoredPlaceId });
    } else if (reviewLink) {
        reviewLink.href = buildPageUrl('add_review.html');
    }
}

function updateCurrentPagePlaceId(placeId) {
    if (!placeId || !window.history || !window.history.replaceState) {
        return;
    }

    const path = window.location.pathname.split('/').pop() || 'index.html';
    if (path !== 'add_review.html') {
        return;
    }

    const nextUrl = buildPageUrl('add_review.html', { id: placeId });
    window.history.replaceState({}, '', nextUrl);
}

function buildPageUrl(page, params) {
    const url = new URL(page, window.location.href);
    url.searchParams.set('v', APP_VERSION);

    Object.entries(params || {}).forEach(([key, value]) => {
        if (value === null || value === undefined || value === '') {
            url.searchParams.delete(key);
            return;
        }

        url.searchParams.set(key, value);
    });

    const fileName = url.pathname.split('/').pop() || page;
    return `/${fileName}${url.search}`;
}

function bindNavigationHandlers() {
    const navigationTargets = document.querySelectorAll(
        '.brand-link, .main-nav a, a.details-button, #login-button, #login-link'
    );

    navigationTargets.forEach((element) => {
        if (!element || element.dataset.navBound === 'true') {
            return;
        }

        element.dataset.navBound = 'true';
        element.addEventListener('click', (event) => {
            const href = element.getAttribute('href');
            if (!href) {
                return;
            }

            event.preventDefault();
            window.location.assign(href);
        });
    });
}

function showFormFeedback(feedbackElement, message, type) {
    if (!feedbackElement) {
        return;
    }

    feedbackElement.hidden = false;
    feedbackElement.textContent = message;
    feedbackElement.className = `form-feedback ${type === 'error' ? 'is-error' : 'is-success'}`;
}

function setButtonSubmitting(button, isSubmitting, label) {
    if (!button) {
        return;
    }

    button.disabled = isSubmitting;
    button.textContent = label;
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
    return `${getApiBaseUrl()}/auth/login`;
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

function clearCookie(name) {
    document.cookie = `${name}=; Max-Age=0; Path=/; SameSite=Lax`;
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
