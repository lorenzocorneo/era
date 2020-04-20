import os
from typing import List

keys: List[str] = []

data_dir = os.path.join(os.path.dirname(__file__), "data")

completed_queue = os.path.join(os.path.dirname(__file__),
                               "data/completed.pickle")
scheduled_queue = os.path.join(os.path.dirname(__file__),
                               "data/scheduled.pickle")

results_dir = os.path.join(os.path.dirname(__file__), "results")

probes_archive = os.path.join(os.path.dirname(__file__),
                              "dataset/20200309.json")
