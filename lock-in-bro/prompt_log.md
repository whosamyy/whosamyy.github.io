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


## Key Prompt — Google Dashboard Authentication

I want to add authentication to Lock In Bro.

IMPORTANT: The existing Chrome extension, Flask backend, PostgreSQL database,
Render deployment, focus dashboard, and portfolio are currently working.

Do NOT rewrite the project.
Do NOT change the website-blocking behavior.
Do NOT change focus timers.
Do NOT change the focus-score formula.
Do NOT change the production backend URL.
Do NOT commit, push, or deploy anything yet.

==================================================
GOAL
==================================================

Users should now have to SIGN IN WITH GOOGLE before they can view their
Lock In Bro focus dashboard.

I specifically want to protect DASHBOARD VIEWING.

For this phase, do NOT make the Chrome extension itself require Google login.

The extension should continue working as it currently does:
- starts sessions
- blocks chosen websites
- records blocked attempts
- sends sessions to Flask
- uses its anonymous client_id

Authentication should protect access to the user's stored analytics.

==================================================
DESIRED FLOW
==================================================

Current extension behavior:

Chrome extension
→ anonymous client_id
→ Flask API
→ PostgreSQL

New dashboard behavior:

User clicks "Open focus dashboard"
→ https://lock-in-bro.onrender.com/?client_id=...
→ if not signed in, show/redirect to Google Sign In
→ user signs in
→ that client_id is linked to that Google account
→ user sees their dashboard

After the client_id has been linked, redirect to a clean dashboard URL
without client_id in the query string if practical.

On future dashboard visits:

User signs in
→ backend knows which client_id(s) belong to the user
→ dashboard only shows that user's data

==================================================
AUTHENTICATION TECHNOLOGY
==================================================

Use Google OAuth / OpenID Connect with Flask.

Use a maintained library such as Authlib if appropriate.

Do NOT implement my own password system.

Do NOT store passwords.

Do NOT add username/password registration.

Use server-side Flask session authentication.

==================================================
ENVIRONMENT VARIABLES
==================================================

Do not hardcode OAuth credentials.

Prepare the app to use environment variables such as:

GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
SECRET_KEY

If another variable is genuinely necessary, explain why.

Do not put real credential values in source code.

Keep local development possible.

At the end, tell me exactly which environment variables I will need to add
to Render.

==================================================
DATABASE DESIGN
==================================================

Do not destroy or rewrite my existing FocusSession or BlockedAttempt data.

Add the smallest clean database structure needed for authentication.

A reasonable structure would be:

User
- id
- google_sub
- created_at

ClientInstallation
- id
- client_id
- user_id
- created_at

Use Google's stable "sub" identifier as the external account identifier.

Do NOT store the user's email, name, profile picture, or other Google profile
information unless it is actually necessary.

Prefer collecting the minimum amount of information.

A user may eventually have multiple client installations, so one User should
be able to own multiple client_ids.

Existing focus sessions are already associated with client_id.

Do NOT unnecessarily add user_id to every existing FocusSession if ownership
can cleanly be determined through ClientInstallation.

==================================================
CLIENT ID CLAIMING
==================================================

When a signed-in user visits:

/?client_id=abc123

handle it like this:

1. Validate the client_id.
2. Check whether it already belongs to a user.
3. If it is unclaimed:
   - associate it with the currently signed-in user.
4. If it already belongs to the current user:
   - continue normally.
5. If it belongs to a DIFFERENT user:
   - do NOT show that dashboard.
   - return a safe error/403 page.
6. After successful linking, redirect to a clean dashboard route without
   exposing client_id unnecessarily in the URL.

The client_id values are random UUIDs already generated by the extension.

Clearly document that possession of an unclaimed client UUID is being used
as the initial pairing mechanism and that this is not as strong as having
the extension itself authenticate.

Do NOT pretend this is perfect production-grade account linking.

==================================================
DASHBOARD ACCESS
==================================================

The dashboard route must require authentication.

If someone visits:

https://lock-in-bro.onrender.com/

while logged out:

they should not see focus analytics.

Instead, show a clean Lock In Bro login screen or redirect to /login.

Use wording such as:

LOCK IN BRO
Lock in now. Scroll later.

Sign in to view your focus dashboard.

[ Continue with Google ]

Match the existing pink Lock In Bro dashboard design.

Do not redesign the rest of the site.

==================================================
ROUTES
==================================================

Add clean authentication routes, for example:

GET /login
GET /auth/callback
POST or GET /logout

Use appropriate OAuth state protection.

The exact route names may differ if there is a better Flask/Authlib pattern,
but keep them simple.

