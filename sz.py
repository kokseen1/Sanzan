from sanzan import *
import argparse

def main():
    parser = argparse.ArgumentParser(description="Connect to an Iro server")
    
    ifile_group = parser.add_mutually_exclusive_group(required=True)
    ifile_group.add_argument("-e", "--enc", help="path of file to encrypt", type=str)
    ifile_group.add_argument("-d", "--dec", help="path of file to decrypt", type=str)
    
    parser.add_argument("-k", "--key", help="path of key", type=str)
    parser.add_argument("-o", "--out", help="path of output file", type=str)
    
    parser.add_argument('-p', action='store_true')
    parser.add_argument('-s', action='store_true')

    args = parser.parse_args()
    if args.enc:
        x = Encryptor(args.enc)
        x.gen_key(args.key)

    if args.dec:
        x = Decryptor(args.dec)
        if args.key:
            x.set_key(args.key)

    if args.out:
        x.set_output(args.out)

    x.run(preview=args.p, silent=args.s)


if __name__ == "__main__":
    main()