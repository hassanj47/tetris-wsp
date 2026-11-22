from .cohorts import validate_seeds
from .simulation import arguments, simulate, write_json


def main():
    parser = arguments("Record one self-contained game")
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    try:
        validate_seeds(args.cohort, [args.seed])
    except ValueError as exc:
        parser.error(str(exc))
    write_json(args.out, {**simulate(args, args.seed, True), "cohort": args.cohort})


if __name__ == "__main__":
    main()
