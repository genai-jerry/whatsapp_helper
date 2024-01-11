CREATE TABLE IF NOT EXISTS instances (
                id INT AUTO_INCREMENT PRIMARY KEY,
                mobile_number VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL
            );

CREATE TABLE IF NOT EXISTS templates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                template_text TEXT
            );