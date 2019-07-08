import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.pool import NullPool
import datetime
import sys


logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] : %(message)s'
)
logger = logging.getLogger()


class ProjectRunner:

    def __init__(
        self,
        configuration: dict,
        from_step: int = 1,
        to_step: int = None
    ):
        self.configuration = configuration
        self.from_step_index = from_step - 1
        self.to_step_index = \
            len(configuration["order"]) - 1 if to_step is None else to_step - 1

        if self.from_step_index > self.to_step_index:
            raise Exception('Start step must be lower or equal the final step')

    def run_project(self) -> None:
        self.starting_logs()

        start = datetime.now()
        connection = create_connection(self.configuration["connection_url"])
        for i, query in enumerate(self.configuration["order"]):

            # we skip the queries out of index
            if i < self.from_step_index or i > self.to_step_index:
                continue

            # we run the query and monitor the time it takes
            query_start = datetime.now()
            rendered_query = self.configuration["queries"][query]
            logger.info(f"Now running '{query}'...")

            connection.execute(rendered_query)

            query_end = datetime.now()
            timing = str(query_end - query_start)
            logger.info(f"Query '{query}' successfully executed in {timing}.")

        end = datetime.now()
        self.ending_logs(start, end)

    def starting_logs(self):
        logger.info("---------------------------------------")
        logger.info("               _  __ _                 ")
        logger.info("              | |/ _| |                ")
        logger.info("     ___  __ _| | |_| | _____      __  ")
        logger.info("    / __|/ _` | |  _| |/ _ \ \ /\ / /  ")
        logger.info("    \__ \ (_| | | | | | (_) \ V  V /   ")
        logger.info("    |___/\__, |_|_| |_|\___/ \_/\_/    ")
        logger.info("            | |                        ")
        logger.info("            |_|                        ")
        logger.info("---------------------------------------")
        logger.info('')
        logger.info('')
        logger.info(
            f"Starting project \"{self.configuration['project_name'].upper()}\""
            f" for connection \"{self.configuration['connection_name'].upper()}\""
            f"\n\n"
        )
        logger.info(f"Variables: {self.configuration['context']}")

        queries = list()
        for i, query in enumerate(self.configuration["order"]):
            if i < self.from_step_index or i > self.to_step_index:
                continue
            queries.append(query)

        logger.info("\n\n\nRunning the following queries:"
                    "\n\t" + "\n\t".join(queries))

    def ending_logs(self, start, end):
        logger.info(f"Project '{self.configuration['project_name']}' "
                    f"successfully completed for database "
                    f"'{self.configuration['connection_name']}'")
        logger.info(f"Project completed in {end - start}")


def create_connection(connection_url: str) -> Connection:
    engine = create_engine(
        connection_url,
        poolclass=NullPool,
        isolation_level="AUTOCOMMIT"
    )
    connection = engine.connect()
    return connection


if __name__ == '__main__':
    project_config = {
        "order": ["1.sql", "2.sql", "3.sql", "4.sql", "5.sql", "6.sql"],
        "project_name": "Super project",
        "connection_name": "wl",
        "context": {"vars": {"something": 1}, "envs": {"whatever": 2}}
    }
    runner = ProjectRunner(configuration=project_config)
    runner.starting_logs()
