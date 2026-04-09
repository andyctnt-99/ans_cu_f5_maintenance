import psycopg2
from psycopg2.extras import execute_values
from structure import PostgresStructure


class PostgresQuery:
    def __init__(self):
        pass

    def absent_insertar_or_update(self, query, params, quer_name):
        params_connection = PostgresStructure()
        try:
            connection = psycopg2.connect(**params_connection.connection_params)
            cursor = connection.cursor()
            ids = {}

            if params:
                cursor.execute(query, params)

                # DO NOTHING no retorna fila, fetchone() devuelve None
                row = cursor.fetchone()
                if row:
                    ids["id"] = row[0]

                connection.commit()

            return ids

        except Exception as e:
            print(f"Error {quer_name}: {e}")
            return {}  # <-- antes retornaba None implícito, mejor retornar dict vacío
        finally:
            cursor.close()
            connection.close()

    def get_query(self, query, params, quer_name):
        params_connection = PostgresStructure()
        results = None
        try:
            # Establecer conexión
            connection = psycopg2.connect(**params_connection.connection_params)  # type: ignore
            cursor = connection.cursor()
            # Insertar o actualizar
            if params:
                cursor.execute(query, params)
                results = cursor.fetchall()
                # Confirmar los cambios
                connection.commit()

            return results  # Devolver los resultados de la consulta

        except Exception as e:
            print(f"Error {quer_name}: {e}")
        finally:
            # Cerrar el cursor y la conexión
            cursor.close()
            connection.close()

    def absent_insertar_or_update_masive(self, query, params, quer_name):
        params_connection = PostgresStructure()
        try:
            connection = psycopg2.connect(**params_connection.connection_params)  # type: ignore
            cursor = connection.cursor()

            if params:
                # Insertar múltiples registros eficientemente
                execute_values(cursor, query, params)
                connection.commit()
                return {"status": "OK", "rows": len(params)}

        except Exception as e:
            print(f"Error {quer_name}: {e}")
            return {"status": "ERROR", "error": str(e)}
        finally:
            cursor.close()
            connection.close()
