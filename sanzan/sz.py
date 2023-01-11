import argparse

from .audio import DEFAULT_AUDIO_FORMAT
from .video import DEFAULT_SCRAMBLE
from .sanzan import Sanzan, DEFAULT_MODE


def main(args=None):
    parser = argparse.ArgumentParser(description="Sanzan")

    parser.add_argument("input", type=str)

    modes = parser.add_mutually_exclusive_group(required=True)

    modes.add_argument("-e", "--encrypt", action="store_true")
    modes.add_argument("-d", "--decrypt", action="store_true")

    parser.add_argument("-k", "--key", type=str)
    parser.add_argument("-o", "--output", type=str)

    parser.add_argument("-m", "--mode", type=str, default=DEFAULT_MODE)
    parser.add_argument("-a", "--audio_format", type=str, default=DEFAULT_AUDIO_FORMAT)
    parser.add_argument("-s", "--scramble", type=str, default=DEFAULT_SCRAMBLE)

    parser.add_argument("-l", "--light", action="store_true")
    parser.add_argument("-dn", "--denoise", action="store_true")
    parser.add_argument("-f", "--per_frame", action="store_true")
    parser.add_argument("-p", "--preview", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")

    parser.add_argument("-pp", "--padding", action="store_false", help="Disable audio padding")

    args = parser.parse_args()

    s = Sanzan(args.input, args.mode)
    if args.key:
        s.set_password(args.key)
    if args.encrypt:
        s.encrypt(args.output, args.scramble, args.preview, args.per_frame, args.quiet, args.padding, args.audio_format, args.denoise, args.light)
    elif args.decrypt:
        s.decrypt(args.output, args.scramble, args.preview, args.per_frame, args.quiet, args.padding, args.audio_format, args.denoise, args.light)


if __name__ == "__main__":
    main()
