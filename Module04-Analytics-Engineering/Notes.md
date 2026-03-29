# What is Analytics Engineering

- **Data Engineer**: Prepares and maintains infrastructure the data team needs.
- **Data Analyst**: Uses data to answer questions and solve problems.
- **Analytics Engineer**: Introduces the good software engineering practices to the efforts of data analysts and data scientists

## Tools that Analytics Engineers may be exposed to

- **Data Storing**: Cloud data warehouses like Snowflake, BigQuery, Redshift, ...
- **Data Modeling**: dbt or Dataform
- **Data Presentation**: BI tools like Google Data Studio, Looker, Mode or Tableau.

## Data Modeling Concepts

### ETL VS ELT

- ETL Takes longer to implement because we have to transform the data, but also means slightly more stable and compliant data analysis but higher storage and compute costs
- ELT Offers Faster and more flexible data analysis, since data already loaded in the warehouse and also lower cost and lower maintenance. 

### Kimball's Dimensional Modeling

- **Objective**:
	- Deliver data understandable to the business users
	- Deliver fast query performance
- **Approach**: Prioritize user understand ability and query performance over non redundant data (3NF)

#### Elements of Dimensional Modeling

- **Fact Tables**:
	- Measurements, metrics or facts about our business
	- Corresponds to a business process
	- verbs
- **Dimension Tables**:
	- Corresponds to a business entity
	- Provides context to a business process
	- nouns
- This is called **Star Schema**.

#### Architecture of Dimensional Modeling (Kitchen Analogy)

- **Stage Area**: (Contains The food)
	- Contains the raw data
	- Not meant to be exposed to everyone
- **Processing Area**: (The kitchen)
	- From raw data to data models
	- Focuses in efficiency
	- Ensuring standards
- **Presentation Area**: (The Dining hall)
	- Final representation of the data
	- Exposure to business stakeholder

# What is dbt

**dbt** is a transformation workflow that allows anyone that knows SQL to deploy analytics code following software engineering best practices like modularity, portability, CI/CD, and documentation.

## How does dbt work?

- **Read**: We take the tables we want from our data warehouse which have the raw data and pull them into **Modeling Layer**.
- **Transform**: Inside the yellow Modeling Layer, We write logic that takes those raw tables, joins them, cleans them, or aggregates them to create a new, refined dataset. This resulting dataset, labeled **Derived Model**.
- **Write:** dbt automatically takes the result of your transformation and saves it back into your Data Warehouse as a brand-new table or view, ready for analytics or reporting.

## What is a Model

In dbt terminology, a "model" is just a single file that contains the logic to transform a specific piece of data:

- **It is a `*.sql` file:** You don't need to learn a complex new programming language; it's mostly standard SQL.
- **Select statement, no DDL or DML:** This is dbt's biggest superpower. You **only** write the `SELECT` query that shapes your data. You never have to write boilerplate code like `CREATE TABLE data_mart AS` or `INSERT INTO` (which are DDL/DML commands). dbt handles all of that creation and insertion logic behind the scenes.
- **dbt compiles and runs:** You write the code in your dbt project, and dbt translates it and executes it directly inside your Data Warehouse.

## How to use dbt?

### dbt Core

Open-source project that allows the data transformation.

- Builds and runs a dbt project (.sql and .yml files).
- Includes SQL compilation logic, macros and database adapters.
- Includes a CLI interface to run dbt commands locally

### dbt Cloud

SaaS application to develop and manage dbt projects.

- Web-based IDE and cloud CLI to develop, run and test a dbt project.
- Managed environments
- Jobs orchestration
- Logging and Alerting
- Integrated documentation
- Admin and metadata API
- Semantic Layer

## dbt Fusion

**dbt Fusion** is the brand-new, next-generation execution engine that powers dbt.

To understand why it exists, you have to look at the "legacy" version of dbt (which you have been learning in the Zoomcamp). Legacy dbt was built in **Python**. It essentially treated your SQL code as dumb text strings, used Jinja to stitch them together, and then sent them to your data warehouse. As companies scaled to thousands of models, Python became a massive performance bottleneck, taking minutes just to parse a project.

dbt Labs completely threw out that Python architecture and rebuilt the entire engine from scratch using **Rust**.

Here is why dbt Fusion is a massive game-changer for data engineers:

