# OLTP VS OLAP

| | OLTP | OLAP |
| :--- | :--- | :--- |
| **Purpose** | Control and run essential business operations in real time | Plan, solve problems, support decisions, discover hidden insights |
| **Data updates** | Short, fast updates initiated by user | Data periodically refreshed with scheduled, long-running batch jobs |
| **Database design** | Normalized databases for efficiency | Denormalized databases for analysis |
| **Space requirements** | Generally small if historical data is archived | Generally large due to aggregating large datasets |
| **Backup and recovery** | Regular backups required to ensure business continuity and meet legal and governance requirements | Lost data can be reloaded from OLTP database as needed in lieu of regular backups |
| **Productivity** | Increases productivity of end users | Increases productivity of business managers, data analysts, and executives |
| **Data view** | Lists day-to-day business transactions | Multi-dimensional view of enterprise data |
| **User examples** | Customer-facing personnel, clerks, online shoppers | Knowledge workers such as data analysts, business analysts, and executives |


# What is a data warehouse 

- OLAP Solution
- Used for reporting and data analysis
- They have many sources
- Consists of meta data, summary data and raw data
- Outputs Data Marts for analysts, while other users (machine learning engineers or data scientists) might want to access the raw data directly

# BigQuery

- A data warehouse solution
- Serverless data warehouse, no severs to manage or database software to install
- Offers software as well as infrastructue including: scalability and high-availability
- Built-in features like
    - machine learning
    - geosatial analysis
    - business intelligence
- BigQuery maximizes flexibility by separating the compute engine that analyzes your data from your storage (huge advantage in terms of cost)

## External Tables in BigQuery

An **external table** in BigQuery acts like a window to data that lives somewhere else. Instead of physically loading and storing the data inside BigQuery's own storage system, you create a table schema that points to external files—usually sitting in a data lake like Google Cloud Storage (GCS).

When building the end-to-end pipeline for the Premier League project, the ETL process physically moved and loaded the data into the data warehouse. External tables flip that model. The data stays in its raw file format (like CSV, Parquet, or JSON) in the external storage, and BigQuery just reads it on the fly when you run a SQL query.

This is often called a **federated query**.

### Why Use External Tables?

- **Zero Loading Time**: You can query the data the second it lands in your GCS bucket without waiting for a data transfer job to finish.

- **Cost Efficiency**: You save on BigQuery storage costs because you are only paying to store the files in GCS (which is generally cheaper).

- **Rapid Exploration**: They are perfect for quickly inspecting new datasets to decide if they are worth fully importing into your warehouse.

- **ETL to ELT Shift**: You can use BigQuery's massive compute power to transform the raw external data and write the clean results into a standard, internal BigQuery table.

### The Trade-offs

- **Performance**: Queries on external tables are noticeably slower than queries on internal BigQuery tables. BigQuery can't optimize the storage or use its native caching as effectively.

- **Fewer Features**: You cannot use standard BigQuery performance tuning features like clustering on an external table. (Though, you can use Hive partitioning if your GCS folders are structured correctly, like `year=2024/month=01/`).

- **Data Consistency**: If a process overwrites or deletes the file in GCS while a query is running, the query might fail or return inconsistent results.

- Example Syntax for creating External Table:

