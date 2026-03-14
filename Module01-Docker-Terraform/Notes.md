
# Docker

**Docker** is a tool that solves the classic programmer excuse: _"But it worked on my machine!"_

- It allows you to package an application with everything it needs to run (code, libraries, settings) into a single, lightweight unit called a **Container**.

**Analogy**: A Shipping Container

Before shipping containers existed, loading a ship was a nightmare. You had barrels, sacks, and boxes of different sizes. They were hard to stack, and sometimes the heavy stuff crushed the fragile stuff.

- **Before Docker:** You install Python on your laptop, then Postgres, then some libraries. If your friend has a different version of Python or a Mac instead of Windows, your code might break on their computer.
- **With Docker:** You put your code and tools inside a standardized "Container." You can hand that container to anyone—your friend, a server, or the cloud—and it will run exactly the same way, every single time.

**Key Concepts:** 

- **Image (The Blueprint):** Think of this as the "recipe" or a snapshot. It is a read-only file that contains the instructions to create a container (e.g., "I need a computer with Python 3.9 installed").
- **Container (The House):** This is the running instance of the Image. You can start, stop, and delete it. If the Image is the recipe, the Container is the actual cake you baked.
- **Dockerfile:** A simple text file where you write the instructions to build an Image (e.g., `FROM python:3.9`, `COPY . /app`, `RUN pip install pandas`).
- **Docker Compose:** A tool that lets you run _multiple_ containers at once.


- Containers is stateless whatever you install/write/do there you have to install again once you exit

Docker provides the following advantages:

- Reproducibility: Same environment everywhere
- Isolation: Applications run independently
- Portability: Run anywhere Docker is installed

## Docker File Syntax

|**Instruction**|**What it does**|**Example**|
|---|---|---|
|**`FROM`**|**The Base Layer.** Starts the build from a pre-existing image (like Python or Ubuntu). This is almost always the first line.|`FROM python:3.9`|
|**`WORKDIR`**|**The Folder.** Sets the working directory inside the container. Future commands will happen here. It's like doing `cd /app`.|`WORKDIR /app`|
|**`COPY`**|**The Transfer.** Copies files from your _local computer_ (host) into the _container_.|`COPY pipeline.py pipeline.py`|
|**`RUN`**|**The Build Action.** Runs a command _while the image is being built_. Used to install libraries.|`RUN pip install pandas`|
|**`ENV`**|**The Variables.** Sets environment variables that persist when the container runs.|`ENV PORT=8080`|
|**`ENTRYPOINT`**|**The Main Event.** The command that runs when the container _starts_. It makes the container executable.|`ENTRYPOINT ["python", "pipeline.py"]`|
## Docker Syntax

- Install Ubuntu image
```bash
docker run ubuntu
```

- Run Ubuntu container
```bash
docker run -it ubuntu
```

- Install Python and run it
```bash
docker run -it python: 3.13.11 
```

```bash
docker run -it python: 3.13.11-slim
```
for smaller version

- Bash session with python
```bash
docker run -it --entrypoint=bash python: 3.13.11-slim
```

- To see all executed docker containers
```bash
docker ps -a
```

to see the ids of all containers

```bash
docker ps -aq
```

to remove all docker containers

```bash
docker rm 'docker ps -aq'
```

- Volumes: mapping data from host machine to docker container
```bash
docker run -it --entrypoint=bash -v $(pwd)/test:/app/test python:3.13.11
```
we specify the data on host machine first `$(pwd)/test:` then where we want to map it in the container `/app/test`

- we add `--rm` to not save the state of the container.

# Data Pipelines

 A **data pipeline** is a service that receives data as input and outputs more data. For example, reading a CSV file, transforming the data somehow and storing it as a table in a PostgreSQL database.

```mermaid

graph LR
    A[CSV File] --> B[Data Pipeline]
    B --> C[Parquet File]
    B --> D[PostgreSQL Database]
    B --> E[Data Warehouse]
    style B fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff

```

## Parquet

- **Apache Parquet** is a file format designed specifically for "Big Data."

If CSV is like a text file that a human can read, **Parquet is like a highly compressed zip file optimized for computers** to read very fast

- Parquet is Column-Oriented

## Virtual Environment 

**A Virtual Environment** is an isolated workspace for a Python project. Think of it as a "sandbox." Everything you do inside this sandbox stays inside it and does not affect your main computer or other projects.

- The Problem It Solves ("Dependency Hell")

