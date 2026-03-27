# What Are Environments in dbt?

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