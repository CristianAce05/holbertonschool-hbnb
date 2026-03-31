document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const placesList = document.getElementById('places-list');
    const placeDetails = document.getElementById('place-details');
    const reviewForm = document.getElementById('review-form');
    const token = getCookie('token');

    initializeAuthUI(token);

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
        window.location.href = 'index.html';
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
        window.location.href = 'index.html';
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
            window.location.href = 'index.html';
        } catch (error) {
            showFormFeedback(feedback, error.message || 'Unable to log in right now.', 'error');
            setButtonSubmitting(submitButton, false, 'Sign In');
        }
    });
}

async function setupIndexPage(placesList, token) {
    const priceFilter = document.getElementById('price-filter');
    const feedback = document.getElementById('places-feedback');

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
        showFormFeedback(feedback, error.message || 'Unable to load places right now.', 'error');
    }
}

async function setupPlacePage(token) {
    const placeId = getPlaceIdFromURL();
    const feedback = document.getElementById('place-feedback');
    const addReviewSection = document.getElementById('add-review');
    const addReviewLink = document.getElementById('add-review-link');

    if (addReviewSection) {
        addReviewSection.hidden = !token;
    }

    if (!placeId) {
        showFormFeedback(feedback, 'No place ID was provided in the URL.', 'error');
        return;
    }

    if (addReviewLink) {
        addReviewLink.href = `add_review.html?id=${encodeURIComponent(placeId)}`;
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
    token = requireAuthentication(token);
    if (!token) {
        return;
    }

    const placeId = getPlaceIdFromURL();
    const feedback = document.getElementById('review-feedback');
    const placeSelect = document.getElementById('place');
    const reviewHeading = document.getElementById('review-form-heading');
    const supportingCopy = document.getElementById('review-supporting-copy');
    const submitButton = document.getElementById('review-submit');
    const reviewInput = document.getElementById('review');

    if (!placeId) {
        window.location.href = 'index.html';
        return;
    }

    const userId = getUserIdFromToken(token);
    if (!userId) {
        window.location.href = 'index.html';
        return;
    }

    try {
        const place = await fetchPlaceDetails(token, placeId);
        populateReviewPlaceField(placeSelect, place);

        if (reviewHeading) {
            reviewHeading.textContent = `Add your review for ${place.name || 'this place'}.`;
        }

        if (supportingCopy) {
            supportingCopy.textContent = 'Only authenticated users can submit reviews. Your review will be posted to the API and kept focused on the selected place.';
        }

        showFormFeedback(feedback, 'Ready to submit your review.', 'success');
    } catch (error) {
        showFormFeedback(feedback, error.message || 'Unable to load the selected place.', 'error');
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
                placeId,
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
    const price = Number(place.price_by_night) || 0;
    const facts = buildPlaceFacts(place);
    const amenities = Array.isArray(place.amenities) ? place.amenities : [];
    const reviews = Array.isArray(place.reviews) ? place.reviews : [];

    document.title = `HBNB | ${place.name || 'Place Details'}`;

    if (placeName) {
        placeName.textContent = place.name || 'Unnamed place';
    }

    if (placeHost) {
        placeHost.textContent = `Hosted by ${ownerEmail}`;
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

    if (!cards.length) {
        showFormFeedback(feedback, 'No places are available yet.', 'success');
        return;
    }

    if (!visibleCount) {
        showFormFeedback(feedback, 'No places match the selected price.', 'error');
        return;
    }

    showFormFeedback(feedback, `Showing ${visibleCount} place${visibleCount === 1 ? '' : 's'}.`, 'success');
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

    if (place.owner && place.owner.id) {
        facts.push(`Host ID: ${place.owner.id}`);
    }

    if (place.id) {
        facts.push(`Place ID: ${place.id}`);
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

function requireAuthentication(token) {
    token = token || getCookie('token');

    if (!token) {
        window.location.href = 'index.html';
        return null;
    }

    return token;
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

function populateReviewPlaceField(placeSelect, place) {
    if (!placeSelect) {
        return;
    }

    const placeId = place && place.id ? place.id : '';
    const placeName = place && place.name ? place.name : 'Selected place';
    placeSelect.innerHTML = `<option value="${escapeHtml(placeId)}">${escapeHtml(placeName)}</option>`;
    placeSelect.value = placeId;
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