Imagine you are working on two different projects:
- **Project A (Old):** Uses `pandas` version 1.0.
- **Project B (New):** Uses `pandas` version 2.0.

If you install packages directly on your laptop (global installation), you can only have **one** version of `pandas` at a time. Installing version 2.0 will break Project A.

With virtual environments, you create a separate folder for each project.

- **Env A** has Python + pandas 1.0
- **Env B** has Python + pandas 2.0

- we use `UV` tool to manage virtual environments
    - `uv` is an extremely fast, modern tool for managing Python projects, packages, and virtual environments. It is written in **Rust** (a very fast programming language).
    - Think of it as a turbo-charged replacement for both `pip` (the installer) and `venv` (the virtual environment creator) combined into one tool.
- Why is everyone talking about it?
	1. **Speed:** It is 10x–100x faster than `pip`. When you are installing heavy data engineering libraries (like Airflow, Pandas, or PyTorch), this speed difference is massive.
	2. **All-in-One:** Instead of using one tool to create the environment (`python -m venv`) and another to install packages (`pip`), `uv` does both.
	3. **Drop-in Replacement:** It is designed to work exactly like the tools you already know, so you don't have to relearn everything.

## Dockerizing the Pipeline

- we will make our own image with a dockerfile with the instructions we need in the image

- Let's build the image:

```shell
docker build -t test:pandas .
```

- The image name will be `test` and its tag will be `pandas`. If the tag isn't specified it will default to `latest`.

We can now run the container and pass an argument to it, so that our pipeline will receive it:

```shell
docker run -it test:pandas some_number
```

Instead of installing `uv` using a command like `pip install uv` (which requires downloading, compiling, and setting up), you are literally **copying the pre-made executable file** from another Docker image into yours.

Here is the breakdown of that single line:

 The Anatomy of the Command

`COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/`

1. **`COPY --from=...`**: Normal `COPY` takes files from your laptop. `COPY --from` takes files from **another Docker image** (the "Donor").
2. **`ghcr.io/astral-sh/uv:latest`**: This is the **Donor Image**. It is the official image created by the developers of `uv`. It contains a perfectly compiled, ready-to-run version of the tool.
3. **`/uv`**: This is the **File to Copy**. Inside that donor image, the actual program is located at `/uv`.
4. **`/bin/`**: This is the **Destination**. You are pasting it into the `/bin/` folder of _your_ image.
    - _Why `/bin`?_ Because Linux looks in this folder for commands. Placing it here means you can type `uv` from anywhere in your terminal, and it will work immediately.
        

 The Analogy

- **The "RUN pip install" way:** You buy flour, eggs, and sugar, then bake a cake inside your container.
- **The "COPY --from" way:** You go to the bakery next door, buy a finished cake, and bring it into your house.

## Running PostgreSQL with Docker

```bash
docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  postgres:18
```

- `-e` sets environment variables (user, password, database name)
- `-v ny_taxi_postgres_data:/var/lib/postgresql` creates a **named volume**
    - Docker manages this volume automatically
    - Data persists even after container is removed
    - Volume is stored in Docker's internal storage
- `-p 5432:5432` maps port 5432 from container to host
- `postgres:18` uses PostgreSQL version 18 (latest as of Dec 2025)

Once the container is running, we can log into our database with pgcli.

Install pgcli:

```shell
uv add --dev pgcli
```

The `--dev` flag marks this as a development dependency (not needed in production). It will be added to the `[dependency-groups]` section of `pyproject.toml` instead of the main `dependencies` section.

Now use it to connect to Postgres:

```shell
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
```

- pgcli runs on our machine
- `uv run` executes a command in the context of the virtual environment
- `-h` is the host. Since we're running locally we can use `localhost`.
- `-p` is the port.
- `-u` is the username.
- `-d` is the database name.
- The password is not provided; it will be requested after running the command. When prompted, enter the password: `root`

Basic SQL Commands try some SQL commands:

```sql
-- List tables
\dt

-- Create a test table
CREATE TABLE test (id INTEGER, name VARCHAR(50));

-- Insert data
INSERT INTO test VALUES (1, 'Hello Docker');

-- Query data
SELECT * FROM test;

-- Exit
\q
```

## NY Taxi Dataset and Data Ingestion

We will now create a Jupyter Notebook `notebook.ipynb` file which we will use to read a CSV file and export it to Postgres.

Setting up Jupyter:

```shell
uv add --dev jupyter
```

Let's create a Jupyter notebook to explore the data:

```shell
uv run jupyter notebook
```

### Ingesting Data into Postgres

In the Jupyter notebook, we create code to:

1. Download the CSV file
2. Read it in chunks with pandas
3. Convert datetime columns
4. Insert data into PostgreSQL using SQLAlchemy

 Install SQLAlchemy

```shell
uv add sqlalchemy psycopg2-binary
```

 Create Database Connection

```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
```

 Get DDL Schema

```python
print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))
```

- This line generates the **SQL `CREATE TABLE` statement** that matches your pandas DataFrame. It doesn't actually create the table in the database yet; it just **prints the SQL code** that _would_ create it.

Create the Table

```python
df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')
```

`head(n=0)` makes sure we only create the table, we don't add any data yet.

- We cant insert 1 million+ rows at once we will insert it in chunks of equal size.

```python
df_iter = pd.read_csv(
    prefix + 'yellow_tripdata_2021-01.csv.gz',
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000
)
```

Iterate Over Chunks

```python
for df_chunk in df_iter:
    print(len(df_chunk))
```

Inserting Data Chunk by Chunk

```python
df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
```

 Complete Ingestion Loop

```python
first = True

for df_chunk in df_iter:

    if first:
        # Create table schema (no data)
        df_chunk.head(0).to_sql(
            name="yellow_taxi_data",
            con=engine,
            if_exists="replace"
        )
        first = False
        print("Table created")

    # Insert chunk
    df_chunk.to_sql(
        name="yellow_taxi_data",
        con=engine,
        if_exists="append"
    )

    print("Inserted:", len(df_chunk))
```

Convert Notebook to Script

```shell
uv run jupyter nbconvert --to=script notebook.ipynb
mv notebook.py ingest_data.py
```

The script uses `click` for command-line argument parsing:

```python
import click

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    # Ingestion logic here
    pass
```

The script reads data in chunks (100,000 rows at a time) to handle large files efficiently without running out of memory.

Example usage:

```shell
uv run python ingest_data.py \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --target-table=yellow_taxi_trips
```

Run on docker

```shell
docker run -it --rm \taxi_ingest:v001 \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=localhost \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --table-name=yellow_taxi_trips
```

Create a private wifi network that our containers can use to talk to each other.

```shell
docker network create pg-network
```

then we add this network as a parameter for both containers in our example the postgres and ingestion script containers

new postgreSQL run

```shell
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql \
  -p 5432:5432 \
  --network=pg-network \
  --name pgdatabase \
  postgres:18
```

new ingestion script run

```shell
docker run -it --rm \
--network=pg-network \
  taxi_ingest:v001 \
  --pg-user=root \
  --pg-pass=root \
  --pg-host=pgdatabase \
  --pg-port=5432 \
  --pg-db=ny_taxi \
  --table-name=yellow_taxi_trips
```

## PostgreSQL PG Admin

`pgcli` is a handy tool but it's cumbersome to use for complex queries and database management. `pgAdmin` is a web-based tool that makes it more convenient to access and manage our databases.

It's possible to run pgAdmin as a container along with the Postgres container, but both containers will have to be in the same _virtual network_ so that they can find each other.

```shell
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
```

- Just like with the Postgres container, we specify a network and a name for pgAdmin.
- The container needs 2 environment variables: a login email and a password. We use `admin@admin.com` and `root` in this example.
- pgAdmin is a web app and its default port is 80; we map it to 8085 in our localhost to avoid any possible conflicts.
- The actual image name is `dpage/pgadmin4`.

## Docker Compose

`docker-compose` allows us to launch multiple containers using a single configuration file, so that we don't have to run multiple complex `docker run` commands separately.

- Docker compose makes use of YAML files.

```YAML
services:
  pgdatabase:
    image: postgres:18
    environment:
      POSTGRES_USER: "root"
      POSTGRES_PASSWORD: "root"
      POSTGRES_DB: "ny_taxi"
    volumes:
      - "ny_taxi_postgres_data:/var/lib/postgresql"
    ports:
      - "5432:5432"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: "admin@admin.com"
      PGADMIN_DEFAULT_PASSWORD: "root"
    volumes:
      - "pgadmin_data:/var/lib/pgadmin"
    ports:
      - "8085:80"

volumes:
  ny_taxi_postgres_data:
  pgadmin_data:
```

- We don't have to specify a network because `docker compose` takes care of it: every single container (or "service", as the file states) will run within the same network and will be able to find each other according to their names (`pgdatabase` and `pgadmin` in this example).
- All other details from the `docker run` commands (environment variables, volumes and ports) are mentioned accordingly in the file following YAML syntax.

