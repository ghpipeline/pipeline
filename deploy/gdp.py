
import httpx
from prefect import flow
from prefect.runner.storage import GitRepository
from prefect.blocks.system import Secret

if __name__ == "__main__":
    # use a personal access token stored in Secret block to access private Rook repo
    flow.from_source(
        source=GitRepository(
            url="https://github.com/rookcap/prefect-legacy.git",
            credentials={"access_token": Secret.load("git-hub-access-token")}
        ),
        entrypoint="scripts/datapull.py:CORE_VALUES",
    ).deploy(
        name="CORE-VALUES",
        work_pool_name="gcp-cloud-run"
    )
