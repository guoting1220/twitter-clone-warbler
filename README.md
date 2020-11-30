# twitter-clone-warbler

To run the app:

Create the Python virtual environment:

	$ python3 -m venv venv
	$ source venv/bin/activate
	(venv) $ pip install -r requirements.txt

Set up the database:

	(venv) $ createdb warbler
	(venv) $ python seed.py

Start the server:

	(venv) $ flask run

Open the localhost page:

	http://127.0.0.1:5000/
