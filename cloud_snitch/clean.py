"""Quick module for running snitchers.

Expect this to change into something configured by yaml.
Snitchers will also probably become python entry points.
"""
import logging
import shutil
import time

from cloud_snitch import runs
from cloud_snitch.cli_common import base_parser

logger = logging.getLogger(__name__)


def main():
    # Parse args.
    parser = base_parser(
        description='Removes stale run data that have already synced.'
    )
    args = parser.parse_args()

    start = time.time()
    foundruns = runs.find_runs()
    cleaned = 0
    for run in foundruns:
        if run.synced is not None:
            logger.info("Cleaning {}".format(run.path))
            shutil.rmtree(run.path)
            cleaned += 1
    logger.info(
        "Cleaned {} runs in {:.3f} seconds"
        .format(cleaned, time.time() - start)
    )


if __name__ == '__main__':
    main()
