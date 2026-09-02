# Automation Tool

#### Video Demo : <https://youtu.be/_AsbfwzWXqU>

## Description

Automation Tool is a web application built with Flask that allows users to upload CSV files, choose a processing operation to apply to them, and download the result or receive it by email.

The idea for this project came from my research into potential tools I could build for a future freelance career, if I continue to be interested in Flask/Python development.

Using Claude AI, I asked it to present me different jobs or portfolio exercises that people actually build to introduce themselves when they want to become freelance, and this web app is one of them.

This tool is meant to save precious time when cleaning files: removing duplicate rows, removing blank rows, and normalizing data.

**Update (September 2026):** after submitting this project for CS50x, I kept extending it as a personal portfolio piece: the database was migrated from SQLite to a hosted PostgreSQL database (Neon), and a small JSON REST API was added on top of the existing task history, applying what I learned separately while working through a Flask REST API tutorial.

Users can create an account, log in, log out, upload a CSV file, choose one of the processing types, and download the result or receive it by email.

## Features

- **User authentication**: registration, login, and logout, implemented with Flask-Login and password hashing via Werkzeug. Passwords are never stored in plain text.
- **File upload and processing**: users can upload a .csv file and choose between three processing operations:
- **Remove duplicates**: removes exact duplicate rows.
- **Remove empty rows**: removes rows where every column is empty.
- **Normalize text case**: converts all text columns to lowercase.
- **Download**: processed files can be downloaded securely — a user can only download files linked to their own account, verified server-side.
- **Email notifications**: users can optionally provide an email address to receive the processed file as an attachment, using Flask-Mail.
- **Task history**: a dedicated page lists every task a user has submitted, along with its status and a download link when available.
- **JSON REST API**: `GET /api/tasks` and `GET /api/tasks/<id>` expose the same task history as JSON, protected by the same Flask-Login session as the rest of the app. A 404 on an `/api/...` route returns JSON instead of an HTML page.
- **Environment-based configuration**: sensitive values (secret key, mail server credentials, database URL) are stored in a .env file, excluded from version control, rather than hardcoded in the source.

## Project structure and file roles

- **app.py**: the main Flask application. It defines all the routes (/, /register, /login, /logout, /upload, /download/<id>, /history, /api/tasks, /api/tasks/<id>), the User class used by Flask-Login, and the logic connecting file uploads to the processing functions and email notifications.
- **processing.py**: contains the three data-processing functions (remove_duplicates, remove_empty_rows, normalize_text_case), each built with Pandas. Keeping this logic in a separate file from app.py makes it easy to add new processing types later without cluttering the route logic.
- **database.py**: handles the PostgreSQL connection (via `psycopg2`, using a `DATABASE_URL` read from `.env`). It exposes get_db_connection(), which returns a connection configured with `RealDictCursor` so that query results can still be accessed by column name exactly like before, and init_db(), which creates the database tables from schema.sql if they don't already exist.
- **schema.sql**: defines the two database tables, users (id, email, password hash, creation date) and tasks (id, linked user, original filename, processing type, status, result filename, creation date), using PostgreSQL syntax (`SERIAL` primary keys). The tasks table uses a foreign key to users to guarantee that every task belongs to a valid account.
- **templates/**: contains all HTML templates (index.html, register.html, login.html, upload.html, history.html), each extended with a simple navigation bar that adapts depending on whether the user is logged in.
- **static/style.css**: a single shared stylesheet providing basic, consistent styling across all pages.
- **.env / .env.example**: .env stores the real secret key and mail credentials locally and is excluded from Git; .env.example documents which variables are required, without exposing real values.

## Design choices

I chose to keep the file processing **synchronous**: when a user uploads a file, the processing happens immediately within the same request, rather than being queued for background processing. This was a deliberate simplification appropriate for the scope of this project — CSV files processed here are small, so the user does not experience any noticeable delay. A production version handling larger files or heavier operations would likely need an asynchronous task queue instead.

For the CS50 submission, I chose SQLite over a more complex database system, since it required no additional setup and was consistent with what I learned in CS50's SQL lessons, while still being a real relational database with foreign key constraints. Afterwards, as a personal extension, I migrated the project to PostgreSQL hosted on Neon — closer to what a real freelance client project would use, since SQLite's single-file design handles concurrent writes poorly under multiple simultaneous users. The SQL itself barely changed (mostly placeholder syntax and the primary key declaration); what changed is the connection layer and how a generated id is retrieved after an insert (`RETURNING id` instead of `cursor.lastrowid`, which psycopg2 doesn't provide).

## AI usage disclosure

Portions of this project were developed with the assistance of Claude (Anthropic), used as a learning and debugging aid: explaining Flask-Login's internals, reviewing my code for mistakes, and helping troubleshoot environment issues (PowerShell execution policy, a broken virtual environment after a folder rename, a .gitignore misconfiguration). GitHub Copilot / VS Code autocompletion suggestions were also used for some lines of code. All code was reviewed and understood before being included, and no code was submitted without me being able to explain what it does.

The PostgreSQL migration and the `/api/tasks` JSON endpoints were added after the CS50 submission, also with Claude's help, as a deliberate practice exercise following a separate Flask REST API tutorial — the goal was to apply that tutorial's patterns (JSON responses, HTTP status codes, error handling) to a real project instead of a throwaway example. A `requirements.txt` encoding bug (the file had been saved as UTF-16 instead of UTF-8, likely from `pip freeze > requirements.txt` in PowerShell, which could have broken installation for anyone else cloning the repo) was also caught and fixed during this pass.