```SQL
CREATE OR REPLACE EXTERNAL TABLE `taxi-rides-ny.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'CSV',
  uris = ['gs://nyc-tl-data/trip data/yellow_tripdata_2019-*.csv', 'gs://nyc-tl-data/trip data/yellow_tripdata_2020-*.csv']
);
```

# Partitioning in BigQuery
**Partitioning** is a way to divide a massive table into smaller, logical segments—called partitions—based on the values in a specific column.

Instead of scanning the entire database every time you run a query, BigQuery can use these partitions to only look at the specific chunks of data you actually need.

Number of partitions limit is 4000.

## Why is it so important?
- **Massive Cost Reduction**: BigQuery charges you based on the amount of data processed (scanned) during a query. If you filter your query to only look at one specific partition instead of the whole table, you process far less data and pay significantly less.

- **Performance Boost**: Because BigQuery is reading a fraction of the data, your queries will return results much faster.

## How can you partition a table?
BigQuery allows you to partition tables in three main ways:

1. **Time-unit column**: This is the most common method. You partition based on a `DATE`, `TIMESTAMP`, or `DATETIME` column in your data (e.g., partitioning by a `transaction_date`). You can set the partition granularity to be hourly, daily, monthly, or yearly.

2. **Ingestion time**: BigQuery automatically assigns the data to a partition based on the exact time the data arrived in the table. This uses hidden pseudo-columns (like _PARTITIONDATE) that you can reference in your queries.

3. **Integer range**: Partitioning based on a specific integer column. You define the start, end, and the interval (e.g., partitioning by `customer_id` into buckets of 10,000).

- A Conceptual Example:
Imagine you have a table of website events containing 5 years of data. If you partition it daily by the `event_date`, BigQuery creates separate physical storage blocks for every single day.

If you write a query and include `WHERE event_date = '2026-03-08'`, BigQuery goes straight to that specific day's block and completely ignores the partitions for the other 1,800+ days.

- Example Syntax:

```SQL
-- Create a partitioned table from external table
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitioned
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;

```

- We can inspect our partitions in table through a query like this:
```SQL
-- Let's look into the partitions
SELECT table_name, partition_id, total_rows
FROM `nytaxi.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'yellow_tripdata_partitioned'
ORDER BY total_rows DESC;
```

# Clustering in BigQuery
If partitioning is like putting your data into separate, labeled filing cabinets based on a date, **clustering** is how you organize the files inside those cabinets.

When you cluster a table in BigQuery, you are instructing it to automatically sort the underlying data based on the values of up to four columns you specify. BigQuery then groups these sorted rows into storage blocks.

When you run a query that filters or aggregates by those clustered columns, BigQuery uses the sorted blocks to skip scanning data it doesn't need, making the query significantly faster and cheaper.

## When to use Clustering
**Clustering** really shines when you are dealing with high-cardinality columns. High cardinality means a column has a massive number of distinct, unique values.

For example, if you were analyzing a massive dataset of football match events, you might partition the table by `match_date` (since there are only 365 days in a year), but you would cluster it by `player_id` or `team_id` because there are thousands of unique players.

Tables with data size < 1 GB, don’t show significant improvement with partitioning and clustering

Clustering columns must be top-level, non-repeated columns (`DATE`, `BOOL`, `GEOGRAPHY`, `INT64`, `NUMERIC`, `BIGNUMERIC`, `STRING`, `TIMESTAMP`, `DATETIME`)

## You should consider clustering when:

- Your queries frequently use `WHERE`, `JOIN`, or `GROUP BY` clauses on specific columns.

- You need more granularity than partitioning can provide (BigQuery limits you to 4,000 partitions per table).

- You are working with columns where partitioning would result in chunks of data that are too small (less than 1 GB per partition).

## How it compares to other Data Warehouses
If you've spent any time looking into other modern data warehousing platforms like Snowflake, BigQuery's clustering serves a very similar purpose to sorting data within micro-partitions to prune unnecessary data during a scan.

## The Golden Rules of Clustering
- **Order Matters**: You can specify up to four clustering columns, but the order you list them in your `CREATE TABLE` statement is crucial. BigQuery sorts by the first column, then the second, and so on. Your queries need to filter on those columns in the same order to get the performance benefits.

- **Cost Predictability**: Unlike partitioning, where BigQuery can tell you exactly how many bytes will be billed before you run the query, clustering reduces costs dynamically during execution. The pre-query cost estimate will show the maximum possible cost, but you are only billed for the data actually scanned after the clustering optimization kicks in.



