import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_db_connection():
    """Retourne une connexion PostgreSQL (Neon).

    cursor_factory=RealDictCursor fait que chaque curseur ouvert sur
    cette connexion renvoie des lignes accessibles par nom de colonne
    (row["email"]), comme le faisait row_factory = sqlite3.Row avec
    SQLite. C'est ce qui permet au reste du code (templates compris,
    qui font tasks.email, tasks.status, etc.) de continuer a fonctionner
    sans changement.
    """
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    """Cree les tables si elles n'existent pas encore, a partir de
    schema.sql. Appelee une seule fois au demarrage du serveur."""
    conn = get_db_connection()
    cur = conn.cursor()
    with open("schema.sql") as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
