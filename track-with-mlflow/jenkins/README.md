# Pipelines

CI (jenkins, github-action):
  - run_unit_tests_on_pr + run_sonar_on_pr (Python CI Pipeline Jenkins)

CD (jenkins, github-action):
  - databricks workflow deploy + update + delete (Databricks V2 Pipeline (replaces the original v1))
    - databricks UI manual run
    - databricks API automated triggers
    - databricks Workflow Scheduler
  - databricks job trigger pipeline (shared for workspace to be created after databricks v2 pipline late 2024)
    - runs the job using databricks API
    - monitors the created job and outputs logs to jenkins logs


CI + CD:
  - mlflow project run
    - checkout code
    - run_unit_tests_on_pr + run_sonar_on_pr
    - ensure test passes
    - run the project using backend config provided
