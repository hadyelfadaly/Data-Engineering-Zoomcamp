# Why we need orchestration tools?

That is the classic Data Engineer interview question: **"Why do I need a complex tool like Airflow when I could just write a Python script and put it on a Cron job?"**

For a simple project, a script is actually faster. But in a production environment (like a company or this course), scripts are a "trap" that will eventually hurt you.

Here are the 4 main reasons why "just writing a script" fails in Data Engineering:

### 1. The "Retry" Nightmare

- **Script:** You write a script to download data. The API blips for 1 second. Your script crashes. You have to manually wake up, check the logs, and run it again.
- **Airflow:** You set `retries=3`. If the API blips, Airflow waits 5 minutes and tries again automatically. You sleep through the night.

### 2. Dependency Hell (The "DAG" Advantage)

- **Script:** Imagine you have 3 steps: `Download` -> `Clean` -> `Upload`.
    - If `Download` fails, you don't want `Clean` to run.
    - In a script, you end up writing complex "Spaghetti Code" with nested `if/else` statements to manage this logic.
- **Airflow:** It understands **dependencies**. You just say `task_A >> task_B`. Airflow guarantees `task_B` will _never_ start unless `task_A` succeeded. If `task_A` fails, everything downstream pauses safely.

### 3. The "Time Machine" (Backfilling)

- **Script:** Your boss says, "Hey, we changed the logic. Can you re-run this for the past 24 months?"
    - In a script, you have to write a `for` loop, manually calculate dates, and pray it doesn't crash halfway through.
- **Airflow:** You simply clear the status of the past runs in the UI, and Airflow treats the past as if it's happening _now_. It spins up 24 workers and re-processes the last 2 years of data in parallel. This is the **Backfilling** superpower.
### 4. Visibility (The "Green Wall")

- **Script:** To see if your job worked, you have to SSH into a server and `cat` a log file.
- **Airflow:** You get a dashboard. You can see at a glance: "Yesterday worked (Green), Today failed (Red)."

### **Summary**

- **Scripts** are for **Tasks** (doing one thing).
- **Airflow** is for **Workflows** (managing the relationship between tasks, time, and failure).

Since you are learning to be a Data Engineer, you are learning to manage **Reliability**, not just code execution. That is why you use Airflow.

# Data Workflow

A data workflow is the **end-to-end journey of data** as it moves through a system. It is a defined sequence of steps that dictates how data is collected, processed, and delivered to a destination where it provides value.

Think of it like a **manufacturing assembly line**: raw materials (raw data) enter at one end, pass through various stations where they are modified and assembled (transformation), and a finished product (clean, usable data) exits at the other end.

Here are the standard stages of a data workflow, specifically mapped to what you are doing in the Data Engineering Zoomcamp:

### 1. Ingestion (Extract)

This is the "Gathering" phase. You pull raw data from various sources into your system.

- **Goal:** Get the data out of the wild and into your environment.
- **Zoomcamp Example:** Your Python code downloading the `yellow_tripdata_2021-01.csv` file from a GitHub URL or NYC government website.

### 2. Transformation (Transform)

This is the "Cleaning" phase. Raw data is often messy (wrong formats, duplicates, null values). You write logic to fix it.

- **Goal:** Make the data reliable and structured.
- **Zoomcamp Example:** Converting the `tpep_pickup_datetime` column from a confusing "String" of text into a proper "Timestamp" object, or removing taxi rides with `passenger_count` of 0.

### 3. Loading (Load)

This is the "Delivery" phase. You put the clean data into a storage system where it can be used.

- **Goal:** Store the data for the long term.
- **Zoomcamp Example:** Uploading your processed Parquet file to a **Google Cloud Storage (GCS)** bucket (your Data Lake) and then moving it into **BigQuery** (your Data Warehouse).

### 4. Orchestration (The Manager)

This is the most critical part—the "Brain" that controls the workflow. It ensures the steps happen in the correct order and handles problems.

- **Goal:** Automation and Reliability.
- **Zoomcamp Example:** **Airflow** (or Kestra). It triggers the Ingestion task at 6:00 AM. It waits for it to finish. If it succeeds, it starts the Transformation task. If Ingestion fails (e.g., the website is down), it retries 3 times and then sends you an alert.

### Why do we call it a "Workflow" and not just "a script"?

A script runs from top to bottom and usually crashes if something breaks. A **Workflow** is engineered to be:

- **Dependent:** Step B strictly waits for Step A.
- **Idempotent:** You can run the same workflow 5 times, and it won't duplicate data; it will just produce the same correct result.
- **Observable:** You can see exactly which step failed and why.

# DAG