### 1. Blazing Fast Speed

Because Fusion is a compiled Rust binary, it is incredibly lightweight and fast. Parsing and compiling your DAG (Directed Acyclic Graph) is up to **30x faster**. Multi-minute waits drop down to mere milliseconds.

### 2. True SQL Comprehension

This is Fusion's biggest superpower. Legacy dbt didn't actually "know" SQL; it just passed text to BigQuery. Fusion natively reads and understands SQL syntax (using Abstract Syntax Trees). This means it can catch syntax errors, data type mismatches, and broken column references _locally on your machine_ before you ever spend a single cent running a broken query in the cloud.

### 3. Smart, Cost-Saving Orchestration

Because Fusion deeply understands your code, it introduces **Column-Level Lineage**. If you change a single column name in a staging model, Fusion knows exactly which downstream models actually use that specific column. During CI/CD runs, it will intelligently skip rebuilding any models that weren't impacted by your change, saving massive amounts of warehouse compute costs.

### 4. A Modern IDE Experience

Fusion acts as a Language Server Protocol (LSP). If you install the new official dbt VS Code extension in your Ubuntu environment, Fusion runs in the background. It gives you live autocompletion for models and macros, instant previews of your CTEs, and highlights errors with red squiggly lines as you type—just like a modern software engineering environment.

## What Are Environments in dbt?

In dbt, **environments** define different contexts where your data transformations run:

- **Development Environment**: Your personal workspace for building and testing models
    
    - Uses your personal credentials
    - Creates temporary schemas with your name (e.g., `dbt_<your_name>`)
    - Changes only affect your work, not production
    - Used when working in the dbt Cloud IDE
- **Deployment Environment**: The production workspace where final models run on schedule
    
    - Uses service account credentials
    - Creates production schemas (e.g., `dbt_prod_staging`, `dbt_prod_marts`)
    - Used by scheduled jobs that keep your data warehouse updated

Think of it like having a draft folder (development) and a published folder (deployment) for your analytics code.


# dbt Project Structure
```

taxi_rides_ny/
├── dbt_project.yml   <-- The Brain
├── models/           <-- The Muscle (Your SQL)
│   ├── staging/      
│   └── core/         
├── seeds/            <-- The Reference Data (CSVs)
├── macros/           <-- The Functions
├── snapshots/        <-- The Time Machine
├── tests/            <-- The Quality Control
└── analyses/         <-- The Scratchpad
```
### 1. The Core Configuration

- **`dbt_project.yml`:** This is the execution center of your project. It tells dbt the name of your project, which profile to use for the database connection (BigQuery), and exactly where to look for your models and macros. You will also configure global materialization settings (e.g., whether to build views or tables) in here.

### 2. The Big Three (Where you will spend 95% of your time)

- **`models/`:** This is where all your `.sql` files live. Every file in this folder represents one transformation (one `SELECT` statement).
    - **`staging/`:** For light cleaning and renaming of your raw data.
	- **`intermediate/`:** For more complex transformations that are still not quite ready for business users. This is where you might do some heavy lifting like joining multiple tables together or calculating new metrics.
		- Anything that is not raw nor you want to expose
		- No guidelines, just nice for heavy duty cleaning and transformations.
    - **`marts/`:** For your heavy joins, aggregations, and final fact/dimension tables.
		- If its in marts, its ready for consumption.
		- Tables read for dashboards
		- Properly modeled, clean Tables.
- **`seeds/`:** This folder is for static data, specifically `.csv` files. For example, the NY Taxi dataset uses location IDs (like `LocationID = 1`). You will upload a `taxi_zone_lookup.csv` into this folder, and dbt will automatically turn that CSV into a real BigQuery table so you can join it to your models to get the actual zone names.
	- Quick and dirty approach (better to fix at source)
- **`macros/`:** Think of these as custom functions. If you find yourself writing the exact same complex `CASE WHEN` statement in five different models, you can write it once using Jinja in the `macros` folder and simply call that function whenever you need it.
	- They behave like python function (reusable logic)
	- They help encapsulate logic in one place 

### 3. The Advanced Folders

- **`tests/`:** Where you define data quality assertions. You can write custom SQL to check for weird edge cases, or use built-in tests to ensure a specific column is `unique` and `not_null`.
	- A place to put assertions in SQL format
	- A place for single column tests (unique, not null, etc)
	- If this SQL returns any rows, dbt will fail the test and alert you that something is wrong with your data.
