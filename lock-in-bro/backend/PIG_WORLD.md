# Lock In Pig world

The catalog has grown from the original 12 items documented below to 29 items.
See [PIG_SHOP.md](PIG_SHOP.md) for the current shop, weekly and seasonal dates,
new milestone unlocks, variant slots, and compatibility details.

This extends the existing dashboard and SVG pig. Extension blocking, timers,
Google OAuth architecture, session ingestion, focus-score calculation, analytics,
and the original XP formula and accessory thresholds are unchanged.

## Mood rules

`determine_pig_mood` in `pig_room.py` uses the latest finished session within
48 hours, ordered by end time and ID. Running sessions and future-dated finishes
do not determine atmosphere. Naive SQLite timestamps are interpreted as UTC.
The first matching rule wins:

| Priority | Mood | Condition | Visual | Message |
| --- | --- | --- | --- | --- |
| 1 | Excited | Recent completed session crossed an XP level or became the fifth/tenth/etc. completion; or a successful new room purchase | Star eyes and a little sparkle | “new little win unlocked!! ✨”; purchase: “NEW ITEM UNLOCKED!! ✨” |
| 2 | Sleepy | No finished session within 48 hours | Closed droopy eyes, little z's | “piggy needs a tiny coffee ☕” |
| 3 | Distracted | Latest recent session has at least 5 blocked attempts | Side-eye and blue sweat drop | “a tiny detour? piggy saved your seat 💗” |
| 4 | Sleepy | Session started at 21:00–05:59 in the browser's timezone, or actual duration below 5 minutes | Droopy eyes, little z's | “piggy needs a tiny coffee ☕” |
| 5 | Proud | Latest session completed, and either score at least 90 or at least 3 completed sessions in the past 48 hours | Confident curved eyes and raised brows | “academic weapon behavior” |
| 6 | Happy | Latest completed session has score at least 70 and at most 2 blocked attempts | Happy closed eyes and a small heart | “piggy is proud of you 💗” |
| 7 | Cozy | Any other recent finished session, including an early finish | Original relaxed shiny eyes | “we’re locked in and comfy” |

All rules and messages are deterministic. No XP/coins are removed for early
finishes or distractions. A milestone stays celebratory until another finished
session changes the context or it becomes older than 48 hours. A purchase returns
an excited response; the dashboard holds that atmosphere for 15 seconds. This
short UI celebration does not persist as mood data.

## Weather rules

`determine_focus_weather` uses the same recent session and timezone. The first
matching rule wins:

1. **Sparkle:** new purchase, XP level crossed, every fifth completion, or a
   completed session with score at least 98. Warm sky with small golden stars.
2. **Star night:** session started at 21:00–05:59 local time. Lavender sky, moon,
   stars, and a glow on equipped fairy lights.
3. **Cozy rain:** at least 5 blocked attempts or a recorded score below 50.
   Pale lavender clouds and gentle rain, while the room stays warm.
4. **Sunny:** completed session, score at least 90, at most 2 blocked attempts.
   Soft cream sky with a small golden sun.
5. **Soft clouds:** all remaining cases, including no recent finished sessions.

The browser sends its IANA timezone as a query parameter. The server validates
it through `zoneinfo`, falling back to UTC. Old sessions contain UTC instants,
not the historical study-location timezone; switching timezones changes the
night interpretation. Mood/weather do not alter stored sessions or focus scores.

## Room and catalog

`templates/pig_room.html` is a responsive local SVG with a fixed 480 × 400
coordinate system. It includes the existing pig SVG, a rounded desk, rug, and
weather window. Equipment controls toggle SVG groups by catalog ID. Faces and
weather use CSS states; no external image services, emoji artwork, canvas, or
new client dependencies are used. Item previews clone the same illustration
used in the room.