==================================================
STATS SECURITY
==================================================

IMPORTANT:

The current endpoint:

GET /api/stats/<client_id>

must no longer allow arbitrary unauthenticated users to retrieve another
client's analytics.

Protect dashboard statistics.

Either:

A. Require an authenticated Flask session AND verify that the requested
   client_id belongs to that user

or preferably:

B. Add a user-scoped authenticated endpoint such as:

GET /api/me/stats

which automatically gets all client_ids belonging to the signed-in user.

If a user owns multiple client_ids, aggregate their analytics reasonably.

The dashboard JavaScript should no longer trust a client_id from the URL
to decide whose data to display after linking.

Do not break the extension's session-writing endpoints in this phase.

==================================================
IMPORTANT API SCOPE
==================================================

For THIS phase:

Do NOT require authentication for the extension's existing session-write
endpoints yet.

The extension must continue being able to:

POST /api/sessions
POST /api/sessions/<id>/blocked
POST /api/sessions/<id>/finish

without requiring the user to sign in through the extension.

This phase is specifically about protecting DASHBOARD READ ACCESS.

Clearly note in your final response that write authentication remains a
future security improvement.

==================================================
PRIVACY
==================================================

Preserve Lock In Bro's privacy-focused design.

Do NOT store:

- passwords
- general browsing history
- allowed websites
- page contents
- search queries
- Google access tokens permanently unless technically necessary
- unnecessary Google profile information

Store only what is needed for authentication and focus analytics.

Request the minimum Google scopes needed for sign-in.

==================================================
SESSION SECURITY
==================================================

Use secure Flask session settings appropriate for production.

Use:
- HTTPOnly cookies
- SameSite protection
- Secure cookies in production over HTTPS

Make sure local development over http://127.0.0.1:5000 can still work.

Handle Render's HTTPS/proxy environment correctly.

Do not disable OAuth state validation.

==================================================
EXISTING USERS / EXISTING DATA
==================================================

Do not delete my existing PostgreSQL focus-session data.

After authentication is added:

If I open the dashboard from my existing Chrome extension using its existing
client_id and then sign in with Google, my existing sessions for that
client_id should become visible under my account.

That way I do not lose my current analytics.

==================================================
DATABASE INITIALIZATION
==================================================

Update:

flask --app app init-db

so a new database creates the new authentication-related tables.

For the existing deployed PostgreSQL database, make sure adding these NEW
tables does not delete or overwrite existing tables/data.

Do not introduce destructive schema operations.

If a migration is needed, explain it before doing anything destructive.

==================================================
LOCAL TESTING
==================================================

Do not require real Google credentials for automated tests.

Mock or stub OAuth behavior in tests.

Add tests for at least:

1. Logged-out user cannot view dashboard analytics.
2. Logged-out stats request is rejected.
3. Authenticated user can access their dashboard.
4. User can claim an unclaimed client_id.
5. Existing sessions associated with that client_id appear after claiming.
6. Same user can revisit their dashboard.
7. Another user cannot claim an already-owned client_id.
8. Another user cannot access that client's stats.
9. Missing client_id does not crash.
10. Invalid client_id does not crash.
11. Existing extension write API tests still pass.
12. Existing blocking/browser tests still pass.
13. Existing PostgreSQL configuration tests still pass.
14. Logout removes dashboard access.

Do not make tests call Google's real OAuth servers.

==================================================
EXTENSION
==================================================

Do not rewrite the extension.

The existing "Open focus dashboard" button should continue opening a URL
containing the local anonymous client_id so the backend can perform initial
account linking.

Do not add chrome.identity or extension-side Google OAuth in this phase.

Do not modify the blocking permissions unless authentication actually
requires something.

==================================================
LOGIN UI
==================================================

Make the login page fit the current Lock In Bro style.

Keep it simple.

Something like:

LOCK IN BRO

Lock in now. Scroll later.

Your focus history is private.
Sign in to view your dashboard.

[ Continue with Google ]

Do not add fake testimonials, marketing copy, pricing, or unnecessary pages.

==================================================
ERROR STATES
==================================================

Handle these cleanly:

- Google login cancelled
- OAuth callback error
- missing OAuth environment variables
- malformed client_id
- client_id already owned by another account
- database error
- logged-out stats request
- expired Flask session

Do not expose stack traces or secrets to users.

==================================================
RENDER PREPARATION
==================================================

Do NOT deploy yet.

Prepare the project so I can later configure Google OAuth on Render.

My production site is:

https://lock-in-bro.onrender.com

At the end, tell me the exact Google OAuth redirect URI I should register.

It will likely be something similar to:

https://lock-in-bro.onrender.com/auth/callback

but determine the exact URI from your implementation.

Also tell me the localhost redirect URI needed for development.

==================================================
README
==================================================

Do NOT rewrite my README.

If authentication changes make something factually outdated, tell me what
section I should update myself.

==================================================
PROMPT LOG
==================================================

Append THIS ENTIRE PROMPT verbatim to:

lock-in-bro/prompt_log.md

as the next Key Prompt.

Do not summarize it.
Do not rewrite it.
Do not invent development history.

==================================================
DO NOT DO
==================================================

Do NOT:

- deploy to Render
- create Google credentials for me
- commit
- push
- publish a new ZIP yet
- modify my portfolio yet
- implement extension-side Google OAuth
- implement passwords
- delete existing session data
- redesign the dashboard
- change the focus score
- change blocking behavior

==================================================
WHEN FINISHED
==================================================

Tell me:

1. Every file you changed or created.
2. The authentication architecture.
3. The database changes.
4. How client_id ownership works.
5. How existing anonymous sessions become linked to a user.
6. Every authentication route.
7. How dashboard access is protected.
8. How stats API access is protected.
9. What remains unauthenticated and why.
10. What Google OAuth scopes are requested.
11. Exactly which Render environment variables I need.
12. Exact production OAuth redirect URI.
13. Exact localhost OAuth redirect URI.
14. How SECRET_KEY should be generated.
15. How to initialize the new tables without deleting existing data.
16. Test results.
17. Any security limitations that still remain.
18. Exactly what I need to do in Google Cloud Console.
19. Exactly what I need to do in Render afterward.
20. A manual local testing checklist.
21. A suggested commit message.

Stop after implementing and testing locally.
Do not deploy or push.


## Key Prompt — Lock In Pig Rewards

I want to add a cute reward feature to Lock In Bro: a super cute little pig on the focus dashboard.

IMPORTANT:
- The existing Chrome extension, Flask backend, PostgreSQL/SQLite setup, dashboard, and deployment already work.
- Do NOT rewrite the project.
- Do NOT break the existing blocking, timer, session-saving, focus-score, or dashboard functionality.
- Do NOT redesign the whole app.
- Do NOT commit, push, or deploy anything yet.

==================================================
GOAL
==================================================

Add a cute dashboard reward system centered around a little pig character.

The pig should make the dashboard feel more fun and rewarding.

The pig should be:
- super cute
- pastel pink
- round/chubby
- simple and polished
- expressive and friendly
- visually consistent with the current pink Lock In Bro aesthetic

I want this to feel like a "focus pet" / "study buddy" feature.

==================================================
CORE FEATURE
==================================================

Add a "Lock In Pig" section to the focus dashboard.

The user should see:

- a cute pig character
- pig level
- pig XP
- unlocked accessories or rewards
- a short encouraging message

This pig should reward the user for completing focus sessions.

==================================================
REWARD LOGIC
==================================================

Use existing session data to power the pig rewards.

A simple system is fine.

For example:

- completed focus session -> gain XP
- more focused minutes -> more XP
- higher focus score -> bonus XP
- good streak / low blocked attempts -> optional bonus

Keep it simple and easy to explain.

I do NOT want overly complicated game logic.

You may implement something like:

- XP earned per completed session
- pig level increases at XP thresholds
- small cosmetic unlocks at certain levels

Example unlocks:
- Level 2: blush sparkle
- Level 3: pink bow
- Level 5: headphones
- Level 7: tiny strawberry
- Level 10: heart glasses

These rewards are just examples. Keep them cute and simple.

==================================================
VISUAL DESIGN
==================================================

The pig must be VERY cute.

Visual guidance:
- big shiny eyes
- round pink body
- darker pink snout
- little ears
- blush cheeks
- tiny hooves
- happy expression
- optional sparkle/hearts nearby

Do NOT use a realistic pig.
Do NOT use a corporate mascot style.
Do NOT use anything creepy, overly detailed, or childish in a low-quality way.

I want something that looks polished, adorable, and charming.

Implement the pig using local HTML/CSS/SVG or inline SVG if appropriate.
Do NOT depend on external image APIs.
Do NOT use copyrighted character art.

The pig should scale nicely on desktop and mobile.

==================================================
DASHBOARD UI
==================================================

Add a new dashboard section/card, something like:

LOCK IN PIG

[ super cute pig ]
Level 3
XP: 85 / 120

Unlocked:
- Pink Bow
- Sparkle Blush

Message:
"bro you actually locked in today 💖"

This should fit nicely into the current dashboard layout.
Match the current pink style.

Do NOT redesign the rest of the dashboard unless small layout adjustments are necessary.