In the world of Airflow and Data Engineering, **DAG** stands for **Directed Acyclic Graph**.

It sounds like a complex math term, but it is actually the most accurate way to describe a data pipeline.

Here is the breakdown of the three words:

### 1. Directed (One-Way Street)

The workflow moves in **one specific direction**.

- **Concept:** Task A must happen _before_ Task B. The data flows downstream, never upstream.
- **Example:** You must _Download_ the file before you can _Upload_ it. You cannot upload a file you haven't downloaded yet.

### 2. Acyclic (No Infinite Loops)

The workflow **never loops back** to the beginning.

- **Concept:** "Acyclic" literally means "without a cycle." Once a task is finished, it is done. You never see a flow like `A -> B -> C -> A`.
- **Why it matters:** If your pipeline had a cycle, it would run forever and never finish. A DAG guarantees that the pipeline has a clear start and a clear finish line.

### 3. Graph ( The Map)

In computer science, a "Graph" is just a fancy word for a network of nodes (dots) connected by lines.

- **Nodes:** The actual tasks (e.g., `download_data`, `upload_to_gcs`).
- **Edges:** The lines connecting them that represent dependency (the `>>` arrow in Python).

### **In Summary**

When you write a "DAG" in Airflow, you are drawing a map that tells the system:

_"Start here, move to this step next, then split into parallel steps here, and finish there. And whatever you do, **don't go in circles**."_

## Operators

In Airflow, an **Operator** represents a single, specific task inside your DAG.

- **What it does:** The `BashOperator` allows you to execute standard Linux terminal commands right from your pipeline.
- **How you will use it:** In the data ingestion pipeline you are building, this is typically used as the very first step to download the raw dataset from the web using command-line tools like `wget` or `curl`.

- Syntax:
```Python
wget_task = BashOperator(
        task_id="wget",
        bash_command=f'curl -sSL {URL_TEMPLATE} > {OUTPUT_FILE_TEMPLATE}'
    )
```

 `from airflow.operators.python import PythonOperator`

- **What it does:** This operator allows you to trigger and execute a specific Python function as a step in your pipeline.
- **How you will use it:** Once the `BashOperator` finishes downloading the raw data, the next step in your DAG will likely be a `PythonOperator`. This operator will trigger the Python code you write to read that file with Pandas, format it, and push it up into your Google Cloud Storage bucket.

- Syntax:
```Python
ingest_task = PythonOperator(
        task_id="ingest",
        python_callable=run,
        op_kwargs={}
    )
```

- `op_kwargs`: are used to pass parameters of the function we are calling.

We can use cron expressions to specify our DAG schedule if we don't want the normal (@daily, @monthly, ....), we can use crontab.guru website for this 

We use `curl -sS or -sSL` to download file via bash operator
 - **`curl`**: This is the standard command-line tool used to transfer data to or from a server. It is most commonly used to download files from the internet or make requests to APIs.
 - **`-s` (Silent mode)**: This tells `curl` to shut up. By default, `curl` prints a constantly updating progress bar and transfer statistics to your terminal. In automated tools like Airflow or Docker, this progress bar creates a massive, messy wall of text in your logs. The `-s` flag hides all of that.
- **`-S` (Show error)**: This is the safety net. When you use the silent flag (`-s`), `curl` suppresses _everything_, including error messages if a download fails. Adding the capital `-S` modifies the silent behavior, telling `curl`: _"Keep the progress bar hidden, but if something actually breaks or fails, make sure you print the error message so I can debug it."_
- ding the `-L` flag tells `curl`: _"If the server tells you the file has moved to a new location, automatically follow the new link and keep following them until you hit the actual file."_

To prevent this from happening again, you can add the `-f` (or `--fail`) flag to your `curl` command.

If you run `curl -sSLf`, it tells `curl` to immediately crash and fail the Airflow task if the server returns an error (like a 403 Access Denied or 404 Not Found), rather than quietly saving the error message into a dummy CSV file.

## Ingestion

We can either ingest by python operator or docker operators

### The PythonOperator (The Standard Workhorse)

This operator runs your Python function directly inside the Airflow worker's environment.

- **The Pros:** It is incredibly fast to write, test, and execute. You do not have to build a new Docker image every time you change a line of code. It is also very easy to pass small pieces of metadata between tasks using Airflow's built-in XCom system.
- **The Cons:** Dependency hell. If Task A needs `pandas==1.5` to process legacy data, but Task B needs `pandas==2.2`, they will clash because they are sharing the exact same Airflow worker environment. Also, if your Python script runs out of memory (like trying to load a 10GB CSV), it can crash the entire Airflow worker process.
- **Best for:** Standard ETL scripts, API calls, and pipelines where all tasks share the same basic Python libraries (which is exactly what you are doing right now).