| Category | Item | Unlock |
| --- | --- | --- |
| Accessory | Sparkle Blush | Existing level 2 |
| Accessory | Pink Bow | Existing level 3 |
| Accessory | Cozy Headphones | Existing level 5 |
| Accessory | Tiny Strawberry | Existing level 7 |
| Accessory | Heart Glasses | Existing level 10 |
| Desk | Tiny Laptop | Free |
| Desk | Pink Mug | 75 coins |
| Desk | Heart Lamp | 180 coins |
| Desk | Little Book Stack | 120 coins |
| Wall | Heart Poster | 105 coins |
| Wall | Fairy Lights | 240 coins |
| Decor | Desk Plant | 150 coins |

Each full completed focused minute earns one coin, including historical
sessions from all linked installations. Minutes are floored per session and
clamped to 0–480, as with XP. No bonuses or penalty system are introduced.
Balance is derived earned coins minus stored spending. Unlocking is permanent;
repeat unlock requests never charge twice. Purchasing does not automatically
equip: the card changes to **Equip**. Every cosmetic can be equipped or put away
independently. Multiple accessories are allowed, matching the original system.

Before the first room modification, the free laptop and all current XP
accessories appear equipped, preserving the existing pig. The first modification
saves those choices. Later XP unlocks remain available in the catalog but do not
override the user's saved equipment. An empty equipment list intentionally stays
empty across reloads, browsers, and sign-ins.

## Database and initialization

There was no stored pig profile. The additive `PigProfile` model references the
existing `User` by `user_id` (also its primary key), with:

- `coins_spent`: nonnegative integer, protected by a database check constraint.
- `purchased_items`: validated JSON array of known room-item IDs.
- `equipped_items`: validated JSON array of known IDs; nullable for the legacy
  default, while `[]` means intentionally unequipped.
- `updated_at`: UTC timestamp.

XP, levels, earned coins, mood, weather, and XP accessory unlocks remain derived.
No existing account, installation, session, or attempt columns are changed. No
existing data is deleted. The existing `flask --app app init-db` command creates
the new table through `db.create_all()` on SQLite and PostgreSQL. Before a future
release, run that existing additive command against the intended database, then
start the new application. This work does not initialize or modify production.
The additive initialization is tested against a preexisting SQLite account and
focus history; PostgreSQL schema generation is checked without connecting to a
production database.

## APIs and ownership

- `GET /api/me/pig`: complete account pig/catalog/room snapshot.
- `POST /api/me/pig/unlock`: JSON `{ "item_id": "plant" }`.
- `POST /api/me/pig/equip`: JSON `{ "item_id": "plant", "equipped": true }`.
- Existing `GET /api/me/stats` includes the same expanded pig snapshot without
  removing analytics. Existing installation-scoped stats retain their scoped XP.

All require the existing authenticated Google user's server session. Mutations
also require `X-CSRF-Token` matching the dashboard's session token. Browser
ownership IDs and unknown input fields are rejected. Only sessions linked through
existing `ClientInstallation` ownership contribute to the account's rewards.
Locked equipment, unknown catalog IDs, nonboolean equipment flags, and
insufficient balances are rejected. Stored JSON values are validated on assignment.

A transaction locks the existing user row with a no-op row update before reading
and updating the profile, serializing same-account purchases/equipment across
workers on PostgreSQL and SQLite. Repeated concurrent purchases charge once.
Validation/database errors roll back. Read requests do not create profiles.

## Accessibility and verification

The scene has an accessible description updated with mood/weather. Decorative
item previews are hidden from assistive technology. A native modal provides
keyboard controls, Escape dismissal, focus containment, and focus restoration.
Polling reuses item buttons so focus is not lost. A pending stats response cannot
overwrite a newer customization result. All pig/weather/steam animations stop
with `prefers-reduced-motion: reduce`.

Tests:

- `tests/test_pig_room.py`: deterministic atmosphere, priorities, timezone/UTC
  handling, coin rules, catalog validation, purchase/equip persistence, empty
  equipment, CSRF/login/ownership checks, additive initialization, and concurrent
  duplicate purchases.
- Existing backend tests cover API/session ingestion, XP progression, analytics,
  Google callbacks/token validation, and PostgreSQL schema/driver setup.