==================================================
PERSISTENCE
==================================================

Persist the pig progress.

Use the cleanest reasonable option.

If the app already has authentication, associate the pig with the signed-in user.
If the app is still using the client_id dashboard model, associate it with the same user/client data model already used for analytics.

You may:
- derive XP/level directly from focus sessions, OR
- create a small pig profile table if needed

Prefer the simplest clean architecture.

If adding a database table is useful, something like this is fine:

PigProfile
- id
- user_id OR client_id
- total_xp
- level
- unlocked_items (JSON or similar)
- updated_at

But if the same result can be achieved cleanly from existing data, that is also acceptable.

Explain which approach you chose and why.

==================================================
ENCOURAGING MESSAGES
==================================================

Show a short fun message near the pig.

Examples of the tone I want:
- "bro you locked in 💖"
- "piggy is proud of you"
- "one more session and piggy gets a new accessory"
- "you resisted the scroll... legendary behavior"
- "academic weapon energy"

Keep the tone cute, playful, and consistent with "Lock In Bro."

Do not make it cringe or overly long.

==================================================
DO NOT CHANGE
==================================================

Do NOT:
- change the extension blocking behavior
- change timer behavior
- change backend endpoints unless needed for pig data
- change the focus-score formula unless absolutely necessary
- change the auth system unless needed to attach pig progress
- add new external services
- add paid APIs
- add unnecessary complexity
- replace the dashboard analytics

The existing dashboard analytics should remain and still work.

==================================================
TESTING
==================================================

After implementing, verify:

1. Existing dashboard analytics still load.
2. Pig section appears correctly.
3. Pig looks cute on desktop.
4. Pig looks good on mobile.
5. XP/level/rewards display correctly.
6. Pig progress persists correctly.
7. Existing session data still works.
8. Existing tests still pass if possible.
9. No console errors.
10. No broken CSS/layout issues.

If you add pig-specific backend logic, add reasonable tests.

==================================================
README / PROMPT LOG
==================================================

Do NOT rewrite my README.

If this feature means I should update a README section later, tell me what to update.

Append THIS ENTIRE PROMPT verbatim to:
lock-in-bro/prompt_log.md

as the next Key Prompt.

Do not summarize or rewrite it.

==================================================
WHEN FINISHED
==================================================

Tell me:
1. Every file you changed or created.
2. How the pig reward system works.
3. Whether pig progress is derived or stored.
4. How XP is calculated.
5. How levels/unlocks work.
6. How persistence works.
7. How the pig is rendered (CSS/SVG/etc.).
8. Any tests you added or updated.
9. Any limitations.
10. A suggested commit message.

Do not commit, push, or deploy anything.


## Key Prompt — Lock In Pig Moods, Room Customization, and Focus Weather

I want to expand Lock In Bro’s existing cute pig reward system with three connected features:

1. Pig Mood System
2. Pig Room / Desk Customization
3. Focus Weather

IMPORTANT:
- Lock In Bro already has a working Chrome extension, Flask backend, PostgreSQL database, Google sign-in, focus dashboard, and pig reward system.
- Preserve all existing functionality.
- Do NOT rewrite the app.
- Do NOT break Google authentication.
- Do NOT break extension blocking, timers, session saving, analytics, focus scores, or existing pig progression.
- Do NOT commit, push, or deploy anything yet.

==================================================
OVERALL DESIGN GOAL
==================================================

I want these new features to feel like one cohesive, adorable “Lock In Pig” world.

The vibe should be:

- super cute
- cozy
- pastel pink
- soft and polished
- slightly playful
- charming without looking childish or messy
- consistent with the existing pink Lock In Bro dashboard

Think:
cute study buddy
cozy desk setup
soft pastel room
little pig reacting to how the user studies

Avoid:
- corporate dashboard styling
- realistic animals
- overly complex game UI
- loud neon colors
- childish clip-art look
- excessive animations
- clutter

The dashboard should still be usable as a real productivity dashboard.

==================================================
FEATURE 1 — PIG MOOD SYSTEM
==================================================

Add a mood system for the existing Lock In Pig.

The pig’s mood should react to the user’s recent focus behavior.

Use existing focus session data when possible.

Possible moods:

HAPPY
- user completed a recent session
- strong focus score
- low distraction count

PROUD
- especially strong completed session
- high focus score such as 90+
- or completed multiple sessions recently

COZY
- average/normal session
- user is making progress without anything extreme

SLEEPY
- very short session
- late-night / low-energy vibe if time data is available
- or no recent focus activity

DISTRACTED / SIDE-EYE
- many blocked attempts during the recent session
- keep this funny, not mean

