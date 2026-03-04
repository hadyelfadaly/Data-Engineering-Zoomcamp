# 1. Start with the modern Airflow image
FROM apache/airflow:2.9.1

# 2. Switch to 'root' to install Google Cloud tools (The Easy Way)
USER root

# This single block replaces the 20 lines of "curl/tar/install.sh" in the screenshot
RUN apt-get update -qq && apt-get install -y -qq \
    apt-transport-https \
    ca-certificates \
    gnupg \
    curl \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update && apt-get install -y google-cloud-sdk

# 3. Switch back to 'airflow' user to install Python packages
USER airflow

# 4. Copy your requirements file
COPY requirements.txt .

# 5. Install uv and then install your requirements
RUN pip install uv && uv pip install --system --no-cache -r requirements.txt