### The DockerOperator (The Production Sandbox)

This operator tells Airflow to spin up a brand-new, isolated Docker container, run a specific script inside it, and then destroy the container when it finishes.

- **The Pros:** Total isolation. Task A and Task B can have completely different operating systems, Python versions, and libraries without ever conflicting. It is also language-agnostic; you can have a pipeline where one task runs Python, the next runs a Rust binary, and the last runs a Node.js script. If a task crashes, the Airflow worker remains perfectly safe.
- **The Cons:** It is slower because Airflow has to spin up a new container for every task. It is also much harder to pass data between tasks, as the container is destroyed immediately after execution.
- **Best for:** Enterprise production environments, highly complex data science models, or teams where different data engineers write scripts in different languages.

### The "Docker-in-Docker" Trap

There is a massive catch to be aware of right now. Because your entire Airflow environment is _already_ running inside Docker containers (via that `docker-compose.yaml` file), using the `DockerOperator` means you are asking a Docker container to spawn another Docker container.

This is called "Docker-in-Docker" (DinD). It requires mounting the host machine's Docker socket (`/var/run/docker.sock`) into the Airflow worker container, which can be a massive headache to configure securely and often causes permission errors on Linux/WSL.

## Implicit vs Explicit

In Airflow, what you are referring to as the "implicit" way is called the **TaskFlow API** (using `@dag` and `@task` decorators), while the "explicit" way is the **Traditional Method** (defining Operators and using `>>` bitshift arrows).

There is a fierce debate in the data engineering community about which is better. Here is the candid reality of both, and which one you should use for this specific NYC Taxi project.

### 1. The "Implicit" Way (TaskFlow API)

This is the newer, modern way Airflow encourages. You write standard Python functions, put `@task` above them, and Airflow _implicitly_ figures out the dependencies based on how you pass the variables.

Python

```
@task
def download_data():
    return "file.parquet"

@task
def upload_to_gcp(file_name):
    print(f"Uploading {file_name}")

# Airflow implicitly knows upload runs AFTER download
file = download_data()
upload_to_gcp(file)
```

- **The Pros:** It looks incredibly clean. You don't have to write boilerplate code, and passing data between tasks feels like normal Python.
- **The Fatal Trap for Data Engineers:** By default, when a `@task` returns a value, Airflow uses a system called XCom to save that value inside its internal PostgreSQL metadata database. If you use TaskFlow to return a massive Pandas DataFrame of NYC Taxi data, **Airflow will try to shove a 100MB file into a tiny database cell and instantly crash your entire cluster.**

## Syntax

```Python
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# 1. Define the Default Arguments (The rules every task inherits)
default_args = {
    "owner": "airflow",
    "start_date": datetime(2021, 1, 1),
    "depends_on_past": False, # If yesterday's run failed, should today's run still start?
    "retries": 1,             # How many times to retry a failed task
    "retry_delay": timedelta(minutes=5), # How long to wait before retrying
}

# 2. Open the Context Manager to define the DAG
with DAG(
    dag_id="my_general_template_dag", # The name you see in the UI
    schedule_interval="@monthly",     # How often it runs (e.g., "0 6 2 * *", "@daily")
    default_args=default_args,        # Plugging in the dictionary from step 1
    catchup=False,                    # Stop it from running historical dates instantly
    max_active_runs=1,                # Prevent concurrent overlaps
    tags=['template', 'learning'],    # UI filters
) as dag:

    # 3. Define your Tasks
    task_one = BashOperator(
        task_id="download_something",
        bash_command="echo 'Downloading file...'"
    )

    task_two = PythonOperator(
        task_id="process_data",
        python_callable=lambda: print("Processing the file...")
    )

    task_three = BashOperator(
        task_id="cleanup",
        bash_command="echo 'Deleting the file...'"
    )

    # 4. Set the Execution Order (The Dependencies)
    task_one >> task_two >> task_three
```

