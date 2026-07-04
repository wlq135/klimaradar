# KlimaRadar Launch Runbook

Use this runbook to take KlimaRadar from staging to public launch. All file paths below are absolute and refer to this repository.

Reference files:
- `d:\py_practice\bywork\EU_AC\render.yaml`
- `d:\py_practice\bywork\EU_AC\railway.json`
- `d:\py_practice\bywork\EU_AC\launch_content\email_invite.md`
- `d:\py_practice\bywork\EU_AC\launch_content\press_pitch.md`
- `d:\py_practice\bywork\EU_AC\launch_content\reddit_de.md`
- `d:\py_practice\bywork\EU_AC\launch_content\reddit_fr.md`
- `d:\py_practice\bywork\EU_AC\launch_content\twitter_x.md`
- `d:\py_practice\bywork\EU_AC\launch_content\deal_forums.md`

---

## 1. Pre-Launch Checklist

Complete all items before deploying production traffic.

### 1.1 Domain
- [x] Decide domain: `klima-radar.com` (recommended).
- [ ] Register `klima-radar.com` with Cloudflare, Namecheap, or your existing provider.
- [ ] Add `klima-radar.com` as a Custom Domain in Render (see section 3.1).
- [ ] Add the DNS records your provider asks for, then wait for Render to verify.
- [ ] Enable Cloudflare proxy only **after** Render custom-domain verification succeeds.

### 1.2 Environment Variables
Match the keys in `render.yaml` and Railway dashboard exactly.

| Key | Source | Notes |
|-----|--------|-------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./klimaradar.db` (default in `render.yaml`) | Upgrade to PostgreSQL before 1,000+ active alerts |
| `BASE_URL` | `https://klima-radar.com` | Must match the canonical domain users see. No trailing slash. |
| `SENDGRID_API_KEY` | SendGrid dashboard | Use domain-authenticated sending domain |
| `AMAZON_DE_AFFILIATE_TAG` | Amazon Associates DE | Replace placeholder; verify links include `tag=` |
| `MEDIAMARKT_DE_AFFILIATE_TAG` | Awin / affiliate network | Replace placeholder |
| `BOULANGER_FR_AFFILIATE_TAG` | Awin / Effiliation | Replace placeholder |
| `DARTY_FR_AFFILIATE_TAG` | Awin / Effiliation | Replace placeholder |
| `PLAYWRIGHT_PROXY_SERVER` | Proxy provider for FR retailers | e.g. `http://proxy.example.com:8080` |
| `PLAYWRIGHT_PROXY_USERNAME` | Proxy provider | Only if required |
| `PLAYWRIGHT_PROXY_PASSWORD` | Proxy provider | Only if required |

- [ ] No secrets committed to `render.yaml` or `railway.json` (they use `sync: false` / dashboard variables).
- [ ] `BASE_URL` does **not** have a trailing slash.

### 1.3 Real Affiliate Tags
- [ ] Apply for Amazon Associates DE and FR.
- [ ] Apply for Awin/Effiliation for MediaMarkt, Boulanger, Darty.
- [ ] Generate tracking links and confirm affiliate IDs render in outgoing emails.
- [ ] Add an affiliate disclosure in the footer and on the signup page (EU consumer law / platform rules).

### 1.4 SendGrid
- [ ] Create a SendGrid account.
- [ ] Complete domain authentication (DKIM, SPF, DMARC aligned).
- [ ] Create a single sender or dynamic template for stock alerts.
- [ ] Whitelist the production `BASE_URL` in click-tracking settings if needed.
- [ ] Run a test send to Gmail, Outlook, GMX, and Yahoo; check spam folders.

### 1.5 French Proxy (FR)
- [ ] Confirm `PLAYWRIGHT_PROXY_*` values point to a French-residential or French-datacenter proxy.
- [ ] Verify Boulanger and Darty product pages load through the proxy without blocking.
- [ ] Set retry/backoff and rotate proxy sessions if you see 403s.
- [ ] Log a canary scrape to confirm prices and stock status are extracted.

---

## 2. Deploy to Render or Railway Step-by-Step

### 2.1 Render (uses `render.yaml`)

1. Push code to GitHub at `https://github.com/YOUR_USERNAME/klimaradar`.
2. In Render dashboard, click **New +** → **Blueprint**.
3. Connect the repository. Render reads `render.yaml`.
4. Replace placeholder env vars in the Render dashboard:
   - `SENDGRID_API_KEY`
   - `AMAZON_DE_AFFILIATE_TAG`
   - `MEDIAMARKT_DE_AFFILIATE_TAG`
   - `BOULANGER_FR_AFFILIATE_TAG`
   - `DARTY_FR_AFFILIATE_TAG`
   - `PLAYWRIGHT_PROXY_SERVER`
   - `PLAYWRIGHT_PROXY_USERNAME`
   - `PLAYWRIGHT_PROXY_PASSWORD`
