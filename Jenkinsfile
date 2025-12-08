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
                        # Build the application image
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
                        # Stop and remove existing container if running
                        docker stop ${CONTAINER_NAME} 2>/dev/null || true
                        docker rm ${CONTAINER_NAME} 2>/dev/null || true
                        
                        # Run the application container
                        docker run -d --name ${CONTAINER_NAME} -p 5001:5001 ${DOCKER_IMAGE}:latest
                        
                        # Wait for application to be ready
                        echo "Waiting for application to start..."
                        sleep 10
                        
                        # Check if application is running
                        docker ps | grep ${CONTAINER_NAME}
                        
                        # Verify application is accessible
                        echo "Testing application endpoint..."
                        curl -f http://localhost:5001 || (echo "Application failed to start" && exit 1)
                        
                        echo "Application is running successfully!"
                    '''
                }
            }
        }
        
        stage('Build Test Docker Image') {
            steps {
                script {
                    echo '========== Building Test Environment =========='
                    sh '''
                        # Create Dockerfile for testing
                        cat > Dockerfile.test <<'EOF'
FROM python:3.9-slim

# Install dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    --no-install-recommends \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) && \
    CHROME_DRIVER_VERSION=$(curl -sS "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}") && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64

# Install Python packages
RUN pip install --no-cache-dir selenium pytest pytest-html

# Set working directory
WORKDIR /tests

# Default command
CMD ["pytest"]
EOF

                        # Build test image
                        docker build -t selenium-test:latest -f Dockerfile.test .
                        
                        echo "Test environment built successfully"
                    '''
                }
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                script {
                    echo '========== Running Selenium Tests =========='
                    sh '''
                        # Create test-results directory
                        mkdir -p test-results
                        
                        # Run tests in Docker container
                        docker run --rm \
                            --network host \
                            -v "$(pwd)/tests:/tests" \
                            -v "$(pwd)/test-results:/test-results" \
                            selenium-test:latest \
                            pytest /tests/test_todo_app.py \
                                -v \
                                --junitxml=/test-results/results.xml \
                                --html=/test-results/report.html \
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
                    # Stop and remove application container
                    docker stop ${CONTAINER_NAME} 2>/dev/null || true
                    docker rm ${CONTAINER_NAME} 2>/dev/null || true
                    
                    echo "Cleanup completed"
                '''
                
                // Publish test results
                junit allowEmptyResults: true, testResults: 'test-results/results.xml'
                
                // Publish HTML report
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
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Project:</td>
                                    <td style="padding: 8px;">${env.JOB_NAME}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Build Number:</td>
                                    <td style="padding: 8px;">#${env.BUILD_NUMBER}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Build Status:</td>
                                    <td style="padding: 8px; color: #4CAF50; font-weight: bold;">SUCCESS</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Duration:</td>
                                    <td style="padding: 8px;">${currentBuild.durationString}</td>
                                </tr>
                            </table>
                            
                            <h3>Links:</h3>
                            <ul>
                                <li><a href="${env.BUILD_URL}">Build URL</a></li>
                                <li><a href="${env.BUILD_URL}console">Console Output</a></li>
                                <li><a href="${env.BUILD_URL}Selenium_20Test_20Report/">Test Report</a></li>
                            </ul>
                            
                            <h3>Test Summary:</h3>
                            <p>All Selenium tests passed successfully!</p>
                            
                            <p style="margin-top: 20px; color: #666;">
                                <strong>Triggered by:</strong> ${env.CHANGE_AUTHOR ?: 'Manual Build'}<br>
                                <strong>Commit:</strong> ${env.GIT_COMMIT ?: 'N/A'}
                            </p>
                            
                            <hr style="margin: 20px 0;">
                            <p style="font-size: 12px; color: #999;">
                                This is an automated message from Jenkins CI/CD Pipeline.
                            </p>
                        </body>
                        </html>
                    """,
                    mimeType: 'text/html',
                    to: "${env.CHANGE_AUTHOR_EMAIL ?: env.BUILD_USER_EMAIL ?: 'attiatulhayee508@gmail.com'}",
                    from: 'jenkins@yourdomain.com',
                    replyTo: 'noreply@yourdomain.com'
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
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Project:</td>
                                    <td style="padding: 8px;">${env.JOB_NAME}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Build Number:</td>
                                    <td style="padding: 8px;">#${env.BUILD_NUMBER}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Build Status:</td>
                                    <td style="padding: 8px; color: #f44336; font-weight: bold;">FAILURE</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Duration:</td>
                                    <td style="padding: 8px;">${currentBuild.durationString}</td>
                                </tr>
                            </table>
                            
                            <h3>Links:</h3>
                            <ul>
                                <li><a href="${env.BUILD_URL}">Build URL</a></li>
                                <li><a href="${env.BUILD_URL}console">Console Output (Check for errors)</a></li>
                                <li><a href="${env.BUILD_URL}Selenium_20Test_20Report/">Test Report</a></li>
                            </ul>
                            
                            <h3>Action Required:</h3>
                            <p>Please check the console output and test report for details about the failure.</p>
                            
                            <p style="margin-top: 20px; color: #666;">
                                <strong>Triggered by:</strong> ${env.CHANGE_AUTHOR ?: 'Manual Build'}<br>
                                <strong>Commit:</strong> ${env.GIT_COMMIT ?: 'N/A'}
                            </p>
                            
                            <hr style="margin: 20px 0;">
                            <p style="font-size: 12px; color: #999;">
                                This is an automated message from Jenkins CI/CD Pipeline.
                            </p>
                        </body>
                        </html>
                    """,
                    mimeType: 'text/html',
                    to: "${env.CHANGE_AUTHOR_EMAIL ?: env.BUILD_USER_EMAIL ?: 'attiatulhayee508@gmail.com'}",
                    from: 'jenkins@yourdomain.com',
                    replyTo: 'noreply@yourdomain.com'
                )
            }
        }
    }
}
