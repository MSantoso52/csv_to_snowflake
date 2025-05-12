# csv_to_snowflake
Data ingestion from CSV to Snowflake:
1. Import necessary python libs -- snowflake.connector, csv, os
2. Build connecton to Snoflake cloud
3. Create stage to temporary storage before load into Snowflake
4. Load csv file into stage
5. Get column form csv file's header
6. Create table if doesn't exist
7. Load data into Snowflake from stage
8. Remove file from stage
9. Commit the transactions
10. Close connection