We can now run Docker compose by running the following command from the same directory where `docker-compose.yaml` is found. Make sure that all previous containers aren't running anymore:

```shell
docker-compose up
```

If you want to run the containers again in the background rather than in the foreground (thus freeing up your terminal), you can run them in detached mode:

```shell
docker-compose up -d
```

You will have to press `Ctrl+C` in order to shut down the containers when running in foreground mode. The proper way of shutting them down is with this command:

```shell
docker-compose down
```

Other Useful Commands

```shell
# View logs
docker-compose logs

# Stop and remove volumes
docker-compose down -v
```

 Benefits of Docker Compose:

- Single command to start all services
- Automatic network creation
- Easy configuration management
- Declarative infrastructure

If you want to re-run the dockerized ingest script when you run Postgres and pgAdmin with `docker compose`, you will have to find the name of the virtual network that Docker compose created for the containers.

```shell
# check the network link:
docker network ls

# it's pipeline_default (or similar based on directory name)
# now run the script:
docker run -it --rm\
  --network=pipelines_default \
  taxi_ingest:v001 \
    --pg-user=root \
    --pg-pass=root \
    --pg-host=pgdatabase \
    --pg-port=5432 \
    --pg-db=ny_taxi \
    --table-name=yellow_taxi_trips_nov25 \
    --year=2025 \
    --month=november
```


# Google Cloud Platform (GCP)

**Google Cloud Platform** (GCP) is a suite of cloud computing services offered by Google. It runs on the same infrastructure that Google uses internally for its end-user products, such as Google Search, Gmail, and YouTube.

Instead of buying a physical server, putting it in a room, and installing software on it, you can "click a button" on GCP to get access to those resources instantly over the internet.

It provides services in several main categories:
- **Compute:** Renting virtual machines to run your code (e.g., **Google Compute Engine**).
- **Storage:** Storing files and data securely (e.g., **Google Cloud Storage**).
- **Databases:** Managing SQL and NoSQL databases without the headache of maintenance (e.g., **Cloud SQL**, **Firestore**).
- **Big Data & AI:** Analyzing massive datasets and building machine learning models (e.g., **BigQuery**, **Vertex AI**).

## Buckets

In Google Cloud Platform (GCP), a **bucket** is the fundamental container that holds your data within Google Cloud Storage (GCS).

The easiest way to think of a bucket is as a massive, infinitely scalable, top-level folder in the cloud where you dump your files.

Here is a breakdown of how it works and what makes it unique:

### Key Characteristics of a Bucket

- **It uses Object Storage:** Unlike the hard drive on your computer (which uses file/block storage), buckets use object storage. This means it stores "objects" (which are just your files, like CSVs, Parquet files, or images) bundled together with their metadata.
- **Names Must Be Globally Unique:** Much like a website domain name, a bucket name must be entirely unique across all of Google Cloud. If someone else in the world has already created a bucket named `my-test-bucket`, you cannot use that name.
- **It has a Flat Structure:** Buckets do not actually have real folders or sub-directories inside them. Even though the interface might show something like `my-bucket/data/2026/file.csv`, the `/data/2026/` part is just a prefix attached to the file's name to simulate a folder structure for human readability.
- **Objects are Immutable:** You cannot open a file sitting in a bucket, edit a single line of data, and save it. To make a change, you must overwrite the entire object with a new version.

### Why Data Engineers Use Them

In data engineering pipelines, a bucket usually serves as the **Data Lake** or "landing zone." It is the first place raw data gets dropped (often uploaded by tools like Apache Airflow) before it is cleaned, processed, and loaded into a Data Warehouse like BigQuery.
## Service Account

A **Service Account** is a special type of Google account intended to represent a **non-human user**—like a computer program, a virtual machine, or a tool like Terraform.

Think of it as an **ID badge for a robot**.

 1. Humans vs. Robots

	- **User Account (You):** You log in with an email and a password. You might use 2-Factor Authentication (phone/authenticator app).
	- **Service Account (Terraform):** Terraform cannot type a password or check a phone for a code. Instead, it uses a **Service Account** to prove its identity to Google.

2. How it works

Since a Service Account doesn't have a password, it uses a **Key**.

