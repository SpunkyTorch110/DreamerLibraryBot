
import aiosqlite

SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version
(
    version INTEGER NOT NULL
);"""

PLAYERS_TABLE = """
CREATE TABLE IF NOT EXISTS players
(
    discord_id      INTEGER PRIMARY KEY,

    username        TEXT NOT NULL,
    display_name    TEXT,

    gold            INTEGER NOT NULL DEFAULT 0,

    last_roll       INTEGER,
    last_claim      INTEGER,

    created_at      INTEGER NOT NULL
);
"""

COLLECTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS collections
(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,

    name            TEXT NOT NULL UNIQUE,

    description     TEXT,

    image_url       TEXT
);
"""

PAGES_TABLE = """
CREATE TABLE IF NOT EXISTS pages
(
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,

    name                TEXT NOT NULL UNIQUE,

    gender              INTEGER,

    rank                INTEGER NOT NULL,

    rarity              INTEGER NOT NULL,

    type                INTEGER NOT NULL,

    description         TEXT,

    strength            INTEGER NOT NULL,
    dexterity           INTEGER NOT NULL,
    constitution        INTEGER NOT NULL,
    intelligence        INTEGER NOT NULL,
    wisdom              INTEGER NOT NULL,
    charisma            INTEGER NOT NULL,

    collection_id       INTEGER,

    owner_id            INTEGER,

    discovered          INTEGER NOT NULL DEFAULT 0,

    created_at          INTEGER NOT NULL,

    FOREIGN KEY(collection_id) REFERENCES collections(id) ON DELETE SET NULL,
    
    FOREIGN KEY(owner_id) REFERENCES players(discord_id)
);"""

PAGE_IMAGES_TABLE = """
CREATE TABLE IF NOT EXISTS page_images
(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,

    page_id         INTEGER NOT NULL,

    image_url       TEXT NOT NULL,

    display_order   INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY(page_id) REFERENCES pages(id) ON DELETE CASCADE
);"""

PAGE_ALIASES_TABLE = """
CREATE TABLE page_aliases
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    page_id INTEGER NOT NULL,

    alias TEXT NOT NULL COLLATE NOCASE,

    UNIQUE(alias),

    FOREIGN KEY(page_id)
        REFERENCES pages(id)
        ON DELETE CASCADE
);
"""

INVENTORY_TABLE = """
CREATE TABLE IF NOT EXISTS inventory
(
    player_id           INTEGER NOT NULL,

    page_id             INTEGER NOT NULL,

    amount              INTEGER NOT NULL DEFAULT 1,

    favourite           INTEGER NOT NULL DEFAULT 0,

    first_obtained      INTEGER NOT NULL,

    PRIMARY KEY(player_id, page_id),

    FOREIGN KEY(player_id) REFERENCES players(discord_id) ON DELETE CASCADE,

    FOREIGN KEY(page_id) REFERENCES pages(id)
);"""

TABLES = [
    SCHEMA_VERSION_TABLE,
    PLAYERS_TABLE,
    COLLECTIONS_TABLE,
    PAGES_TABLE,
    PAGE_IMAGES_TABLE,
    PAGE_ALIASES_TABLE,
    INVENTORY_TABLE
]

INDEXES = [
    """
    CREATE INDEX IF NOT EXISTS idx_players_username
    ON players(username);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_pages_name
    ON pages(name);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_pages_collection
    ON pages(collection_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_pages_owner
    ON pages(owner_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_inventory_player
    ON inventory(player_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_inventory_page
    ON inventory(page_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_aliases_alias
    ON page_aliases(alias);
    """
]

async def create_tables(connection: aiosqlite.Connection) -> None:
    """
    Creates every table if it does not exist.
    """

    for table in TABLES:
        await connection.execute(table)


async def create_indexes(connection: aiosqlite.Connection) -> None:
    """
    Creates every db index.
    """

    for index in INDEXES:
        await connection.execute(index)


async def initialize(connection: aiosqlite.Connection) -> None:
    """
    Initializes the complete db schema.
    """

    await create_tables(connection)
    await create_indexes(connection)

    await connection.commit()