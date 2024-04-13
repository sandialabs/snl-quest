import sys


def a():
    pass


def foo():
    b = "" + []


if __name__ == "__main__":
    print("import2")
    sys.stdout.flush()
    foo()
    print("import1 b=" + str(b))
