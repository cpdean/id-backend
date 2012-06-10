1. Somehow install postgresql 9.1
2. Put an account on there named "herokuflask", and make sure it can access postgres locally without a password
3. Make herokuflask the owner of a database: "herokudb"

4. Do your virtualenv stuff to the folder v

5. Run these guys:

    # update schema
    python manage.py
    # test locally
    ./dev_server.sh

    # deploy on heroku
    heroku create --stack cedar
    heroku addons:add shared-database
    heroku push heroku master
    heroku run "python manage.py"
    heroku open
