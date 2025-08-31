import os
import sys
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector, IPTypes
import asyncio

load_dotenv()  # đọc file .env

# Trên Windows, set event loop policy để asyncpg không bị lỗi loop
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not service_account_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path

DATABASE_URL = "postgresql+psycopg2://postgres:MY_SECURE_PASSWORD@35.240.252.40:5432/postgres"
GCP_PROJECT_ID = "gen-lang-client-0974620078"
GCP_REGION = "asia-southeast1"
CLOUDSQL_INSTANCE_NAME = "my-postgres"
DB_USER = "postgres"
DB_PASSWORD = "MY_SECURE_PASSWORD"
DB_NAME = "postgres"
GOOGLE_APPLICATION_CREDENTIALS = "C:\\Users\\mt200\\OneDrive\\Desktop\\AI\\AI_challenge\\software\\back-end\\service-account.json"

connector = Connector()

async def test():
    # **không await connector.connect**
    conn = connector.connect(
        f"{GCP_PROJECT_ID}:{GCP_REGION}:{CLOUDSQL_INSTANCE_NAME}",
        "asyncpg",
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        ip_type=IPTypes.PUBLIC
    )
    
    # Sau đó dùng asyncpg methods với await
    result = await conn.fetchval("SELECT 1")
    print(result)
    
    await conn.close()        # đóng connection
    await connector.close()   # đóng connector

asyncio.run(test())