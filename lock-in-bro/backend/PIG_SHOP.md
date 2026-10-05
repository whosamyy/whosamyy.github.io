# A growing pig shop

The code-defined catalog now has 29 definitions: all 12 original items, six
weekly finds, five earned cosmetics, four seasonal finds, and two rare treats.
Original item IDs, prices, XP thresholds, coin earning, and valid owned/equipped
items are preserved. Google authentication, focus scores, extension behavior,
analytics, mood, and weather calculations are unchanged.

## Calendar and weekly finds

`shop_calendar` in `pig_shop.py` uses the current server date in **UTC**. The
week starts Monday at 00:00 UTC. The displayed key uses ISO year/week, including
year boundaries. Rotation uses the number of Mondays since 1970-01-05, modulo
the six-entry weekly pool, then takes four consecutive entries with wrapping.
There are no duplicate finds. The selection is stable for the whole week,
changes next Monday, and repeats after six weeks. No scheduled job, database
calendar table, random selection, or browser-supplied date is needed.

| Weekly pool | Coins | Shared artwork |
| --- | --- | --- |
| Lavender Bow | 90 | Bow, lavender colors |
| Strawberry Bow | 110 | Bow, berry colors and green knot |
| Cloud Lamp | 130 | Existing lamp with a cloud motif |
| Lavender Mug | 70 | Existing mug, lavender colors |
| Strawberry Pot | 100 | Existing plant, pink pot and tiny strawberry emblem |
| Checkerboard Rug | 120 | Existing rug with a small SVG checker pattern |

For **October 5–11, 2026 (2026-W41)** the four finds are Lavender Mug,
Strawberry Pot, Checkerboard Rug, and Lavender Bow. Next rotation is October 12.
The UI displays the week key, days until rotation, and the Monday/UTC convention.

## Earned by Locking In

New earned items are free and cannot be bought to bypass their requirements.
They use existing finished, completed focus sessions across the authenticated
user's linked installations. No duplicate counters are stored.

| Cosmetic | Requirement |
| --- | --- |
| Star Glasses | Complete a session with score 95+ |
| Cozy Blanket | Complete a session with 60 actual focused minutes |
| Flower Vase | Complete sessions on three distinct UTC start dates |
| Little Victory Pennant | Complete five sessions |
| Cloud Rug | Accumulate 300 full completed focused minutes |

Minutes are clamped to 0–480 and floored per session, matching the existing coin
rules. Early-ended and running sessions do not count. Requirements, numerical
progress, and little heart-lock badges appear on colorful cards. Once earned,
the button becomes Equip. New earned cosmetics are not automatically equipped;
they do not overwrite a saved room. Original Tiny Laptop stays free and Fairy
Lights stays purchasable for 80 coins; neither is moved behind a new milestone.

## Seasonal finds

All dates use the same UTC calendar, repeat annually, and are inclusive:

| Cosmetic | Availability | Coins | Shared artwork |
| --- | --- | --- | --- |
| Ghost Mug | October 1–31 | 90 | Cream mug with a tiny ghost face |
| Hot Cocoa | December 1–February's last day | 90 | Warm cocoa mug and little marshmallows |
| Heart Rug | February 1–14 | 140 | Pink rug with a heart motif |
| Tulip Plant | March 1–May 31 | 100 | Existing plant with a tulip and lavender pot |

Winter and Valentine availability can overlap. Out-of-season unowned finds are
hidden from the shop and cannot be purchased by posting their ID directly.
Owned seasonal finds remain equipable forever, appearing in Your Keepsakes when
they are outside their season. Monthly/season checks are simple to expand in code.

## Rare treats

- **Strawberry Computer Setup — 600 coins:** the shared laptop geometry with
  strawberry colors and a little strawberry screen emblem.
- **Giant Pig Plushie — 900 coins:** a soft pink plush pig beside the desk.

Both are always available, entirely cosmetic, and use the unchanged coin balance.
There are no real-money purchases, penalties, loot boxes, or gameplay advantages.

## Rendering and equipment