- `tests/browser_pig_room.py`: mocked provider sign-in with real local authenticated
  room APIs, all 12 items, balance, reload persistence, all visual states, chart
  and history, keyboard controls, desktop 1280px, tablet 768px, mobile 390px and
  320px without page/dialog overflow, reduced motion, and no console/HTTP 5xx errors.
- `tests/browser_integration.py`: existing actual extension online/offline blocking,
  timer completion, durable writes, mocked Google sign-in, live analytics, pig XP,
  original five accessories, reduced motion, and logout. Its accessory selector
  now targets the pig specifically, since the room has separate item groups.
- `tests/history_sync.test.cjs`: existing durable session retry tests.

Google provider responses are mocked in automated browser tests; real provider
login and a live PostgreSQL server are not exercised. Existing tests deliberately
simulate unavailable databases and rejected OAuth tokens, so their expected
warning/error logs do not indicate a room failure. Existing dependency deprecation
and SQLite resource warnings may appear in unittest output.

## README suggestions for later

The README is deliberately unchanged. Add small mentions to **Main Features**
for pig moods, room customization, and focus weather. Add a short paragraph to
**How to Use It** explaining Customize Pig Room and completed-minute coins.
Add one sentence to **Architecture** about account-owned server-side cosmetics
and derived rewards, and update **Privacy** to reflect the existing Google
sign-in/account ownership (the current no-account sentence is outdated).

Suggested commit: `Add cozy pig moods, persistent room customization, and focus weather`

Final verification: 40 backend unittest cases passed; history-sync Node test passed;
both browser scripts passed; JavaScript syntax and `git diff --check` passed.
The room browser suite also verifies that a delayed pre-purchase stats response
cannot overwrite newer customization state.

## Global dashboard atmosphere

The same resolved weather that `renderPig` already uses (including its existing
15-second purchase celebration) now goes through `applyFocusWeather`, which sets
both `body[data-weather]` and `.pig-art[data-weather]`. Backend weather rules,
rewards, analytics, authentication, and extension behavior are unchanged. Before
the first snapshot, both start in the existing cloudy state.

`templates/weather_background.html` supplies five small decorative inline SVG
layers; `static/weather.css` styles them:

| State | Full-page atmosphere | Motion |
| --- | --- | --- |
| Sunny | Pink and peach gradients, cream light, translucent sun, sparse light specks | Gentle 18-second light drift |
| Cloudy | Dusty blush and lavender, soft translucent clouds | 28-second cloud drift |
| Rainy | Muted mauve and lavender, warm rose glow, sparse rain-glass streaks | Subtle five-second downward drift |
| Star night | Dusty rose and muted plum, cream crescent and small stars | Nine-second star glow |
| Sparkle | Brighter blush, warm radial light, tiny stars and hearts | Seven-second sparkle pulse |

Layers cross-fade with a 1.4-second opacity transition. Only the current state's
layers animate. The fixed container is clipped to the viewport, sits behind
`main`, has `pointer-events: none` throughout, and is `aria-hidden`. It does not
introduce layout movement or horizontal overflow. Mobile reduces decoration size
and opacity. There is no canvas, raster background, video, external API, new
animation library, or additional weather state.

Cards retain opaque existing backgrounds, borders, geometry, and text colors;
a small shared shadow adds separation. Night privacy text and the heading accent
use darker colors against the dusty rose gradient. Reduced motion disables all
global animations and transitions while keeping the selected static atmosphere.
The existing reduced-motion rule continues to cover the pig room.

The expanded local browser suite verifies all five states at all four requested
widths (1280, 768, 390, 320), matching page/room/purchase weather, five distinct
gradients, click-through decoration, fixed positioning while scrolling, opaque
card readability, text contrast against all opaque gradient stops, and static
reduced-motion behavior. Screenshots were visually reviewed. All 40 backend
tests and the existing Node history-sync test passed; no browser console errors
or local Flask HTTP 5xx occurred. Google browser sign-in still uses a mocked
provider; this change does not exercise live Google or production services.

Suggested commit: `Extend focus weather across the dashboard background`
