# Prompt Log

## Tools Used
- Codex

## Code I Wrote or Substantially Modified Myself
I wrote the focus score calculation myself. It uses whether the session
was completed, how long I actually focused compared to the planned time,
and how many times I tried to visit a blocked site to calculate a score
from 0–100. I also manually tested the extension and adjusted parts of
the behavior based on what I found.

## Which Tool I Used for Which Job
I used Codex for most of the implementation, including setting up the
Chrome extension, Flask backend, database, and analytics dashboard. I
used ChatGPT to help plan the project architecture, think through
features, and write/debug prompts for Codex. I manually tested the
extension throughout development.

## One Place AI Got Something Wrong
The first version Codex generated looked like it was working, but it did
not actually block the websites that I asked it to block. It also did not 
show that a focus session was still active after I closed and reopened the 
extension popup. I found both problems while manually testing it. I then gave 
Codex a more specific debugging prompt about Chrome permissions, blocking 
rules, and persistent session state, and tested the fixes again.

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

## Key Prompt — Focus Score Implementation

Implement the unfinished computeFocusScore() function in:

lock-in-bro/extension/focus-score.js

Do NOT modify any other part of the project unless it is absolutely necessary for the function to work.

The function currently receives:

computeFocusScore({
completed,
plannedMinutes,
actualMinutes,
blockedCount
})

Requirements:

1. Return an integer focus score from 0 to 100.

2. Start the score at 100.

3. Subtract 5 points for every attempt to visit a blocked website.

Example:
0 blocked attempts -> lose 0 points
1 blocked attempt  -> lose 5 points
3 blocked attempts -> lose 15 points

4. If actualMinutes is less than plannedMinutes, subtract a time penalty based on the percentage of the planned session that was missed.

Use:

percentMissed =
(plannedMinutes - actualMinutes) / plannedMinutes

The maximum time penalty should be 30 points.

For example:

- completing 100% of the planned time -> lose 0 points
- completing 50% of the planned time -> lose 15 points
- completing 0% -> lose 30 points

5. If completed is false, subtract an additional 10 points.

6. Clamp the final score so it can never be below 0 or above 100.

7. Round the final score to the nearest integer.

8. Handle invalid values safely, including:

- plannedMinutes <= 0
- negative actualMinutes
- negative blockedCount
- missing/non-numeric values

Do not allow invalid inputs to produce NaN or Infinity.

9. Keep the implementation simple and readable. Do not create an overly complicated scoring system.

10. Do not change the Flask backend, dashboard, blocking behavior, timer behavior, or database schema.

11. After implementing it, test the function with examples including:

A.
completed = true
plannedMinutes = 45
actualMinutes = 45
blockedCount = 1

Expected score: 95

B.
completed = false
plannedMinutes = 60
actualMinutes = 30
blockedCount = 3

Expected score:
100

- 15 for blocked attempts
- 15 for missing half the planned time
- 10 for ending early
  \= 60

C.
completed = true
plannedMinutes = 25
actualMinutes = 25
blockedCount = 0

Expected score: 100

D.
A case with enough penalties that the result would otherwise be negative.
Confirm that it returns 0.

When finished:

- show me the final computeFocusScore() implementation
- explain each part briefly
- show the test results
- tell me exactly which files were changed
- do not commit or push anything

Also append THIS ENTIRE PROMPT verbatim to prompt\_log.md as the next Key Prompt.
Do not summarize or rewrite it.


## Key Prompt — Render Deployment Preparation

Phase 2 of Lock In Bro is working locally. I now want to prepare the project for deployment to Render.

Project location:

/Users/whosamy/Documents/whosamyy.github.io/lock-in-bro

Current structure:

lock-in-bro/
├── extension/
├── backend/
├── README.md
├── prompt_log.md
└── .gitignore

The Chrome extension, Flask backend, SQLite database, and analytics dashboard are already working locally.

IMPORTANT:
- Do NOT rewrite working features.
- Do NOT redesign the extension.
- Do NOT deploy anything yet.
- Do NOT commit or push.
- Preserve local development behavior.
- Do NOT write my README prose for me.