The room remains local SVG/CSS. Existing bow, lamp, mug, plant, laptop, and rug
geometry is reused; catalog `asset` and `style` fields select it. CSS variables
provide variant colors. Tiny motif groups handle cloud/heart/ghost/berry/tulip
styles; small new SVG groups provide glasses, blanket, vase, pennant, and plushie.
Shop previews clone the exact same asset and style shown in the room. SVG
structure is parsed in a test to verify every catalog asset exists and item groups
are independent, avoiding duplicated/nested preview assets.

Catalog `slot` distinguishes styles of one item. Equipping Lavender Bow replaces
Pink Bow or Strawberry Bow but leaves headphones and other accessories alone.
Star Glasses replaces Heart Glasses; cup styles replace one another; lamp,
plant, laptop, and rug styles likewise share their respective slot. Unequipping
a rug style restores the permanent original pink rug. Unequipping another item
puts it away. Switching styles does not remove ownership of the previous style.

The modal uses Permanent Favorites, This Week's Finds, Earned by Locking In,
Seasonal, Rare Treats, and (when needed) Your Keepsakes. Empty collections and
navigation chips are hidden. Shortcuts scroll to collections; the close button
stays visible. Polls preserve existing controls and restore focus when an owned
find moves into Keepsakes. Hidden controls are excluded from the keyboard focus
loop. Two-column mobile cards stay inside the modal at 390px and 320px. Existing
reduced-motion behavior continues to apply, including button hover transitions.

## State, compatibility, and authorization

**No database migration or new table/column is required.** Existing `PigProfile`
JSON arrays store purchased and equipped IDs, and `coins_spent` stores cumulative
spending. The catalog itself is not copied into profiles. Model validation now
allows purchased accessory variants while continuing to reject direct purchases
of XP and milestone items. Existing catalog IDs remain recognized.

Definitions carry kind, category, price, asset, style, slot, and relevant level,
requirement, season, or milestone metadata. Each account snapshot derives:
`available`, `owned`, backwards-compatible `unlocked`, `equipped`, `visible`,
`section`, `can_buy`, and milestone progress. Unowned unavailable definitions may
remain in the API catalog for validation, but are not rendered as shop cards.

Purchases remain in the existing server-side purchased-ID list when their week
or season ends. Milestone ownership is derived from preserved focus history.
Repeated purchases—including unavailable items already owned—are successful
no-ops and never charge twice. Purchases, affordability, time availability, and
slot replacement are enforced on the server. Existing authenticated user context,
CSRF checks, per-account transaction serialization, and installation ownership
continue to protect both API endpoints. Browser-supplied ownership or dates are
not accepted as authority.

One full completed focused minute still earns one coin. Existing `coins_spent`
and all original prices remain unchanged; no coins or inventory are reset.
Original equipment is unchanged until the user explicitly selects a replacement
style. The original default of current XP accessories plus the free laptop remains
for users who have never customized. No existing database data is modified by
this development work; tests use temporary/in-memory databases.

## Validation and limitations

- 51 backend tests pass, including all existing tests plus week/year boundaries,
  return cycles, season boundaries, all milestone thresholds, unavailable-item
  purchase rejection, rare affordability, duplicates, owner isolation, legacy
  inventory, variant slots, and independent SVG assets.
- `browser_pig_shop.py` buys and equips every new weekly, seasonal, earned, and
  rare item; advances across six weeks and all seasons; verifies off-season
  Keepsakes, exact coin totals, reload persistence, previews, keyboard focus,
  original analytics, and 1280/768/390/320px layouts.
- Existing room/global-weather browser QA and Node history-sync tests pass.
- Browser tests use a mocked Google provider, a mocked shop calendar, and local
  temporary SQLite. Live Google and production PostgreSQL are not exercised.
- The pool is deliberately small and repeats after six weeks. Additional future
  catalog entries require a code update; there is no generated endless inventory.
- Dates and distinct-day milestones use UTC, not historical local study time.

The README is unchanged. Later, add one short Main Features bullet covering the
rotating shop, milestone unlocks, seasonal cosmetics, and item variants. A sentence
in How to Use It can explain that purchased finds stay in Your Keepsakes.

Suggested commit: `Expand pig shop with weekly finds, milestones, seasons, and variants`
