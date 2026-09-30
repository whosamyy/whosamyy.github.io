# Prompt Log

## Tools Used
- Codex

## Key Prompts

### Prompt 1

I am building my CMU 15-113 Project 2 from scratch.

Project name: Lock In Bro

The idea is a Chrome extension that helps students focus by blocking ONLY the websites they personally choose during a study session.

Students often need lots of websites/apps while studying, so I do NOT want to treat every tab switch as a distraction. Instead, users create their own blocklist (for example Instagram, Reddit, X, TikTok), start a timed study session, and those specific sites are blocked until the session ends.

For this first phase, DO NOT build the entire final project. I want a clean, working MVP that I can understand and test before adding more features.

==================================================
TECHNOLOGIES
==================================================

Use:

- Chrome Extension Manifest V3
- HTML
- CSS
- Vanilla JavaScript

Also create the basic structure for a future Flask backend, because later I want to save study-session data and build a statistics dashboard.

Backend:
- Python
- Flask
- Flask-SQLAlchemy
- SQLite for LOCAL development only

Do NOT use:
- React
- Vite
- npm
- Node
- complicated frontend frameworks

Keep the code beginner-readable because I need to understand and explain it.

==================================================
PROJECT STRUCTURE
==================================================

Create this general structure:

lock-in-bro/
│
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.css
│   ├── popup.js
│   ├── background.js
│   ├── blocked.html
│   ├── blocked.css
│   └── blocked.js
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   ├── templates/
│   │   └── dashboard.html
│   └── static/
│       ├── dashboard.css
│       └── dashboard.js
│
├── README.md
├── prompt_log.md
└── .gitignore

Do not create unnecessary files.

==================================================
PHASE 1: CHROME EXTENSION MVP
==================================================

Build the first working version of the Chrome extension.

The popup should show:

LOCK IN BRO

A short subtitle such as:
"Lock in now. Scroll later."

The user should be able to:

1. Enter what they are studying.

Example:
"Study probability"

2. Choose a focus duration:
- 25 minutes
- 45 minutes
- 60 minutes
- custom number of minutes

3. Add websites to a blocklist.

For example:
instagram.com
reddit.com
x.com
tiktok.com

Display blocked websites clearly and allow the user to remove them.

Prevent duplicates.

Normalize domains so obvious variants such as:

www.instagram.com

and

instagram.com

are treated as the same site.

4. Click:

"Start Focus Session"

==================================================
ACTIVE SESSION
==================================================

During an active session, the popup should show:

- current study task
- time remaining
- number of blocked attempts
- End Session button

Do not let the timer depend only on the popup staying open.

Chrome extension popups close whenever the user clicks somewhere else, so store:

- start time
- planned end time
- active status
- study task
- active blocklist
- blocked attempt count

in chrome.storage.local.

Calculate time remaining using timestamps so closing/reopening the popup does not reset the timer.

Use chrome.alarms and/or the background service worker appropriately.

==================================================
ACTUAL SITE BLOCKING
==================================================

This is the most important feature.

While a focus session is ACTIVE:

If the user tries to navigate to a domain in their blocklist:

1. Do not allow them to continue normally to that distracting site.
2. Redirect the tab to the extension's blocked.html page.
3. Increase the blocked-attempt counter.

The blocked page should say something like:

"Bro. Lock in."

"You are studying: [task]"

"23:14 remaining"

"You tried to open instagram.com"

Add a button:

"Back to Work"

Make the page fun and visually polished but still simple.

Sites NOT on the user's blocklist must continue working normally.

==================================================
PRIVACY
==================================================

Privacy is important.

The extension should NOT:

- record complete browsing history
- save every website the user visits
- collect page contents
- collect passwords
- collect search queries
- collect names or emails

Only inspect navigation enough to determine whether the domain matches an ACTIVE blocked domain.

Only store blocked-attempt information for sites that the user personally placed on their blocklist.

Use the minimum Chrome permissions necessary.

After implementation, explain every permission in manifest.json and why it is needed.

==================================================
ENDING A SESSION
==================================================

When the user clicks End Session or the timer finishes:

- stop blocking sites
- record the end time
- preserve a simple session summary
- show:
  - task
  - planned study time
  - actual study time
  - number of blocked attempts

For now, saving this locally is enough.

Later we will connect it to the database.