==================================================
GOAL
==================================================

Prepare Lock In Bro so that:

1. The Flask backend/dashboard can be deployed on Render.
2. Production can use PostgreSQL.
3. Local development can continue using SQLite.
4. The extension can easily switch from localhost to the final Render URL.
5. The public dashboard continues working.
6. Everything remains tested locally.

==================================================
1. PRODUCTION DEPENDENCIES
==================================================

Inspect:

backend/requirements.txt

Make sure it contains all dependencies required for production deployment, including:

- Flask
- Flask-SQLAlchemy
- gunicorn
- an appropriate PostgreSQL driver

Use a modern PostgreSQL driver compatible with the existing SQLAlchemy setup.

Do not add unnecessary packages.

==================================================
2. DATABASE CONFIGURATION
==================================================

Inspect the current SQLAlchemy configuration.

Requirements:

LOCAL:
If DATABASE_URL is not set, continue using the existing SQLite database.

PRODUCTION:
If DATABASE_URL is set, use that database connection.

Do NOT:
- hardcode credentials
- hardcode database passwords
- commit a DATABASE_URL
- store secrets in source code

Make sure the configuration works correctly with Render PostgreSQL.

If Render provides a PostgreSQL URL format that SQLAlchemy needs normalized, handle that safely.

==================================================
3. DATABASE INITIALIZATION
==================================================

Inspect the current:

flask --app app init-db

behavior.

Make sure a completely new PostgreSQL database can initialize all required tables cleanly.

The schema currently includes:

FocusSession:
- id
- client_id
- task
- planned_minutes
- actual_minutes
- blocked_domains
- started_at
- ended_at
- completed
- blocked_count
- focus_score

BlockedAttempt:
- id
- session_id
- domain
- timestamp

Do not rely on SQLite-specific ALTER TABLE behavior for a brand-new PostgreSQL deployment.

Preserve existing local SQLite compatibility.

==================================================
4. GUNICORN
==================================================

Verify that the backend can be started from:

lock-in-bro/backend

with:

gunicorn app:app

Make any minimal changes necessary.

Do not change the Flask app architecture unnecessarily.

==================================================
5. EXTENSION BACKEND URL
==================================================

The extension currently communicates with:

http://127.0.0.1:5000

Refactor the backend URL configuration so there is ONE obvious place where I can switch between:

DEVELOPMENT:
http://127.0.0.1:5000

and later:

PRODUCTION:
https://MY-REAL-RENDER-URL.onrender.com

For example, create a small configuration file or clearly defined constant if appropriate.

Do NOT invent my Render URL.

Tell me exactly which line/file I will edit after Render gives me the real URL.

==================================================
6. CHROME EXTENSION PERMISSIONS
==================================================

Inspect:

extension/manifest.json

The extension will eventually need to send fetch requests to the Render backend.

Determine exactly what host permission will be needed once I receive the real Render URL.

Do NOT use unnecessarily broad permissions such as:

https://*/*

if a specific Render origin can be used.

For now, preserve localhost development access.

Explain exactly what I need to add/change after I receive the production URL.

Do not break the existing website-blocking permissions.

==================================================
7. CORS
==================================================

Determine whether the Flask backend needs CORS configuration for requests originating from the Chrome extension.

If it does, configure it narrowly and safely.

Do not allow every origin unless technically necessary.

Explain what origin rules apply to Chrome extensions and why.

Keep local development working.

==================================================
8. DASHBOARD
==================================================

The Flask root route:

/

must continue serving the Lock In Bro analytics dashboard.

Make sure it handles:

- valid client_id
- no client_id
- invalid/nonexistent client_id
- a client with no sessions

The dashboard should never crash just because there is no data.

Do not redesign it.

==================================================
9. HEALTH CHECK
==================================================

Keep:

GET /api/health

Make sure it is suitable for checking whether the deployed Render service is alive.

It should return simple JSON and HTTP 200 when healthy.

==================================================
10. PRODUCTION DATABASE SETUP
==================================================

Do not create a real database yet.

Instead, make the application ready so that later I can set:

DATABASE_URL=<Render PostgreSQL connection string>

as a Render environment variable.

Tell me whether any other environment variables are needed.

==================================================
11. FOCUS SCORE
==================================================

Do not change the focus-score formula unless required for deployment compatibility.

If computeFocusScore() has already been implemented, preserve it exactly unless there is a bug.

Do not redesign the scoring algorithm.

==================================================
12. TESTING
==================================================

After making deployment-preparation changes, run all existing backend tests.

Also verify:

1. Flask works with SQLite when DATABASE_URL is absent.
2. /api/health works.
3. Dashboard loads.
4. Session creation still works.
5. Blocked-attempt saving still works.
6. Finishing a session still works.
7. Stats endpoint still works.
8. Extension still communicates with localhost.
9. Extension blocking still works.
10. Extension still works when the backend is offline.
11. gunicorn app:app starts successfully.
12. No credentials or secrets are present in tracked files.

If practical, test the database configuration against SQLAlchemy's PostgreSQL URL handling without requiring a real production database.

==================================================
13. .GITIGNORE
==================================================

Inspect .gitignore.

Make sure it excludes things such as:

.env
.env.*
.venv/
venv/
__pycache__/
*.pyc
instance/
*.db
.DS_Store

Do not ignore source files that need to be deployed.

==================================================
14. README
==================================================

Do NOT write my final README prose.

If necessary, update only placeholder headings or technical setup placeholders.

I will write the README in my own words.

==================================================
15. PROMPT LOG
==================================================

Append THIS ENTIRE PROMPT verbatim to:

lock-in-bro/prompt_log.md

as the next Key Prompt.

Do not summarize it.
Do not rewrite it.
Do not invent any development history.

==================================================
16. DO NOT DO YET
==================================================

Do NOT:

- deploy to Render
- create a Render account/service
- create a PostgreSQL database
- change my portfolio
- package the extension
- create a GitHub release
- record a demo
- publish to the Chrome Web Store
- commit
- push

==================================================
WHEN FINISHED
==================================================

Give me:

1. Every file you changed.
2. What each change was for.
3. Whether gunicorn app:app works.
4. Which PostgreSQL driver is being used.
5. Exactly how DATABASE_URL is handled.
6. Whether a new PostgreSQL database can initialize correctly.
7. Where the extension backend URL is configured.
8. Exactly what I need to change once I get my Render URL.
9. Any manifest permission changes I will need after getting the Render URL.
10. Whether CORS is needed and how it is configured.
11. Exact Render settings I should enter:

   - Root Directory
   - Build Command
   - Start Command

12. Every Render environment variable I need.
13. How to initialize the production database after deployment.
14. A manual deployment checklist for me.
15. Any remaining deployment risks or bugs.
16. A suggested commit message.

Stop after preparing the code. Do not deploy anything.


## Key Prompt — Downloadable Extension

I want to make the Lock In Bro Chrome extension directly downloadable from my portfolio.

The project is inside:

/Users/whosamy/Documents/whosamyy.github.io/lock-in-bro

My portfolio is the whosamyy.github.io repository.

The deployed dashboard is:

https://lock-in-bro.onrender.com

IMPORTANT:
- The extension is already working.
- Do NOT change extension functionality.
- Do NOT change blocking, timer, backend syncing, database logic, or focus-score logic.
- Do NOT deploy anything.
- Do NOT commit or push yet.

==================================================
GOAL
==================================================

I want my Lock In Bro portfolio project to have three buttons:

[Open Dashboard]
[Download Extension]
[View Code]

The Download Extension button should directly download a clean ZIP file that a user can unzip and load through Chrome's Developer Mode.

==================================================
1. CREATE A CLEAN EXTENSION ZIP
==================================================

Create:

lock-in-bro/downloads/lock-in-bro-extension.zip

The ZIP should contain ONLY the files required for the Chrome extension to run.

Include the contents of:

lock-in-bro/extension/

including files such as:

- manifest.json
- config.js
- popup.html
- popup.css
- popup.js
- background.js
- blocked.html
- blocked.css
- blocked.js
- focus-score.js
- any other extension assets that are actually referenced by manifest.json or the extension code

