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
