# Lock In Bro dashboard authentication

This change is prepared and tested locally. No credentials were created, no
production database was accessed or modified, and nothing was committed,
pushed, deployed, or published as an extension ZIP during this phase.

## Architecture and data

The Chrome extension continues sending anonymous session writes to the same
backend using its existing `client_id`. Google OpenID Connect protects only
dashboard reads. Authlib uses Google's discovery document, authorization-code
flow with PKCE S256, OAuth state and OIDC nonce validation. The only requested
scope is `openid`; email and profile scopes are not requested.

Flask-Session keeps login state on the server. The browser holds a signed,
random session identifier, not analytics, Google profile data or OAuth tokens.
Only the internal user ID is retained after successful login; Google tokens
and full claims are discarded after the callback request. The session ID is
rotated at login, and logout deletes its server-side record. Logout requires
a CSRF token. Cookies are HTTPOnly and SameSite=Lax, and Secure on Render.
Logged-in sessions expire after 12 hours; an OAuth attempt expires after
10 minutes. Private responses use `Cache-Control: no-store` and
`Referrer-Policy: no-referrer`.

Flask-Session 0.8 is bounded below 0.9 because this implementation uses its
supported signed-session-ID option, which is deprecated for a future release.
Review that setting when upgrading the library. The session store is CacheLib's
file cache under Flask's instance directory (`backend/instance/dashboard_sessions`).
It is shared by Gunicorn workers on **one** Render instance and is not source
controlled. A restart, cache eviction or deployment can sign users out. The
database ownership records and analytics remain intact. Before scaling to
multiple Render instances, replace the file cache with a shared server-side
store such as Redis; the current setup is not designed for multiple instances.

Two new database tables are added:

| Table | Columns and constraints |
| --- | --- |
| `user` | `id`, unique `google_sub`, `created_at` |
| `client_installation` | `id`, unique `client_id`, indexed `user_id` foreign key to `user.id`, `created_at` |

Google's stable `sub` identifies the account. No passwords, email, name,
photo, permanent Google tokens, general browsing history, allowed sites,
page contents or search queries are stored. Existing `focus_session` and
`blocked_attempt` tables and rows are preserved. No `user_id` is added to
individual focus sessions.

## Pairing an existing installation

1. Open the dashboard from the existing extension:
   `https://lock-in-bro.onrender.com/?client_id=<existing-UUID>`.
2. The backend validates a canonical lowercase version-4 UUID and retains the
   pending installation in the server-side session while you sign in.
3. After Google validates your identity, an unclaimed UUID is associated with
   your account. The unique `client_id` constraint prevents two accounts from
   owning the same installation; concurrent claims use a database savepoint.
4. An installation already owned by you is accepted. Another account receives
   a safe 403 page, and ownership is not changed.
5. Successful pairing redirects to `/`, without a UUID query string.

The existing session rows stay associated with the same UUID. The stats query
selects sessions whose client IDs belong to your account, so old history appears
without a data migration. Future visits to `/` work without a UUID. Multiple
owned installations are aggregated: total minutes, completions and blocked
counts are summed, scores and session lengths are averaged over finished
sessions, and recent history shows the latest 20 across installations.

**Pairing limitation:** possession of an unclaimed installation UUID is the
initial pairing mechanism. Whoever knows it can claim it first. This is weaker
than authenticating the extension or using a separate pairing secret. Initial
URLs can also appear in browser history or server access logs; do not share
unclaimed dashboard links. This phase does not provide account relinking,
account deletion, or authentication for extension writes.

## Routes and access controls

| Method and route | Behavior |
| --- | --- |
| `GET /` | Requires a login; optionally claims `client_id`, then redirects to a clean `/` |
| `GET /login` | Pink login page; signed-in users return to `/` |
| `GET /auth/google` | Starts Google OAuth; fails safely with 503 if not configured |
| `GET /auth/callback` | Authlib validates state and Google ID token; creates/reuses user, rotates session, links pending installation |
| `POST /logout` | CSRF-protected local logout; removes dashboard access without signing out of Google itself |
| `GET /api/me/stats` | Requires authentication; reads all and only the current user's installations |
| `GET /api/stats/<client_id>` | Compatibility read endpoint; requires authentication and verifies ownership; never claims an ID |
| `GET /api/health` | Remains public |
| `POST /api/sessions` | Remains anonymous for the extension |
| `POST /api/sessions/<id>/blocked` | Remains anonymous for the extension |
| `POST /api/sessions/<id>/finish` | Remains anonymous for the extension |

Stats return JSON 401 after logout/session expiry, or 403 for an unowned
installation. The dashboard JavaScript always requests `/api/me/stats` and
returns to `/login` after expiry; it does not select data from URL parameters.
Malformed pairing IDs return 400; cancelled/invalid callbacks return a safe
400 page; missing OAuth configuration and database failures return 503 without
secrets or stack traces. OAuth failure/cancellation requires reopening the
extension's dashboard link if you were pairing a new installation.

