import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import pandas as pd

#load variables from the .env file
load_dotenv()

#the function can either connect with or without specifying a database
def create_connection(with_database=True):
    connection = None
    try:
        #print connection details for debugging purposes
        #print(f"Attempting to connect to:")
        #print(f"Host: {os.getenv('DB_HOST')}")
        #print(f"User: {os.getenv('DB_USER')}")
        # if with_database:
        #     print(f"Database: {os.getenv('DB_NAME')}")

        #establish connection to the database
        if with_database:
            #if the database is already created, connect with it
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS'),
                database=os.getenv('DB_NAME')
            )
        else:
            #when creating the database - without specifying
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS')
            )
        #debug message
        # print("Successfully connected to the database")
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return connection

#create the database if it doesn't already exist
def create_database(connection):
    print("Creating database...")
    create_db_query = f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')};"
    try:
        #create database with SQL query
        with connection.cursor() as cursor:
            cursor.execute(create_db_query)
            print(f"Database '{os.getenv('DB_NAME')}' created or already exists.")
    except Error as e:
        print(f"Error creating database: {e}")

#create influencers table
def create_influencers_table(connection):
    print("Creating influencers table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS influencers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        vibe_score DECIMAL(5, 2) DEFAULT 0.00
    );
    """
    try:
        #execute query to create table
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()  #changes committed to the database
    except Error as e:
        print(f"Error creating influencers table: {e}")

#create content table / logic is same as influencer table
def create_content_table(connection):
    print("Creating content table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS content (
        id INT AUTO_INCREMENT PRIMARY KEY,
        influencer_id INT,
        platform VARCHAR(50),
        url TEXT NOT NULL,
        title VARCHAR(255),
        sentiment_score INT,
        FOREIGN KEY (influencer_id) REFERENCES influencers(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
    except Error as e:
        print(f"Error creating content table: {e}")

#create comments table / logic is same as influencer table
def create_comments_table(connection):
    print("Creating comments table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS comments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        content_id INT,
        comment_text TEXT NOT NULL,
        sentiment_score DECIMAL(5, 2),
        FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
    except Error as e:
        print(f"Error creating comments table: {e}")

#create votes table / logic is same as influencer table
def create_votes_table(connection): 
    print("Creating votes table...")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS votes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        influencer_id INT,
        content_id INT,
        FOREIGN KEY (influencer_id) REFERENCES influencers(id) ON DELETE CASCADE,
        FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
    );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
    except Error as e:
        print(f"Error creating votes table: {e}")

#read merged and cleaned data from .csv
def clean_data():
    merged_file = os.path.join('scraping', 'celebrity_scraped.csv')  # path to the merged CSV file
    data_df = pd.read_csv(merged_file)
    #select only required columns
    data_df = data_df[['Name', 'Title', 'URL', 'comment']].dropna(subset=['Name', 'Title', 'URL'])
    return data_df

#add influencers into database
def add_influencer(connection, influencer_data):
    #check if an influencer exists
    check_influencer_query = "SELECT id FROM influencers WHERE name = %s"
    #insert the new influencer
    insert_influencer_query = "INSERT INTO influencers (name) VALUES (%s)"

    try:
        with connection.cursor() as cursor:
            for _, row in influencer_data.iterrows():
                # Check if already exists
                cursor.execute(check_influencer_query, (row['Name'],))
                result = cursor.fetchone()

                if result is None:
                    #if it doesn't, insert
                    cursor.execute(insert_influencer_query, (row['Name'],))
                    connection.commit()
                    print(f"Influencer '{row['Name']}' added.")
    except Error as e:
        print(f"Error inserting influencers: {e}")

#add content into database / checking for existing logic is same as add_influencer
def add_content(connection, content_data):
    #check if the content exists
    check_content_query = "SELECT id FROM content WHERE url = %s"
    #insert new content
    insert_content_query = "INSERT INTO content (influencer_id, platform, url, title) VALUES (%s, %s, %s, %s)"
    try:
        with connection.cursor() as cursor:
            for _, row in content_data.iterrows():
                #check if content exists
                cursor.execute(check_content_query, (row['URL'],))
                result = cursor.fetchone()
                if result is None:
                    #determine platform based on comment presence
                    platform = "YouTube" if pd.notna(row['comment']) else "TMZ"
                    #get the influencer ID
                    cursor.execute("SELECT id FROM influencers WHERE name = %s", (row['Name'],))
                    influencer_id = cursor.fetchone()
                    if influencer_id:
                        # Insert the content with the determined platform
                        cursor.execute(insert_content_query, (influencer_id[0], platform, row['URL'], row['Title']))
                        connection.commit()
                        print(f"Content '{row['Title']}' added for influencer '{row['Name']}' on platform '{platform}'.")
                    else:
                        print(f"Influencer '{row['Name']}' not found for content '{row['Title']}'.")
    except Error as e:
        print(f"Error inserting content: {e}")

#add comments into database / checking for existing logic is same as add_influencer
def add_comment(connection, comment_data):
    check_comment_query = "SELECT id FROM comments WHERE comment_text = %s AND content_id = %s"

    insert_comment_query = insert_comment_query = "INSERT INTO comments (content_id, comment_text) VALUES (%s, %s)"
    try:
        with connection.cursor() as cursor:
            for _, row in comment_data.dropna(subset=['comment']).iterrows():
                #find the content ID based on the title
                content_id_query = "SELECT id FROM content WHERE title = %s"
                cursor.execute(content_id_query, (row['Title'],))
                content_id = cursor.fetchone()
                if content_id:
                    #check if the comment already exists
                    cursor.execute(check_comment_query, (row['comment'], content_id[0]))
                    result = cursor.fetchone()
                    if result is None:
                        #if the comment doesn't exist, insert it
                        cursor.execute(insert_comment_query, (content_id[0], row['comment']))
                        connection.commit()
                        print(f"Comment added for content '{row['Title']}'.")

    except Error as e:
        print(f"Error inserting comments: {e}")

#add and delete columns we need/do not need for out project
def adjust_tables(connection):
    try:
        with connection.cursor() as cursor:
            #check and add columns for the 'votes' table
            cursor.execute("SHOW COLUMNS FROM votes LIKE 'good_vote';")
            if cursor.fetchone() is None:
                cursor.execute("ALTER TABLE votes ADD COLUMN good_vote INT DEFAULT 0;")
                print("New columns added successfully (if they were missing).")
            cursor.execute("SHOW COLUMNS FROM votes LIKE 'bad_vote';")
            if cursor.fetchone() is None:
                cursor.execute("ALTER TABLE votes ADD COLUMN bad_vote INT DEFAULT 0;")
                print("New columns added successfully (if they were missing).")

            #same logic for 'content' table
            cursor.execute("SHOW COLUMNS FROM content LIKE 'sentiment_score';")
            if cursor.fetchone() is None:
                cursor.execute("ALTER TABLE content ADD COLUMN sentiment_score DECIMAL(5, 2);")
                print("New columns added successfully (if they were missing).")

            #same logic for 'influencers' table
            cursor.execute("SHOW COLUMNS FROM influencers LIKE 'image_url';")
            if cursor.fetchone() is None:
                cursor.execute("ALTER TABLE influencers ADD COLUMN image_url TEXT;")
                print("New columns added successfully (if they were missing).")

            #check and delete columns
            cursor.execute("SHOW COLUMNS FROM votes LIKE 'vote';")
            if cursor.fetchone() is not None:
                #drop the 'vote' column if it exists
                cursor.execute("ALTER TABLE votes DROP COLUMN vote;")
                print("Column 'vote' has been removed from 'votes' table.")
            else:
                print("Column 'vote' does not exist in 'votes' table, no action needed.")


            # Commit changes
            connection.commit()
            
    
    except Error as e:
        print(f"Error adding new columns: {e}")

#main function that creates the database and tables
def main():
    #connect without specifying the database first to see if it doesn't exist
    connection = create_connection(with_database=False)
    if connection:
        create_database(connection)                         #create if it doesn't exist
        connection.close()

    #connect to the created database and create the tables
    connection = create_connection(with_database=True)
    if connection:
        create_influencers_table(connection)                #create influencers table 
        create_content_table(connection)                    #create content table
        create_comments_table(connection)                   #create comments table
        create_votes_table(connection)                      #create votes table

        #add new columns to the existing tables
        adjust_tables(connection)

        #save the CSV data
        merged_data = clean_data()

        #insert cleaned data into MySQL
        add_influencer(connection, merged_data)
        add_content(connection, merged_data)
        add_comment(connection, merged_data)
        
        connection.close()

#check if the script is run directly
if __name__ == "__main__":
    main()

