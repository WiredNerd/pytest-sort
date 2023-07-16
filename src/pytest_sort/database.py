import os
from functools import wraps

from pony.orm import Database, OperationalError, PrimaryKey, Required, db_session

database_file = os.path.join(os.getcwd(), ".pytest_sort")
db = Database()



class TestTab(db.Entity):
    nodeid = PrimaryKey(str)
    setup = Required(int, size=64)
    call = Required(int, size=64)
    teardown = Required(int, size=64)
    total = Required(int, size=64)


def _init_db(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not db.provider:
            db.bind(provider='sqlite', filename=database_file, create_db=True)
            try:
                db.generate_mapping(create_tables=True)
            except OperationalError:
                db.drop_all_tables(with_all_data=True)
                db.schema = None  # Pony will only rebuild build tables if this is None
                db.generate_mapping(create_tables=True)
        return f(*args, **kwargs)

    return wrapper


@_init_db
@db_session
def update_test_case(nodeid: str, setup=0, call=0, teardown=0):
    test: TestTab = TestTab.get(nodeid=nodeid)
    if not test:
        TestTab(nodeid=nodeid, setup=setup, call=call, teardown=teardown, total=setup + call + teardown)
    else:
        if (test.setup < setup):
            test.setup = setup
        if (test.call < call):
            test.call = call
        if (test.teardown < teardown):
            test.teardown = teardown
        total = test.setup + test.call + test.teardown
        if (test.total < total):
            test.total = total


@_init_db
@db_session
def get_total(nodeid: str):
    test: TestTab = TestTab.get(nodeid=nodeid)
    if not test:
        return 0
    return test.total