**Write authentication remains a future security improvement.** Anonymous
writes preserve current extension behavior, but someone who knows a client ID
can submit fabricated sessions, and someone who knows a server session ID may
submit blocked attempts or finish it. Google sign-in restricts read access; it
does not verify the authenticity of submitted analytics. Rate limiting and a
stronger pairing protocol are also future improvements.

## Google Cloud Console setup

Do these steps yourself when ready; no Google credentials have been created.
Google's [OpenID Connect documentation](https://developers.google.com/identity/openid-connect/openid-connect)
describes the provider configuration and identity claims.

1. Select or create a Google Cloud project and open **Google Auth Platform**
   (or **APIs & Services → OAuth consent screen** in the legacy navigation).
2. Configure Branding for **Lock In Bro**, including your support/developer
   contact. Configure Audience as External for personal/public Google accounts
   (Internal is appropriate only for a restricted Workspace organization).
3. Start with the app in Testing and add the Google accounts you will use as
   test users. Follow any Console domain/branding/verification requirements
   before later switching the OAuth app to Production. Public extension ZIP
   availability does not publish the OAuth app.
4. Under Data Access, request only the `openid` scope. Do not add email,
   profile, offline access or other Google API scopes.
5. Create an OAuth client with application type **Web application**.
6. Add these exact **Authorized redirect URIs** (no trailing slash):
   - Production: `https://lock-in-bro.onrender.com/auth/callback`
   - Local: `http://127.0.0.1:5000/auth/callback`
7. This flow is server-side, so JavaScript origins are not needed. Do not
   create a Chrome-extension OAuth client for this phase.
8. Save the Client ID and Client Secret privately, and configure them in
   Render and your local shell. Do not paste credentials into source code,
   commit messages, logs, screenshots or this setup file.

## Exact environment configuration

Add these **three** environment variables to the existing Render web service:

| Variable | Value |
| --- | --- |
| `GOOGLE_CLIENT_ID` | The Web application OAuth Client ID from Google |
| `GOOGLE_CLIENT_SECRET` | Its OAuth Client Secret |
| `SECRET_KEY` | A stable, randomly generated secret used by Flask to sign the opaque session cookie |

