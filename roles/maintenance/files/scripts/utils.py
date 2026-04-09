inventory_insert = """
INSERT INTO inventory (host_ip, state)
VALUES (%s, %s)
ON CONFLICT (host_ip) DO UPDATE
SET state = EXCLUDED.state
RETURNING id;
"""

pool_insert = """
INSERT INTO pool (name, state)
VALUES (%s, %s)
ON CONFLICT (name) DO UPDATE
SET state = EXCLUDED.state
RETURNING id;
"""

member_insert = """
INSERT INTO member (name, address, state)
VALUES (%s, %s, %s)
ON CONFLICT (name) DO UPDATE
SET
    address = EXCLUDED.address,
    state   = EXCLUDED.state
RETURNING id;
"""

catalog_insert = """
INSERT INTO catalog (category, value)
VALUES (%s, %s)
ON CONFLICT (category, value) DO NOTHING
RETURNING id;
"""

maintenance_insert = """
INSERT INTO maintenance (
    inventory_id,
    pool_id,
    member_id,
    partition_id,
    real_state_id,
    real_session_id,
    f5_state_id,
    ratio,
    priority_group,
    connection_limit,
    rate_limit,
    created_at,
    state
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (inventory_id, pool_id, member_id, created_at) DO UPDATE
SET
    partition_id    = EXCLUDED.partition_id,
    real_state_id   = EXCLUDED.real_state_id,
    real_session_id = EXCLUDED.real_session_id,
    f5_state_id     = EXCLUDED.f5_state_id,
    ratio           = EXCLUDED.ratio,
    priority_group  = EXCLUDED.priority_group,
    connection_limit= EXCLUDED.connection_limit,
    rate_limit      = EXCLUDED.rate_limit,
    state           = EXCLUDED.state
RETURNING id;
"""