# Context from my IDE setup:

## Active file: index.html

## Open tabs:
- index.html: index.html
- prompt_log.md: lock-in-bro/prompt_log.md
- README.md: lock-in-bro/README.md

## My request:
Inside my current whosamyy.github.io repository, create a new folder called:

hw6-drink-diary

This is for CMU 15-113 HW6.

For now, only create the starter structure and database setup.

Create:

hw6-drink-diary/
  app.py
  README.md
  prompt_log.md
  templates/
  static/

The project is called "Amy's Drink Diary". It will be a Flask + SQLite app for tracking drinks like matcha, boba, coffee, and tea.

Use:
- Python
- Flask
- Python's built-in sqlite3 module
- regular HTML/CSS
- no React
- no SQLAlchemy
- no external database

In app.py:

1. Set up a basic Flask app.
2. Create a SQLite database called drinks.db if it does not already exist.
3. Create a table called drinks with these columns:

id INTEGER PRIMARY KEY AUTOINCREMENT
shop TEXT NOT NULL
drink_name TEXT NOT NULL
category TEXT NOT NULL
sugar_level TEXT
ice_level TEXT
rating INTEGER NOT NULL
date TEXT
notes TEXT

Make sure the database initialization does not erase existing data when the app restarts.

Add *.db to the main repository's .gitignore if it is not already ignored.

Do not implement all CRUD features yet.

Do not commit or push anything.

Also add this exact prompt verbatim to hw6-drink-diary/prompt_log.md.

When finished, tell me:
- which files you created
- how the database is initialized
- how I can run the Flask app locally

# Context from my IDE setup:

## Active file: index.html

## Open tabs:
- index.html: index.html
- prompt_log.md: lock-in-bro/prompt_log.md
- README.md: lock-in-bro/README.md

## My request:
Now continue building the existing hw6-drink-diary project.

Do not replace the project structure or rewrite everything from scratch. Build on the Flask + SQLite setup that already exists.

I need the app to clearly demonstrate CRUD for CMU 15-113 HW6.

==================================================
CREATE
==================================================

Add an "Add a Drink" page/form.

Fields:

- Shop
- Drink name
- Category
- Sugar level
- Ice level
- Rating
- Date
- Notes

Categories:
- Matcha
- Boba
- Coffee
- Tea
- Other

Rating must be an integer from 1 to 10.

When the form is submitted, insert the drink into the SQLite drinks table using a parameterized SQL query.

==================================================
READ
==================================================

Make the home page show all saved drinks.

Display each drink as a card showing:

- shop
- drink name
- category
- sugar level
- ice level
- rating /10
- date
- notes

If there are no drinks, show:

"No drinks yet 🧋 Time to go get one."

==================================================
UPDATE
==================================================

Add an Edit button to each drink.

Create an edit page that loads the drink's current information into the form.

Allow the user to edit any field and save the changes back to SQLite.

Use parameterized SQL.

==================================================
DELETE
==================================================

Add a Delete button to each drink.

Ask for simple confirmation before deleting.

Delete using the drink's id.

==================================================
FILTERING / SORTING
==================================================

On the home page, add controls to:

- filter by category
- filter by shop
- filter by minimum rating
- sort by newest
- sort by oldest
- sort by highest rating
- sort by lowest rating

Use SQL WHERE and ORDER BY where appropriate.

==================================================
SMALL STATS SECTION
==================================================

Show:

- total number of drinks
- average rating
- most visited shop

Also show a "Top Rated" section for drinks rated 9 or 10.

Keep the SQL and Python straightforward and easy for a student to understand.

==================================================
DESIGN
==================================================

Make the site cute and café-themed.

Header:

Amy's Drink Diary 🧋

Subtitle:

"because apparently I need a database for my matcha opinions"

Style:
- soft pink
- cream
- light brown
- rounded cards
- simple buttons
- clean spacing
- readable
- no complicated animations

Use regular HTML and CSS only.

==================================================
VALIDATION
==================================================

Do not let the app crash if the user enters bad data.

Require:
- shop
- drink name
- category
- rating

Rating must be from 1 to 10.

==================================================
IMPORTANT
==================================================

- Keep the code simple enough that I can understand and explain it.
- Do not use SQLAlchemy.
- Do not use JavaScript unless it is needed for delete confirmation.
- Do not use an external database.
- Do not deploy anything.
- Do not commit or push.
- Do not delete existing code unless necessary.
- Use parameterized SQL queries instead of inserting user input directly into SQL strings.

Add this exact prompt verbatim to prompt_log.md.

After implementing everything:

1. Run the app locally.
2. Test adding a drink.
3. Test viewing drinks.
4. Test editing a drink.
5. Test deleting a drink.
6. Test every filter.
7. Test every sort option.
8. Check that the stats are correct.
9. Check that drinks.db actually contains the saved data.

Do not claim a test passed unless you actually ran it.

When finished, explain:
- which Flask routes you created
- which route is Create
- which route is Read
- which route is Update
- which route is Delete
- how filtering works
- how sorting works
- the exact command I should run to open the app
