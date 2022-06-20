from sanzan import *
import argparse


def main(args=None):
    parser = argparse.ArgumentParser(description="Encrypt or decrypt video files")

    ifile_group = parser.add_mutually_exclusive_group(required=True)
    ifile_group.add_argument("-e", "--encrypt", help="path of file to encrypt", type=str)
    ifile_group.add_argument("-d", "--decrypt", help="path of file to decrypt", type=str)

    parser.add_argument("-kv", "--videokey", help="path of video keyfile", type=str)
    parser.add_argument("-ka", "--audiokey", help="path of audio keyfile", type=str)
    parser.add_argument("-o", "--output", help="path of output file", type=str)
    parser.add_argument("-pw", "--password", help="password to encrypt or decrypt", type=str)
    parser.add_argument("-c", "--chunksize", help="audio chunksize", type=int)

    parser.add_argument("-p", "--preview", action="store_true", help="show real time preview of output")
    parser.add_argument("-s", "--silent", action="store_true", help="hide progress bar")
    parser.add_argument("-ex", "--export", action="store_true", help="export keyfiles")
    parser.add_argument("-na", "--noaudio", action="store_true", help="remove audio track")

    args = parser.parse_args(args)

    if not (args.output or args.preview):
        parser.error("no action specified, add -o or -p")

    if args.encrypt:
        x = Encryptor(args.encrypt, noaudio=args.noaudio)
        x.gen_key(args.videokey, args.password, args.export)
        x.gen_audio_key(args.password, args.chunksize, args.export)

    if args.decrypt:
        if not (args.videokey or args.password):
            parser.error("keyfile or password not specified, add -kv or -pw")

        x = Decryptor(args.decrypt, noaudio=args.noaudio)
        x.set_key(args.videokey, args.password)
        x.set_audio_key(args.audiokey, args.password, args.chunksize)

    if args.output:
        x.set_output(args.output)

    x.run(preview=args.preview, silent=args.silent)


if __name__ == "__main__":
    main()
