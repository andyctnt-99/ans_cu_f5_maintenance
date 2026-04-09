import psycopg2
from vars import DATABASE, HOST, PASSWORD, PORT, USER

host = str(HOST)
port = str(PORT)
database = str(DATABASE)
user = str(USER)
password = str(PASSWORD)


class PostgresStructure:
    def __init__(self):
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }

    def create_tables(self):
        try:
            # Crear la conexión a PostgreSQL
            conexion: Any = psycopg2.connect(**self.connection_params)  # type: ignore
            cursor = conexion.cursor()

            create_tables = """
                CREATE TABLE IF NOT EXISTS inventory (
                    id      SERIAL PRIMARY KEY,
                    host_ip VARCHAR(100) UNIQUE NOT NULL,  -- ansible_host
                    state   BOOLEAN DEFAULT TRUE
                );

                CREATE TABLE IF NOT EXISTS pool (
                    id    SERIAL PRIMARY KEY,
                    name  VARCHAR(150) UNIQUE NOT NULL,
                    state BOOLEAN DEFAULT TRUE
                );

                CREATE TABLE IF NOT EXISTS member (
                    id        SERIAL PRIMARY KEY,
                    name      VARCHAR(150) UNIQUE NOT NULL,  -- node_ocbqa5.bancatlan.hn_1:8080
                    address   VARCHAR(50) NOT NULL,          -- 10.128.254.131
                    state     BOOLEAN DEFAULT TRUE
                );

                -- Catálogo reutilizable solo para valores repetitivos reales
                CREATE TABLE IF NOT EXISTS catalog (
                    id       SERIAL PRIMARY KEY,
                    category VARCHAR(50) NOT NULL,   -- 'partition', 'real_state', 'real_session', 'f5_state'
                    value    VARCHAR(100) NOT NULL,
                    UNIQUE (category, value)
                );

                CREATE TABLE IF NOT EXISTS maintenance (
                    id                     SERIAL PRIMARY KEY,
                    inventory_id           INTEGER NOT NULL,
                    pool_id                INTEGER NOT NULL,
                    member_id              INTEGER NOT NULL,

                    -- catálogos
                    partition_id           INTEGER NOT NULL,   -- Common, partition_x
                    real_state_id          INTEGER NOT NULL,   -- up, down, unknown
                    real_session_id        INTEGER NOT NULL,   -- monitor-enabled, user-disabled
                    f5_state_id            INTEGER NOT NULL,   -- present, disabled, force_offline

                    -- valores numéricos directos (no ameritan catálogo)
                    ratio                  INTEGER DEFAULT 1,
                    priority_group         INTEGER DEFAULT 0,
                    connection_limit       INTEGER DEFAULT 0,
                    rate_limit             VARCHAR(50) DEFAULT 'no',

                    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    state                  BOOLEAN DEFAULT TRUE,

                    FOREIGN KEY (inventory_id)   REFERENCES inventory(id) ON DELETE RESTRICT,
                    FOREIGN KEY (pool_id)        REFERENCES pool(id)      ON DELETE RESTRICT,
                    FOREIGN KEY (member_id)      REFERENCES member(id)    ON DELETE RESTRICT,
                    FOREIGN KEY (partition_id)   REFERENCES catalog(id)   ON DELETE RESTRICT,
                    FOREIGN KEY (real_state_id)  REFERENCES catalog(id)   ON DELETE RESTRICT,
                    FOREIGN KEY (real_session_id)REFERENCES catalog(id)   ON DELETE RESTRICT,
                    FOREIGN KEY (f5_state_id)    REFERENCES catalog(id)   ON DELETE RESTRICT,

                    UNIQUE (inventory_id, pool_id, member_id, created_at)
                );


            """
            create_views = """
                CREATE OR REPLACE VIEW v_maintenance_detail AS
                SELECT
                    m.id                                        AS maintenance_id,
                    m.created_at,

                    -- Inventario (host F5)
                    i.host_ip                                   AS f5_host,

                    -- Pool
                    p.name                                      AS pool_name,

                    -- Member
                    mb.name                                     AS member_name,
                    mb.address                                  AS member_address,

                    -- Catálogos
                    cat_part.value                              AS partition,
                    cat_rs.value                                AS real_state,
                    cat_rse.value                               AS real_session,
                    cat_st.value                                AS f5_state,

                    -- Valores numéricos
                    m.ratio,
                    m.priority_group,
                    m.connection_limit,
                    m.rate_limit,

                    -- Estado del registro
                    m.state                                     AS active

                FROM maintenance m
                JOIN inventory  i       ON i.id   = m.inventory_id
                JOIN pool       p       ON p.id   = m.pool_id
                JOIN member     mb      ON mb.id  = m.member_id
                JOIN catalog    cat_part  ON cat_part.id  = m.partition_id
                JOIN catalog    cat_rs    ON cat_rs.id    = m.real_state_id
                JOIN catalog    cat_rse   ON cat_rse.id   = m.real_session_id
                JOIN catalog    cat_st    ON cat_st.id    = m.f5_state_id;
            """

            cursor.execute(create_tables)
            cursor.execute(create_views)
            conexion.commit()

            print("Tablas creadas o verificadas correctamente.")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error al crear las tablas: {error}")
        finally:
            if conexion:
                cursor.close()
                conexion.close()