- Example Syntax:
```SQL
-- Creating a partition and cluster table
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitioned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;
```

## Partitioning vs Clustering

| Clustering | Partitioning |
| :--- | :--- |
| Cost benefit unknown | Cost known upfront |
| You need more granularity than partitioning alone allows | You need partition-level management. |
| Your queries commonly use filters or aggregation against multiple particular columns | Filter or aggregate on single column |
| The cardinality of the number of values in a column or group of columns is large | |

---

## Clustering over partitioning

* Partitioning results in a small amount of data per partition (approximately less than 1 GB)
* Partitioning results in a large number of partitions beyond the limits on partitioned tables
* Partitioning results in your mutation operations modifying the majority of partitions in the table frequently (for example, every few minutes)

## Automatic reclustering
As data is added to a clustered table
the newly inserted data can be written to blocks that contain key ranges that overlap with the key ranges in previously written blocks, these overlapping keys weaken the sort property of the table

To maintain the performance characteristics of a clustered table, BigQuery performs automatic re-clustering in the background to restore the sort property of the table

For partitioned tables, clustering is maintained for data within the scope of each partition.

It doesn't cost the end user anything, it is done in the background of BQ and has no cost at all.

# BigQuery Best Practices

## Cost reduction tips
- Avoid SELECT * and only select the columns you need
- Price your queries by using the dry-run option to see how much data will be scanned before you run the query
- Use partitioning and clustering to reduce the amount of data scanned
- Use streaming inserts with caution, they can increase costs drastically
- Materialize query results in stages to avoid repeatedly scanning the same data, BQ also caches query results.

## Query performance tips
- Filter on partitioned and clustered columns to take advantage of pruning
- Denormalize your data to avoid expensive JOINs
- Use nesterd and repeated fields to store related data together and reduce the need for JOINs
- Use external data sources appropriately, they are great for quick exploration but not for production queries, don't use it, in case you want a high query performance.
- Reduce data before using a JOIN, for example by using a CTE to filter the data before joining it with another table.
- Do not treat WITH clauses as prepared statements, they are not, they are just a way to organize your query and make it more readable, they do not reduce the amount of data scanned.
- Avoid oversharding tables
- Avoid JavaScrups user-defined functions (UDFs) in BigQuery, they are not optimized for performance and can significantly slow down your queries.
- Use approximate aggregation functions like `APPROX_COUNT_DISTINCT` instead of `COUNT(DISTINCT ...)` when you can tolerate a small margin of error in exchange for much faster query performance.
- Order last, for query operation to maximize performance.
- Optimize your join patterns, as a best practice, place the table with the largest number of rows first, followed by the table with the fewest rows, and then place the remaining tables by decreasing size. The reason for this is that the first table will be evenlly distributed across all worker nodes, while the last table will be broadcasted to all worker nodes, and the middle tables will be shuffled across the network. By placing the largest table first, you can minimize the amount of data that needs to be shuffled across the network, which can significantly improve query performance.

# Streaming Inserts in BigQuery

Instead of waiting for a large file to be processed and loaded all at once, streaming inserts allow you to push data into a BigQuery table record-by-record (or in very small batches) in real time.

## How It Works
When you stream data, you use an API (traditionally the `tabledata.insertAll` API, or the newer, more efficient BigQuery Storage Write API) to send JSON objects directly to BigQuery. The moment the API accepts the data, it becomes immediately available for querying.

## When to Use Streaming Inserts
Streaming is essential when you have a use case that requires near real-time analytics.

- **Live Dashboards**: If you were upgrading your football dashboard to show live match statistics, you would stream the events (goals, fouls, passes) into BigQuery so the dashboard updates instantly.

- **System Monitoring**: Tracking application logs or website errors as they happen.

- **Fraud Detection**: Analyzing transactions the second a user swipes their credit card.

## The Trade-offs
While real-time data is powerful, streaming comes with a few catches:

