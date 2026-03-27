# What is dlt?

- An open-source Python library
- Automates schema evolution, normalization, and data loading.
- dlt is code

1. We define our source
2. We build the pipeline, it facilitates the extraction and transformation of data.
	- Every Pipeline has a name and it must be unique
	- We specify the name and destination 
3. Run the pipeline

- **The source** describes where the data comes from and how to fetch it from the API.
- **The pipeline** describes where the data should go (DuckDB) and keeps track of tables, schemas, and run history.

# Source

```Python
def openlibrary_source(query: str = "harry potter"):

return rest_api_source({
"client": {
"base_url": "https://openlibrary.org",
},
"resource_defaults": {
"primary_key": "key",
"write_disposition": "replace",
},
"resources": [
{
"name": "books",
"endpoint": {
"path": "search.json",
"params": {
"q": query,
"limit": 100,
},
"data_selector": "docs",
"paginator": {
"type": "offset",
"limit": 100,
"offset_param": "offset",
"limit_param": "limit",
"total_path": "numFound",
},
},
},
],
})
```

What you are looking at is a declarative **dlt REST API source configuration**. Instead of writing a massive Python script with `while` loops, `requests.get()`, and manual JSON parsing, this single dictionary tells dlt exactly how to scrape book data from the Open Library API and load it into your data warehouse.

Here is the exact breakdown of what every block of this code is doing:

1. The Function & Base Setup

```Python
def openlibrary_source(query: str = "harry potter"):
    return rest_api_source({
        "client": {
            "base_url": "https://openlibrary.org",
        },
```

- **The wrapper:** It’s wrapped in a standard Python function so you can pass it a dynamic search `query` (defaulting to "harry potter").
- **`rest_api_source`:** This is a built-in dlt function. It takes a configuration dictionary and automatically generates the complex Python code needed to interact with an API.
- **`client`:** Defines the root URL. Every request dlt makes will start with `https://openlibrary.org`.

2. The Database Settings (`resource_defaults`)

```Python
        "resource_defaults": {
            "primary_key": "key",
            "write_disposition": "replace",
        },
```

This section tells dlt how to handle the data once it reaches your destination (like BigQuery or DuckDB):

- **`primary_key`:** Tells dlt that the column named `key` in the API response is the unique identifier for each book.
- **`write_disposition: "replace"`:** This is important! It means every time you run this pipeline, dlt will `DROP` the existing table in your database and recreate it from scratch with the fresh data. (Other options are `append` or `merge`).

 3. The Target Endpoint (`resources`)

```Python
        "resources": [
            {
                "name": "books",
                "endpoint": {
                    "path": "search.json",
                    "params": {
                        "q": query,
                        "limit": 100,
                    },
```

A "resource" in dlt usually translates to a single table in your database.

- **`name: "books"`:** The table created in BigQuery/DuckDB will be named `books`.
- **`path`:** Appends to the base URL. dlt will make requests to `https://openlibrary.org/search.json`.
- **`params`:** The URL query parameters. If you run this with the default, it hits: `.../search.json?q=harry+potter&limit=100`.

4. The "Magic" of dlt: Selectors and Pagination

``` Python
                    "data_selector": "docs",
                    "paginator": {
                        "type": "offset",
                        "limit": 100,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "numFound",
                    },
```

This is the part that saves data engineers hours of work:

- **`data_selector: "docs"`:** APIs usually return metadata you don't want in your database. The Open Library returns something like `{"numFound": 800, "start": 0, "docs": [{book1}, {book2}]}`. By setting the selector to `docs`, dlt ignores the metadata and only extracts the actual array of books to put in your table.
- **`paginator`:** Since there are thousands of Harry Potter books, the API only gives you 100 at a time. Instead of you writing a manual `for` loop to fetch page 1, then page 2, then page 3, you just configure this block.
    - It tells dlt to use an **offset** strategy (skip 0, then skip 100, then skip 200).
    - **`total_path`** tells dlt to look at the `numFound` field in the API's JSON response to know exactly when it has scraped all the books and can stop making requests.

# Pipeline

