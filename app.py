import sys
from kophinos import app
from kophinos.blueprints.users import users
from kophinos.blueprints.authentication import authentication

def main(argv):
    app.register_blueprint(users)
    app.register_blueprint(authentication)

    if argv[1] == 'api':
        app.run()
    else:
        print('Sorry no valid option given')
        exit(-1)


if __name__ == '__main__':
    main(sys.argv)

