from sanzan import *
import argparse


def main():
    parser = argparse.ArgumentParser(description="Encrypt or decrypt video files")

    ifile_group = parser.add_mutually_exclusive_group(required=True)
    ifile_group.add_argument("-e", "--enc", help="path of file to encrypt", type=str)
    ifile_group.add_argument("-d", "--dec", help="path of file to decrypt", type=str)

    parser.add_argument("-k", "--key", help="path of keyfile", type=str)
    parser.add_argument("-o", "--out", help="path of output file", type=str)

    parser.add_argument("-p", action="store_true")
    parser.add_argument("-s", action="store_true")

    args = parser.parse_args()

    if not (args.out or args.p):
        parser.error("no action specified, add -o or -p")

    if args.enc:
        x = Encryptor(args.enc)
        x.gen_key(args.key)

    if args.dec:
        if not args.key:
            parser.error("path of keyfile not specified with -k")

        x = Decryptor(args.dec)
        x.set_key(args.key)

    if args.out:
        x.set_output(args.out)

    x.run(preview=args.p, silent=args.s)


if __name__ == "__main__":
    main()