EXCITED
- level up
- unlocked a new room item
- hit a focus milestone

Do NOT punish the user harshly.
This should feel supportive and funny.

Examples of pig messages:

Happy:
"piggy is proud of you 💗"

Proud:
"academic weapon behavior"

Cozy:
"we’re locked in and comfy"

Sleepy:
"piggy needs a tiny coffee ☕"

Distracted:
"bro… instagram again? 😭"

Excited:
"NEW ITEM UNLOCKED!! ✨"

==================================================
MOOD LOGIC
==================================================

Keep the mood logic simple and deterministic.

Create a clearly named function or helper for calculating mood.

For example:

determinePigMood({
  latestSession,
  recentSessions,
  focusScore,
  blockedCount,
  completed,
  unlockedSomething
})

The exact parameters may differ based on the current architecture.

Document the logic clearly.

Do not make the mood random except for choosing between several equivalent messages for the same mood.

==================================================
PIG VISUAL STATES
==================================================

The pig itself should visually change slightly by mood.

Examples:

Happy:
- closed happy eyes or smile
- pink cheeks
- tiny hearts

Proud:
- confident expression
- little sparkle
- maybe chest-out pose

Cozy:
- relaxed expression
- sitting at desk
- warm mug nearby

Sleepy:
- droopy eyes
- tiny "zzz"
- cozy blanket or mug

Distracted:
- side-eye expression
- tiny sweat drop or confused face

Excited:
- sparkling eyes
- little stars/hearts
- arms/hooves raised if practical

Do not create completely separate art styles for each state.
It should always clearly be the same pig.

If the pig is currently SVG/CSS-based, extend the existing implementation rather than replacing it.

==================================================
FEATURE 2 — PIG ROOM / DESK CUSTOMIZATION
==================================================

Add a cute little pig study room to the dashboard.

The pig should sit or stand near a tiny study desk.

The room should be visually integrated into the existing pig card.

I want users to be able to unlock/equip cosmetic room items.

Start with a SMALL set of items.

Categories:

DESK ITEMS
- tiny laptop
- pink mug
- little lamp
- stack of books
- strawberry drink

WALL / ROOM ITEMS
- heart poster
- little calendar
- fairy lights
- window
- tiny shelf

DECOR
- plant
- rug
- plushie
- cushion
- flower vase

PIG ACCESSORIES
- bow
- headphones
- heart glasses
- tiny beanie
- strawberry accessory

Keep everything very cute and visually consistent.

==================================================
ROOM ECONOMY
==================================================

Use the existing reward system if it already has coins/XP.

If focus coins already exist:
- use those

If only XP exists:
- do NOT create an overly complicated second economy unless necessary

If adding coins makes sense:
use a simple system such as:

1 completed focus minute = 1 coin

Optional small bonuses:
+10 coins for high focus score
+5 coins for completing the full session
+5 coins for very low distraction count

Do not remove coins for distractions.

Rewards should be positive.

==================================================
SHOP / UNLOCK UI
==================================================

Add a small customization button such as:

"Customize Pig Room"

Clicking it should open a cute modal/panel.

Show available items as small cards.

Example:

🎀 Pink Bow
Unlocked
[Equip]

🌱 Desk Plant
50 coins
[Unlock]

💡 Heart Lamp
100 coins
[Unlock]

Do not make a huge store page.

Keep the first version to around 8–12 total items.

Show:

- item name
- cute preview/icon/mini SVG if practical
- cost if locked
- unlocked status
- equip/unequip state

Users should be able to equip room items they have unlocked.

==================================================
ROOM PERSISTENCE
==================================================

Persist:

- unlocked items
- equipped items
- current room configuration

Since Google authentication now exists, associate customization with the authenticated user.

If an existing pig profile model/table exists, extend it cleanly.

Do NOT duplicate user ownership systems.

Do not store customization only in browser local storage if authenticated server-side storage already exists.

Use PostgreSQL in production and preserve SQLite local development.

==================================================
FEATURE 3 — FOCUS WEATHER
==================================================

Add subtle weather/atmosphere to the pig room.

Weather should represent the user’s recent focus quality.

Examples:

SUNNY
- strong focus session
- high focus score
- low distraction count

SOFT CLOUDS
- normal/average session

RAINY
- rough session / many distractions
- should still look cozy, not depressing

STAR NIGHT
- evening/night session
- or strong late-night focus session

SPARKLE WEATHER
- milestone
- level up
- perfect/near-perfect session

Optional:
SNOW
- rare seasonal/cozy state if easy to support

==================================================
WEATHER VISUALS
==================================================

