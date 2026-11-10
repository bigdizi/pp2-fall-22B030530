# Practice 7 - Python & PostgreSQL PhoneBook

## Setup
1. Create a Neon PostgreSQL project and copy its connection string from **Connect**.
2. Create a local file named `.env` in this folder (copy `.env.example`) and replace the example URL with your real Neon connection string.
3. In the VS Code terminal, run:
   ```bash
   python -m pip install -r requirements.txt
   python phonebook.py
   ```
4. Choose menu option 3 to import `contacts.csv`, then test options 1, 2, 4, 5, and 6.

The `.env` file contains your database password. Never commit it to GitHub.

Phone numbers must contain 10-15 digits and may start with `+`; do not include spaces or dashes.
