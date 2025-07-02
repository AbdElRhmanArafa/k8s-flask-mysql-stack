-- Create database
CREATE DATABASE IF NOT EXISTS flaskapp;

-- Create user and grant privileges
CREATE USER IF NOT EXISTS 'flaskuser'@'%' IDENTIFIED BY 'flaskpassword';
GRANT ALL PRIVILEGES ON flaskapp.* TO 'flaskuser'@'%';
FLUSH PRIVILEGES;

-- Use the database
USE flaskapp;

-- Create tables
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some initial data
INSERT INTO tasks (title, description, status) 
VALUES 
    ('Setup Kubernetes Cluster', 'Configure a multi-node Kubernetes cluster', 'in-progress'),
    ('Create Helm Charts', 'Develop Helm charts for deploying applications', 'pending'),
    ('Implement Monitoring', 'Set up Prometheus and Grafana for monitoring', 'pending');
