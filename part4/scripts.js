document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (!loginForm) {
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
});

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
