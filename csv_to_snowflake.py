import snowflake.connector
import csv
import os

def load_csv_to_snowflake(
    account,
    user,
    password,
    database,
    schema,
    warehouse,
    table_name,
    csv_file_path,
    stage_name,
    file_format_name="my_csv_format", # Added file format name
    create_table=True  # Added create_table parameter
):
    try:
        # 1. Connect to Snowflake
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema,
        )
        cursor = conn.cursor()

        # 2. Create the file format (if it doesn't exist)
        cursor.execute(f"""
            CREATE FILE FORMAT IF NOT EXISTS {file_format_name}
            TYPE = 'CSV'
            FIELD_DELIMITER = ','
            SKIP_HEADER = 1
            NULL_IF = ('NULL', 'null', '')
            EMPTY_FIELD_AS_NULL = TRUE;
        """)

        # 3. Create the stage (if it doesn't exist)
        cursor.execute(f"CREATE STAGE IF NOT EXISTS {stage_name}")

        # 4. Upload the CSV file to the stage
        #    Use put with overwrite=True to handle re-uploads.
        cursor.execute(f"PUT file://{csv_file_path} @{stage_name} AUTO_COMPRESS=TRUE OVERWRITE=TRUE")

        # 5. Get column names from the CSV file's header row.
        with open(csv_file_path, 'r', encoding='utf-8') as f: # Explicit encoding
            reader = csv.reader(f)
            header = next(reader)  # Get the header row
            columns = ", ".join(f'"{col}"' for col in header) # Quote column names
            columns_for_table_creation = ", ".join(f'"{col}" VARCHAR' for col in header) # For CREATE TABLE

        # 6. Create the table if it doesn't exist AND create_table is True
        if create_table:
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} ({columns_for_table_creation})
                """)
                print(f"Table {table_name} created (if it didn't exist).")
            except Exception as e:
                print(f"Error creating table {table_name}: {e}")
                #  Don't raise here;  try to load data anyway.
        else:
            print(f"Skipping table creation. Assuming table {table_name} exists.")

       # 7. Load data from the CSV file in the stage into the table
        cursor.execute(f"""
            COPY INTO {table_name}
            FROM @{stage_name}/{os.path.basename(csv_file_path)}
            FILE_FORMAT = (FORMAT_NAME = '{file_format_name}')
            ON_ERROR = 'SKIP_FILE';  --  Important:  Handle errors robustly.
        """)
        print(f"Data loaded into table {table_name} successfully.")

        # 8. Clean up: Remove the file from the stage
        cursor.execute(f"REMOVE @{stage_name}/{os.path.basename(csv_file_path)}")

        # 9. Commit the transaction
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()  # Rollback on any error
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    #  Replace these with your actual Snowflake credentials and details
    snowflake_account = "*******"  # e.g., "myaccount.us-east-1.snowflakecomputing.com"
    snowflake_user = "******"
    snowflake_password = "*******"
    snowflake_database = "ORDERCUSTOMERS"
    snowflake_schema = "CUSTOMERS"
    snowflake_warehouse = "COMPUTE_WH"
    table_name = "customers"  # The name of the table you want to create or load into
    csv_file_path = "customers_data.csv"  #  Path to your CSV file
    stage_name = "my_staged"      # The name of the stage you want to use
    file_format_name = "my_csv_formated" # The name of the file format

    # Example usage:
    load_csv_to_snowflake(
        account=snowflake_account,
        user=snowflake_user,
        password=snowflake_password,
        database=snowflake_database,
        schema=snowflake_schema,
        warehouse=snowflake_warehouse,
        table_name=table_name,
        csv_file_path=csv_file_path,
        stage_name=stage_name,
        file_format_name=file_format_name, # added file format name
        create_table=True # added create_table
    )