- **`default_args` (The Inheritance Dictionary):** Think of this as the genetic code passed down to every task in your pipeline. Instead of typing `owner='hady'`, `retries=3`, and `retry_delay=timedelta(minutes=5)` on every single `BashOperator` or `PythonOperator`, you put them in one dictionary at the top of your file. When you pass that dictionary into `default_args=default_args`, every task automatically inherits those rules. It saves you from writing repetitive code.
- **`max_active_runs` (The Traffic Cop):** This is a massive safety net, especially when dealing with heavy data! If you set `max_active_runs=1`, you are telling Airflow: _"Never, ever let two instances of this specific DAG run at the exact same time."_ If Monday's run is taking longer than expected and Tuesday's run gets triggered, Tuesday will sit politely in the queue until Monday completely finishes. This prevents your pipeline from accidentally launching multiple massive downloads at once and crashing your server's RAM or disk space (which we know all too well!).
- **`tags` (The UI Filter):** This is purely visual metadata. When you eventually have 50 different DAGs running in your Airflow environment, the UI becomes a mess. By adding `tags=['dtc-de']` (DataTalksClub Data Engineering), a little blue pill-shaped tag will appear next to your DAG in the Airflow dashboard. You can click that tag to instantly filter your view to only show pipelines related to your course.

To understand `depends_on_past`, you have to understand the difference between dependencies **inside** a single run, and dependencies **across** time.

- When you use `>>` (like `download_task >> upload_task`), you are telling Airflow: _"Inside this specific month's run, do not upload until the download finishes."_
- When you use `depends_on_past`, you are telling Airflow how to handle the **exact same task** across **different days or months**.

Here is how it changes your pipeline's behavior:

#### Scenario A: `depends_on_past = False` (The Independent Slices)

If you set this to `False`, every single DAG run is treated as a completely independent universe.

**Example:** You have a pipeline scheduled to run for January, February, and March.

- January's run starts, but the `download_task` fails because the website is down.
- When February rolls around, Airflow says: _"I don't care that January failed. I am going to try and run February's download anyway."_

**When to use this:** This is perfect for the NYC Taxi dataset! January's taxi data has absolutely nothing to do with February's taxi data. If you miss a month, you still want the rest of your pipeline to keep working and fetching the latest data.

#### Scenario B: `depends_on_past = True` (The Domino Effect)

If you set this to `True`, a task will **refuse to run** unless the exact same task from the _previous_ schedule interval succeeded.

**Example:** * January's `download_task` fails.

- When February is supposed to start, February's `download_task` will look at January, see the failure, and go into a state called `upstream_failed` (or just wait indefinitely). It will not even attempt to run. March will then wait for February, creating a massive traffic jam.

**When to use this:** You use this for **cumulative data**. Imagine you are writing a pipeline to calculate a daily running total of a bank account. You _cannot_ calculate Tuesday's total balance if Monday's pipeline failed to calculate Monday's balance. Tuesday strictly depends on Monday's success.
### 2. The "Explicit" Way (Traditional Operators) 

- This is what you built in your local ingestion file. You define explicit operators (`BashOperator`, `PythonOperator`) and physically draw the map using bitshift operators (`wget_task >> format_task >> upload_task`).
- **The Pros:** It creates absolute, rigid boundaries. It forces you to save the massive taxi file to the hard drive, and then the next task reads it from the hard drive. It protects Airflow's internal brain from getting crushed by data. It is also much easier to read when you are mixing different systems (like a Bash script, a Python script, and a Google Cloud command).
- **The Cons:** It requires more typing and looks a bit chunkier.

### The Verdict for Your GCP Pipeline

For this specific pipeline, **the Explicit / Traditional way is significantly better.**

Here is why: your DAG is a hybrid. You are using `curl` (Bash) to download the data, Pandas (Python) to format it, and Google Cloud Storage (GCS) to host it. Mixing `@task` decorators with `BashOperators` often results in messy, confusing code. Using the explicit `>>` arrows gives you a highly visual, bulletproof map of exactly how the pipeline flows.

Later on, when you write DAGs that _only_ execute tiny SQL commands or API triggers, the implicit TaskFlow API is king. But for heavy data lifting, stick to the explicit map.

## Pyarrow vs pandas

### 1. Cutting Out the Heavy "Middleman"

To understand why PyArrow is better here, you have to look at what Pandas actually does under the hood. Pandas cannot natively write Parquet files. When you call `df.to_parquet()`, Pandas is secretly just handing the data over to PyArrow to do the actual writing anyway!

- **The Pandas Route:** CSV -> Load into a Pandas DataFrame -> Convert to PyArrow Table -> Save as Parquet.
- **The PyArrow Route:** CSV -> Load into PyArrow Table -> Save as Parquet.

By using PyArrow directly, you skip the step of building a heavy, full-featured Pandas DataFrame.

### 2. The RAM Bloat (Avoiding Docker Crashes)

This is a classic memory management optimization you'd encounter in computer science architecture. Pandas is notoriously memory-hungry. When Pandas reads a 100MB CSV file, it can easily balloon to take up 400MB to 500MB of RAM because of how it allocates memory for strings and objects.

