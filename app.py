import sys
from kophinos import app

def main(argv):
    if argv[1] == 'api':
        app.run()
    else:
        print('Sorry no valid option given')
        exit(-1)


if __name__ == '__main__':
    main(sys.argv)

