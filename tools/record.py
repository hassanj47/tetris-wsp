from .simulation import arguments, simulate, write_json


def main():
    parser = arguments("Record one self-contained game")
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    write_json(args.out, simulate(args, args.seed, True))


if __name__ == "__main__":
    main()
