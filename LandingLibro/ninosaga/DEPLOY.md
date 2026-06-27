# Saga Nino — Deploy & Config Guide

Everything in the code is fixed. The steps below are the parts only **you** can do,
because they need your Cloudflare login, your Stripe key, and your real download link.
**Never paste those secrets into a chat — only into your own terminal / dashboards.**

---

## 1. One-time setup (your machine)

```bash
# from the project folder:
cd worker-stripe

# log in to Cloudflare (opens your browser — no token to copy/paste)
npx wrangler login
```

## 2. Set your real values

Open `worker-stripe/wrangler.toml` and set the **per-language** download links:

```toml
FRONTEND_URL     = "https://jesusguzmanautor.com"   # confirm this is correct
DOWNLOAD_URL_ES  = "https://YOUR-SECURE-LINK/saga-nino-bundle-es.zip"  # Spanish bundle
DOWNLOAD_URL_EN  = "https://YOUR-SECURE-LINK/saga-nino-bundle-en.zip"  # English bundle
PDF_DOWNLOAD_URL = "https://YOUR-SECURE-LINK/saga-nino-bundle-es.zip"  # fallback
```

> The page now has an ES/EN language selector. The buyer's choice is sent to the Worker,
> which charges in that language and returns the matching bundle above.
> **The Spanish bundle should only include books that exist in Spanish.** Until Nino – Hell
> is translated to Spanish, the ES bundle delivers The Anomaly (ES) only — adjust the ES
> bundle contents / wording accordingly, or hold ES checkout until Hell (ES) is ready.

Then add your Stripe secret key (you'll be prompted to paste it — it stays local):

```bash
npx wrangler secret put STRIPE_SECRET_KEY
```

> Use your **live** key (`sk_live_…`) for real sales, or a **test** key (`sk_test_…`) while testing.

## 3. Deploy

```bash
npx wrangler deploy
```

Wrangler prints the deployed URL, e.g. `https://ninosaga-worker.<your-subdomain>.workers.dev`.

## 4. Confirm the Worker URL matches the site

The site currently calls `https://ninosaga-worker.jaguzman123.workers.dev` in two files:

- `index.html` (checkout button)
- `gracias.html` (download validation)

If your deployed subdomain is **not** `jaguzman123`, update both files to match, then re-upload the site.

## 5. Confirm the site path

The Worker sends buyers to `…/ninosaga/gracias.html` after payment. This assumes the
site lives at **https://jesusguzmanautor.com/ninosaga/**.

- If that's correct → nothing to do.
- If the site is at the **root** (e.g. jesusguzmanautor.com/), edit `worker-stripe/src/index.js`
  lines 40–41 (`success_url`, `cancel_url`) and the "Volver" links in `gracias.html` to drop `/ninosaga`.

## 6. Test before going live

1. Open the page, click **Comprar Ahora**.
2. Use Stripe test card `4242 4242 4242 4242`, any future date/CVC.
3. Confirm you're redirected to `gracias.html` and the **download button works**.
4. Switch to your live Stripe key and redeploy when satisfied.

---

## What was changed in the code
- Price corrected to **€4.99** (`unit_amount: 499` in the Worker + `4,99€` on the page).
- Language claim corrected to **English only** (was advertising 7 languages we don't have).
- Real book covers wired in (`assets/nino-anomaly-cover.jpg`, `assets/nino-hell-cover.jpg`).
- Checkout button JS hardened (`comprarSaga(event)`).
- Added an FAQ section and a clearer price block for conversions.
- Thank-you page wording corrected.

## Still on you (not done here)
- Real `PDF_DOWNLOAD_URL` (the secure file link).
- Stripe secret key via `wrangler secret put`.
- Verifying the workers.dev subdomain and the `/ninosaga/` path.
- A human review of all buyer-facing copy and the refund terms before going live.
