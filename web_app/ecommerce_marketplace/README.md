- first unzip the folder

SQL Setup and Working :


- then use this command to install dependencies needed for the project `pip install -r requirements.txt`
- then `python run.py`
- this will only start the app but not the database to install your mysql
- once you install mysql set up your environment varaibles 
- paste the path of the mqsql installation bin file : it will be  in     c drive / programfiles / server or version / bin /  ( copy this path ) 
- now click on windows - then search for "edit the system environment varaibles" in the above box double click on path and click on new and paste the copied path 
- this sets up your mqsql..
- later the db.txt file in our project needs to be added into mysql - now , just type mysql port command and < with the db.txt file 
- it setup your sql base - now run.py will work completely

NoSQL Setup and Working :

- open noSQL folder
- install nodejs
- install mongodb compass
- connect to 27017 port number
- now run ```python mongo_insertion.py``` this inserts our db values : sample
- then run ```python app.py```
- open website and you can perform all operations as we did for SQL