Do NOT include:

- backend/
- database files
- .git/
- .env
- .venv/
- __pycache__/
- prompt_log.md
- README.md
- tests
- .DS_Store
- unrelated portfolio files

Before packaging, verify that config.js is currently using the production backend:

https://lock-in-bro.onrender.com

Do not change it if it is already correct.

==================================================
2. ZIP STRUCTURE
==================================================

Make the ZIP easy to install.

When the user unzips it, I want the result to look like:

lock-in-bro-extension/
├── manifest.json
├── config.js
├── popup.html
├── popup.css
├── popup.js
├── background.js
├── blocked.html
├── blocked.css
├── blocked.js
├── focus-score.js
└── any other required extension assets

I do NOT want an unnecessary extra nesting level such as:

lock-in-bro-extension/extension/manifest.json

manifest.json should be directly inside the unzipped extension folder.

==================================================
3. INSTALLATION INSTRUCTIONS
==================================================

Create a short installation instruction file at:

lock-in-bro/downloads/INSTALL.txt

Keep it concise and student-friendly.

It should explain:

1. Download lock-in-bro-extension.zip
2. Unzip it
3. Open chrome://extensions
4. Turn on Developer mode
5. Click Load unpacked
6. Select the unzipped lock-in-bro-extension folder
7. Pin Lock In Bro if desired
8. Start a focus session and grant access to the websites the user chooses to block

Do not claim the extension is published on the Chrome Web Store.

==================================================
4. PORTFOLIO BUTTON
==================================================

Inspect my existing portfolio and the Lock In Bro project card/page that was already added.

Add a third button:

Download Extension

The three buttons should now be:

Open Dashboard
Download Extension
View Code

Match the existing portfolio styling exactly.

The Download Extension button should link directly to:

/lock-in-bro/downloads/lock-in-bro-extension.zip

Use the correct relative/absolute path for GitHub Pages so that clicking the button from:

https://whosamyy.github.io/

downloads the ZIP successfully.

If appropriate, use the HTML download attribute, but make sure the link still works normally if the browser ignores it.

==================================================
5. OPTIONAL INSTALL INSTRUCTIONS LINK
==================================================

If the Lock In Bro project page already has space for it, add a small:

"How to install"

link pointing to:

/lock-in-bro/downloads/INSTALL.txt

Do not clutter the main project card if it would look awkward.

==================================================
6. VERIFY THE ZIP
==================================================

After creating the ZIP:

- inspect its contents
- confirm manifest.json is at the correct top level
- confirm every file referenced by manifest.json exists
- confirm no backend/database/private/unnecessary files are included
- confirm config.js points to:
  https://lock-in-bro.onrender.com
- confirm there are no secrets or credentials
- confirm the ZIP can be extracted successfully

Do not modify the working extension just to make the ZIP.

==================================================
7. TEST PORTFOLIO LINKS
==================================================

Verify:

Open Dashboard
-> https://lock-in-bro.onrender.com

Download Extension
-> the new lock-in-bro-extension.zip

View Code
-> the existing GitHub source link

Also verify that the new button does not break the desktop or mobile layout.

==================================================
8. DO NOT DO
==================================================

Do NOT:

- publish to Chrome Web Store
- modify the Flask backend
- modify PostgreSQL
- modify Render settings
- rewrite the extension
- change my focus score
- change unrelated portfolio projects
- write my final Project 2 README
- commit
- push

==================================================
9. PROMPT LOG
==================================================

Append THIS ENTIRE PROMPT verbatim to:

lock-in-bro/prompt_log.md

as the next Key Prompt.

Do not summarize or rewrite it.

==================================================
WHEN FINISHED
==================================================

Tell me:

1. Exactly which files were created or changed.
2. The exact contents of the ZIP.
3. Confirm manifest.json is at the top level after extraction.
4. The exact URL the Download Extension button will use.
5. Where the installation instructions are.
6. How I can test the download locally.
7. How I should test it after pushing to GitHub Pages.
8. Any problems you found.
9. A suggested commit message.

Do not commit or push anything.
