import sys
from . import RequirementFile

if __name__ == "__main__":

    try:
        for child in RequirementFile.parse(open(sys.argv[1]).read()).children:
            print(repr(child))
    except Exception:
        print(sys.argv[1])
        raise

