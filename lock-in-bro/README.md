# Lock In Bro

## What It Does
Lock In Bro is a Chrome extension I made to help me stay focused while studying. You can choose websites that distract you, start a focus session, and the extension will block those sites until the session is over. It also tracks things like how long you studied and how many times you tried to open a blocked website.

## How to Use It
Open the extension, type in what you are working on, choose how long you want to focus, and add the websites you want to block. Once you start the session, those websites will redirect to a blocked page if you try to visit them.

The timer keeps running even if you close the extension popup. When the session ends, the websites are unblocked again. You can also open the focus dashboard to see your past sessions and statistics.

## Main Features
- Custom website blocklist
- Focus timer with preset and custom durations
- Session stays active even when the popup is closed
- Redirect page when you try to visit a blocked site
- Tracks blocked website attempts
- Saves completed study sessions
- Focus score for each session
- Dashboard showing focus time, recent sessions, blocked websites, and other statistics
- Downloadable Chrome extension that can be loaded through Developer Mode

## How to Run It
Download the extension ZIP, unzip it, and go to `chrome://extensions` in Chrome. Turn on Developer Mode, click **Load unpacked**, and select the extracted Lock In Bro folder.

The dashboard is already deployed online through Render. For local development, the Flask backend can also be run from the `backend` folder using the commands in the project setup.

## Architecture
Lock In Bro has two main parts: a Chrome extension and a Flask backend. The extension handles the focus timer, blocked websites, session state, and blocked-attempt tracking. It uses `chrome.storage.local` so an active session can keep working even after the popup is closed.

The extension sends session data to the Flask backend, which stores it in a database. SQLite is used locally and PostgreSQL is used for the deployed version. The Flask backend also serves the analytics dashboard, which displays past focus sessions and statistics.

## Privacy
Lock In Bro only stores information related to focus sessions. It does not collect general browsing history, page contents, search queries, passwords, names, or emails.

The extension only keeps track of websites that the user personally adds to their blocklist and attempts to visit during an active session. It uses a randomly generated anonymous client ID instead of requiring an account.

## AI Usage
I used Codex for most of the implementation, including the Chrome extension, Flask backend, database, dashboard, and debugging. I used ChatGPT to help plan the project, decide how the different parts should work together, and write more specific prompts for Codex.

I also manually tested the project throughout development. One example was when the first version appeared to start a focus session, but it did not actually block the websites that I told it to block and did not keep showing the active session after reopening the popup. I found those issues through testing and then used more specific debugging prompts to fix them.