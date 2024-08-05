import mysql.connector
from mysql.connector import pooling
from server import ServerError, UserError
from utils.aws import get_aws_secret
from contextlib import contextmanager
from botocore.exceptions import NoCredentialsError, ClientError, EndpointConnectionError

invites_connection_pool = None


def initialize_db_connection():
    global invites_connection_pool
    invites_connection_pool = init_connection_pool("huskerlyinvitesdb")


def init_connection_pool(dbname):
    secret_name = "huskerly-db-credentials"
    credentials = get_aws_secret(secret_name)
    try:
        return pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=8,  # Maximum number of connections
            pool_reset_session=True,
            database=dbname,
            user=credentials['username'],
            password=credentials['password'],
            host=credentials['host'],
            ssl_disabled=False,
            connection_timeout=10
        )
    except mysql.connector.Error as err:
        raise ValueError(f"Error initializing connection pool: {err}")


def connect_to_invites_database():
    global invites_connection_pool

    if not invites_connection_pool:
        invites_connection_pool = init_connection_pool("huskerlyinvitesdb")

    if invites_connection_pool is None:
        raise ValueError("Failed to initialize connection pool")

    return invites_connection_pool.get_connection()


@contextmanager
def get_cursor():
    conn = connect_to_invites_database()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except (ClientError, NoCredentialsError, UserError) as e:
        conn.rollback()
        raise UserError(f"AWS client error: {e.response['Error']['Message']}")
    except (EndpointConnectionError, ServerError):
        conn.rollback()
        raise ServerError("Failed to connect to AWS endpoint.")
    except Exception as e:
        conn.rollback()
        raise ServerError(f"An unexpected error occurred: {str(e)}")
    finally:
        cursor.close()
        conn.close()
