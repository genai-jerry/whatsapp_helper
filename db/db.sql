CREATE TABLE IF NOT EXISTS instances (
                id INT AUTO_INCREMENT PRIMARY KEY,
                mobile_number VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL
            );

CREATE TABLE IF NOT EXISTS templates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL unique,
                active bit NOT NULL,
                template_text TEXT
            );

CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                type VARCHAR(10) NOT NULL,
                sender VARCHAR(20) NOT NULL,
                receiver VARCHAR(20) NOT NULL,
                receiver_id INT,
                message TEXT NOT NULL,
                template VARCHAR(255),
                status VARCHAR(10) NOT NULL,
                error_message VARCHAR(255),
                create_time datetime default now(),
                update_time datetime,
                FOREIGN KEY (receiver_id) REFERENCES opportunity(id)
            );

CREATE TABLE IF NOT EXISTS opportunity (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL unique,
                phone VARCHAR(15) NOT NULL unique,
                comment VARCHAR(250),
                register_time datetime NOT NULL,
                opportunity_status INT,
                call_status INT,
                sales_agent INT,
                FOREIGN KEY (opportunity_status) REFERENCES opportunity_status(id),
                FOREIGN KEY (call_status) REFERENCES lead_call_status(id),
                FOREIGN KEY (sales_agent) REFERENCES sales_agent(id)
            );

CREATE TABLE IF NOT EXISTS lead_communication (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                template_id INT,
                sent_date datetime default now(),
                template_name VARCHAR(255),
                FOREIGN KEY (template_id) REFERENCES templates(id)
            );

CREATE TABLE IF NOT EXISTS opportunity_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL unique,
                color_code varchar(25)
            );

CREATE TABLE IF NOT EXISTS lead_call_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL unique,
                color_code varchar(25)
            );

CREATE TABLE IF NOT EXISTS sales_agent (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL unique,
                color_code varchar(25)
            );