Weather should appear around/in the pig room.

Examples:

Sunny:
- soft sunlight
- tiny sun through window

Cloudy:
- pale clouds
- muted soft sky

Rainy:
- rain outside window
- pig cozy inside with warm lamp
- perhaps mug steam

Night:
- dark lavender sky
- little stars
- moon
- fairy lights glowing

Sparkle:
- subtle stars/hearts
- celebratory glow

Important:
Rain should feel cozy, not sad.

Keep animations lightweight.

Examples:
- slowly drifting cloud
- tiny rain streaks
- gentle sparkle
- subtle lamp glow

Respect prefers-reduced-motion.

Do not use heavy canvas animations.

==================================================
WEATHER LOGIC
==================================================

Use simple rules based on:

- latest focus score
- completion status
- blocked count
- current local/session time if already available

Example logic:

focusScore >= 90 AND completed
→ sunny or sparkle

focusScore >= 70
→ soft clouds / cozy

many blocked attempts
→ rainy

nighttime session
→ star night

milestone/level-up
→ sparkle

Clearly document the priority when multiple conditions apply.

For example:

milestone > nighttime > high-focus > distracted > default

Do not make weather confusing or random.

==================================================
INTEGRATION WITH DASHBOARD
==================================================

The dashboard should still prioritize useful information.

Do not replace:

- total focus time
- sessions completed
- distractions blocked
- average focus score
- charts
- recent sessions

The pig room should be a fun section near the top or between summary cards and analytics.

A layout like this is fine:

LOCK IN BRO

[ analytics summary ]

────────────────────────

MY LOCK IN PIG

[ cozy pig room scene ]

🐷 Level 6
Mood: Proud
XP: 380 / 500
Coins: 145

"academic weapon behavior"

[ Customize Pig Room ]

────────────────────────

[ analytics charts/history ]

Keep it balanced.

==================================================
DATABASE / BACKEND
==================================================

Inspect the existing pig/account models first.

Extend existing models rather than creating duplicate concepts.

Possible fields if needed:

PigProfile
- id
- user_id
- total_xp
- coins
- level
- mood
- unlocked_items
- equipped_items
- updated_at

If mood can be derived dynamically, do NOT store it unnecessarily.

If unlocked/equipped items are stored as JSON, validate them.

Do not delete existing pig data.

Do not delete or modify existing focus history.

==================================================
AUTHENTICATION
==================================================

All pig customization should belong to the authenticated Google user.

A logged-out user should not be able to modify another user's room.

Protect any new customization API endpoints.

Do not weaken the existing dashboard authentication.

==================================================
POSSIBLE API ENDPOINTS
==================================================

Only add endpoints if needed.

Examples:

GET /api/me/pig
GET /api/me/pig/items
POST /api/me/pig/unlock
POST /api/me/pig/equip

Use authenticated current-user context.

Do not use user_id passed by the browser as proof of identity.

Do not expose another user's pig data.

==================================================
CUTE VISUAL STYLE
==================================================

This part matters a lot.

Please spend time making the pig room actually adorable.

Use:
- rounded shapes
- pastel pink
- cream/off-white
- soft lavender accents
- subtle shadows
- tiny hearts/stars
- cozy warm desk lighting
- rounded furniture

The pig should be the visual focus.

Possible scene:

window with weather
      ↓
☁️ / ☀️ / 🌙

     🎀
    🐷
  ┌───────┐
  │ 💻 ☕ │
  └───────┘
    🌱  💡
  soft rug

Do NOT literally use emoji as the final visual if the existing pig uses SVG/CSS.
The final result should look intentionally designed.

Use local SVG/CSS illustrations if that matches the existing implementation.

==================================================
MOBILE
==================================================

The room must work at:

- desktop
- tablet
- 390px mobile
- 320px mobile

On mobile:
- room can scale down
- customization panel can stack
- no horizontal overflow
- analytics must remain readable

==================================================
ACCESSIBILITY
==================================================

Keep:
- readable contrast
- keyboard-accessible customization controls
- visible focus states
- alt/aria labels where appropriate
- reduced motion support

Decorative visuals should not confuse screen readers.

==================================================
TESTING
==================================================

Add tests where appropriate.

Verify:

1. Existing dashboard still works.
2. Google sign-in still works.
3. Pig mood changes based on session state.
4. Mood messages match the mood.
5. User can unlock an item if they have enough coins.
6. User cannot unlock an item without enough coins.
7. User can equip an unlocked item.
8. User cannot equip a locked item.
9. Equipped items persist.
10. Another authenticated user cannot modify this user's pig room.
11. Focus weather logic works.
12. Mobile layout works.
13. Reduced-motion preference is respected.
14. Existing analytics and charts still work.
15. Existing extension tests still pass.
16. No console errors.
17. No Flask errors.
18. No existing database data is deleted.

