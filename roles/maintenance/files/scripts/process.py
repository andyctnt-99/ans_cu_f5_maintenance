import json
import os
import sys
from datetime import datetime
from query import PostgresQuery
from structure import PostgresStructure
from utils import (
    inventory_insert,
    pool_insert,
    member_insert,
    catalog_insert,
    maintenance_insert,
)

url = os.path.realpath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(url, ".."))


class ProccessF5Maintenance:
    def __init__(self):
        pass

    def get_or_create_catalog(self, category, value):
        catalog_id = PostgresQuery().absent_insertar_or_update(
            query=catalog_insert,
            params=(category, value),
            quer_name="catalog_insert",
        )

        # Si insertó, retorna el id directamente
        if catalog_id.get("id"):
            return catalog_id.get("id")

        # DO NOTHING no retorna id, fallback con get_query
        result = PostgresQuery().get_query(
            query="SELECT id FROM catalog WHERE category = %s AND value = %s",
            params=(category, value),
            quer_name="catalog_select",
        )
        return result[0][0] if result else None

    def main(self):
        PostgresStructure().create_tables()

        archivos_json = [
            archivo
            for archivo in os.listdir(f"{parent_dir}")
            if archivo.endswith(".json")
        ]

        for item in archivos_json:
            with open(f"{parent_dir}/{item}", "r", encoding="utf-8") as record:
                data = json.load(record)
                _host= os.path.splitext(item)[0]
                print(_host)

                # Inventory (host F5) ****************************************************
                inventory_id = PostgresQuery().absent_insertar_or_update(
                    query=inventory_insert,
                    params= (_host, True),
                    quer_name="inventory_insert",
                )

                # Pool *******************************************************************
                pool_id = PostgresQuery().absent_insertar_or_update(
                    query=pool_insert,
                    params=(data.get("pool", "N/A"), True),
                    quer_name="pool_insert",
                )

                # Members ****************************************************************
                for member in data.get("members", []):

                    member_id = PostgresQuery().absent_insertar_or_update(
                        query=member_insert,
                        params=(
                            member.get("name", "N/A"),
                            member.get("address", "N/A"),
                            True,
                        ),
                        quer_name="member_insert",
                    )

                    # Catálogos **********************************************************
                    partition_id = self.get_or_create_catalog(
                        "partition", member.get("partition", "N/A")
                    )
                    real_state_id = self.get_or_create_catalog(
                        "real_state", member.get("real_state", "N/A")
                    )
                    real_session_id = self.get_or_create_catalog(
                        "real_session", member.get("real_session", "N/A")
                    )
                    f5_state_id = self.get_or_create_catalog(
                        "f5_state", member.get("state", "N/A")
                    )

                    # Maintenance ********************************************************
                    PostgresQuery().absent_insertar_or_update(
                        query=maintenance_insert,
                        params=(
                            inventory_id.get("id", None),
                            pool_id.get("id", None),
                            member_id.get("id", None),
                            partition_id,
                            real_state_id,
                            real_session_id,
                            f5_state_id,
                            member.get("ratio", 1),
                            member.get("priority_group", 0),
                            member.get("connection_limit", 0),
                            member.get("rate_limit", "no"),
                            datetime.now(),
                            True,
                        ),
                        quer_name="maintenance_insert",
                    )


if __name__ == "__main__":
    proceso = ProccessF5Maintenance()
    try:
        proceso.main()
    except Exception as e:
        print(f"Error durante la ejecución: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)