5. Update `BASE_URL` to your final domain when ready, otherwise keep `https://klimaradar.onrender.com`.
6. Click **Apply** and wait for the first deploy.
7. Confirm health check returns `200 OK` from `GET /api/health`.
8. (Optional) Set **Auto-Deploy** to `on` for the main branch.

### 2.2 Railway (uses `railway.json`)

1. Push code to GitHub.
2. In Railway dashboard, click **New Project** → **Deploy from GitHub repo**.
3. Select the repository; Railway detects `railway.json` and uses Dockerfile builder.
4. Go to **Variables** and add the same keys listed in section 1.2.
5. Generate a public domain under **Settings → Environment → Generate Domain**, or add a custom domain.
6. Deploy and wait for the health check on `/api/health` to pass.
7. Verify `railway.json` `startCommand` matches your app: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

### 2.3 Post-Deploy Smoke Tests
- [ ] `GET /api/health` returns 200.
- [ ] Home page loads in < 2 s.
- [ ] Signup form accepts an email and stores the alert.
- [ ] One manual alert send reaches inbox (not spam).
- [ ] Affiliate links in emails include the correct `tag=` parameters.
- [ ] French scraper returns a product result through the proxy.

---

## 3. Domain and DNS Setup

### 3.1 Render Custom Domain

We will use Render to host the app and Cloudflare (recommended) for DNS.

#### 3.1.1 Add the domain in Render
1. Push your code to GitHub first and deploy the service from `render.yaml`.
2. In the Render dashboard, open the `klimaradar` service → **Settings** → **Custom Domains**.
3. Click **Add Custom Domain** and enter `klima-radar.com`.
4. Render will show a verification target like `klima-radar.com.onrender.com` or similar CNAME.
   Copy this value — you will need it in Cloudflare.
5. Repeat for `www.klima-radar.com` if you want `www` to work.

#### 3.1.2 Add DNS records in Cloudflare
1. Log in to Cloudflare, select the `klima-radar.com` domain.
2. Go to **DNS** → **Records**.
3. Add a **CNAME** record:
   - Name: `@` (root/apex)
   - Target: the CNAME value Render gave you (e.g. `klima-radar.com.onrender.com`)
   - TTL: Auto
   - Proxy status: **DNS only** (grey cloud) during Render verification
4. Add a second **CNAME** record:
   - Name: `www`
   - Target: `klima-radar.com` (or the Render CNAME)
   - TTL: Auto
5. Wait 30 seconds to 5 minutes, then click **Verify** in Render.
6. Once Render says the domain is verified and HTTPS is active, you can optionally turn on the Cloudflare proxy (orange cloud) for caching and DDoS protection.

#### 3.1.3 Important notes
- Keep Cloudflare on **DNS only** until Render verification succeeds.
- Do **not** enable Cloudflare proxy before verification, or Render may fail to issue the certificate.
- If your DNS provider does not allow CNAME at the root, use an `ANAME`/`ALIAS` record, or switch to Cloudflare which supports CNAME flattening.

### 3.2 Railway Custom Domain (if you choose Railway instead)
1. In Railway project **Settings → Domains**, click **Custom Domain**.
2. Enter `klima-radar.com`.
3. Railway gives DNS records (CNAME or A).
4. Add the records at your DNS provider.
5. Verify in Railway and enable HTTPS.

### 3.3 Domain Checklist
- [ ] `https://klima-radar.com` loads without certificate warnings.
- [ ] `http://` redirects to `https://`.
- [ ] `www` redirects to apex (or vice versa) consistently.
- [ ] `BASE_URL` env var matches the canonical domain.
- [ ] Update social-share links and press pitch with the canonical URL.

---

## 4. Google Search Console + Sitemap Submission