If you are running this inside a constrained Docker container (like your Airflow worker), a large dataset will instantly cause an Out Of Memory (OOM) crash. PyArrow is written in highly optimized C++ and uses a memory-mapped columnar format that is significantly lighter and faster.

### 3. The "NaN" Integer Trap

Pandas has a historical, frustrating quirk with data types. If you have a column of integers (like `passenger_count`), but a few rows have missing data (NaN), Pandas will automatically convert that entire column into `float64` decimals because its older backend couldn't handle missing integers.

Apache Arrow and Apache Parquet are sister projects. PyArrow understands Parquet's strict schema requirements perfectly and will safely preserve your nullable integers without silently altering your data types.

---

In short: Pandas is for _analyzing and manipulating_ data. PyArrow is for _moving and formatting_ massive amounts of data efficiently. Since this specific function's only job is format conversion, PyArrow is the right tool for the job.

# Airflow Architecture

This is the official **Airflow Architecture Diagram**. It shows how the different "organs" of the Airflow body work together to keep your data pipelines alive.

![Airflow Architecture](Imgs/Pasted%20image%2020260303030128.png)

Here is the breakdown of each component using a simple "Restaurant Kitchen" analogy to make it stick:

### 1. The DAG Directory (The Recipe Book)

- **What it is:** This is the folder on your computer (or server) where your Python files live (the code you wrote).
- **Role:** It holds the blueprints. Airflow reads these files to know _what_ tasks exist, _when_ to run them, and _in what order_.
### 2. The Scheduler (The Head Chef)

- **What it is:** The most critical component. It is a process that runs permanently in the background.
- **Role:** It monitors time and the "Recipe Book.
    - It checks the clock: _"Is it 6:00 AM? Yes."_
    - It checks the dependencies: _"Did the download finish? Yes."_
    - **Action:** When it's time, it creates a "Task Instance" and hands it to the **Executor**.

### 3. The Executor (The Sous-Chef / Dispatcher)

- **What it is:** Shown inside the Scheduler box because it is tightly connected.
- **Role:** It decides _how_ and _where_ the work gets done.
    - In a simple setup (LocalExecutor), it runs the task on the same machine.
    - In a complex setup (Celery/Kubernetes), it sends the task to a different computer (Worker) to execute.

### 4. The Workers (The Line Cooks)

- **What it is:** The actual computers or processes that execute your code.
- **Role:** They do the heavy lifting. They take the "order" from the Executor, run your Python script (download data, process data), and then report back: _"I'm done!"_ or _"I burned the steak (Failed)!"_

### 5. The Metadata Database (The Order Ticket System)

- **What it is:** A database (usually Postgres or MySQL).
- **Role:** It is the **Memory** of Airflow. It stores the state of everything.
    - _"Task A ran yesterday at 5:00 PM and succeeded."_
    - _"Task B is currently running."_
    - The Scheduler and Webserver constantly read from and write to this database to stay in sync.

### 6. TheWebserver & UI (The Dining Room / Menu)

- **What it is:** The visual interface you see in your browser (localhost:8080)
- **Role:** It allows you to inspect the kitchen. You can check logs, trigger runs manually, and see if tasks are green (success) or red (failed). It fetches all this info from the **Metadata Database**.

### 7. Other Components

