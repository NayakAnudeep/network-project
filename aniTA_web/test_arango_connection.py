# correct_arango_test.py
from arango import ArangoClient
import sys

print(f"Python version: {sys.version}")

# ArangoGraph requires specific endpoint format
HOST = "https://d285766d74a6.arangodb.cloud:8529"  # Include the port 
USERNAME = "root"
PASSWORD = "p8k1EmWeR5O150EJZMTE"
DATABASE = "aita_db"

print(f"Testing connection to: {HOST}")

try:
    # Configure with correct hosts array format
    client = ArangoClient(hosts=[HOST])
    
    # Connect to database with correct auth
    db = client.db(
        name=DATABASE,
        username=USERNAME,
        password=PASSWORD,
        verify=True
    )
    
    # Test a simple API call
    system_info = db.properties()
    print(f"Connected successfully!")
    print(f"Database properties: {system_info}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
