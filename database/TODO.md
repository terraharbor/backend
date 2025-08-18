The database can be created via python

```zsh
pip install psycopg2
```

```python
# ...existing code...
import psycopg2

def create_database():
    """
    Crée la base de données et les tables définies dans init.sql.
    """
    conn = psycopg2.connect(
        dbname="mydatabase",
        user="myuser",
        password="mypassword",
        host="localhost",
        port="5432"
    )
    with conn:
        with conn.cursor() as cur:
            with open("../database/init.sql", "r") as f:
                sql = f.read()
                cur.execute(sql)
    conn.close()
    print("Base de données créée avec succès.")

# Pour lancer la création, décommente la ligne suivante :
# create_database()
# ...existing code...
```