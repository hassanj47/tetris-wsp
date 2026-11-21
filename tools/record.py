from .simulation import parser, simulate, write

def main():
    p=parser("Record a self-contained replay")
    p.add_argument("--seed",type=int,required=True)
    args=p.parse_args()
    _, replay=simulate(args,args.seed,True)
    write(args.out,replay)

if __name__=="__main__":
    main()
