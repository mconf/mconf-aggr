import json
import os
import time

import psycopg2
import requests

# Get Institution GUID from environment variable
r_institution_guid = os.getenv("R_INSTITUTION_GUID")

# Get Hook URL from environment variable
hook_url = os.getenv("HOOK_URL")

# Get Dry Run from environment variable
dry_run = os.getenv("DRY_RUN", 1)

# Get Query Limit from environment variable
limit = os.getenv("QUERY_LIMIT", 100000)

# Get Start and End Dates from environment variables
start_date = os.getenv("START_DATE")
end_date = os.getenv("END_DATE")

# Get DB connection parameters from environment variables
db_params = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

print("-----------------------------------------------------------------------------------------")
print("Environment Variables collected")
print("Institution GUID:", r_institution_guid)
print("Hook URL:", hook_url)
print("Dry Run:", dry_run)
print("Query Limit:", limit)
print("Start Date:", start_date)
print("End Date:", end_date)
print("DB Parameters:", db_params)
print("-----------------------------------------------------------------------------------------")

time.sleep(5)

# Indexes for named columns
COLUMNS = {
    "id": 0,
    "server_id": 1,
    "meeting_event_id": 2,
    "external_meeting_id": 3,
    "internal_meeting_id": 4,
    "record_id": 5,
    "name": 6,
    "created_at": 7,
    "updated_at": 8,
    "is_breakout": 9,
    "published": 10,
    "start_time": 11,
    "end_time": 12,
    "participants": 13,
    "size": 14,
    "raw_size": 15,
    "metadata": 16,
    "playback": 17,
    "download": 18,
    "workflow": 19,
    "status": 20,
    "current_step": 21,
    "r_shared_secret_guid": 22,
    "r_institution_guid": 23,
    "parent_meeting_id": 24,
    "is_deleted": 25
}

try:
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(**db_params)

    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()

    # SQL query to select all fields from the "recordings" table and filter by r_institution_guid and specific created_at dates
    query = """
            SELECT *
            FROM recordings
            WHERE r_institution_guid = %s
            AND created_at::date >= %s
            AND created_at::date <= %s
            LIMIT %s
            """

    # Execute the SQL query with the provided r_institution_guid parameter
    cursor.execute(query, (r_institution_guid, start_date, end_date, limit))

    # Fetch all rows from the query result
    rows = cursor.fetchall()

    # Prepare a list to store formatted JSON objects
    json_objects = []

    # Iterate through rows and format the JSON objects
    for row in rows:
        # Use empty dictionaries if JSON fields are not present
        metadata = row[COLUMNS["metadata"]] if row[COLUMNS["metadata"]] else {}
        playback = row[COLUMNS["playback"]] if row[COLUMNS["playback"]] else {}
        download = row[COLUMNS["download"]] if row[COLUMNS["download"]] else {}
        workflow = row[COLUMNS["workflow"]] if row[COLUMNS["workflow"]] else {}

        # Create JSON object
        json_object = {
            "data": {
                "type": "event",
                "id": "rap-publish-ended",
                "attributes": {
                    "meeting": {
                        "internal-meeting-id": row[COLUMNS["internal_meeting_id"]],
                        "external-meeting-id": row[COLUMNS["external_meeting_id"]]
                    },
                    "record-id": row[COLUMNS["record_id"]],
                    "success": True,
                    "step-time": row[COLUMNS["end_time"]],    # Check later
                    "workflow": workflow,
                    "recording": {
                        "name": row[COLUMNS["name"]],
                        "is-breakout": row[COLUMNS["is_breakout"]],
                        "size": row[COLUMNS["size"]],
                        "metadata": metadata,
                        "playback": playback,
                        "download": download
                    }
                },
                "event": {
                    "ts": row[COLUMNS["end_time"]]    # Check later
                }
            }
        }

        # Append the formatted JSON object to the list
        json_objects.append(json_object)

except psycopg2.Error as error:
    print("Error connecting to the PostgreSQL database:", error)

finally:
    # Close the cursor and connection
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection closed.")

if dry_run == 0 or dry_run == '0': # Dry Run is explicitly set as off
    # Send events to Hook
    ok_events = 0
    not_ok_events = 0
    for object in json_objects:
        try:
            print("Sending event...")
            hook_response = requests.post(hook_url, json=object)
        except Exception as error:
            print("Error sending event:", error)
            not_ok_events += 1
        else:
            if hook_response.ok:
                print("Hook response OK")
                ok_events += 1
            else:
                print("Hook response NOT OK:", hook_response.raise_for_status())
                not_ok_events += 1

    print("Successful events:", ok_events)
    print("Not successful events:", not_ok_events)
    print("Total Recordings:", len(json_objects))

else:
    # Print the formatted JSON objects
    print("Printing builded JSON events...")
    print(json.dumps(json_objects, indent=4))
    print("Total Recordings:", len(json_objects))