==================================================
BACKEND STARTER
==================================================

Set up a BASIC Flask backend, but do not spend most of this phase on it.

Create:

GET /api/health

Return:

{
  "status": "healthy"
}

Set up Flask-SQLAlchemy.

Create a simple FocusSession model with fields such as:

- id
- client_id
- task
- planned_minutes
- started_at
- ended_at
- completed
- blocked_count

Create a BlockedAttempt model with:

- id
- session_id
- domain
- timestamp

Set up the relationship appropriately.

Use SQLite locally.

Make the database configuration ready so that later I can provide a DATABASE_URL environment variable for a production database.

Do NOT deploy anything yet.

==================================================
FOCUS SCORE — DO NOT IMPLEMENT
==================================================

Later I want the app to calculate a Focus Score based on things like:

- session completion
- blocked attempts
- planned session duration

I need to write or substantially modify meaningful code myself for this class.

Create a clearly marked placeholder function such as:

computeFocusScore(...)

BUT DO NOT IMPLEMENT THE FINAL ALGORITHM.

Add comments explaining:
- what inputs it should eventually receive
- what it should return
- where it will eventually be used

Leave the actual algorithm for me to implement.

==================================================
README
==================================================

Create README.md, but DO NOT write the final prose for me.

Only create this structure:

# Lock In Bro

## What It Does
[Write this yourself]

## How to Use It
[Write this yourself]

## Main Features
[Write this yourself]

## How to Run It
[Write this yourself]

## Architecture
[Write this yourself]

## Privacy
[Write this yourself]

## AI Usage
[Write this yourself]

I need to write the final README in my own words.

==================================================
PROMPT LOG
==================================================

Create prompt_log.md.

Use:

# Prompt Log

## Tools Used
- Codex

## Key Prompts

### Prompt 1

Paste THIS ENTIRE PROMPT verbatim underneath Prompt 1.

Do not summarize it.
Do not rewrite it.
Do not shorten it.
Do not invent any prompts.

Also add EMPTY sections:

## Code I Wrote or Substantially Modified Myself

## Which Tool I Used for Which Job

## One Place AI Got Something Wrong

Do not invent content for those sections. I will fill them in later.

==================================================
GITIGNORE / SECURITY
==================================================

Create .gitignore containing at least:

.env
.env.*
venv/
.venv/
__pycache__/
*.pyc
.DS_Store
instance/
*.db

Do not create or commit:

- passwords
- API keys
- access tokens
- database passwords
- private credentials

==================================================
DESIGN
==================================================

Give Lock In Bro a fun but clean identity.

I want it to feel like a student-made productivity tool, not a corporate SaaS product.

Use:
- clean typography
- bold timer
- simple cards
- subtle animations
- good spacing
- slightly playful wording

Do not spend too much time styling in Phase 1.

Functionality comes first.

==================================================
TESTING
==================================================

Before stopping, verify that:

1. The extension can be loaded through chrome://extensions using "Load unpacked".
2. The popup opens without console errors.
3. I can add blocked domains.
4. I can remove blocked domains.
5. Duplicate domains are prevented.
6. I can start a focus session.
7. Closing and reopening the popup does not reset the timer.
8. Visiting a blocked site during an active session redirects me to blocked.html.
9. Visiting an allowed website works normally.
10. A blocked attempt increases the counter.
11. Ending the session immediately stops blocking.
12. The timer ending automatically stops blocking.
13. The Flask backend starts locally.
14. GET /api/health returns valid JSON.
15. The SQLite database can be initialized.
16. There are no private keys or secrets anywhere in the project.

==================================================
IMPORTANT
==================================================

Do NOT:

- deploy anything yet
- publish to the Chrome Web Store
- create user accounts
- add authentication
- add fancy analytics
- add charts
- add streaks
- add sounds
- add strict mode
- add AI features
- redesign this into something much larger
- commit or push anything yet

For now I only want the first working MVP.

==================================================
WHEN YOU FINISH
==================================================

Stop and give me:

1. The final file tree.
2. A short explanation of every important file.
3. Every Chrome permission you used and why.
4. A simple explanation of how website blocking works.
5. A simple explanation of how the timer survives the popup closing.
6. Instructions for loading the extension into Chrome.
7. Instructions for running the Flask backend locally.
8. Instructions for initializing the local database.
9. A manual testing checklist.
10. Any bugs or limitations still present.
11. Where the unfinished computeFocusScore function is located.
12. A suggestion for my first Git commit message.

