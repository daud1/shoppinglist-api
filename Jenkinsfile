pipeline {
    agent any

    stages {
        stage('build') {
            echo 'cloning ShoppingListAPI Repo'
            git 'https://github.com/daud1/ShoppingListAPI.git'
            sh 'virtualenv venv'
            sh '. venv/bin/activate'
            sh 'pip install -r requirements.txt'
        }

        stage('test') {
            echo 'Running tests'
            sh 'py.test --cov=. tests/ --cov-config .coveragerc'
        }
    }
}