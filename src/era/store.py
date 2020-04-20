import os
import pickle

from typing import List, Any
from domain import Measurement
from config import completed_queue, scheduled_queue, data_dir


def save_state(filename: str, xs: List[Any]):
    # Create results directory if it does not exists.
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    pickle.dump(xs, open(filename, "wb"))


def load_state(filename: str) -> List[Any]:
    if os.path.isfile(filename):
        return pickle.load(open(filename, "rb"))
    return []


# TODO: Implement equality condition on Measurement dataclass
def update_queues(cmds: List[Measurement]):
    scheduled = load_state(scheduled_queue)
    completed = load_state(completed_queue)

    for c in cmds:
        if c.command() not in [x.command() for x in scheduled] and not c.mid:
            scheduled.append(c)
        elif c.mid not in [x.mid for x in completed]:
            completed.append(c)
        elif c.mid in [x.mid for x in completed]:
            idx = [x.mid for x in completed].index(c.mid)
            completed[idx].last_updated = c.last_updated

    save_state(completed_queue, completed)
    save_state(scheduled_queue, scheduled)


def get_scheduled_measurements() -> List[Measurement]:
    return load_state(scheduled_queue)


def get_completed_measurements() -> List[Measurement]:
    return load_state(completed_queue)
