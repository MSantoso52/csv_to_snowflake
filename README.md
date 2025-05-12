# csv_to_snowflake
Data ingestion from CSV to Snowflake:
1. Import necessary python libs -- snowflake.connector, csv, os
2. Build connecton to Snoflake cloud
3. Create stage to temporary storage before load into Snowflake
4. Load data into Snowflake from stage by creating table
5. Close connection