==================================================
DO NOT DO
==================================================

Do NOT:

- change extension website blocking
- change focus timer behavior
- change Google login architecture
- change focus-score formula
- replace PostgreSQL
- remove existing analytics
- add multiplayer/social features
- add leaderboards
- add real-money purchases
- add external image APIs
- add AI-generated pet dialogue
- add dozens of items
- add complex game mechanics
- deploy
- commit
- push

==================================================
README
==================================================

Do NOT rewrite my README.

Tell me what small sections should be updated later to mention:

- Lock In Pig moods
- Pig room customization
- Focus weather

==================================================
PROMPT LOG
==================================================

Append THIS ENTIRE PROMPT verbatim to:

lock-in-bro/prompt_log.md

as the next Key Prompt.

Do not summarize it.
Do not rewrite it.

==================================================
WHEN FINISHED
==================================================

Tell me:

1. Every file changed or created.
2. How the pig mood system works.
3. All moods and their conditions.
4. How mood visuals differ.
5. How the pig room is rendered.
6. All initial customization items.
7. How coins/unlocks work.
8. How items are stored.
9. How equipped items persist.
10. How focus weather is determined.
11. All weather states and priority rules.
12. What database/model changes were made.
13. Any new API endpoints.
14. How authenticated ownership is enforced.
15. Test results.
16. Desktop/mobile results.
17. Any limitations.
18. What README sections I should update later.
19. A suggested commit message.

Do not commit, push, or deploy anything.


## Key Prompt — Global Focus Weather Atmosphere

I want to improve the existing Focus Weather system so it changes the ENTIRE Lock In Bro dashboard background/atmosphere.

Right now the dashboard background is mostly plain pink.

I do NOT want Focus Weather to only appear inside the pig room card.

I want the whole dashboard background to visually reflect the current focus weather while still keeping the cute pink Lock In Bro aesthetic.

IMPORTANT:
- Preserve all existing functionality.
- Do NOT redesign the whole dashboard.
- Do NOT change analytics logic.
- Do NOT change Google auth.
- Do NOT change extension behavior.
- Do NOT change focus-score logic.
- Do NOT change pig reward logic except what is needed for weather visuals.
- Do NOT commit, push, or deploy yet.

==================================================
GOAL
==================================================

Make Focus Weather affect the main dashboard background.

The dashboard should no longer look like one flat pink page.

Instead, the background should feel alive and change based on the user’s current Focus Weather state.

Keep the overall Lock In Bro identity:
- pink
- cute
- soft
- cozy
- polished

Weather should add atmosphere, not replace the pink theme completely.

==================================================
WEATHER STATES
==================================================

Use the existing Focus Weather states if they already exist.

Support states like:

SUNNY
CLOUDY / SOFT CLOUDS
RAINY
STAR NIGHT
SPARKLE / CELEBRATION

If SNOW already exists, support that too.

Do not create lots of extra weather states.

==================================================
GLOBAL BACKGROUND BEHAVIOR
==================================================

The ENTIRE dashboard page background should react to weather.

Use:
- layered gradients
- soft decorative SVG/CSS elements
- subtle animated weather
- atmospheric lighting
- soft overlays

Do NOT use:
- heavy canvas animation
- video backgrounds
- external image APIs
- giant distracting effects

The content cards should remain easy to read.

==================================================
SUNNY BACKGROUND
==================================================

Sunny should still feel pink.

Example vibe:
- pale blush pink base
- soft peach / warm cream glow near the top
- very subtle sun glow
- maybe a few tiny floating light particles
- soft warm highlight around the pig room

Do NOT make the page bright yellow.

Think:
pink morning sunlight.

==================================================
CLOUDY BACKGROUND
==================================================

Cloudy should feel soft and calm.

Example:
- dusty pink base
- pale lavender / cream gradients
- soft translucent cloud shapes near the top/background
- slightly muted lighting

Clouds should be decorative and subtle.

Do not cover text.

==================================================
RAINY BACKGROUND
==================================================

Rainy should feel COZY, not sad.

Example:
- muted rose / mauve background
- soft lavender-gray gradient
- subtle rain streaks in the page background
- tiny blurred window/rain feeling
- warm pink glow around cards
- pig room can feel extra warm inside

Do not make it dark/depressing.

The goal is:
"cozy rainy study day"

not:
"bad weather punishment"

==================================================
STAR NIGHT BACKGROUND
==================================================

Night should be one of the prettiest states.