```Python
pipeline = dlt.pipeline(
pipeline_name="ol_demo",
destination="duckdb",
dataset_name="ol_data",
progress="log" # logs the pipeline run (Optional)
)
```

Instead of running everything at once by `pipeline.run(source)`, we will now run the pipeline in three separate phases so we can clearly see what happens at each stage:

1. **Extract**: download raw data from the API
2. **Normalize**: turn nested JSON into relational tables
3. **Load**: write those tables into DuckDB

## Extract

**Extract** means:

- dlt sends requests to the Open Library API
- the raw JSON responses are downloaded
- the results are stored in dlt’s local working folder

At this stage, the data is **not** in DuckDB yet. We are just confirming that we successfully pulled data from the API.

```Python
extract_info = pipeline.extract(openlibrary_source())
```

## Normalize

This is where dlt transforms raw JSON into a clean relational structure.

During normalization, dlt does three key things:

 1. Adds Tracking Columns to the Main Table

dlt adds special columns to every table:

- `_dlt_id`: A unique identifier for each row
- `_dlt_load_id`: Links each row to the load job that created it

 2. Flattens Nested Data into Child Tables

APIs often return nested JSON. For example, a book can have multiple authors (a list), multiple editions, and multiple identifiers.

dlt flattens these nested structures into separate **child tables** with names like:

- `books__author_name`
- `books__author_key`
- `books__language`

Each child table has a `_dlt_parent_id` column that references `_dlt_id` in the parent table. This is how dlt maintains relationships.

 3. Creates Metadata Tables

dlt also creates internal tables to track pipeline state:

- `_dlt_loads`: Tracks load history (when data was loaded, status)
- `_dlt_pipeline_state`: Stores pipeline state for incremental loading
- `_dlt_version`: Tracks schema versions

```Python
normalize_info = pipeline.normalize()
```

### What happened during Normalize?

After running `pipeline.normalize()`, we now see multiple tables instead of just one.

Tables created/updated:

- `books`
- `books__author_key`
- `books__author_name`
- `books__editions__docs`
- `books__editions__docs__language`
- `books__ia`

---

### What does this mean?

We started with **N book search results** in the `books` table.

During normalization:

- Each book may have **more than N authors**, so those were split into:
    - `books__author_name`
    - `books__author_key`
- Each book may contain **edition information**, which became:
    - `books__editions__docs`
- Some editions contain **language information**, which became:
    - `books__editions__docs__language`
- The `ia` field (Internet Archive IDs) is a list, so it became:
    - `books__ia`

This is the key moment in the pipeline.

The data has been transformed from nested JSON into a **relational structure** with multiple linked tables. This makes it much easier to query and analyze.

### Schema Visualization

dlt can render the schema as a visual diagram.

```Python
# Display schema
pipeline.default_schema
```

##  Load

Now we run the final stage of the pipeline: **Load**.

Load means:

- dlt creates tables in DuckDB (if they do not already exist)
- the normalized rows are inserted into those tables
- the pipeline records the load in its internal tracking tables

```Python
load_info = pipeline.load()
```

After this step, the data is fully stored in the database and ready to query.

At this point:

- The `books` table contains our books
- The related tables (such as `books__author_name` and `books__editions__docs`) contain the exploded nested data
- Everything is now queryable using `pipeline.dataset()` or SQL

This is the moment where the data officially moves from “pipeline processing” into a database you can explore.

## Run The Pipeline

Now that we have walked through each step individually, we can run the entire workflow using a single command:

```Python
load_info = pipeline.run(openlibrary_source())
```

### What does `pipeline.run()` do?

`pipeline.run()` simply combines the three steps we already executed manually:

1. **Extract** – fetch data from the Open Library API
2. **Normalize** – convert nested JSON into relational tables
3. **Load** – write those tables into DuckDB

In other words, this:

```
pipeline.run(source)
```

is equivalent to:

```
pipeline.extract(source)
pipeline.normalize()
pipeline.load()
```

There is no hidden magic. It just runs the full ELT process in order.

## Inspect the Loaded Data

Now that the data is loaded into DuckDB, we can inspect it using `pipeline.dataset()`.

