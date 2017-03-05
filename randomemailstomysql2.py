import os, random, string, MySQLdb

domains = [ "hotmail.com", "gmail.com", "aol.com", "mail.com" , "mail.kz", "yahoo.com"]
letters = ["a", "b", "c", "d","e", "f", "g", "h", "i", "j", "k", "l"]

def get_one_random_domain(domains):
        return domains[random.randint( 0, len(domains)-1)]


def get_one_random_name(letters):
    email_name = ""
    for i in range(7):
        email_name = email_name + letters[random.randint(0,11)]
    return email_name

def generate_random_emails():

    for i in range(0,110):
         one_name = str(get_one_random_name(letters))
         one_domain = str(get_one_random_domain(domains))
         email = (one_name  + "@" + one_domain)
	 print (email)
	 length = 13
	 chars = string.ascii_letters + string.digits + '!@#$%^&*()'
	 random.seed = (os.urandom(1024))
	 pwd = ''.join(random.choice(chars) for i in range(length))
	 print (pwd)
	 add_email s= ("INSERT INTO test (email,pwd) values(%s,%s)")
	 data_emails = (email,pwd)
	 cursor.execute(add_emails,data_emails)

def main():
    generate_random_emails()

# Open database connection ( If database is not created don't give dbname)
db = MySQLdb.connect("localhost","root","CogiaTest33","CogiaDB2" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# For creating create db
# Below line  is hide your warning 
cursor.execute("SET sql_notes = 0; ")
# create db here....
cursor.execute("create database IF NOT EXISTS CogiaDB2")

# create table
cursor.execute("SET sql_notes = 0; ")
cursor.execute("create table IF NOT EXISTS test (email varchar(70),pwd varchar(20));")
cursor.execute("SET sql_notes = 1; ")

main()

# Commit your changes in the database
db.commit()

# disconnect from server
db.close()
