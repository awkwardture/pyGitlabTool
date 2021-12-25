import sys
from gitlabtool import confmaker, gitlog2chglog


def main():
    confmaker.main(sys.argv)


def g2c():
    gitlog2chglog.main(sys.argv)


if __name__ == "__main__":
    main()