Use:
- deep dusty pink
- lavender
- muted plum
- darker rose gradient

Add:
- small stars
- subtle moon glow
- tiny sparkles
- maybe soft fairy-light feeling

Keep text readable.

Cards can stay lighter pink/cream so the page is still easy to use.

Do NOT turn the whole dashboard black/navy.

It should still unmistakably look like Lock In Bro.

==================================================
SPARKLE / CELEBRATION BACKGROUND
==================================================

For milestones or level-ups:

Use:
- brighter pink gradient
- tiny hearts/stars/sparkles
- subtle glow
- maybe a soft radial highlight behind the pig section

Keep it tasteful.

Do not use confetti everywhere.

==================================================
BACKGROUND LAYERS
==================================================

Prefer a layered approach.

For example:

body/dashboard wrapper:
- base gradient

pseudo-elements:
- weather decoration layer

weather container:
- clouds/rain/stars/sparkles

content:
- normal cards above everything

Use appropriate z-index layering.

The decorative weather layer should:
- not block clicks
- use pointer-events: none
- stay behind dashboard content

==================================================
TRANSITIONS
==================================================

When weather changes, visually transition between states smoothly.

Use subtle CSS transitions for:
- background gradients
- opacity
- atmospheric elements

Do not animate huge layout changes.

==================================================
MOTION
==================================================

Use lightweight animations only.

Examples:
- slow drifting cloud
- very subtle falling rain
- twinkling star
- tiny sparkle pulse

Animations should be slow and soft.

Respect:

@media (prefers-reduced-motion: reduce)

When reduced motion is enabled:
- remove continuous motion
- keep static weather visuals

==================================================
READABILITY
==================================================

This is extremely important.

Weather backgrounds must NOT make analytics harder to read.

Keep:
- strong text contrast
- light readable cards
- card borders/shadows consistent
- charts visible
- recent session text readable

If necessary, slightly adjust card background opacity depending on weather.

Do not make cards transparent enough that text becomes hard to read.

==================================================
WEATHER CLASS / STATE
==================================================

Use a clean state/class approach.

For example:

body or main dashboard wrapper could receive:

weather-sunny
weather-cloudy
weather-rainy
weather-night
weather-sparkle

or equivalent.

Do not duplicate entire dashboard markup for each weather state.

==================================================
INTEGRATION
==================================================

Use the SAME weather logic already used by Focus Weather.

Do not create a second separate calculation.

There should be one source of truth for the weather state.

The pig room weather and global dashboard weather must always match.

For example:

Focus Weather = rainy

should mean:
- pig room window shows rain
- entire dashboard becomes cozy rainy pink

==================================================
MOBILE
==================================================

Test the background at:

- desktop
- tablet
- 390px
- 320px

On mobile:
- decorative weather should not crowd content
- rain/clouds/stars can be reduced
- no horizontal overflow
- no giant fixed SVGs breaking layout

==================================================
PERFORMANCE
==================================================

Keep this lightweight.

Avoid:
- giant SVG files
- large raster images
- canvas particle engines
- external animation libraries

Prefer:
- CSS
- small inline/local SVG
- pseudo-elements

==================================================
TESTING
==================================================

Verify:

1. Sunny changes the global dashboard atmosphere.
2. Cloudy changes the global background.
3. Rainy changes the global background.
4. Night changes the global background.
5. Sparkle changes the global background.
6. Pig room and page always use the same weather state.
7. Text/cards remain readable in every state.
8. Dashboard analytics still work.
9. Google auth still works.
10. Mobile layouts still work.
11. Reduced-motion mode works.
12. No console errors.
13. No Flask errors.
14. Weather decoration does not block clicks.

==================================================
DO NOT DO
==================================================

Do NOT:
- redesign dashboard cards
- remove pink branding
- make weather overly realistic
- use stock backgrounds
- add external APIs
- use WebGL
- use video
- use heavy JavaScript animation
- change backend weather rules unless absolutely necessary
- change extension behavior
- commit
- push
- deploy

==================================================
PROMPT LOG
==================================================

Append THIS ENTIRE PROMPT verbatim to:

lock-in-bro/prompt_log.md

as the next Key Prompt.

Do not summarize it.
Do not rewrite it.

==================================================
WHEN FINISHED
==================================================

Tell me:

1. Which files changed.
2. How each weather state changes the global dashboard background.
3. How pig-room weather and global weather share one source of truth.
4. What animations were added.
5. How reduced-motion is handled.
6. How readability is preserved.
7. Desktop/mobile test results.
8. Any limitations.
9. A suggested commit message.

Do not commit, push, or deploy anything.
