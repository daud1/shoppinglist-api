# ShoppingListAPI
[![Build Status](https://travis-ci.org/daud1/week-two-API.png)](https://travis-ci.org/daud1/ShoppingListAPI)
[![Coverage Status](https://coveralls.io/repos/github/daud1/ShoppingListAPI/badge.svg?branch=master)](https://coveralls.io/github/daud1/ShoppingListAPI?branch=master)
[![CircleCI](https://circleci.com/gh/daud1/ShoppingListAPI/tree/master.svg?style=svg)](https://circleci.com/gh/daud1/ShoppingListAPI/tree/master)

An API for the shopping list application

> ShoppingList is a simple API that allows users to record and keep track of their shopping lists.

## Features
- Users can create accounts.
- Users can log in.
- Users can create, view, update and delete shopping lists. 
- Users can add, update, view or delete items in a shopping list

## Tools
Tools used for development of this API are;
- Documentation : [Apiary](https://apiary.io/)
- Database: [Postgresql](https://www.postgresql.org)
- Microframework: [Flask](http://flask.pocoo.org/)
- Editor: [VSCode](https://code.visualstudio.com)
- Programming language: [Python 3.x.x](https://docs.python.org/3/)
- API Testing environment: [Postman](https://www.getpostman.com)

## Running the tests

From the project's repository, to run tests, use
```sh
   pytest -r Pf test_api.py 
 ``` 

## Getting Started
### Prerequisites
1. Install requirements, run 
```sh
     pip install -r requirements.txt
```
2. Create a postgres database and edit the database configurations as desired.

From the project's repository, 
```sh 
    $ python manage.py db init
    $ python manage.py db migrate
    $ python manage.py db upgrade
    $ python run.py runserver
 ```
### Base URL for the API
URL:

## End points
### Endpoints to create a user account and login into the application
HTTP Method|End point | Public Access|Action
-----------|----------|--------------|------
POST | /auth/register | True | Create an account
POST | /auth/login | True | Login a user
POST | /auth/logout | False | Logout a user
POST | /auth/reset-password | False | Reset a user password
GET | /user | False | Returns details of a logged in user
PUT | /user | False | Updates details of a logged in user
### Endpoints to create, update, view and delete a shopping list
HTTP Method|End point | Public Access|Action
-----------|----------|--------------|------
POST | /shoppinglists | False | Create a shopping list
GET | /shoppinglists | False | View all shopping lists
GET | /shoppinglists/id | False | View details of a shopping list
PUT | /shoppinglists/id | False | Updates a shopping list with a given id
DELETE | /shoppinglists/id | False | Deletes a shopping list with a given id
### Endpoints to create, update, view and delete a shopping list item
HTTP Method|End point | Public Access|Action
-----------|----------|--------------|------
GET | /shoppinglists/id/items | False | View Items of a given list id
GET | /shoppinglists/id/items/<item_id> | False | View details of a particular item on a given list id
POST | /shoppinglists/id/items | False | Add an Item to a shopping list
PUT | /shoppinglists/id/items/<item_id> | False | Update a shopping list item on a given list
DELETE | /shoppinglists/id/items/<item_id> | False | Delete a shopping list item from a given list
