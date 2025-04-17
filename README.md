# Messaging App Backend with Flask and PostgreSQL DB

## Working locally

### Clone this repo on your machine
To clone the repo, run the following command:
```bash
git clone https://github.com/VladChira/ip-messaging-server.git
```
You will be asked to enter your credentials. For the password, you must enter a Personal Access Token instead of your account password. Click [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) to learn how to create a token.

### Installing dependencies
You will need python installed system-wide and docker. The other dependencies will be installed in a virtual environment.

If you are on Ubuntu, the easiest way to install Docker is using the convenience script [here](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script). For other distros/operating system, please refer to the Docker docs.

### Creating a branch
Create a new branch using ``git branch <branch name>`` and switch to it with ``git checkout <branch name>``. Here is where you will work on features. When ready to merge to main, push to the branch and submit a pull request.

### Creating a virtual environment
For better isolation, python packages will not be installed globally, but in a virtual environment instead. Create one in root of the project with ``python3 -m venv venv`` then activate it with ``source venv/bin/activate``.

To install the necessary packages, run
``pip install -r requirements.txt``.

If during development you find yourself installing other packages, add them to the ``requirements.txt`` file using ``pip freeze > requirements.txt``

### Injecting secrets
Sensitive information cannot be stored in the github repo, such as the postgresql username and password. These secrets will be injected into the app at runtime using the ``dotenv`` package. Create a file in the root of the project called ``.env`` and ask Vlad for the secrets. The ``.env`` file is automatically gitignored.

### Running the database container
The postgresql database will be run in a Docker container. A script to launch the database has been provided: ``run_local.sh``, as well as a script to test the database connection with the injected secrets: ``test_db_conn.py``.

To look at logs/errors, run ``sudo docker logs chatapp-db -f``.

To stop the db, run ``sudo docker stop chatapp-db``. To remove the db, run ``sudo docker rm chatapp-db`` after stopping the container.


### Running the Flask app
In development mode, there is no reason to run the Flask app in a container. Run ``python3 run.py`` to launch the Flask app. The app will run on the port specified in the ``run.py`` file (i.e. 5000).

### Schema migrations
TODO

## Deploying to production
In production, both the Flask backend and the database will be run in containers. 

To deploy your code to production, submit a pull request. After it's merged to the main branch, a Github workflow will automatically deploy the backend to the server. 

You may review the workflow that deploys this app in the ``.github/workflows`` folder and/or ask Vlad for more info.