- **`snapshots/`:** Used for slowly changing dimensions (SCDs). If a record in your source data changes (like a user updating their address), snapshots allow dbt to keep a historical record of the old address rather than just overwriting it.
	- Useful to track the history of a column that overwrites itself
- **`analyses/`:** This is a scratchpad for analytical queries that you want dbt to compile, but _not_ actually materialize into BigQuery tables. It's mostly used for ad-hoc investigations.
	- A place for SQL files you dont want to expose
	- I generally use it for data quality reports


# dbt Sources

In dbt, a **source** is a way to define and manage your raw data tables that exist in your data warehouse. It serves as a bridge between your raw data and the transformations you will build in dbt.

we define sources in a `.yml` file, typically located in the `models/staging` directory. This YAML file describes where your raw data lives and what it looks like. For example, you might have a source definition that points to a BigQuery table containing your raw taxi trip data.

## Naming Conventions for Sources

- **Source Name**: This is a unique identifier for your source. It should be descriptive and follow a consistent naming convention. For example, if you are working with raw taxi trip data, you might name your source `raw_taxi_trips`.
- **Table Name**: This is the actual name of the table in your data warehouse. It should match exactly what exists in BigQuery. For example, if your raw data is stored in a table called `raw_data.green_taxi_trips`, your source definition would include that exact table name.

and for SQL files we name them according to which layer we are so if we in the staging layer we name the file `stg_green_taxi_trips.sql` and if we are in the marts layer we name it `mrt_green_taxi_trips.sql` and so on.

in SQL we use the `{{ source('source_name', 'table_name') }}` function to reference our sources. This tells dbt to pull data from the specified source when running our transformations. For example, if we have a source defined as `raw_taxi_trips` that points to the `raw_data.green_taxi_trips` table, we would use `{{ source('raw_taxi_trips', 'green_taxi_trips') }}` in our SQL code to access that raw data.

But thats only for the first layer (staging) after that we reference the previous layer so if we are in the intermediate layer we reference the staging layer and if we are in the marts layer we reference the intermediate layer and so on by using `{{ ref('model_name') }}` function. For example, if we have a staging model called `stg_green_taxi_trips`, we would use `{{ ref('stg_green_taxi_trips') }}` in our intermediate layer SQL code to reference the output of that staging model. This creates a dependency between the models, ensuring that dbt runs them in the correct order.

# dbt Models

We populate our three layers (staging, intermediate, marts) with dbt models. Each model is a `.sql` file that contains a `SELECT` statement to transform the data.

- **Staging Models**: These are your light cleaning and renaming models. They take the raw data from your sources and make it more user-friendly. For example, you might have a staging model called `stg_green_taxi_trips.sql` that selects from the raw source and renames columns to be more descriptive.
- **Intermediate Models**: These are for more complex transformations that are still not quite ready for business users. This is where you might do some heavy lifting like joining multiple tables together or calculating new metrics. For example, you might have an intermediate model called `int_taxi_trips.sql` unifies both green and yellow taxi trip data into a single table with additional calculated fields like trip duration or distance.
- **Marts Models**: These are your final fact and dimension tables that are ready for consumption by business users and dashboards. For example, you might have a mart model called `mrt_taxi_trips.sql` that aggregates the data to show total trips, revenue, and average trip duration by day and taxi type. Each model builds on the previous layer, creating a clear and organized transformation pipeline from raw data to final analytics-ready tables.

In seed we put the reference data that we want to use in our transformations, for example the `taxi_zone_lookup.csv` file that contains the mapping of location IDs to zone names. dbt will automatically create a table from this CSV file in BigQuery, allowing us to join it with our models to get more meaningful insights.

In macros we can write reusable logic that we want to use across multiple models. For example, if we have a complex `CASE WHEN` statement to determine the vendor name based on the `vendor_id`, we can write that logic once in a macro called `get_vendor_names.sql` and then call that macro in any model where we need to get the vendor name. This promotes code reusability and keeps our SQL files cleaner and more maintainable. We start the macro with `{% macro get_vendor_names(vendor_id) %}` and end it with `{% endmacro %}`. Inside the macro, we can write our SQL logic using Jinja templating to make it dynamic based on the input parameter `vendor_id`.

