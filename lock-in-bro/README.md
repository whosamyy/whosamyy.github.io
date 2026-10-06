# Lock In Bro

## What It Does
Lock In Bro is a Chrome extension I made to help make studying less distracting and a little more fun. You can choose websites that distract you, enter what you are working on, and start a focus session. During the session, the extension blocks those websites and redirects you to a custom page if you try to open them.

It also saves your focus sessions and shows your study history on a dashboard. The dashboard tracks things like focus time, blocked attempts, focus scores, and recent sessions.

I also added a reward system with a cute pig study buddy. Completing focus sessions earns progress and rewards that can be used to customize the pig and its study room. The pig has different moods, the room has changing focus weather, and users can unlock different decorations and accessories.

## How to Use It
Download the extension ZIP from my portfolio, unzip it, and go to `chrome://extensions` in Chrome. Turn on Developer Mode, click **Load unpacked**, and select the extracted Lock In Bro extension folder.

Open the extension, enter what you are working on, choose a focus time, and add the websites you want to block. Once the session starts, those websites will be blocked until the session ends.

The timer keeps running even if the popup is closed. When the session is over, the websites become available again.

You can also click **Open Focus Dashboard** to view your stats. The dashboard uses Google sign-in so each user can access their own focus history and pig customization.

## Main Features
- Custom website blocklist
- Focus timer with preset and custom durations
- Active sessions stay running even when the popup is closed
- Custom blocked page when you try to visit a distracting site
- Tracks blocked website attempts
- Saves focus sessions to a Flask backend and PostgreSQL database
- Focus score for each session
- Google sign-in for the focus dashboard
- Dashboard with focus time, recent sessions, blocked sites, and charts
- Cute Lock In Pig reward system
- Pig moods that react to recent focus behavior
- Pig room and desk customization
- Unlockable accessories and room decorations
- Focus coins and progression rewards
- Rotating, milestone, seasonal, and rare shop items
- Focus weather that changes both the pig room and dashboard background
- Downloadable Chrome extension that can be loaded through Developer Mode

## How to Run It
Download the extension ZIP, unzip it, and go to `chrome://extensions` in Chrome. Turn on Developer Mode, click **Load unpacked**, and select the extracted Lock In Bro extension folder.

The dashboard and backend are deployed through Render, so normal users do not need to run the backend themselves.

For local development, the Flask backend can be run from the `backend` folder. The local version uses SQLite by default, while the deployed version uses PostgreSQL.

## Architecture
Lock In Bro has two main parts: a Chrome extension and a Flask backend.

The Chrome extension handles the timer, website blocking, active session state, and blocked-attempt tracking. It uses `chrome.storage.local` so the session keeps working even when the popup is closed.

The extension sends session information to the Flask backend. The backend saves focus sessions and blocked attempts in a database. SQLite is used for local development and PostgreSQL is used for the deployed version on Render.

The Flask backend also serves the focus dashboard. Google OAuth is used to sign users in and connect their dashboard to the focus data from their extension.

The dashboard also handles the pig reward system, including pig progress, customization, unlocked items, moods, and focus weather.

## Privacy
Lock In Bro only collects information that is needed for focus sessions and the dashboard. It does not save general browsing history, page contents, search queries, passwords, or websites that are not part of the user's blocklist.

During a focus session, it only records attempts to visit websites that the user specifically chose to block.

Users sign in to the dashboard with Google, but Lock In Bro does not store Google passwords. Google handles the actual authentication. The app uses the user's Google account identity to connect them to their own dashboard and saved focus data.

## AI Usage
I used Codex for most of the implementation, including the Chrome extension, Flask backend, database, Google authentication, analytics dashboard, and the pig reward/customization system.

I used ChatGPT mainly to help plan the project, think of features, decide how different parts of the app should work together, and make more detailed prompts for Codex.

I also manually tested the project throughout development. One of the biggest issues I found was that an early version appeared to start a focus session but did not actually block the websites I selected. It also did not keep showing the active session after reopening the popup. I found those problems through testing and then used more specific debugging prompts to fix them.

Later in the project, I also manually tested the deployed backend, Google login, downloadable extension, dashboard, and pig customization features to make sure the generated code actually worked together.