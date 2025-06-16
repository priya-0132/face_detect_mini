-- Insert a test admin user
INSERT INTO users (username, email, role)
VALUES ('admin123', 'admin@example.com', 'admin')
ON DUPLICATE KEY UPDATE email = 'admin@example.com';

-- Insert a test user
INSERT INTO users (username, email, role)
VALUES ('user1', 'user1@example.com', 'user')
ON DUPLICATE KEY UPDATE email = 'user1@example.com';
