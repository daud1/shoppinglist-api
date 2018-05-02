pipeline {
    agent any

    stages {
        stage('build') {
            steps{
                echo 'cloning ShoppingListAPI Repo'
            git 'https://github.com/daud1/ShoppingListAPI.git'
            sh 'pwd'
            sh 'virtualenv --python=python3 venv'
            sh '''
                . venv/bin/activate
                pip install -r requirements.txt
            '''
            }
            
        }

        stage('test') {
            steps{
                echo 'Running tests'
            sh '''
                . venv/bin/activate
                py.test --cov=. tests/ --cov-config .coveragerc
            '''
            }
            
        }
    }
}