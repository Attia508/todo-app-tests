pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'todo-app'
        CONTAINER_NAME = 'todo-app-container'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                script {
                    echo '========== Checking out code from GitHub =========='
                    checkout scm
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    echo '========== Verifying Environment =========='
                    sh '''
                        echo "Docker version:"
                        docker --version
                        echo "Python version:"
                        python3 --version
                    '''
                }
            }
        }
        
        stage('Build Application Docker Image') {
            steps {
                script {
                    echo '========== Building Application Docker Image =========='
                    sh '''
                        docker build -t ${DOCKER_IMAGE}:latest .
                        echo "Docker image built successfully"
                        docker images | grep ${DOCKER_IMAGE}
                    '''
                }
            }
        }
        
        stage('Start Application') {
            steps {
                script {
                    echo '========== Starting Application Container =========='
                    sh '''
                        docker stop ${CONTAINER_NAME} 2>/dev/null || true
                        docker rm ${CONTAINER_NAME} 2>/dev/null || true
                        docker run -d --name ${CONTAINER_NAME} -p 5001:5001 ${DOCKER_IMAGE}:latest
                        echo "Waiting for application to start..."
                        sleep 10
                        docker ps | grep ${CONTAINER_NAME}
                        echo "Testing application endpoint..."
                        curl -f http://localhost:5001 || (echo "Application failed to start" && exit 1)
                        echo "Application is running successfully!"
                    '''
                }
            }
        }
        
        stage('Install Test Dependencies') {
            steps {
                script {
                    echo '========== Installing Chrome and Test Tools =========='
                    sh '''
                        # Install Chrome if not present
                        if ! command -v google-chrome &> /dev/null; then
                            echo "Installing Google Chrome..."
                            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
                            sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
                            sudo apt-get update
                            sudo apt-get install -y google-chrome-stable
                        else
                            echo "Chrome already installed"
                        fi
                        
                        # Install ChromeDriver if not present
                        if ! command -v chromedriver &> /dev/null; then
                            echo "Installing ChromeDriver..."
                            CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
                            wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}.0.6778.204/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip || \
                            wget -q "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" -O /tmp/chromedriver.zip
                            sudo unzip -o /tmp/chromedriver.zip -d /tmp/
                            sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ 2>/dev/null || sudo mv /tmp/chromedriver /usr/local/bin/
                            sudo chmod +x /usr/local/bin/chromedriver
                            rm -f /tmp/chromedriver.zip
                        else
                            echo "ChromeDriver already installed"
                        fi
                        
                        # Install Python packages
                        pip3 install --user selenium pytest pytest-html || \
                        python3 -m pip install --user selenium pytest pytest-html
                        
                        echo "All dependencies installed!"
                    '''
                }
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                script {
                    echo '========== Running Selenium Tests =========='
                    sh '''
                        mkdir -p test-results
                        
                        # Add Python user packages to PATH
                        export PATH=$PATH:~/.local/bin
                        
                        # Run tests
                        python3 -m pytest tests/test_todo_app.py \
                            -v \
                            --junitxml=test-results/results.xml \
                            --html=test-results/report.html \
                            --self-contained-html \
                        || exit 1
                        
                        echo "All tests completed successfully!"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo '========== Cleaning Up =========='
                sh '''
                    docker stop ${CONTAINER_NAME} 2>/dev/null || true
                    docker rm ${CONTAINER_NAME} 2>/dev/null || true
                    echo "Cleanup completed"
                '''
                
                junit allowEmptyResults: true, testResults: 'test-results/results.xml'
                
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test-results',
                    reportFiles: 'report.html',
                    reportName: 'Selenium Test Report'
                ])
            }
        }
        
        success {
            script {
                echo '========== Build Successful =========='
                emailext (
                    subject: "✓ SUCCESS: Jenkins Build #${env.BUILD_NUMBER} - ${env.JOB_NAME}",
                    body: """
                        <html>
                        <body style="font-family: Arial, sans-serif;">
                            <h2 style="color: #4CAF50;">✓ Build Successful!</h2>
                            <table style="border-collapse: collapse; margin: 20px 0;">
                                <tr><td style="padding: 8px; font-weight: bold;">Project:</td><td style="padding: 8px;">${env.JOB_NAME}</td></tr>
                                <tr><td style="padding: 8px; font-weight: bold;">Build Number:</td><td style="padding: 8px;">#${env.BUILD_NUMBER}</td></tr>
                                <tr><td style="padding: 8px; font-weight: bold;">Build Status:</td><td style="padding: 8px; color: #4CAF50; font-weight: bold;">SUCCESS</td></tr>
                                <tr><td style="padding: 8px; font-weight: bold;">Duration:</td><td style="padding: 8px;">${currentBuild.durationString}</td></tr>
                            </table>
                            <h3>Links:</h3>
                            <ul>
                                <li><a href="${env.BUILD_URL}">Build URL</a></li>
                                <li><a href="${env.BUILD_URL}console">Console Output</a></li>
                                <li><a href="${env.BUILD_URL}Selenium_20Test_20Report/">Test Report</a></li>
                            </ul>
                            <h3>Test Summary:</h3>
                            <p>All Selenium tests passed successfully!</p>
                            <p style="margin-top: 20px; color: #666;"><strong>Triggered by:</strong> ${env.CHANGE_AUTHOR ?: 'Manual Build'}</p>
                        </body>
                        </html>
                    """,
                    mimeType: 'text/html',
                    to: "attiatulhayee508@gmail.com",
                    from: 'jenkins@yourdomain.com'
                )
            }
        }
        
        failure {
            script {
                echo '========== Build Failed =========='
                emailext (
                    subject: "✗ FAILURE: Jenkins Build #${env.BUILD_NUMBER} - ${env.JOB_NAME}",
                    body: """
                        <html>
                        <body style="font-family: Arial, sans-serif;">
                            <h2 style="color: #f44336;">✗ Build Failed!</h2>
                            <table style="border-collapse: collapse; margin: 20px 0;">
                                <tr><td style="padding: 8px; font-weight: bold;">Project:</td><td style="padding: 8px;">${env.JOB_NAME}</td></tr>
                                <tr><td style="padding: 8px; font-weight: bold;">Build Number:</td><td style="padding: 8px;">#${env.BUILD_NUMBER}</td></tr>
                                <tr><td style="padding: 8px; font-weight: bold;">Build Status:</td><td style="padding: 8px; color: #f44336; font-weight: bold;">FAILURE</td></tr>
                            </table>
                            <h3>Links:</h3>
                            <ul>
                                <li><a href="${env.BUILD_URL}">Build URL</a></li>
                                <li><a href="${env.BUILD_URL}console">Console Output</a></li>
                            </ul>
                            <p>Please check the console output for details.</p>
                        </body>
                        </html>
                    """,
                    mimeType: 'text/html',
                    to: "attiatulhayee508@gmail.com",
                    from: 'jenkins@yourdomain.com'
                )
            }
        }
    }
}
