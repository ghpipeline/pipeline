To authenticate to GCP, we mount a service account key stored in the repo at `secrets/gcp-key.json`. The key is passed into the container using an environment variable:

```
GOOGLE_APPLICATION_CREDENTIALS: /opt/airflow/secrets/gcp-key.json
```

Mounting is handled in `docker-compose.yml` and ensures Airflow tasks have secure access to GCP resources.

### Deployment

To build and run Airflow, we use:

```
docker compose down -v && docker compose up -d --build
```

DAGs can be triggered via:

```
docker exec -it airflow-project-airflow-webserver-1 airflow dags trigger <dag_id>
```

Or tested manually with:

```
docker exec -it airflow-project-airflow-webserver-1 airflow tasks test <dag_id> <task_id> <date>
```

To access the Airflow UI, visit:

```
http://<your-vm-external-ip>:8080
```

Note: The external IP for the VM is currently ephemeral. If needed, it can be converted to a static IP via the GCP console to ensure long-term access.