# dbt Documentation

dbt allows you to add documentation to your models, sources, and macros using YAML files. This documentation can include descriptions of what each model does, the purpose of each column, and any important notes for users. Once you have added this documentation, dbt can generate a user-friendly website that displays all of this information in an organized manner. This makes it easier for business users and other stakeholders to understand the data and how to use it effectively. The documentation site is automatically updated whenever you run `dbt docs generate`, ensuring that it always reflects the latest state of your project. And show the website by running `dbt docs serve` which will open the documentation in your browser.

We can document even single columns in our models to explain what they represent and how they should be used. This is especially helpful for business users who may not be familiar with the technical details of the data but need to understand its meaning and context to make informed decisions. By providing clear documentation, we can improve data literacy and empower users to leverage the data more effectively in their analyses and reporting.
	- Data type
	- Description
	- Example values

## metadata tags

- `PII`: Personally Identifiable Information. This tag indicates that the data contains sensitive information that can be used to identify an individual, such as names, email addresses, or social security numbers. Tagging a model or column with `PII` helps ensure that appropriate security measures are taken to protect this sensitive data and comply with privacy regulations.
- `Ownership`: This tag indicates who is responsible for the model or column. It can be used to assign ownership to specific team members or departments, making it clear who to contact for questions or issues related to that data. This promotes accountability and helps ensure that the data is well-maintained and accurate.
- `Importance`: This tag indicates the criticality of the model or column. It can be used to prioritize maintenance and monitoring efforts, with higher importance models receiving more attention to ensure they are always accurate and up-to-date. This helps teams focus their resources on the most crucial parts of their data infrastructure.
- `formatting`: This tag indicates the expected format of the data in a model or column. For example, it can specify that a date column should be in `YYYY-MM-DD` format or that a phone number should follow a specific pattern. This helps ensure data consistency and makes it easier for users to understand how to work with the data correctly.

For models we use schema.yml files to define the documentation and metadata for our models. This YAML file allows us to specify descriptions for the model itself, as well as for each individual column within the model. We can also add metadata tags to both the model and its columns to provide additional context and information about the data. This structured approach to documentation helps improve data literacy and makes it easier for users to understand and work with the data effectively.

Documentation process should be done with the business users, they are the ones who understand the data and its context the best, so involving them in the documentation process ensures that the information is accurate, relevant, and useful for those who will be consuming the data. By collaborating with business users, we can create documentation that truly meets their needs and helps them leverage the data more effectively in their analyses and decision-making.

# dbt Testing

## Singular Tests

Singular tests are custom SQL queries that you write to check for specific conditions in your data. For example, you might write a singular test to check for negative values in a column that should only contain positive numbers (like `trip_distance`). If the query returns any rows, it indicates that there is an issue with the data, and dbt will fail the test and alert you to investigate further. Singular tests are highly flexible and allow you to implement complex logic to validate your data according to your specific business rules and requirements.

## Source Freshness Tests

Source freshness tests are a specific type of test in dbt that checks how recently the data in your source tables has been updated. This is important because if your source data is stale (not updated for a long time), it can lead to inaccurate analyses and decisions based on outdated information. By configuring source freshness tests, you can set thresholds for how old the data can be before it is considered stale, and dbt will automatically check this each time you run your transformations. If the data exceeds the defined freshness threshold, dbt will fail the test and alert you to investigate the issue with the data source.

Example:

```yaml
sources:
  - name: raw_taxi_trips
	tables:
	  - name: green_taxi_trips
		freshness:
		  warn_after: {count: 1, period: day}
		  error_after: {count: 2, period: day}
```

## Generic Tests

Generic tests are reusable tests that you can apply to multiple models or columns in your dbt project. They are defined in a YAML file and can be used to check for common data quality issues such as uniqueness, non-null values, or referential integrity. For example, you can define a generic test to ensure that a specific column (like `trip_id`) is unique across all records. Once defined, you can easily apply this generic test to any model or column by referencing it in the model's schema.yml file. This promotes consistency and efficiency in testing across your entire data transformation pipeline.

Example:

```yaml
models:
  - name: stg_green_taxi_trips
	columns:
	  - name: trip_id
		tests:
		  - unique
		  - not_null
```

