import argparse

from domain import Measurement
from store import (get_completed_measurements,
                   get_scheduled_measurements,
                   save_state)

from config import (completed_queue, scheduled_queue)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-completed", action="store_true")
    parser.add_argument("--show-scheduled", action="store_true")
    parser.add_argument("--remove-completed", type=int)
    parser.add_argument("--remove-scheduled", type=int)
    parser.add_argument("--add-completed", type=int)
    args = parser.parse_args()

    if args.show_completed:
        [print(f"[{i}] - {c.mid}")
         for i, c in enumerate(get_completed_measurements())]

    if args.remove_completed:
        ms = get_completed_measurements()
        del ms[args.remove_completed]
        save_state(completed_queue, ms)

    if args.remove_scheduled:
        ms = get_scheduled_measurements()
        del ms[args.remove_scheduled]
        save_state(scheduled_queue, ms)

    if args.add_completed:
        ms = get_completed_measurements()
        save_state(completed_queue, ms +
                   [Measurement("", mid=args.add_completed)])


if __name__ == '__main__':
    main()