- **Cost**: Batch loading data from Google Cloud Storage into BigQuery is generally free (you just pay for the storage). Streaming data, however, incurs a specific cost per GB of data streamed.

- **Complexity**: You have to handle potential network failures or API limits. If a stream fails, your application needs the logic to retry without accidentally inserting duplicate rows.

- **Buffer Time**: While the data is instantly queryable, it sits in a temporary streaming buffer for up to 90 minutes before being fully written to the underlying columnar storage. During this time, it cannot be exported, and it might not immediately respond to clustering optimizations.

# Oversharding Tables in BigQuery
To understand **oversharding**, we first need to quickly look at what "sharding" is.

Before BigQuery introduced native partitioning, the only way to manage large datasets was to create a brand new, separate table for every single day. They usually shared a prefix, like `sales_20260301`, `sales_20260302`, `sales_20260303`, and so on. This is called table sharding. To query them all at once, you would use a wildcard query like `SELECT * FROM mydataset.sales_*`.

**Oversharding** happens when you take this practice to the extreme and break your data down into way too many tiny tables—like creating a new table for every single hour, every single customer, or holding onto thousands of daily tables over many years.

## Why is Oversharding a Problem?
In a distributed system like BigQuery, oversharding causes a massive headache for a few key reasons:

- **Metadata Overload**: When you run a query against a natively partitioned table, BigQuery only has to read the schema and metadata for one table. When you query 500 sharded tables, BigQuery has to read the metadata and build an execution plan for 500 separate tables before it even starts looking at your data. This severely slows down query performance.

- **The Wildcard Limit**: BigQuery has a hard limit on wildcard queries. You can only reference a maximum of 1,000 tables in a single query. If you overshard, you will hit this wall and your queries will simply fail.

- **The "Small File" Problem**: Columnar databases like BigQuery are designed to read massive, continuous blocks of data. Reading thousands of tiny tables is incredibly inefficient and ruins the performance benefits of the platform.

## The Solution
The rule of thumb in modern BigQuery is almost always: Use native partitioning instead of sharding. Native partitioning manages all the data segregation under the hood within a single table, keeping your schemas clean, your metadata light, and completely avoiding the 1,000-table limit.

# JavaScript UDFs in BigQuery
UDF stands for User-Defined Function. While standard SQL is incredibly powerful for filtering, joining, and aggregating data, it is a declarative language—it's not always great at complex, step-by-step procedural logic.

JavaScript UDFs allow you to write custom functions using JavaScript directly inside your BigQuery environment, and then call those functions from your standard SQL queries just like you would a built-in function like `LOWER()` or `SUM()`.

## Why Use JavaScript UDFs? 
If you are building your ETL pipelines and run into a transformation that SQL just can't handle elegantly, a JS UDF is usually the escape hatch. They are perfect for:

- **Complex Parsing**: If you have highly nested, messy JSON or custom string formats where standard SQL regex gets too complicated.
- **Procedural Logic**: When you need for loops, if/else chains, or try/catch error handling to clean a specific column row-by-row.
- **Reusing Existing Code**: You can actually point BigQuery to external JavaScript libraries stored in Google Cloud Storage. If your company already has a complex JS function for validating account numbers, you can import it and use it right in your SQL queries without rewriting it.

## How They Work
You can define a JS UDF in two ways:
- **Temporary**: Defined at the very top of your SQL script (using a `CREATE TEMP FUNCTION` statement) and only exists for the duration of that specific query.
- **Persistent**: Saved permanently in your BigQuery dataset so anyone on your team can call it in their own queries whenever they want.

## The Trade-offs
- **Performance Hit**: This is the biggest catch. Native SQL functions are heavily optimized and run natively in BigQuery's engine (C++). To run a JS UDF, BigQuery has to spin up a JavaScript V8 engine instance on its worker nodes, serialize the data, pass it to the JS engine, and then pass it back. This makes JS UDFs noticeably slower than native SQL.
- **Data Type Conversions**: You have to strictly map BigQuery SQL data types (like `INT64` or `TIMESTAMP`) to JavaScript data types (like `Number` or `Date`), which can sometimes lead to precision loss if you aren't careful.