We can write our own custom generic tests using Jinja macros. For example, if we want to create a generic test to check for negative values in a column, we can define a macro that takes the column name as an argument and generates the appropriate SQL query to check for negative values. This allows us to easily reuse this logic across multiple models and columns without having to write the same SQL code repeatedly. By creating custom generic tests, we can ensure that our data quality checks are tailored to our specific business rules and requirements while still maintaining the flexibility and reusability of generic tests in dbt. This custome tests is placed inside the '`test/generic` folder. For example, we can create a file called `negative_values.sql` in the `tests/generic` folder with the following content:

```sql
{% test negative_values(model, column_name) %}
SELECT *
FROM {{ model }}
WHERE {{ column_name }} < 0
{% endtest %}
```

## Unit Tests

Unit tests are a type of test in dbt that focuses on validating the logic of individual transformations or models. They are designed to test specific pieces of code in isolation to ensure that they produce the expected results. For example, if you have a model that calculates the total revenue from taxi trips, you can write a unit test to check that the calculation is correct for a known set of input data. Unit tests help catch errors early in the development process and ensure that each component of your data transformation pipeline is functioning correctly before it is integrated with other components. By writing unit tests for your dbt models, you can improve the reliability and maintainability of your data transformations.

## Model Contracts

Model contracts are a way to define the expected structure and schema of your dbt models. They act as a contract between the model and its consumers, specifying what columns should be present, their data types, and any other relevant metadata. By defining model contracts, you can ensure that any changes to the model's structure are intentional and communicated to downstream users. This helps prevent breaking changes and ensures that consumers of the model can rely on a consistent schema when building their analyses and reports. Model contracts can be defined in the model's schema.yml file, where you can specify the expected columns, their data types, and any additional documentation or metadata for each column.

# dbt Packages

dbt packages are reusable collections of dbt models, macros, and tests that can be shared across multiple projects. They allow you to leverage the work of others and avoid reinventing the wheel for common transformations or analyses. For example, if there is a popular dbt package that provides pre-built models for calculating common metrics like customer lifetime value or churn rate, you can easily install that package into your project and use those models without having to write the SQL logic yourself. This promotes collaboration and efficiency within the dbt community, as users can share their work and benefit from the contributions of others. To use a dbt package, you typically add it as a dependency in your `packages.yml` file and then run `dbt deps` to install it into your project.

## Example Packages

- **dbt_utils**: This is the most popular dbt package that provides a wide range of utility macros and functions to simplify common transformations and analyses. It includes macros for things like generating surrogate keys, performing date calculations, and handling null values, among many others. By using dbt_utils, you can save time and reduce the amount of custom SQL you need to write for common tasks in your dbt project.

- **codegen**: This package provides macros that help generate SQL code dynamically based on your models and sources. It can be used to create more flexible and reusable transformations by allowing you to generate SQL snippets on the fly based on the structure of your data. For example, you can use code_gen to automatically generate `CASE WHEN` statements for handling different categories of data without having to write out each condition manually. This can be especially useful when dealing with large datasets or complex transformations that require dynamic SQL generation.

- **audit_helper**: This package provides macros and models to help with data auditing and quality checks. It includes pre-built tests and reports that can be used to monitor the health of your data and identify potential issues. For example, it might include models that calculate the number of null values in each column or the distribution of values in a specific field, allowing you to quickly identify anomalies or data quality problems. By using audit_helper, you can enhance your data monitoring capabilities and ensure that your data remains accurate and reliable over time.

- **dbt_expectations**: This package provides a set of macros that allow you to define expectations for your data. It helps you create more robust tests by allowing you to specify the expected distribution of values in a column, the expected range of values, or other statistical properties of your data. For example, you can use dbt_expectations to define an expectation that a certain column should have a mean value within a specific range, and then automatically generate tests to validate that expectation against your data. This can help you catch data quality issues that may not be immediately obvious through simple uniqueness or null checks, providing a deeper level of validation for your data transformations.

## Steps

1. Add the package to your `packages.yml` file with the appropriate version.
2. Run `dbt deps` to install the package and make its macros and models available in your project.
3. Reference the package's macros and models in your own dbt project as needed to leverage the functionality it provides. For example, you can call a macro from the package in your SQL files or use its pre-built models as part of your transformation pipeline. By following these steps, you can easily integrate dbt packages into your project and take advantage of the reusable code and functionality they offer, saving you time and effort in building your data transformations.


