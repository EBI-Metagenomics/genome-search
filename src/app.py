import hug

import search
import index


@hug.not_found()
def not_found_handler():
    return "Not Found"


@hug.extend_api(sub_command="index")
def extend_with():
    return (index,)


@hug.extend_api(sub_command="search")
def extend_with():
    return (search,)


if __name__ == "__main__":
    hug.API(__name__).cli()
