# Automation Tool

#### Video Demo : <https://youtu.be/_AsbfwzWXqU>

## Description

Automation Tool is a web application built with Flask that allows users to upload CSV files, choose a processing operation to apply to them, and download the result or receive it by email.

The idea for this project came from my research into potential tools I could build for a future freelance career, if I continue to be interested in Flask/Python development.

Using Claude AI, I asked it to present me different jobs or portfolio exercises that people actually build to introduce themselves when they want to become freelance, and this web app is one of them.

This tool is meant to save precious time when cleaning files: removing duplicate rows, removing blank rows, and normalizing data.

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
- **Environment-based configuration**: sensitive values (secret key, mail server credentials) are stored in a .env file, excluded from version control, rather than hardcoded in the source.

## Project structure and file roles

- **app.py**: the main Flask application. It defines all the routes (/, /register, /login, /logout, /upload, /download/<id>, /history), the User class used by Flask-Login, and the logic connecting file uploads to the processing functions and email notifications.
- **processing.py**: contains the three data-processing functions (remove_duplicates, remove_empty_rows, normalize_text_case), each built with Pandas. Keeping this logic in a separate file from app.py makes it easy to add new processing types later without cluttering the route logic.
- **database.py**: handles the SQLite connection. It exposes get_db_connection(), which returns a connection with row_factory set so that query results can be accessed by column name, and init_db(), which creates the database tables from schema.sql if they don't already exist.
- **schema.sql**: defines the two database tables, users (id, email, password hash, creation date) and tasks (id, linked user, original filename, processing type, status, result filename, creation date). The tasks table uses a foreign key to users to guarantee that every task belongs to a valid account.
- **templates/**: contains all HTML templates (index.html, register.html, login.html, upload.html, history.html), each extended with a simple navigation bar that adapts depending on whether the user is logged in.
- **static/style.css**: a single shared stylesheet providing basic, consistent styling across all pages.
- **.env / .env.example**: .env stores the real secret key and mail credentials locally and is excluded from Git; .env.example documents which variables are required, without exposing real values.

## Design choices

I chose to keep the file processing **synchronous**: when a user uploads a file, the processing happens immediately within the same request, rather than being queued for background processing. This was a deliberate simplification appropriate for the scope of this project — CSV files processed here are small, so the user does not experience any noticeable delay. A production version handling larger files or heavier operations would likely need an asynchronous task queue instead.

I also chose SQLite over a more complex database system, since it required no additional setup and was consistent with what I learned in CS50's SQL lessons, while still being a real relational database with foreign key constraints.

## AI usage disclosure

Portions of this project were developed with the assistance of Claude (Anthropic), used as a learning and debugging aid: explaining Flask-Login's internals, reviewing my code for mistakes, and helping troubleshoot environment issues (PowerShell execution policy, a broken virtual environment after a folder rename, a .gitignore misconfiguration). GitHub Copilot / VS Code autocompletion suggestions were also used for some lines of code. All code was reviewed and understood before being included, and no code was submitted without me being able to explain what it does.