# dbt Commands

1. `dbt init`: Initializes a new dbt project in the current directory, creating the necessary folder structure and configuration files.
2. `db debug`: Provides detailed information about the dbt environment, including configuration settings, database connections, and other relevant details to help troubleshoot issues.
3. `dbt seed`: Loads CSV files from the `seeds/` directory into your data warehouse as tables, allowing you to use static reference data in your transformations.
4. `dbt snapshot`: Creates snapshots of your data to track changes over time, particularly useful for slowly changing dimensions (SCDs).
5. `dbt source freshness`: Checks the freshness of your source data against defined thresholds to ensure that your data is up-to-date.
6. `dbt docs generate`: Generates documentation for your dbt project based on the descriptions and metadata defined in your YAML files.
7. `dbt docs serve`: Serves the generated documentation on a local web server, allowing you to view it in your browser.
8. `dbt clean`: Removes all compiled SQL files and other artifacts from previous runs, giving you a clean slate for your next run.
9. `dbt compile`: Compiles your dbt models into executable SQL files without actually running them against the database. This allows you to review the generated SQL and catch any syntax errors before executing the transformations.
10. `dbt run`: Executes your dbt models against the database, creating or updating tables and views based on your SQL transformations.
11. `dbt test`: Runs the tests defined in your dbt project, including singular tests, generic tests, and source freshness tests, to validate the quality and integrity of your data.
12. `dbt build`: A comprehensive command that combines `dbt run`, `dbt test`, and `dbt seed` to execute your transformations and then immediately validate the results with your tests in a single step. This is often used in CI/CD pipelines to ensure that any changes to your dbt project are both executed and validated before being deployed to production.
13. `dbt retry`: Retries any failed models from the previous run, allowing you to quickly re-run only the models that encountered issues without having to execute the entire project again. This can save time and resources when dealing with transient errors or when you have a large project with many models.
14. `dbt -h` or `dbt --help`: Displays a help message with a list of available dbt commands and their descriptions, providing guidance on how to use the various features of dbt effectively. This is a useful command for both beginners and experienced users to quickly reference the available commands and their functionalities.
15. `dbt -v` or `dbt --version`: Displays the current version of dbt that you have installed, along with any relevant information about the environment and dependencies. This can be helpful for troubleshooting compatibility issues or ensuring that you are using the latest features and improvements in dbt.
16. `dbt --full-refresh`: When running `dbt run`, this flag forces dbt to drop and recreate all models, rather than just updating existing tables. This can be useful when you want to ensure that all data is refreshed from the source, but it should be used with caution as it can lead to longer execution times and increased costs if you have a large dataset.
17. `dbt run --fail-fast`: This flag tells dbt to stop execution immediately if any model fails during the run. This can be useful in CI/CD pipelines to prevent further processing and alert you to issues as soon as they occur, allowing for quicker debugging and resolution of problems in your dbt project.
18. `dbt run -t` or `dbt target`: This flag allows you to specify a particular target environment to run your dbt models against. For example, you might have different targets for development, staging, and production environments, and this flag lets you choose which one to execute against without having to change your profile configuration. This is especially useful for testing changes in a non-production environment before deploying them to production.
19. `dbt run --select`: This flag allows you to specify a subset of models to run based on various selection criteria. For example, you can select models by name, tag, or even by their position in the DAG (Directed Acyclic Graph). This is useful when you want to run only a specific part of your dbt project without having to execute the entire set of models, saving time and resources during development and testing. we can add + sign to include downstream dependencies and ~ sign to include upstream dependencies. For example, `dbt run --select stg_green_taxi_trips+` would run the `stg_green_taxi_trips` model along with all models that depend on it downstream, while `dbt run --select +stg_green_taxi_trips` would run the `stg_green_taxi_trips` model along with all models that it depends on upstream. This allows for flexible execution of specific parts of your dbt project based on your current needs and focus areas. We can also use `dbt run --select state:modified` to run only the models that have been modified since the last run, which is particularly useful during development to quickly test changes without having to run the entire project. This selection method helps improve efficiency and speed up the development process by targeting only the relevant models that have been updated.