Do NOT continue to Phase 2 until I ask.

### Prompt 2

The Lock In Bro extension loads, the popup works, and I can start a session, but it does NOT actually block or redirect instagram.com or reddit.com.

Do not add any new features yet. Fix ONLY the blocking functionality.

Please inspect:

- extension/manifest.json
- extension/background.js
- extension/popup.js
- extension/blocked.html
- any declarativeNetRequest rules

I am using Chrome Extension Manifest V3.

The expected behavior is:

1. I add:
   instagram.com
   reddit.com

2. I start a focus session.

3. If I navigate to:
   [https://instagram.com](https://instagram.com)
   [https://www.instagram.com](https://www.instagram.com)
   [https://reddit.com](https://reddit.com)
   [https://www.reddit.com](https://www.reddit.com)

the tab should be redirected to the extension's blocked.html page.

4. Sites that are not on the blocklist should still work normally.

Please debug this carefully instead of rewriting the whole extension.

Specifically check:

A. HOST PERMISSIONS

Verify that the extension actually has host permission for the selected domains before installing declarativeNetRequest redirect rules.

I am currently using declarativeNetRequestWithHostAccess, so do not assume that declaring that permission alone gives access to every website.

If optional\_host\_permissions are being used:

- make sure manifest.json declares the appropriate patterns
- make sure popup.js actually calls chrome.permissions.request(...)
- confirm that the permission request succeeds before starting the session
- handle both the root domain and subdomains correctly

For example, if reddit.com is blocked, permission/rules should correctly cover:
[https://reddit.com/](https://reddit.com/)\*
[https://](https://.reddit.com/)[*.reddit.com/*](https://.reddit.com/)

and the same for http if necessary.

If the current permission strategy is unnecessarily fragile, explain whether using declarativeNetRequest with broader host permissions would be simpler for this class project, but do not silently increase permissions without explaining it.

B. DYNAMIC / SESSION RULES

Inspect the rules created by:
chrome.declarativeNetRequest.updateDynamicRules(...)
or
chrome.declarativeNetRequest.updateSessionRules(...)

Verify that:

- each rule has a unique positive integer id
- action.type is "redirect"
- redirect uses extensionPath correctly
- the condition matches the target domain
- resourceTypes includes "main\_frame"
- the URL filter actually matches both the domain and subdomains
- old rules are removed before replacement if needed

Use a Chrome-supported pattern such as an appropriate urlFilter or requestDomains condition.

C. BLOCKED PAGE

If redirecting to blocked.html using:

redirect: {
extensionPath: "/blocked.html"
}

make sure blocked.html is declared correctly under web\_accessible\_resources in manifest.json if required.

D. SESSION STATE

Confirm that blocking rules are actually installed AFTER Start Focus Session is pressed.

Add temporary development logging so I can see:

- normalized blocklist
- whether host permission was granted
- generated DNR rules
- result of updateDynamicRules/updateSessionRules
- currently installed rules after installation

Do not log general browsing history or unrelated URLs.

E. DEBUGGING

Add a temporary developer function or console output using:

chrome.declarativeNetRequest.getDynamicRules()

or getSessionRules(), depending on which strategy this project uses.

After starting a session with reddit.com and instagram.com, I should be able to inspect the service worker console and see that the appropriate rules exist.

Also check chrome.runtime.lastError / caught Promise errors around all permission and rule update calls.

F. DO NOT CHANGE

Do not:

- change the app design
- change the timer system unless it is directly causing the issue
- change the Flask backend
- add database features
- add Phase 2 features
- commit or push anything

G. AFTER FIXING

Tell me:

1. What specifically was wrong.
2. Which files you changed.
3. What permissions the extension now requests.
4. Why those permissions are necessary.
5. What exact DNR rule is generated for instagram.com.
6. What exact DNR rule is generated for reddit.com.
7. How to verify those rules in Chrome.
8. How to reload the unpacked extension correctly after changing manifest.json/background.js.
9. A manual test checklist.

Also append THIS ENTIRE PROMPT verbatim to prompt\_log.md as the next Key Prompt.

Do not summarize or rewrite it.


## Code I Wrote or Substantially Modified Myself

## Which Tool I Used for Which Job

## One Place AI Got Something Wrong


## Key Prompt — Phase 2

Phase 1 of Lock In Bro is now working.

The Chrome extension can:
- add/remove blocked domains
- start a focus session
- persist the active session when the popup closes
- block selected distracting websites
- redirect blocked sites to blocked.html
- count blocked attempts
- end sessions manually or automatically

Now I want to build Phase 2.

Do NOT rewrite the working extension from scratch.
Preserve the blocking and timer behavior that already works.

The goal of this phase is to:

1. connect the Chrome extension to the Flask backend
2. save completed focus sessions to a database
3. save blocked attempts
4. build a useful analytics dashboard
5. keep everything working locally before deployment

==================================================
ARCHITECTURE
==================================================

The intended architecture is:

Chrome Extension
        ↓
      fetch()
        ↓
Flask Backend
        ↓
Database
        ↓
Public Focus Analytics Dashboard

The extension should continue using chrome.storage.local for ACTIVE session state because blocking must keep working even if the backend is temporarily unavailable.

The database should be used for historical session data and analytics.

==================================================
BACKEND API
==================================================

Expand the Flask backend.

Use these endpoints:

GET /api/health

Keep the existing health endpoint.

POST /api/sessions

Called when a focus session starts.

Accept JSON similar to:

{
  "client_id": "...",
  "task": "Study probability",
  "planned_minutes": 45,
  "blocked_domains": [
    "instagram.com",
    "reddit.com"
  ],
  "started_at": "..."
}

Create a FocusSession row.

Return structured JSON including the database session ID:

{
  "success": true,
  "session_id": 12
}

POST /api/sessions/<session_id>/blocked

Called when the user attempts to visit a blocked site.

Accept:

{
  "domain": "instagram.com",
  "timestamp": "..."
}

Create a BlockedAttempt row and update the session's blocked_count.

POST /api/sessions/<session_id>/finish

Called when the focus session ends.

Accept useful summary information such as:

{
  "ended_at": "...",
  "completed": true,
  "actual_minutes": 43.5,
  "blocked_count": 4,
  "focus_score": 87
}

Update the existing FocusSession record.

GET /api/stats/<client_id>

Return structured analytics for that anonymous client.

Include:

- total focus minutes
- total sessions
- completed sessions
- total blocked attempts
- average focus score
- average session length
- recent sessions
- most frequently blocked domains
- focus time grouped by day if practical

Return useful JSON errors and proper status codes.

==================================================
ANONYMOUS CLIENT ID
==================================================

The extension should NOT require user accounts.

Generate a random anonymous client ID the first time the extension is used.

Store it in:

chrome.storage.local

Reuse the same client ID for future sessions.

Do not use:
- name
- email
- password
- Google account
- browsing identity

==================================================
EXTENSION → BACKEND CONNECTION
==================================================

Update the extension so that when a session starts:

1. Keep the local active-session state exactly as it already does.
2. Send a POST request to /api/sessions.
3. Store the returned backend session_id inside the local active session.

If the backend is unavailable:
- DO NOT prevent the user from starting a focus session.
- The blocking feature should still work locally.
- Show/log a reasonable warning instead.
- Do not crash.

When a blocked attempt happens:

- continue incrementing the local blocked count
- if there is a valid backend session_id, send the blocked attempt to the backend
- if the backend request fails, do not break site blocking

When the session finishes:

- compute the final summary locally
- if there is a backend session_id, POST it to /finish
- if the backend is unavailable, preserve the local summary

The extension's core blocking functionality must NOT depend on the backend being online.

==================================================
DATABASE
==================================================

Use the existing SQLAlchemy models or improve them cleanly.

FocusSession should include at least:

- id
- client_id
- task
- planned_minutes
- actual_minutes
- started_at
- ended_at
- completed
- blocked_count
- focus_score

BlockedAttempt should include:

- id
- session_id
- domain
- timestamp

Use a proper relationship.

For LOCAL development:
- SQLite is fine.

Keep support for:

DATABASE_URL

so I can later use PostgreSQL on Render.

Do not hardcode database credentials.

==================================================
FOCUS SCORE — DO NOT IMPLEMENT FOR ME
==================================================

I still need to write or meaningfully modify part of this project myself.

Do NOT implement the final focus-score algorithm.

Keep the existing computeFocusScore(...) TODO.

I will implement it myself.

However:
- make sure the rest of the code is ready to call it
- clearly tell me what parameters it should take
- clearly tell me what output type it should return
- tell me where the returned score will be saved

Do not implement the algorithm elsewhere.

==================================================
ANALYTICS DASHBOARD
==================================================

Turn the Flask root page into a useful Lock In Bro dashboard.

The dashboard should feel like part of the same project.

Use a fun but clean style.

Show:

LOCK IN BRO

"Lock in now. Scroll later."

Then analytics such as:

- Total Focus Time
- Sessions Completed
- Distractions Blocked
- Average Focus Score

Also show:

RECENT SESSIONS

For each session:
- task
- planned time
- actual time
- blocked attempts
- focus score
- completed vs ended early
- date

MOST BLOCKED SITES

Example:

instagram.com — 14
reddit.com — 9
x.com — 6

FOCUS TIME OVER TIME

Add one simple chart.

Use Chart.js from a CDN if appropriate.

A bar chart showing focus minutes by day would be good.

Do not create lots of unnecessary charts.

==================================================
DASHBOARD CLIENT IDENTIFICATION
==================================================

Because there are no accounts, decide on a simple development-friendly way for the dashboard to know which anonymous client to display.

For example:

/?client_id=abc123

or another similarly simple approach.

Explain the tradeoff.

Do not pretend this is secure authentication.

==================================================
ERROR HANDLING
==================================================

Handle:

- invalid JSON
- missing client_id
- missing task
- invalid planned_minutes
- nonexistent session IDs
- malformed blocked-attempt requests
- database errors
- backend unavailable from extension
- empty analytics data

The dashboard should show a friendly empty state if no sessions exist yet.

==================================================
PRIVACY
==================================================

Continue to preserve the privacy design.

Do NOT store:

- general browsing history
- allowed sites
- page contents
- search queries
- passwords
- names
- emails

Only store:

- user-created blocked domains
- attempts to access those blocked domains during active sessions
- focus-session metadata
- task name
- session analytics

Do not add tracking or analytics libraries.

==================================================
TESTING
==================================================

Before stopping, test everything LOCALLY.

Test:

1. Flask backend starts.
2. Database initializes.
3. POST /api/sessions creates a session.
4. POST /blocked creates a blocked attempt.
5. POST /finish updates the session.
6. GET /api/stats/<client_id> returns correct statistics.
7. Dashboard loads.
8. Dashboard handles no-data state.
9. Extension still starts sessions normally.
10. Extension still blocks sites correctly.
11. Extension gets a backend session_id when Flask is running.
12. Blocked attempts appear in the database.
13. Ending a session updates the database.
14. Extension still works if Flask is completely turned off.
15. No browser console errors.
16. No Flask tracebacks during normal use.

==================================================
SECURITY
==================================================

Do not add:
- API keys
- credentials
- tokens
- passwords
- database passwords

Continue respecting .gitignore.

Search files you modify for secrets before stopping.

==================================================
README
==================================================

Do NOT write the final README prose for me.

You may update the README HEADINGS/placeholder structure if the architecture changed.

Keep it for me to write in my own words.

==================================================
PROMPT LOG
==================================================

Append THIS ENTIRE PROMPT verbatim to:

lock-in-bro/prompt_log.md

as the next Key Prompt.

Do not summarize or rewrite it.

Do not invent development history.

==================================================
DO NOT DEPLOY YET
==================================================

Do NOT:
- deploy to Render yet
- configure PostgreSQL yet
- publish to Chrome Web Store
- add user accounts
- add strict mode
- add streaks
- add AI features
- add notification systems
- redesign the whole extension
- commit or push anything

I want Phase 2 working locally first.

==================================================
WHEN YOU FINISH
==================================================

Tell me:

1. Every file you changed.
2. The database schema.
3. Every backend endpoint and what it does.
4. How the extension talks to Flask.
5. What happens if Flask is offline.
6. How the anonymous client ID works.
7. How the dashboard gets its data.
8. How the chart works.
9. Exactly where computeFocusScore() is still unfinished.
10. What inputs computeFocusScore() should take.
11. How I can manually test the entire system locally.
12. Any remaining bugs or limitations.
13. A suggested second commit message.

Do NOT continue to deployment until I ask.