1. Go to [Google Search Console](https://search.google.com/search-console).
2. Add property as **Domain** (`klima-radar.com`) or **URL-prefix** (`https://klima-radar.com/`).
3. Verify ownership via DNS TXT record or HTML file upload.
4. Ensure the site exposes a sitemap at `/sitemap.xml`.
5. Submit `https://klima-radar.com/sitemap.xml` in Search Console.
6. Add an RSS feed or lastmod dates if the listings change frequently.
7. Request indexing for the home page and key listing pages.

### 4.1 SEO Launch Checklist
- [ ] Each product/listing page has unique `<title>` and `<meta name="description">`.
- [ ] No `noindex` tags remain on public pages.
- [ ] Robots.txt allows `/sitemap.xml` and public listing paths.
- [ ] Site passes [Google Mobile-Friendly Test](https://search.google.com/test/mobile-friendly).
- [ ] Core Web Vitals (LCP, CLS, INP) are acceptable.

---

## 5. Analytics Setup

### 5.1 Plausible (recommended, privacy-first)
1. Sign up at [Plausible Analytics](https://plausible.io).
2. Add domain `klima-radar.com`.
3. Copy the script snippet.
4. Add the snippet to the `<head>` of every page.
5. Enable outbound link tracking to monitor affiliate clicks.
6. Set up a custom event: `alert_signup`, `alert_trigger`, `affiliate_click`.

### 5.2 Google Analytics 4 (GA4)
1. Create a GA4 property in [Google Analytics](https://analytics.google.com).
2. Add the GA4 script to the `<head>` of every page.
3. Enable cookie consent banner for EU users (GDPR).
4. Configure conversion events:
   - `sign_up` (alert created)
   - `purchase_intent` (affiliate link click)
   - `alert_sent` (when email fires)

### 5.3 Cookie Consent
- [ ] Use a CMP or simple banner that requires opt-in for analytics cookies.
- [ ] Plausible can run without cookies, simplifying compliance.
- [ ] Document consent in your privacy policy.

### 5.4 Monitoring
- [ ] Add uptime monitoring (e.g. UptimeRobot or Better Uptime) pinging `/api/health` every 5 minutes.
- [ ] Add error tracking (e.g. Sentry) to capture scraper failures and 500s.

---

## 6. Launch Day Sequence

Post in this order, spaced 20–60 minutes apart. Choose the country that matches the current heat-wave conversation.

### Phase A — Soft Launch (T+0 to T+2 hours)
1. **Personal network email** — send `d:\py_practice\bywork\EU_AC\launch_content\email_invite.md` to 10–20 early testers.
2. **Post to Reddit**
   - Germany: use `d:\py_practice\bywork\EU_AC\launch_content\reddit_de.md`
   - France: use `d:\py_practice\bywork\EU_AC\launch_content\reddit_fr.md`
   - Post to `r/germany`, `r/france`, or city subreddits (`r/berlin`, `r/paris`, `r/munich`).
   - Post the link as a **comment**, not in the main body, to avoid auto-removal.
   - Reply to every comment for the first 2 hours.
3. **Deal forums**
   - MyDealz (DE): `d:\py_practice\bywork\EU_AC\launch_content\deal_forums.md`
   - Dealabs (FR): `d:\py_practice\bywork\EU_AC\launch_content\deal_forums.md`
   - Follow each forum's rules on self-promotion and affiliate disclosure.

### Phase B — Public Amplification (T+2 to T+4 hours)
4. **Twitter / X** — use `d:\py_practice\bywork\EU_AC\launch_content\twitter_x.md`
   - Post the English thread first.
   - Quote-tweet with German and French variants if you have followers in those markets.
   - Pin the launch tweet to your profile.
5. **Email press pitch** — send `d:\py_practice\bywork\EU_AC\launch_content\press_pitch.md` to local journalists covering consumer tech, climate, or heat waves.

### Phase C — Engagement (T+4 to T+24 hours)
6. Reply to all comments and DMs.
7. Fix any reported bug within 24 hours.
8. Post an update thread with any quick wins (e.g. "200 alerts created in 6 hours").

### Timing Tips
- Launch on a **Tuesday, Wednesday, or Thursday** between 09:00 and 12:00 local time.
- Avoid public holidays and major news events.
- Time Reddit posts for when target subreddits are most active (use tools like Later for Reddit or manual observation).
- If a heat wave is forecast, launch 2–3 days before temperatures peak.

---

## 7. First 7 Days

### 7.1 Metrics to Watch Daily

| Metric | Tool | Target / Note |
|--------|------|---------------|
| Signups | Database / Plausible / GA4 | Track daily growth rate |
| Alert triggers | App logs / Plausible events | Should correlate with stock drops |
| Email delivery rate | SendGrid | Keep > 95%; watch bounces |
| Spam complaint rate | SendGrid | Keep < 0.1% |
| Unique visitors | Plausible / GA4 | Watch referral sources |
| Affiliate clicks | Plausible outbound tracking | First monetization signal |
| Uptime | UptimeRobot | Target 99.9% |
| Errors | Sentry / logs | Zero unhandled 500s |
| Scraper success rate | Logs | DE > 95%, FR > 90% |
| Page load time | Plausible / Lighthouse | LCP < 2.5 s |

### 7.2 Responding to Stock Alerts
- When a monitored product drops in price or comes back in stock:
  1. Verify the change manually in a browser.
  2. Trigger alert send only for users subscribed to that SKU or price range.
  3. Send within 5–15 minutes of detection.
  4. Include direct affiliate link, current price, and retailer name.
  5. Throttle: do not send more than one alert per user per product per 6-hour window.
- If a product goes out of stock again, do not send a "sold out" email unless the user explicitly opted in.

### 7.3 Daily Standup Questions
- Did any scraper fail? Why?
- Did any user report a bad link or missing stock?
- What was the top referral source today?
- How many new alerts were created?
- Are any emails landing in spam?

---

## 8. Common Issues and Fixes

### 8.1 Spider / Scraper Blocked
**Symptoms:** Empty listings, 403 errors, CAPTCHA pages.
**Fixes:**
- Check proxy status and credentials (`PLAYWRIGHT_PROXY_*`).
- Rotate user-agent strings and headers.
- Add jittered delays between requests.
- Use headless Playwright with realistic viewport and locale.
- For Amazon, reduce request frequency; consider using their Product Advertising API if approved.
- Log response status codes to identify patterns.

### 8.2 Email Not Delivered
**Symptoms:** SendGrid shows dropped/bounced/deferred emails.
**Fixes:**
- Verify domain authentication (DKIM, SPF, DMARC) in SendGrid.
- Check bounce and spam-complaint rates.
- Ensure `from` address uses the authenticated domain.
- Avoid spammy words in subject lines.
- Warm up the sending domain: start with low volume and ramp up.
- Whitelist `BASE_URL` in SendGrid link branding.

### 8.3 No Listings
**Symptoms:** Home page loads but product grid is empty.
**Fixes:**
- Confirm scraper jobs are scheduled and running.
- Check database connection and that products exist in the table.
- Verify country filter matches the retailer being scraped.
- Check for JavaScript-rendered sites requiring Playwright instead of simple HTTP requests.
- Review proxy and regional blocking.
- Add a fallback manual import process for launch day.

### 8.4 High Server Load
**Fixes:**
- Move from SQLite in `render.yaml` to PostgreSQL.
- Add caching for listing pages (Redis or in-memory with TTL).
- Run scrapers on a separate worker service or scheduled job, not the web process.
- Scale Render plan or Railway resources temporarily during traffic spikes.

### 8.5 Affiliate Links Not Tracking
**Fixes:**
- Confirm env vars are set in production, not just locally.
- Inspect outgoing email HTML source for the `tag=` parameter.
- Test one click and verify it registers in the affiliate dashboard.
- Add a small "debug" endpoint that returns a rendered affiliate link for verification.

---

## 9. Next Milestones

### 9.1 100 Subscribers
- [ ] Send a thank-you email to early users.
- [ ] Ask for feedback via a 2-question survey.
- [ ] Create a referral mechanism ("Share KlimaRadar with a friend").
- [ ] Post a launch-retrospective thread on Twitter/X.

### 9.2 Paid Tier
- [ ] Decide value proposition: instant alerts, multi-country coverage, price-history charts.
- [ ] Integrate Stripe for EU VAT compliance.
- [ ] Launch "Pro" at €3–5/month or €25–35/year.
- [ ] Keep a generous free tier to preserve word-of-mouth growth.

### 9.3 New Countries
- [ ] Prioritize markets by heat-wave severity and affiliate availability.
- [ ] Shortlist: Spain, Italy, Netherlands, Belgium, Austria, Switzerland, Poland.
- [ ] Add localized landing pages and translated alert copy.
- [ ] Add local retailers and affiliate programs per country.
- [ ] Register local domains or use subfolders (`/es/`, `/it/`) under `klima-radar.com`.

### 9.4 Long-Term
- [ ] Build a price-history chart to show users when ACs are cheapest.
- [ ] Launch a browser of "best portable ACs by room size" content for SEO.
- [ ] Partner with climate/energy newsletters for cross-promotion.
- [ ] Consider an API or white-label version for publishers.

---

## Launch Sign-Off

Before announcing publicly, confirm:
- [ ] All env vars in section 1.2 are set in production.
- [ ] `/api/health` returns 200.
- [ ] Domain, HTTPS, and redirects are working.
- [ ] SendGrid authenticated and test email received.
- [ ] Sitemap submitted to Google Search Console.
- [ ] Analytics script is firing.
- [ ] At least one manual stock alert has been received end-to-end.
- [ ] Affiliate links are tagged and tracking.
- [ ] Launch content files are updated with the final URL.

Good luck with the launch.