- `redis`: Message broker that forwards messages from scheduler to worker.
- `flower`: The flower app for monitoring the environment. It is available at [http://localhost:5555](http://localhost:5555/).
- `airflow-init`: initialization service (customized as per this design)

---

### **How a Task Runs (The Flow in the Diagram)**

1. **You** write a Python file and put it in the **DAG Directory**.
2. The **Scheduler** reads the file and sees a task scheduled for now.
3. The **Scheduler** updates the **Database**: _"Task scheduled."_
4. The **Executor** grabs the task and sends it to a **Worker**.
5. The **Worker** runs your code.
6. The **Worker** tells the **Database**: _"I finished successfully."_
7. The **Webserver** reads the **Database** and turns the box **Green** in your browser.

# Project Structure:

- `./dags` - `DAG_FOLDER` for DAG files (use `./dags_local` for the local ingestion DAG)
- `./logs` - contains logs from task execution and scheduler.
- `./plugins` - for custom plugins

## Workflow components

- `DAG`: Directed acyclic graph, specifies the dependencies between a set of tasks with explicit execution order, and has a beginning as well as an end. (Hence, “acyclic”)
    - `DAG Structure`: DAG Definition, Tasks (eg. Operators), Task Dependencies (control flow: `>>` or `<<` )
- `Task`: a defined unit of work (aka, operators in Airflow). The Tasks themselves describe what to do, be it fetching data, running analysis, triggering other systems, or more.
    - Common Types: Operators (used in this workshop), Sensors, TaskFlow decorators
    - Sub-classes of Airflow's BaseOperator
- `DAG Run`: individual execution/run of a DAG
    - scheduled or triggered
- `Task Instance`: an individual run of a single task. Task instances also have an indicative state, which could be “running”, “success”, “failed”, “skipped”, “up for retry”, etc.
    - Ideally, a task should flow from `none`, to `scheduled`, to `queued`, to `running`, and finally to `success`.


# Airflow Setup

1. Create a new sub-directory called `airflow` in your `project` dir (such as the one we're currently in)
2. **Set the Airflow user**:
    
    On Linux, the quick-start needs to know your host user-id and needs to have group id set to 0. Otherwise the files created in `dags`, `logs` and `plugins` will be created with root user. You have to make sure to configure them for the docker-compose:
    
```shell
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env
```
3. **Import the official docker setup file** from the latest Airflow version:
```shell
curl -LfO 'https://airflow.apache.org/docs/apacheairflow/stable/dockercompose.yaml'
```
4. It could be overwhelming to see a lot of services in here. But this is only a quick-start template, and as you proceed you'll figure out which unused services can be removed.
5. **Docker Build**:
    When you want to run Airflow locally, you might want to use an extended image, containing some additional dependencies - for example you might add new python packages, or upgrade airflow providers to a later version.
    Create a `Dockerfile` pointing to Airflow version you've just downloaded, such as `apache/airflow:2.2.3`, as the base image,
    And customize this `Dockerfile` by:
    - Adding your custom packages to be installed. The one we'll need the most is `gcloud` to connect with the GCS bucket/Data Lake.
    - Also, integrating `requirements.txt` to install libraries via `pip install`
6. **Docker Compose**:
    Back in your `docker-compose.yaml`:
    - In `x-airflow-common`:
        - Remove the `image` tag, to replace it with your `build` from your Dockerfile
        - Mount your `google_credentials` in `volumes` section as read-only
        - Set environment variables: `GCP_PROJECT_ID`, `GCP_GCS_BUCKET`, `GOOGLE_APPLICATION_CREDENTIALS` & `AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT`, as per your config.
    - Change `AIRFLOW__CORE__LOAD_EXAMPLES` to `false` (optional)

## Execution

1. Build the image (only first-time, or when there's any change in the `Dockerfile`, takes ~15 mins for the first-time):
```shell
docker compose build
```
2. Initialize the Airflow scheduler, DB, and other config
```shell
docker-compose up airflow-init
```
3. Kick up the all the services from the container:
```shell
docker-compose up
```
4. In another terminal, run `docker-compose ps` to see which containers are up & running (there should be 7, matching with the services in your docker-compose file).
5. Login to Airflow web UI on `localhost:8080` with default creds: `airflow/airflow`
6. Run your DAG on the Web Console.
7. On finishing your run or to shut down the container/s:
```shell
docker-compose down
```
To stop and delete containers, delete volumes with database data, and download images, run:
```shell
docker-compose down --volumes --rmi all
```
or
```shell
docker-compose down --volumes --remove-orphans
```

[Airflow Setup with Docker, customized](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2022/week_2_data_ingestion/airflow/2_setup_nofrills.md) This is a quick, simple & less memory-intensive setup of Airflow that works on a LocalExecutor.
### Execution

1. Stop and delete containers, delete volumes with database data, & downloaded images (from the previous setup):  `docker-compose down --volumes --rmi all` or `docker-compose down --volumes --remove-orphans` Or, if you need to clear your system of any pre-cached Docker issues: `docker system prune` Also, empty the airflow `logs` directory.
2. Build the image (only first-time, or when there's any change in the `Dockerfile`): Takes ~5-10 mins for the first-time `shell docker-compose build`  or (for legacy versions) `shell docker build .`
3. Kick up the all the services from the container (no need to specially initialize): `shell docker-compose -f docker-compose-nofrills.yml up`
4. In another terminal, run `docker ps` to see which containers are up & running (there should be 3, matching with the services in your docker-compose file).
5. Login to Airflow web UI on `localhost:8080` with creds: `admin/admin` (explicit creation of admin user was required)
6. Run your DAG on the Web Console.
7. On finishing your run or to shut down the container/s: `shell docker-compose down`


- **Changed `docker-compose.yaml`?** Just run `docker-compose up -d`. It will automatically compare the new file to the currently running setup and recreate only the containers affected by your changes.
- **Changed `Dockerfile` or `requirements.txt`?** You must run `docker-compose build` to bake those new tools into the image, and _then_ run `docker-compose up -d`.

# Data Lake

**Data Lake** is a simple repository that holds big data from many sources, the data can be structured, semi-structured and unstructured.

- The idea is to ingest data as quickly as possible and make it available to other team member (Data Scientist, Data Analysts, ....)
- Data Lake is being used extensively for machine learning as well as analytical solutions
- We add some sort of metadata for faster access.
- It has to be secure and can scale.
- Hardware should be inexpensive

## Data Lake vs Data Warehouse

|**Feature**|**Data Lake**|**Data Warehouse**|
|---|---|---|
|**Data Type**|Unstructured|Structured|
|**Primary Users**|Data Scientists, Data Analysts|Business Analysts|
|**Use Cases**|Stream Processing, Machine Learning, Real-time analysis|Batch Processing, BI, Reporting|
|**Processing State**|**Raw:** Contains unstructured, semi-structured, and structured data with minimal processing. Fits unconventional data like log and sensor data.|**Refined:** Contains highly structured data that is cleaned, pre-processed, and refined for very specific use cases like BI.|
|**Volume & Storage**|**Large:** Holds petabytes of data. Data can be stored indefinitely in any form/size and transformed only when needed.|**Smaller:** Holds terabytes of data. Requires processing before ingestion and periodic purging to maintain cleanliness and health.|
|**Structure & Application**|**Undefined:** Used for a wide variety of applications like Machine Learning, Streaming analytics, and AI.|**Relational:** Contains historic and relational data, such as transaction systems and operations.|

## How did it start?

- Companies realized the value of data
- Store and access data quickly
- Cannot always define structure of data
- Usefulness of data being realized later in the project lifecycle
- Increase in data scientists
- R&D on data projects
- Need for Cheap storage of big data

## ETL VS ELT

- ETL is mainly used for a small amount of data whereas ELT is used for large amounts of data
- ELT provides data lake support (Schema on read)
- ETL must have well defined schema and relationships (Schema on Write)

## Limitations of Data Lake

- Can be converted into Data Swamp, that can make it really hard to be useful for end users. Reasons for this is:
	- No versioning (does not keep a historical record of changes made to it)
	- Incompatible schemas for same data without versioning
	- No metadata associated
	- Joins not possible

## Cloud Providers for Data Lake

- GCP - Cloud Storage
- AWS - S3
- Azure - Azure Blob

# Idempotency

**Idempotency** is arguably the most important golden rule in data engineering.

At its core, an **idempotent** operation means that no matter how many times you execute a task, the final state of your system is exactly the same as if you had only executed it once.

Here is exactly what that means for workflow orchestration and why Airflow relies on it so heavily.
### The Non-Idempotent Nightmare

Imagine your DAG successfully downloads the NYC Taxi CSV and your Python task starts pushing those 1.3 million rows into Postgres.

- It gets to row 600,000, and suddenly your Docker container runs out of memory and crashes.
- You fix the memory limit and click "Clear" in the Airflow UI to restart the ingestion task.
- If your pipeline is **non-idempotent**, it will blindly start inserting the 1.3 million rows all over again from the beginning. You now have 1.9 million rows in your database, including 600,000 duplicates. Your data lake is officially polluted.
### The Idempotent Solution

If your pipeline is **idempotent**, Airflow can crash, restart, backfill, or retry a task 50 times, and you will never end up with duplicate data or a broken state.

You actually achieve idempotency through the code you write inside your tasks. It usually involves writing logic that strictly defines the state or "cleans up" before it inserts:

- **In your Bash Download Task:** When you run `curl ... > output_2024-03.csv.gz`, the `>` operator completely overwrites any existing file with that exact name. If you run that task 100 times, you still only have exactly one file. That task is naturally idempotent!
- **In your Python Ingest Task:** When pushing data to Postgres, an idempotent script won't just blindly `INSERT`. It will first run a SQL command like `DELETE FROM yellow_taxi_data WHERE month = '2024-03'`, or use Pandas' `if_exists='replace'`, wiping the slate clean for that specific run before it starts chunking the new data in.

Because Airflow is designed to constantly retry failed tasks and backfill missing historical dates, it fundamentally assumes that every script you give it is idempotent.

# Ingestion Into GCP

- **Download:** `curl` downloads the `.csv.gz` file (same as before).
- **Format (New):** Convert the CSV into a Parquet file. GCP heavily prefers Parquet for cost and performance.
- **Data Lake (New):** Upload the Parquet file into your Google Cloud Storage (GCS) bucket (`my-unique-zoomcamp-nyc-taxi-data-bucket-998877`).
- **Data Warehouse (New):** Tell Google BigQuery in your `scenic-dynamo-485615-f3` project to create a table reading from that bucket.

## Upload in Chunks

```
storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024
storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024
```

This is a brilliant defensive coding tactic. If you try to upload a massive 100MB file in one single continuous stream, any tiny dip in your internet connection will cause the entire upload to fail and start over from zero.

By hardcoding these limits, you are forcing the Google Cloud library to use **Multipart Upload**. It takes your Parquet file, silently chops it into 5MB chunks ($5 \times 1024 \times 1024$ bytes), and uploads them one by one. If chunk #14 fails due to a network hiccup, it only retries chunk #14, saving you from constant timeout errors.

## Medallion Architecture

```Python
upload_bucket = PythonOperator(

        task_id="upload_to_gcs",
        python_callable=upload_to_gcs,
        op_kwargs=dict(
            bucket_name=BUCKET_NAME,
            object_name=f"raw/{parquet_file}",
            local_file=OUTPUT_FILE_TEMPLATE.replace('.csv.gz', '.parquet')
        )
    )
```

That little `raw/` string might look like a simple file path, but it actually represents the foundation of modern Data Lake architecture!

When you add `raw/` to the front of your `object_name`, you are telling Google Cloud Storage to create a folder named **"raw"** inside your bucket and put the Parquet file inside of it.

Here is exactly why data engineers do this, rather than just dumping everything into the main bucket.

### 1. The "Medallion" Data Lake Architecture

In professional environments, data is separated into different "zones" based on how clean it is. This is often called the Medallion Architecture:

- **Raw (Bronze Zone):** This is exactly what you downloaded. It is untouched, unedited, and might have errors or weird formatting. We dump it in the `raw/` folder first. If we ever mess up our data cleaning later, we can always come back to this folder to get the original file.
- **Processed/Staged (Silver Zone):** Later, you might write another pipeline that reads from the `raw/` folder, removes null values, fixes data types, and saves the cleaned file into a new `processed/` folder.
- **Curated (Gold Zone):** The final, highly aggregated business data ready for dashboards.

By putting your taxi data into a `raw/` folder right now, you are future-proofing your bucket so it doesn't become a disorganized mess of files.

### 2. The Google Cloud "Folder" Illusion

There is a fun technical secret here: **Folders do not actually exist in Google Cloud Storage.** Object storage (like GCS and Amazon S3) is entirely flat. When you pass `raw/output_2021-01.parquet` to the upload function, Google Cloud literally just names the file exactly that whole string.

However, when you look at it in the Google Cloud browser UI, Google sees the `/` slash and kindly draws a little folder icon named "raw" to make it easier for human brains to navigate.

## From Data Lake to BigQuery

```Python
```

To understand what this does, you have to understand the magic of an **External Table**.

### What is an External Table?

Normally, when you put data into a database, the database physically copies that data onto its own internal hard drives.

An **External Table** is different. It is essentially a "ghost table" or a window. BigQuery doesn't actually copy or store a single byte of this taxi data. Instead, it acts as a magnifying glass looking directly at the Parquet file sitting in your GCS bucket.

When you run a SQL query like `SELECT * FROM external_table`, BigQuery reaches out to your GCS bucket on the fly, reads the Parquet file, and hands you the results.

### Why do Data Engineers do this?

1. **Cost Savings:** Storage in BigQuery is more expensive than storage in GCS. By keeping the massive files in GCS and just querying them externally, you save money.
2. **Speed of Access:** You don't have to wait for a massive ingestion job to copy millions of rows into BigQuery. The moment the file lands in the bucket, it is instantly queryable.

### The Code Breakdown

Here is exactly what you are telling the Google API to do with that JSON-like dictionary:

- **`tableReference` (The Address):** This tells BigQuery _where_ to put this ghost table. It uses your `PROJECT_ID`, drops it into the `BIGQUERY_DATASET` (e.g., `trips_data_all`) that you built earlier, and names the table exactly `"external_table"`.
- **`externalDataConfiguration` (The Map):** This is the instruction manual for BigQuery.
    - `"sourceFormat": "PARQUET"` tells BigQuery exactly how to read the file so it can automatically detect the columns and data types without you having to define a rigid schema manually.
    - `"sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"]` is the exact GPS coordinate of your file. Notice it uses `gs://` (Google Storage) instead of `https://`. This is Google's internal network routing.

### The Full Pipeline Flow

If you put all the pieces together, your Airflow DAG now does this:

1. Downloads the CSV from the internet to your local Docker container.
2. Converts that CSV into a highly optimized Parquet file.
3. Uploads that Parquet file into your GCS `raw/` folder.
4. Tells BigQuery to create a permanent window looking at that exact file so you can write SQL against it.