Keep the existing `DATABASE_URL` pointed at the same PostgreSQL database. No
new database URL or additional user-configured environment variable is required.
Render automatically supplies `RENDER=true`; the app uses it for Secure cookies,
trusted production host and the fixed HTTPS callback. It trusts one forwarded
scheme hop from Render's proxy, not a forwarded host. See Render's
[default environment variables](https://render.com/docs/environment-variables).

Generate the secret locally:

```sh
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

Copy that value into Render's private environment settings and keep it stable
across restarts. Generate a separate local development key. Changing the
production secret invalidates signed cookies; it does not delete focus data.

## Local setup and manual checklist

From `lock-in-bro/backend`, create/activate a virtual environment and install:

```sh
python -m pip install -r requirements.txt
```

Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` and `SECRET_KEY` in your local
shell using your own values. The app reads environment variables; it does not
automatically load a `.env` file. Leave `RENDER` unset and leave `DATABASE_URL`
unset to use local SQLite rather than the production database. Then run:

```sh
flask --app app init-db
flask --app app run --host 127.0.0.1 --port 5000
```

1. In a private browser window, open `http://127.0.0.1:5000/`: see login,
   never analytics. Both stats endpoints should return 401 while logged out.
2. For a **temporary copy** of the extension, set its config to
   `http://127.0.0.1:5000`; the existing manifest already allows that local
   origin. Keep the production extension and URL unchanged.
3. Load the copy, start a session, verify chosen-site blocking, finish, and
   open its dashboard link. Continue with Google using a configured test user.
4. Verify the callback returns to `/`, old sessions appear, new completions
   refresh automatically, and the extension worked without its own login.
5. Reopen the link and revisit `/`: ownership should be unchanged.
6. Link another temporary extension installation to the same Google account;
   verify the account-wide totals aggregate both installations.
7. Sign out. Revisit `/` and request stats: access should be removed. The
   extension should still start/block/finish and submit sessions.
8. Sign in as another Google account and try the first client's link and
   legacy stats URL: both should return 403 without its history.
9. Cancel Google login, try a malformed pairing UUID, and let a login attempt
   expire: verify readable error pages. Missing config should show a 503 login
   message, not an exception. Reopen the extension link to pair after a failure.
10. Check desktop/mobile layout and that only `openid` consent is requested.
    Inspect the database to confirm only `google_sub` and ownership are added.

## Adding tables safely and later Render steps

`flask --app app init-db` still uses `db.create_all()`. It creates missing
authentication tables and does not drop, recreate, truncate or overwrite
existing PostgreSQL tables. The existing SQLite-only additive Phase 1 column
upgrade remains unchanged. No destructive migration is introduced.

When you decide to publish later:

1. Finish Google Cloud setup above and keep Render's automatic deploy disabled
   until you are ready. In Render Environment, save the three variables using
   its save-without-deploy option; keep `DATABASE_URL` unchanged.
2. Review/commit/push only when you explicitly choose to. This work has not
   performed any of those actions. Keep the existing backend URL and Gunicorn
   start command; ensure the build installs the updated `requirements.txt`.
3. Make a backup/snapshot of the existing PostgreSQL database for recovery.
   On a staging copy you can first confirm the additive table initialization.
4. For the later release, run `flask --app app init-db` **using the new code**
   against the existing database. Use Render's pre-deploy command if available,
   or its Shell after deploying the new code. An old-code shell does not yet
   know about the new tables. A shell run after deployment may briefly leave
   dashboard reads unavailable until tables are created; health and anonymous
   writes can continue. Never use `drop_all` or reset the database.
5. After table initialization/deployment, verify health, Google login, the
   production callback, old history pairing, account isolation, logout and
   Secure/HTTPOnly/SameSite cookies. Confirm anonymous extension writes still
   work. No extension ZIP update is required for this authentication phase.

## Automated validation

Local verification results: **27 unit/API/auth/deployment tests passed**, the
Node history-sync regression passed, and the Playwright online/offline browser
integration passed. Desktop and mobile login screenshots were inspected.
These validate local SQLite behavior and PostgreSQL configuration/generated
schema; they do not claim a live PostgreSQL migration or a real Google
credentialed sign-in was performed. The latter are manual release checks.

Run unit/API/auth/PostgreSQL configuration checks from the repository root:

```sh
python -m unittest discover -s lock-in-bro/backend/tests -p 'test_*.py'
node lock-in-bro/backend/tests/history_sync.test.cjs
```

The unit suite covers logged-out reads, both stats authorization paths,
ownership/403 isolation, recovery of existing history, multiple installations,
missing/invalid UUIDs, repeat sign-in, logout/CSRF/session revocation, expired
sessions, missing config, provider errors, safe database failures, additive
table initialization, PostgreSQL URL/schema configuration, and unchanged
anonymous session writes. A mock OIDC provider exercises Authlib's real state,
PKCE, ID-token signature, issuer, audience, expiry and nonce checks. Google
servers and real credentials are not used.

The browser integration test needs Playwright and its Chromium installation:

```sh
python lock-in-bro/backend/tests/browser_integration.py
```

It uses a temporary local database and extension copy, stubs only Google's
provider calls, and verifies real site-blocking redirects, popup closure,
anonymous writes, counts, finish, login, clean dashboard URL, live refresh,
chart, logout, invalid link and offline operation. Native permission prompts
remain a manual check because this fixture pre-grants its test site.

## README edits for you

The README was not changed. Update **How to Use It** to mention Google sign-in
for the dashboard, **Architecture** to describe account ownership and protected
reads, **How to Run It** for OAuth environment variables/redirects, and
**Privacy** for storing Google's stable account identifier and installation
ownership. Do not say the extension itself requires Google login.

Suggested commit message: `Add Google sign-in and ownership checks for focus dashboard`

## Files changed in this authentication phase

| File | Change |
| --- | --- |
| `.gitignore` (repository root) | Ignore transient server-side login files |
| `lock-in-bro/backend/app.py` | Session/proxy settings, protected dashboard and stats, safe HTML errors |
| `lock-in-bro/backend/auth.py` (new) | Google OAuth routes, UUID validation, user lookup, ownership and logout |
| `lock-in-bro/backend/models.py` | Add User and ClientInstallation models |
| `lock-in-bro/backend/requirements.txt` | Add Authlib, Flask-Session, CacheLib and Requests |
| `lock-in-bro/backend/static/dashboard.css` | Small matching login/error-page styles |
| `lock-in-bro/backend/static/dashboard.js` | Account-scoped stats and session-expiry redirect |
| `lock-in-bro/backend/templates/dashboard.html` | Remove public UUID selector; add sign-out form |
| `lock-in-bro/backend/templates/login.html` (new) | Pink Google sign-in screen and missing-config state |
| `lock-in-bro/backend/templates/auth_error.html` (new) | Safe matching error screen |
| `lock-in-bro/backend/tests/test_api.py` | Keep write tests anonymous; authenticate analytics assertions |
| `lock-in-bro/backend/tests/test_auth.py` (new) | OAuth, ownership, session and read-security regression tests |
| `lock-in-bro/backend/tests/test_deployment.py` | Protected-route expectations and additive PostgreSQL schema checks |
| `lock-in-bro/backend/tests/browser_integration.py` | Mock Google while testing real extension writes/blocking and login UI |
| `lock-in-bro/backend/AUTH_SETUP.md` (new) | Configuration, architecture, setup, limitations and manual checklist |
| `lock-in-bro/prompt_log.md` | Append the entire supplied prompt verbatim as the next Key Prompt |

Earlier sync fixes remain in the working tree. This authentication phase did
not change extension source files, the ZIP, installation instructions, the
portfolio, README, timer logic, permissions, backend URL or focus-score formula.
