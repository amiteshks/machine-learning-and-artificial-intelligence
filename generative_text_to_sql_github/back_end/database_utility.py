from logging_utility import logger
import snowflake.connector
from typing import List, Dict, Any
from config import SNOWFLAKE_CONFIG
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from datetime import datetime, date
from decimal import Decimal
import json

# PATH_TO_KEY = 'C:\\Softwares\\openssl-0.9.8k_X64\\bin\\rsa_key.p8'
PATH_TO_KEY = "/app/keys/rsa_key.p8"

def convert_types(obj):
    """Convert datetime and Decimal objects to strings"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj

def execute_query(query: str) -> Dict[str, Any]:
    print(f"{SNOWFLAKE_CONFIG['USERNAME']}, {SNOWFLAKE_CONFIG['WAREHOUSE']}")

    try:
        # Load private key
        with open(PATH_TO_KEY, "rb") as key_file:
            p_key = serialization.load_pem_private_key(
                key_file.read(),
                password=SNOWFLAKE_CONFIG['KEY_PASSWORD'].encode(),
                backend=default_backend()
            )

        # Establish the connection
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_CONFIG['USERNAME'],
            private_key=p_key,
            account=SNOWFLAKE_CONFIG['ACCOUNT'],
            warehouse=SNOWFLAKE_CONFIG['WAREHOUSE'],
            database=SNOWFLAKE_CONFIG['DATABASE'],
            schema=SNOWFLAKE_CONFIG['SCHEMA']
        )

        # Create a cursor object using the connection
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        
        # Convert results to dictionaries and handle special types
        results = []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            # Convert datetime and Decimal types
            converted_dict = {k: convert_types(v) for k, v in row_dict.items()}
            results.append(converted_dict)

        # Format the results as a proper message
        message = {
            "role": "tool",
            "tool_call_id": "db_query_1",
            "content": json.dumps({
                "results": results,
                "row_count": len(results)
            })
        }

        return message

    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise
    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    result = execute_query("SELECT * FROM public.invoices LIMIT 10;")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
  