const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
};

// Supported languages. Add new entries here as you add translated bundles.
const SUPPORTED_LANGS = ['es', 'en'];
const DEFAULT_LANG = 'es';

// Localized product copy shown in Stripe Checkout.
const PRODUCTS = {
    es: {
        name: 'Nino – La Anomalía (Edición Digital, Libro 1)',
        description: 'Descarga inmediata (PDF). Libro 1. Idioma: Español. (El Libro 2, Hell, llegará pronto en español.)',
    },
    en: {
        name: 'Nino Saga Digital Bundle (Books 1 & 2)',
        description: 'Instant download (PDF). Language: English.',
    },
};

const UNIT_AMOUNT = 499;   // €4.99 in cents
const CURRENCY = 'eur';

function normalizeLang(raw) {
    const l = (raw || '').toLowerCase();
    return SUPPORTED_LANGS.includes(l) ? l : DEFAULT_LANG;
}

// Per-language download link, configured as Worker vars:
//   DOWNLOAD_URL_ES, DOWNLOAD_URL_EN, ...  (falls back to PDF_DOWNLOAD_URL)
function downloadUrlFor(env, lang) {
    return env['DOWNLOAD_URL_' + lang.toUpperCase()] || env.PDF_DOWNLOAD_URL;
}

export default {
    async fetch(request, env, ctx) {
        if (request.method === 'OPTIONS') {
            return new Response(null, { headers: corsHeaders });
        }

        const url = new URL(request.url);

        // 1. Create Checkout Session
        if (request.method === 'POST' && url.pathname === '/api/create-checkout-session') {
            try {
                let body = {};
                try { body = await request.json(); } catch (_) { /* no body */ }
                const lang = normalizeLang(body.lang);
                const product = PRODUCTS[lang];

                const params = new URLSearchParams({
                    'success_url': `${env.FRONTEND_URL}/ninosaga/gracias.html?session_id={CHECKOUT_SESSION_ID}&lang=${lang}`,
                    'cancel_url': `${env.FRONTEND_URL}/ninosaga/index.html?lang=${lang}`,
                    'mode': 'payment',
                    'locale': lang, // Stripe Checkout UI language
                    'line_items[0][price_data][currency]': CURRENCY,
                    'line_items[0][price_data][product_data][name]': product.name,
                    'line_items[0][price_data][product_data][description]': product.description,
                    'line_items[0][price_data][unit_amount]': String(UNIT_AMOUNT),
                    'line_items[0][quantity]': '1',
                    'metadata[lang]': lang,
                });

                const stripeResponse = await fetch('https://api.stripe.com/v1/checkout/sessions', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${env.STRIPE_SECRET_KEY}`,
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: params.toString(),
                });

                const session = await stripeResponse.json();
                if (session.error) throw new Error(session.error.message);

                return new Response(JSON.stringify({ url: session.url }), {
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                });
            } catch (err) {
                return new Response(JSON.stringify({ error: err.message }), {
                    status: 500,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                });
            }
        }

        // 2. Validate Session and Return Download URL
        if (request.method === 'GET' && url.pathname === '/api/validate-session') {
            try {
                const sessionId = url.searchParams.get('session_id');
                if (!sessionId) {
                    return new Response(JSON.stringify({ error: 'Missing session_id' }), {
                        status: 400,
                        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                    });
                }

                const stripeResponse = await fetch(`https://api.stripe.com/v1/checkout/sessions/${sessionId}`, {
                    headers: { 'Authorization': `Bearer ${env.STRIPE_SECRET_KEY}` },
                });

                const session = await stripeResponse.json();
                if (session.error) throw new Error(session.error.message);

                if (session.payment_status === 'paid') {
                    const lang = normalizeLang(session.metadata && session.metadata.lang);
                    return new Response(JSON.stringify({
                        success: true,
                        lang,
                        downloadUrl: downloadUrlFor(env, lang),
                    }), {
                        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                    });
                } else {
                    return new Response(JSON.stringify({ success: false, error: 'Pago no completado / Payment not completed' }), {
                        status: 400,
                        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                    });
                }
            } catch (err) {
                return new Response(JSON.stringify({ error: err.message }), {
                    status: 500,
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                });
            }
        }

        return new Response('Not Found', { status: 404, headers: corsHeaders });
    }
};
