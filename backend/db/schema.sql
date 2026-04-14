PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS images (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path   TEXT UNIQUE NOT NULL,
    sha256      TEXT UNIQUE NOT NULL,
    phash       TEXT,
    width       INTEGER,
    height      INTEGER,
    indexed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_images_sha256 ON images(sha256);

CREATE TABLE IF NOT EXISTS metadata (
    image_id     INTEGER REFERENCES images(id) ON DELETE CASCADE,
    shot_date    TEXT,
    lat          REAL,
    lon          REAL,
    camera_make  TEXT,
    camera_model TEXT,
    location     TEXT
);
CREATE INDEX IF NOT EXISTS idx_metadata_shot_date ON metadata(shot_date);

CREATE TABLE IF NOT EXISTS faces (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id        INTEGER REFERENCES images(id) ON DELETE CASCADE,
    bbox_x          REAL, bbox_y REAL, bbox_w REAL, bbox_h REAL,
    cluster_id      INTEGER,
    faiss_index_id  INTEGER,
    confidence      REAL
);
CREATE INDEX IF NOT EXISTS idx_faces_cluster_id ON faces(cluster_id);

CREATE TABLE IF NOT EXISTS clusters (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    label               TEXT,
    face_count          INTEGER DEFAULT 0,
    thumbnail_face_id   INTEGER,
    first_seen          TEXT,
    last_seen           TEXT
);

CREATE TABLE IF NOT EXISTS embeddings_map (
    image_id        INTEGER REFERENCES images(id) ON DELETE CASCADE,
    faiss_index_id  INTEGER UNIQUE
);

CREATE TABLE IF NOT EXISTS duplicates (
    image_id_a      INTEGER REFERENCES images(id) ON DELETE CASCADE,
    image_id_b      INTEGER REFERENCES images(id) ON DELETE CASCADE,
    phash_distance  INTEGER,
    PRIMARY KEY (image_id_a, image_id_b)
);
CREATE INDEX IF NOT EXISTS idx_duplicates_phash ON duplicates(phash_distance);