This gives us a convenient Python interface for exploring the tables that dlt created, without writing SQL.

### What dlt handled for us

✔ API requests  
✔ JSON normalization  
✔ Table creation  
✔ Database loading  
✔ Simple dataset inspection

---

### But there are still friction points

• Getting the REST API config exactly right  
• Remembering paginator syntax  
• Remembering how to inspect tables  
• Debugging schema or pagination issues  
• Writing Python or SQL to get insights

It works... but it still takes effort.

# DuckDB

If BigQuery is a massive, enterprise-grade freight train, DuckDB is a Formula 1 car that fits inside your backpack.

The easiest way to understand it is with this analogy: **DuckDB is the "SQLite for Analytics."**

Here is a breakdown of what makes it so incredibly popular right now:

### 1. It is "In-Process" (No Servers Needed)

Think about how you interacted with BigQuery. You wrote a SQL query on your laptop, sent it over the internet to Google's servers, Google's "Borg" cluster spun up resources, crunched the data, and sent the answer back. That is a traditional **client-server** architecture.

DuckDB is **embedded** (in-process). It doesn't run on a background server. It runs directly inside the Python script, Jupyter notebook, or command-line tool you are currently using. There is no infrastructure to set up, no credentials to configure, and zero network latency. You just `pip install duckdb` and start writing SQL.

### 2. Built for Analytics (OLAP)

While SQLite is also embedded, it reads data row-by-row (OLTP), which is great for running a lightweight mobile app, but terrible for summing up 10 million taxi trips.

DuckDB is a **columnar, vectorized** database. This means it stores and processes data exactly like BigQuery or Snowflake does, making it capable of running heavy analytical aggregations on millions of rows in fractions of a second, right on your laptop's CPU.

### 3. It Reads Everything Directly

You don't even have to "load" data into DuckDB to use it. It can execute blazingly fast SQL queries directly on top of raw Parquet files, CSVs, or JSON files sitting on your local hard drive or in an AWS S3/Google Cloud bucket.

SQL

```
-- You can literally just query a file path in DuckDB
SELECT VendorID, COUNT(*) 
FROM 'yellow_tripdata_2024-01.parquet' 
GROUP BY VendorID;
```

### Where does it fit in the Modern Data Stack?

DuckDB has become the absolute darling of the data engineering community for a few specific use cases:

- **Local Development & Testing:** Instead of paying Google every time you test a dbt model, you can use DuckDB to test your dbt transformations locally on a sample of data for free, instantly.
- **Data Science:** Pandas can be notoriously slow and memory-hungry. Data scientists use DuckDB to crunch massive datasets in Python using SQL before passing the summarized data to their machine learning models.
- **Edge Computing:** Running analytics on smaller devices or in environments where setting up a full data warehouse is overkill.

dbt natively supports DuckDB. A very common modern workflow is using **dbt + DuckDB** to build pipelines entirely locally before deploying them to a giant warehouse like BigQuery.

# The AI-Assisted Way

Three step process:

1. Using dltHub LLM scaffolds, A templates dltHub created to give you step by step instructions for setting up the project and writing prompts to create and run the dlt pipelines.
	- Better interacting directly with LLM, it gets instructions tailored directly for a specific source to get best outcome with minimum debugging.
	- [dlthub][https://dlthub.com/context/]
2. Ensure Quality and Validate Schema, data and destination (like how we used `pipeline.dataset()`) via:
	- dlt Dashboard which is a visual tool that we can interact with, that gives us basic metadata and data for a pipeline run.
	- dlt MCP server
3. Create reports & transformations
	- Notebooks
	- IbisLibrary, a Python library that gives the familiar, easy-to-write syntax of **Pandas**, but executes the actual data processing inside a powerful SQL engine like **BigQuery** or **DuckDB**.

## Ibis Library

### The Problem it Solves

Traditionally, data engineers and data scientists had to choose between two less-than-ideal options for transforming data:

1. **Pandas:** It is incredibly easy to write and test in Python, but it processes everything in your computer's RAM. If you try to load 20 million NYC Taxi records into a Pandas DataFrame, your laptop will crash.
2. **Raw SQL:** It runs beautifully on massive data warehouses, but writing thousands of lines of raw SQL strings inside Python scripts is messy, hard to test, and lacks standard software engineering features.

### The Ibis Solution: "Push-Down" Compute

Ibis gives you the best of both worlds. You write your transformations in Python, but Ibis **never actually pulls the data into your computer's memory.** Instead, Ibis acts as a translator. It takes your Python code, automatically compiles it into highly optimized SQL, and "pushes" that SQL down to the database to do the heavy lifting.

```Python
import ibis

# 1. Connect Ibis to your existing BigQuery dataset
con = ibis.bigquery.connect(project_id="your-project", dataset_id="zoomcamp")
table = con.table("yellow_taxi_regular")

# 2. Write Python code (looks just like Pandas!)
result = table.group_by("VendorID").aggregate(
    avg_fare = table.fare_amount.mean()
)

# 3. Ibis secretly translates that into a SQL SELECT statement 
# and makes BigQuery do the work.
print(result.execute()) 
```

### Write Once, Run Anywhere

The absolute superpower of Ibis is that it is **backend agnostic**.

Remember how BigQuery uses a slightly different SQL dialect than PostgreSQL, which is slightly different than DuckDB? Ibis handles all those translations for you.

You can write your Ibis Python code once, test it locally on your laptop using **DuckDB** in fractions of a second, and then change one line of code to deploy that exact same logic to **BigQuery** in production.

## MCP

**MCP** stands for the **Model Context Protocol**. It is an open-source standard recently introduced by Anthropic, but it is rapidly being adopted across the entire AI industry.

The easiest way to understand an MCP Server is to think of it as the **"USB-C port for AI."**

Here is a breakdown of exactly what it is, the problem it solves, and how it works under the hood.

### The Problem it Solves

Right now, Large Language Models are incredibly smart, but they are completely isolated. They don't know what is in your local files, your company's Slack, or your data warehouse.

Previously, if you wanted an AI to be able to read your database, developers had to write custom, brittle integration code specifically for OpenAI's API, and then write a completely different integration for Claude, and another for Google. It was a fragmented nightmare.

### The MCP Solution

MCP creates a universal, standardized way for AI models to connect to external data sources and tools.

Instead of writing custom integrations, you just build one **MCP Server**. Once that server is running, _any_ AI application that speaks the MCP language can instantly connect to it, read its data, and execute its tools securely.

### How the Architecture Works

There are three main pieces to this puzzle:

1. **The MCP Client (The Host):** This is the application you are actively using to chat with the AI. Examples include the Claude Desktop app, or advanced coding IDEs like Cursor and Windsurf.
2. **The MCP Server (The Bridge):** This is a lightweight program that you run locally on your machine or on a remote server. Its only job is to safely expose specific resources. You can have a "Postgres MCP Server," a "GitHub MCP Server," or a "Google Drive MCP Server."
3. **The LLM (The Brain):** The underlying model that takes your prompt, asks the Client to fetch context from the Server, and then generates your answer.

### Why this is huge for Data and Engineering

Since you have been deep-diving into data pipelines, APIs, and databases, MCP is exactly the kind of architecture that changes how you build internal tools.

If you are working with a massive, complex data warehouse, you don't need to copy-paste your SQL schemas into a chat window anymore. You can spin up an MCP Server connected to your database. When you ask the AI, _"Why is my query failing?"_, the AI can use the MCP Server to autonomously inspect your actual, live database schema, test a few queries, and give you the exact, verified solution.

### How to set up MCP Server on Cursor

1. ctrl + shift + p to open command palette
2. Tools & MCP
3. Add new MCP server, in our case the dlt one.
```
{
  "mcpServers": {
    "dlt": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "dlt[duckdb]",
        "--with",
        "dlt-mcp[search]",
        "python",
        "-m",
        "dlt_mcp"
      ]
    }
  }
}
```

## Instructions

1. Initialize the project folder
```bash
uv venv && source .venv/bin/activate
uv pip install "dlt[workspace]"
```
2.   Install the `dlt` AI Workbench:
```bash
uv run dlt ai init --agent <your-agent> # <agent>: claude | cursor | codex
```
3. Install the `rest-api-pipeline` toolkit:
```bash
uv run dlt ai toolkit rest-api-pipeline install
```
4. Start LLM-assisted coding:
```
Use /find-source to load data from the Open Library API into DuckDB.
```
5. Run the pipeline:
```bash
python open_library_pipeline.py
```
6. Inspect pipeline and data:
```bash
dlt pipeline open_library_pipeline show
```



# Needed Libraries for Ingestion
## Requests Library

The `requests` library in Python is a wildly popular tool used to send HTTP requests. In simple terms, it allows your Python code to talk to the internet, acting very much like a web browser without the graphical interface.

Whenever you need your code to fetch data from a website, send data to a server, or interact with a web service, `requests` is usually the go-to tool.

### What is it primarily used for?

- **Interacting with APIs:** This is its most common use case. You can use it to pull live data from REST APIs (like fetching weather data, stock prices, or sports scores) by sending a `GET` request.
- **Web Scraping:** You can use it to download the raw HTML of a webpage. Once downloaded, you'd typically pair it with another library (like `BeautifulSoup`) to extract the specific text or data you want.
- **Sending Data:** You can use it to programmatically submit forms, upload files, or send JSON data to a server using a `POST` request.
- **Downloading Files:** It can easily grab images, CSVs, PDFs, or any other files hosted online and save them directly to your local machine.

### Why is it so popular?

Python actually has a built-in module for handling HTTP requests called `urllib`. However, `urllib` is notoriously clunky and requires a lot of boilerplate code for even simple tasks.

The motto of the `requests` library is "HTTP for Humans." It abstracts away all the confusing complexities behind a beautiful, simple API. Things like passing URL parameters, authenticating with a server, or automatically decoding JSON responses take just a single line of code.


## BytesIO

If `requests` is the tool you use to grab data from the internet, `BytesIO` (from Python's built-in `io` module) is where you can temporarily hold that data without ever saving it to your hard drive.

Think of it as a **virtual file that lives entirely in your RAM.** It tricks Python into thinking it's interacting with a real file saved on your computer, when in reality, everything is happening in memory.

### Why use `BytesIO` with `requests`?

When you download a file (like a CSV, a zip archive, or an image) using `requests`, the raw binary data is stored in `response.content`. However, many Python libraries (like `pandas` or `zipfile`) expect to read from a _file_, not a raw string of bytes.

Instead of writing that data to your disk just to read it again, you wrap it in `BytesIO`.

### Why this is a superpower for Data Pipelines

When you are building automated ETL pipelines—especially ones that run inside isolated environments like Docker containers or are managed by orchestrators like Airflow—you generally want to avoid reading and writing temporary files to the local disk. It slows things down and creates cleanup work.

With `BytesIO`, you can grab data from an API, hold it in memory, transform it, and push it directly into a data warehouse or cloud storage, keeping your pipeline fast and clean.

## Yield

In Python, `yield` is a keyword used to return data from a function, but with a massive twist: **it doesn't destroy the function's local state.** When a function uses `yield` instead of `return`, it becomes a **generator**.

Here is the easiest way to think about the difference:

- **`return` is like a caterer:** It prepares all 1,000 sandwiches in the kitchen, puts them on a massive platter, and brings them to you all at once. This requires a huge platter and a lot of table space (RAM/memory). Once the caterer drops them off, their job is entirely done.
- **`yield` is like a vending machine:** It gives you exactly one sandwich. It then pauses and waits. When you press the button for another one, it remembers exactly where it left off and dispenses the next sandwich. It only takes up enough space for one sandwich at a time.

### Why Data Engineers Love `yield`

Since you are building ETL pipelines and working with tools like `dlt`, `yield` is basically a superpower for memory management.

If you use the `requests` library to pull 5 million rows from a database or an API, putting all 5 million rows into a single Python list and using `return` will likely crash your machine (Out of Memory error).

Instead, you use `yield` to process and pass along one chunk of data at a time. Tools like `dlt` are specifically designed to accept these generators so they can stream data directly to your destination (like BigQuery or your local filesystem) without ever holding the whole dataset in RAM.