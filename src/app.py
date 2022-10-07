import json
import logging

import hug

import search
import index

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@hug.not_found()
def not_found_handler():
    return "Not Found"


@hug.extend_api(sub_command="index")
def extend_with():
    return (index,)


@hug.extend_api(sub_command="search")
def extend_with():
    return (search,)


def lambda_handler(event, context):
    logger.info(event)
    query = json.loads(event["body"])
    search_args = search.search.__code__.co_varnames
    results = search.search(**{arg: val for arg, val in query if arg in search_args})
    return json.dumps(results)


if __name__ == "__main__":
    hug.API(__name__).cli()