- **The Key File:** This is a JSON file (often named `my-key.json`) that acts like a digital passport.
- **The Workflow:**
    1. You create a Service Account in the GCP Console (e.g., named `terraform-runner`).
    2. Set the needed roles for it
    3. Generate a key
    4. You download the JSON key for that account.
    5. You give that key to Terraform.
    6. Terraform shows that key to Google and says, _"I am the terraform-runner robot. Let me in."_
# Terraform

open-source tool by HashiCorp, used for provisioning infrastructure resources
- supports DevOps best practices for change management
- Managing configuration files in source control to maintain an ideal provisioning state for testing and production environments

Terraform is an **Infrastructure as Code (IaC)** tool.

It lets you create, change, and destroy cloud infrastructure (like the GCP resources) by writing code instead of clicking buttons in a website console.

 - The Core Concept: "Blueprints"
Imagine you are building a house.

- **The Manual Way (Console):** You go to the site, lay bricks one by one, install windows, and paint walls. If you want to build a second identical house, you have to do it all over again manually, and you might forget a window.
- **The Terraform Way (IaC):** You draw a detailed **blueprint** (code). You give this blueprint to a robot (Terraform). The robot reads the plan and builds the house exactly as described. If you want a second house, you just tell the robot to run the blueprint again.

- Why Terraform?
	 - Simplicity in keeping track of infrastructure
	 - Easier collaboration
	 - Reproducibility
	 - Ensure recourses are removed
- What Terraform is not:
	- Does not manage and update code on infrastructure
	- Does not give you the ability to change immutable resources
	- Not used to manage resources not defined in your terraform files

- What are providers?
	  Code that allows terraform to communicate to manage resources on (AWS, Azure, GCP, Kubernetes, VSphere, ....)

## Key Terraform Commands

- `init` - Initializes & configures the backend, installs plugins/providers, & checks out an existing configuration from a version control
- `plan` - Matches/previews local changes against a remote state, and proposes an Execution Plan.
- `apply` -  Asks for approval to the proposed plan, and applies changes to cloud
- `destroy` - Removes your stack from the Cloud

- `fmt` - Formats Terraform file nicely

## Declarations

`main.tf` file:

```terraform
terraform {

  required_providers {

    google = {

      source  = "hashicorp/google"

      version = "7.16.0"

    }

  }

}


provider "google" {

  # Configuration options

  credentials = "./keys/my-creds.json"

  project = "scenic-dynamo-485615-f3"

  region  = "us-central1"

}
```
- `terraform`: configure basic Terraform settings to provision your infrastructure
    - `required_version`: minimum Terraform version to apply to your configuration
    - `backend`: stores Terraform's "state" snapshots, to map real-world resources to your configuration.
        - `local`: stores state file locally as `terraform.tfstate`
    - `required_providers`: specifies the providers required by the current module
- `provider`:
    - adds a set of resource types and/or data sources that Terraform can manage
    - The Terraform Registry is the main directory of publicly available providers from most major infrastructure platforms.
- `resource`
    - blocks to define components of your infrastructure
    - Project modules/resources: google_storage_bucket, google_bigquery_dataset, google_bigquery_table
- `variable` & `locals`
    - runtime arguments and constants

```terraform
resource "google_storage_bucket" "auto-expire" {

  name          = "auto-expiring-bucket"

  location      = "US"

  force_destroy = true

  

  lifecycle_rule {

    condition {

      age = 3

    }

    action {

      type = "Delete"

    }

  }


  lifecycle_rule {

    condition {

      age = 1

    }

    action {

      type = "AbortIncompleteMultipartUpload"

    }

  }

}
```

This Terraform code creates a **"Self-Cleaning" Google Cloud Storage Bucket**.

It is designed to be a temporary storage area that automatically deletes old files so you don't get charged for storage you forgot about.

Here is the line-by-line breakdown:

1. The Basics

Terraform

```
resource "google_storage_bucket" "auto-expire" {
  name          = "auto-expiring-bucket"
  location      = "US"
```

- **`resource`**: Tells Terraform to create something.
- **`name`**: The actual name of the bucket in Google Cloud. (Note: Bucket names must be globally unique across all of Google, so `"auto-expiring-bucket"` might already be taken by someone else!).
- **`location`**: Stores data in the US multi-region.

 2. The "Nuke" Option

Terraform

```
  force_destroy = true
```

- **What it does:** Normally, Terraform prevents you from destroying a bucket if it still has files inside (to prevent data loss).
- **Why it's here:** Setting this to `true` lets Terraform delete the bucket **even if it is not empty**. This is perfect for testing environments where you want `terraform destroy` to wipe everything clean instantly.


 3. Rule #1: Delete Old Files

