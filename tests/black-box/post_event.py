import sys
import getopt
import json

from Utility.utils import post_event


def main(argv):
    inputfile = ''
    url = ''
    try:
        opts, args = getopt.getopt(
            argv, "hf:u:", ["file=", "url="])
    except getopt.GetoptError:
        print('post_event.py -f <jsonfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('post_event.py -f <jsonfile> ')
            sys.exit()
        elif opt in ("-f", "--file"):
            inputfile = arg
        elif opt in ("-u", "--url"):
            url = arg
            if not url.startswith("http://"):
                url = f"http://{url}"

    if inputfile == '':
        print('post_event.py -f <jsonfile>')
        sys.exit(3)
    else:
        with open(inputfile) as f:
            data = json.load(f)

        if url != '':
            post_event(data, url)
        else:
            post_event(data)


main(sys.argv[1:])
