# VibeCHECK Project

## Project Overview
VibeCHECK is a web-based application that allows users to analyze influencer behavior and public sentiment. Users can view content related to influencers, such as YouTube videos and comments, and vote whether the influencer's vibe is 'good' or 'bad.' The system analyzes scraped data from YouTube and stores it in a MySQL database. Users will be able to vote on influencer behavior based on publicly available content and comments in the future. (will be further developed to input datas from tmz too.)

## Data Model
The project follows a structured relational database schema using **MySQL**. The data is organized into four key tables:

- **Influencers**: Contains information about influencers.
  - `id`: INT, Primary Key
  - `name`: VARCHAR, Influencer's name
  - `vibe_score`: DECIMAL, Calculated score based on votes  -  to be made

- **Content**: Stores information about influencers' content (e.g., posts or videos).
  - `id`: INT, Primary Key
  - `influencer_id`: INT, Foreign Key references `influencers`
  - `platform`: VARCHAR, The platform of the content (e.g., YouTube)
  - `url`: TEXT, Link to the content
  - `title`: VARCHAR, Title of the content

- **Comments**: Stores the comments for each content.
  - `id`: INT, Primary Key
  - `content_id`: INT, Foreign Key references `content`
  - `comment_text`: TEXT, Comment itself
  - `sentiment_score`: DECIMAL, Sentiment score for the comment  -  to be made

- **Votes**: Tracks user votes on influencer content.
  - `id`: INT, Primary Key
  - `influencer_id`: INT, Foreign Key references `influencers`
  - `content_id`: INT, Foreign Key references `content`
  - `vote`: ENUM ('good', 'bad'), Represents how people voted  -  to be made
 
### ER Diagram
![Database Schema](./schema.png)

### SQL Database:
We chose SQL (MySQL) for the following reasons:
- **Relational Data**: SQL is ideal because the relationships between influencers, content, and comments are clear and structured.
- **Data Integrity**: MySQL enforces strict data integrity with foreign keys to maintain consistency.
- **Efficiency**: SQL allows for efficient querying of structured data, which fits our needs as the data we're working with (influencers, content, votes) follows a well-defined structure.

While MongoDB offers flexibility in schema design, our need for structured data and complex relationships makes SQL a better choice for this project.

## Setup Instructions

### Prerequisites
- **Python 3.8 or higher**
- **MySQL Server** (installed and running)
- **pip** (Python package manager)

### Installation Steps
1. **Clone the Repository**
   ```
   git clone https://github.com/your-username/vibecheck.git](https://github.com/Kyrie21323/FinalProject.git
   cd vibecheck
   ```
2. **Navigate to the project directory**(??)
  ```
  cd path/to/finalproject
  ```
3. **Set Up Virtual Environment**
  ```
  python -m venv .venv
  #On Windows:
  .venv\Scripts\activate
  #On macOS/Linux:
  source .venv/bin/activate
  ```
4. **Install Required Packages - requirements.txt file**
  ```
  pip install -r requirements.txt
  ```
5. **Set up your .env file**
  a. Create a new file in the project root directory and name it .env
  b. Open the .env file in a text editor
  c. Add your MySQL connection details in the following format:
  ```
  DB_HOST=your_mysql_host
  DB_USER=your_mysql_username
  DB_PASS=your_mysql_password
  DB_NAME=your_database_name
  ```
  d. Replace the placeholders with your actual MySQL connection details (provided for you on Slack). For example:
  ```
  DB_HOST=34.123.45.67
  DB_USER=myuser
  DB_PASS=mypassword
  DB_NAME=campy_movies
  ```
  e. Save and close the .env file
6. **Create the database and tables, by running the main.py script**
  ```
  python main.py
  Data Insertion After running main.py, the script will automatically clean the CSV data and insert influencer and content data into the MySQL database.
  ```

## Ethics Considerations
1. Youtube
2. TMZ
3. Reddit

## 



