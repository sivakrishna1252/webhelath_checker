pipeline {
    agent any

    environment {
        // Define variables to be used in the pipeline
        DOCKER_IMAGE_WEB = "server-checker-web"
        DOCKER_IMAGE_MONITOR = "server-checker-monitor"
        // In a real environment, you might use credentials for Docker Hub
        // DOCKER_CREDENTIALS_ID = 'your-docker-credentials'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from your repository
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    // Create a dummy .env file for the build process based on .env.example
                    // Only do this if .env doesn't exist to ensure the build doesn't fail
                    sh 'if [ ! -f .env ]; then cp .env.example .env; fi'
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building Docker images using docker-compose...'
                // Use docker-compose to build the images defined in docker-compose.yml
                sh 'docker-compose build'
            }
        }

        // Optional: Add a testing stage here if you have unit tests set up
        // stage('Test') {
        //     steps {
        //         echo 'Running tests...'
        //         sh 'docker-compose run --rm web python manage.py test'
        //     }
        // }

        stage('Deploy') {
            steps {
                echo 'Deploying the application...'
                // Start the containers in detached mode
                // This stops any existing containers and recreates them with the new images
                sh 'docker-compose up -d'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed.'
            // Clean up old Docker images to save space
            sh 'docker image prune -f'
        }
        success {
            echo 'Pipeline succeeded! Application is running.'
        }
        failure {
            echo 'Pipeline failed. Check the logs for details.'
        }
    }
}



#Jenkinsfile start