# Approximate Aggregate Functions
Imagine you are trying to count the exact number of unique users who visited a massive website over the last year. If you have billions of rows of log data, finding the exact number of unique IP addresses requires BigQuery to keep track of every single IP it has seen so far in memory to check for duplicates. This is incredibly memory-intensive, slow, and expensive.

**Approximate aggregate** functions are BigQuery's solution to this problem. They trade a tiny bit of mathematical precision in exchange for a massive boost in query speed and a reduction in computing resources.

## How It Works
Instead of calculating the perfect answer, these functions use statistical algorithms (like `HyperLogLog++`) to estimate the result.

The most common example is `APPROX_COUNT_DISTINCT()`.

If you run `COUNT(DISTINCT user_id)`, BigQuery does the heavy lifting to give you the exact number.

If you run `APPROX_COUNT_DISTINCT(user_id)`, BigQuery gives you an estimate that is usually within 1% to 2% of the exact answer, but it returns the result in a fraction of the time.

## When to Use Them
You should reach for approximate functions when you are dealing with massive datasets (we're talking billions of rows) and directional accuracy is more important than absolute precision.

- **Good Use Case**: "Roughly how many unique visitors did our marketing campaign drive yesterday?" (If the answer is 1.5 million, being off by 10,000 doesn't change the business decision).

- **Bad Use Case**: "Exactly how many dollars do we owe our partners this month?" (You never want to approximate financial payouts!).

## Other Common Approximate Functions
Besides counting distinct values, BigQuery offers a few others:

- `APPROX_QUANTILES()`: Great for finding the median or percentiles of a massive dataset without sorting the entire thing.

- `APPROX_TOP_COUNT()`: Quickly finds the most frequent values in a column (like the top 10 most common error messages in a massive log table).

## How they work under the hood

To understand why they are so much faster, we have to look at the massive bottleneck that occurs when you try to calculate an exact number in a distributed system like BigQuery.

### The Bottleneck: Exact Aggregation
When you run a standard `COUNT(DISTINCT user_id)` on a table with billions of rows, BigQuery's worker nodes have to physically remember every single unique ID they encounter.

To ensure they don't double-count an ID that exists on two different nodes, the nodes have to send all these values to each other across the network to compare them. This is called data shuffling.

Holding billions of IDs in memory and shuffling them across the network requires a massive amount of RAM, computing power, and time.

### The Solution: Probabilistic Algorithms
Approximate functions completely bypass this memory and network bottleneck by using probabilistic data structures. For `APPROX_COUNT_DISTINCT`, BigQuery uses an algorithm called `HyperLogLog++`.

### Here is how it works under the hood:

- **Hashing**: Instead of storing the actual user_id, the algorithm passes the ID through a hash function, converting it into a long string of binary (0s and 1s).

- **Looking for Patterns**: The algorithm doesn't keep the hashes. It simply looks at the binary strings and counts the longest streak of leading zeros it sees.

- **The Probability Math**: Statistically speaking, a hash starting with one zero (like 0101...) is common (a 50% chance). A hash starting with five zeros (000001...) is rare. If the algorithm spots a hash with a huge number of leading zeros, mathematical probability dictates that it must be looking at a very large dataset to have hit that rare occurrence.

- **Merging States**: Because it only tracks these pattern occurrences, each worker node only needs a few kilobytes of memory. Instead of shuffling billions of rows, the nodes just send their tiny, kilobyte-sized summaries to a master node. The master node merges these summaries and runs a quick mathematical formula to estimate the total count.

### Why it's Lightning Fast
By trading exact counting for pattern-matching and probability, BigQuery reduces the memory requirement from gigabytes to kilobytes and nearly eliminates the need to shuffle data across its network.