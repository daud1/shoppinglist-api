pipeline {
    agent any

    stages {
        stage('build') {
            steps{
                echo 'cloning ShoppingListAPI Repo'
            git 'https://github.com/daud1/ShoppingListAPI.git'
            sh 'pwd'
            sh 'virtualenv --python=python3 venv'
            sh 'ls'
            sh 'source venv/bin/activate'
            sh 'sudo pip install -r requirements.txt'
            }
            
        }

        stage('test') {
            steps{
                echo 'Running tests'
            sh 'py.test --cov=. tests/ --cov-config .coveragerc'
            }
            
        }
    }
}