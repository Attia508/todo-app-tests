pipeline {
    agent any
    
    environment {
        APP_PORT = '5001'
        APP_IMAGE = 'todo-app:latest'
        TEST_IMAGE = 'selenium-test:latest'
        APP_CONTAINER = 'todo-app-container'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                script {
                    echo '========================================='
                    echo '       Checking out code from GitHub     '
                    echo '========================================='
                    checkout scm
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    echo '========================================='
                    echo '         Verifying Environment           '
                    echo '========================================='
                    sh '''
                        echo "Docker version:"
                        docker --version
                        echo ""
                        echo "Python version:"
                        python3 --version
                        echo ""
                        echo "Disk space:"
                        df -h | grep -E '^/dev/'
                        echo ""
                        echo "Memory:"
                        free -h
                    '''
                }
            }
        }
        
        stage('Build Application Docker Image') {
            steps {
                script {
                    echo '========================================='
                    echo '    Building Application Docker Image    '
                    echo '========================================='
                    sh '''
                        docker build -t ${APP_IMAGE} .
                        echo ""
                        echo "✓ Docker image built successfully"
                        echo ""
                        docker images | grep todo-app
                    '''
                }
            }
        }
        
        stage('Start Application') {
            steps {
                script {
                    echo '========================================='
                    echo '      Starting Application Container     '
                    echo '========================================='
                    sh '''
                        # Stop and remove existing container if any
                        docker stop ${APP_CONTAINER} 2>/dev/null || true
                        docker rm ${APP_CONTAINER} 2>/dev/null || true
                        
                        # Start new container
                        docker run -d \
                            --name ${APP_CONTAINER} \
                            -p ${APP_PORT}:${APP_PORT} \
                            ${APP_IMAGE}
                        
                        # Wait for application to start
                        echo ""
                        echo "Waiting for application to start..."
                        sleep 10
                        
                        # Verify container is running
                        echo ""
                        echo "Container status:"
                        docker ps | grep ${APP_CONTAINER}
                        
                        # Test application endpoint
                        echo ""
                        echo "Testing application endpoint..."
                        curl -f http://localhost:${APP_PORT} > /dev/null 2>&1
                        
                        if [ $? -eq 0 ]; then
                            echo "✓ Application is running successfully!"
                        else
                            echo "✗ Application failed to start"
                            docker logs ${APP_CONTAINER}
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Build Test Docker Image') {
            options {
                timeout(time: 15, unit: 'MINUTES')
            }
            steps {
                script {
                    echo '========================================='
                    echo '     Building Test Docker Image          '
                    echo '========================================='
                    sh '''
                        docker build -t ${TEST_IMAGE} -f Dockerfile.test .
                        echo ""
                        echo "✓ Test image built successfully"
                        echo ""
                        docker images | grep selenium-test
                    '''
                }
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                script {
                    echo '========================================='
                    echo '        Running Selenium Tests           '
                    echo '========================================='
                    sh '''
                        # Create reports directory
                        mkdir -p ${WORKSPACE}/reports
                        
                        # Run tests in Docker container
                        docker run --rm \
                            --network host \
                            -v ${WORKSPACE}/reports:/app/reports \
                            -e APP_URL=http://localhost:${APP_PORT} \
                            ${TEST_IMAGE} \
                            pytest tests/ -v \
                                --html=reports/report.html \
                                --self-contained-html \
                                --tb=short
                        
                        echo ""
                        echo "✓ Tests completed successfully!"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo '========================================='
                echo '           Cleanup & Reports              '
                echo '========================================='
                
                // Show container logs if still running
                sh '''
                    if docker ps -a | grep -q ${APP_CONTAINER}; then
                        echo "Application container logs:"
                        docker logs ${APP_CONTAINER} --tail 50
                    fi
                '''
                
                // Stop and remove application container
                sh '''
                    docker stop ${APP_CONTAINER} 2>/dev/null || true
                    docker rm ${APP_CONTAINER} 2>/dev/null || true
                    echo "✓ Containers cleaned up"
                '''
                
                // Publish HTML test report
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'Selenium Test Report',
                    reportTitles: 'Test Results'
                ])
                
                echo "✓ Test report published"
            }
        }
        
        success {
            script {
                echo '========================================='
                echo '  ✓ Pipeline Completed Successfully!     '
                echo '========================================='
                
                // Optional: Send email notification
                // emailext (
                //     to: '${DEFAULT_RECIPIENTS}',
                //     subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                //     body: """
                //         <h2>Build Successful!</h2>
                //         <p><b>Job:</b> ${env.JOB_NAME}</p>
                //         <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
                //         <p><b>Build URL:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                //         <p>All tests passed successfully.</p>
                //     """,
                //     mimeType: 'text/html'
                // )
            }
        }
        
        failure {
            script {
                echo '========================================='
                echo '  ✗ Pipeline Failed                       '
                echo '========================================='
                
                // Show detailed logs
                sh '''
                    echo "Checking for running containers:"
                    docker ps -a
                    
                    if docker ps -a | grep -q ${APP_CONTAINER}; then
                        echo ""
                        echo "Application container logs:"
                        docker logs ${APP_CONTAINER}
                    fi
                '''
                
                // Optional: Send email notification
                // emailext (
                //     to: '${DEFAULT_RECIPIENTS}',
                //     subject: "FAILURE: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                //     body: """
                //         <h2 style="color: red;">Build Failed!</h2>
                //         <p><b>Job:</b> ${env.JOB_NAME}</p>
                //         <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
                //         <p><b>Build URL:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                //         <p>Please check the console output for details.</p>
                //     """,
                //     mimeType: 'text/html'
                // )
            }
        }
    }
}