Terraform

```
  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }
```

- **In Plain English:** "If a file has been in this bucket for **3 days**, delete it."
- **Use Case:** This ensures that temporary logs or test data don't pile up and cost you money forever.

 4. Rule #2: Clean Up Failed Uploads

Terraform

```
  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
```

- **The Problem:** When you upload a massive file (e.g., 10GB), Google splits it into small chunks. If your internet cuts out halfway, those chunks sit there, hidden, costing you money, but effectively useless because the file is "incomplete."
- **The Solution:** This rule finds those "ghost" chunks and deletes them if the upload hasn't finished within **1 day**.

 Summary

This code builds a **temporary sandbox bucket** that:

1. Deletes successful uploads after **3 days**.
2. Deletes failed/stuck uploads after **1 day**.
3. Allows Terraform to delete the whole bucket easily (`force_destroy`).

## State file

The **State File** (`terraform.tfstate`) is the most important file in Terraform. It is the "brain" that remembers what your infrastructure looks like in the real world.

Think of it as **Terraform's Diary**.

 1. What does it do?

When you write code to create a Google Cloud Bucket, Terraform creates it. But tomorrow, when you want to _change_ that bucket, Terraform needs to know:

- "Does this bucket already exist?"
- "What is its ID in Google's system?"
- "Did someone manually delete it while I was sleeping?"

The **State File** stores this mapping between your **Code** (resources in `main.tf`) and the **Real World** (actual GCP resources).

 2. Why is it critical?

Without the state file, Terraform has amnesia.

- **Scenario:** You create a VM. You lose the state file. You run `terraform apply` again.
- **Result:** Terraform thinks, "I don't remember creating a VM." It will try to create a **duplicate** VM (or fail because the name is taken). It won't know how to manage or delete the old one.

 3. The Golden Rules
4. **Never edit it manually:** It is a complex JSON file. If you break the syntax, Terraform breaks.
5. **Don't commit it to GitHub (Usually):**
    - For solo projects (like this course), it's okay to keep it local.
    - For teams, it contains sensitive info (like IP addresses or passwords). Teams store it remotely (e.g., in a GCS Bucket) so everyone shares the same "truth."

 Summary

The State File is how Terraform tracks the link between your code and reality. **Do not delete it.** If you delete `terraform.tfstate`, you lose control over your infrastructure.


- In BigQuery, a **Dataset** is the top-level container used to organize and control access to your tables and views. It sits between your Google Cloud "Project" and your actual "Tables." It acts very much like a **Schema** or **Database** does in systems like MySQL or PostgreSQL.

In Terraform, the `variables.tf` file is where you **define the input arguments** for your infrastructure code.

Think of your Terraform setup like a **function** in Python or Java.

- `main.tf` is the **code** inside the function (the logic).
- `variables.tf` is the **function signature** (the arguments it accepts).
- `terraform.tfvars` is where you actually **pass the values** when calling the function.

### Why do we need it?

Its main purpose is to prevent **hardcoding**.

If you are building a Google Cloud Storage bucket, you don't want to type `"my-project-id"` and `"US"` directly into the resource code every time. If you did, you would have to edit the code manually just to deploy the same infrastructure to a different project or region.

Instead, you use variables to make the code reusable.

### Real-World Example (GCP)

Since you are working with Google Cloud, here is how you would use it to make a storage bucket dynamic.

**1. Define the variable (`variables.tf`)** This tells Terraform: _"I expect a piece of data called `bucket_location`, and it must be a string."_

Terraform

```
variable "bucket_location" {
  description = "The geographic location of the bucket"
  type        = string
  default     = "US"
}

variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}
```

**2. Use the variable (`main.tf`)** Inside your actual logic, you reference the variable using `var.variable_name`.

Terraform

```
resource "google_storage_bucket" "my_data_lake" {
  name     = "dtc-data-lake-bucket"
  location = var.bucket_location  # <--- Injected here
  project  = var.project_id       # <--- Injected here
}
```

**3. Assign the value (`terraform.tfvars`)** This is the file usually ignored by git (added to `.gitignore`) where you put your secrets and specific settings.

Terraform

```
project_id      = "my-zoomcamp-project-2025"
bucket_location = "europe-west1"
```

### Summary of Files

- **`variables.tf`**: "Here are the inputs I accept." (The Definition)
- **`terraform.tfvars`**: "Here are the values for those inputs." (The Data)