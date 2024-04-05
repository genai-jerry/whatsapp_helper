-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: whatsapp_helper
-- ------------------------------------------------------
-- Server version	8.0.36-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `instances`
--

DROP TABLE IF EXISTS `instances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `instances` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mobile_number` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `status` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `instances`
--

LOCK TABLES `instances` WRITE;
/*!40000 ALTER TABLE `instances` DISABLE KEYS */;
INSERT INTO `instances` VALUES (58,'9900180339','Jerry Kurian','Ready');
/*!40000 ALTER TABLE `instances` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lead_call_status`
--

DROP TABLE IF EXISTS `lead_call_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lead_call_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `color_code` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lead_call_status`
--

LOCK TABLES `lead_call_status` WRITE;
/*!40000 ALTER TABLE `lead_call_status` DISABLE KEYS */;
INSERT INTO `lead_call_status` VALUES (1,'Did Not Pick/Reply',NULL),(2,'Wrong Number',NULL),(3,'Picked and Call Back',NULL),(4,'Not Interested Now',NULL),(5,'No Budget',NULL),(6,'Invalid Lead',NULL),(7,'Disconnected',NULL),(8,'Call Booked',NULL),(9,'Cancelled/Disqualified',NULL),(10,'VSL Shared , Followup',NULL),(11,'Call Pending',NULL);
/*!40000 ALTER TABLE `lead_call_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lead_communication`
--

DROP TABLE IF EXISTS `lead_communication`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lead_communication` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `template_id` int DEFAULT NULL,
  `sent_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `template_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `template_id` (`template_id`),
  CONSTRAINT `lead_communication_ibfk_1` FOREIGN KEY (`template_id`) REFERENCES `templates` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lead_communication`
--

LOCK TABLES `lead_communication` WRITE;
/*!40000 ALTER TABLE `lead_communication` DISABLE KEYS */;
/*!40000 ALTER TABLE `lead_communication` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(10) NOT NULL,
  `sender` varchar(20) NOT NULL,
  `receiver` varchar(20) NOT NULL,
  `receiver_id` int DEFAULT NULL,
  `message` text NOT NULL,
  `template` varchar(255) DEFAULT NULL,
  `status` varchar(10) NOT NULL,
  `error_message` varchar(255) DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `receiver_id` (`receiver_id`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`receiver_id`) REFERENCES `opportunity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,'text','9900180339','8951358657',NULL,'Message on Feb 22',NULL,'Pending',NULL,'2024-02-22 22:48:00',NULL),(2,'text','9900180339','8951358657',NULL,'Message on Feb 22',NULL,'Pending',NULL,'2024-02-22 22:50:28',NULL),(3,'text','9900180339','8951358657',NULL,'Message on Feb 22',NULL,'Pending',NULL,'2024-02-22 22:56:24',NULL),(4,'text','9900180339','8951358657',NULL,'Message on Feb 22',NULL,'Sent',NULL,'2024-02-22 22:59:50','2024-02-22 23:00:24'),(5,'template','9900180339','8951358657',NULL,'{name}, Happy Saturday! Use the weekend to explore Generative AI through our concise webinar training video. Webinar covers Generative AI roadmap and job opportunities for aspiring GenAI developers/architect\r\nWatch this webinar training  here: https://bit.ly/3 - Jerry Kurian','Saturday_Reminder','Pending',NULL,'2024-02-22 23:07:06',NULL),(6,'template','9900180339','8951358657',NULL,'{name}, Happy Saturday! Use the weekend to explore Generative AI through our concise webinar training video. Webinar covers Generative AI roadmap and job opportunities for aspiring GenAI developers/architect\r\nWatch this webinar training  here: https://bit.ly/3 - Jerry Kurian','Saturday_Reminder','Pending',NULL,'2024-02-22 23:09:07',NULL),(7,'text','9900180339','8951358657',NULL,'Message on Feb 22',NULL,'Pending',NULL,'2024-02-22 23:09:12',NULL),(8,'text','9900180339','8951358657',NULL,'Message on Feb 22',NULL,'Sent',NULL,'2024-02-22 23:10:09','2024-02-22 23:10:52'),(9,'text','9900180339','8951358657',NULL,'Message on Feb 22',NULL,'Sent',NULL,'2024-02-22 23:10:26','2024-02-22 23:11:36'),(10,'template','9900180339','8951358657',NULL,'{name}, Happy Saturday! Use the weekend to explore Generative AI through our concise webinar training video. Webinar covers Generative AI roadmap and job opportunities for aspiring GenAI developers/architect\r\nWatch this webinar training  here: https://bit.ly/3 - Jerry Kurian','Saturday_Reminder','Sent',NULL,'2024-02-22 23:11:10','2024-02-22 23:11:43'),(11,'template','9900180339','8951358657',NULL,'Jerry, Happy Saturday! Use the weekend to explore Generative AI through our concise webinar training video. Webinar covers Generative AI roadmap and job opportunities for aspiring GenAI developers/architect\r\nWatch this webinar training  here: https://bit.ly/3 - Jerry Kurian','Saturday_Reminder','Sent',NULL,'2024-02-22 23:16:00','2024-02-22 23:16:21'),(12,'template','9900180339','5678901234',NULL,'Hi Lead','new_lead','Pending',NULL,'2024-02-27 13:37:22',NULL),(13,'template','9900180339','8951358657',NULL,'Hi Lead','new_lead','Sent',NULL,'2024-02-27 14:42:10','2024-02-27 14:42:16'),(43,'template','9900180339','8951358657',1,'Hi Lead','new_lead','Sent',NULL,'2024-02-28 17:09:30','2024-02-28 22:37:13');
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `opportunity`
--

DROP TABLE IF EXISTS `opportunity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opportunity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `comment` varchar(250) DEFAULT NULL,
  `register_time` datetime NOT NULL,
  `opportunity_status` int DEFAULT NULL,
  `call_status` int DEFAULT NULL,
  `sales_agent` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`),
  KEY `opportunity_status` (`opportunity_status`),
  KEY `call_status` (`call_status`),
  KEY `sales_agent` (`sales_agent`),
  CONSTRAINT `opportunity_ibfk_1` FOREIGN KEY (`opportunity_status`) REFERENCES `opportunity_status` (`id`),
  CONSTRAINT `opportunity_ibfk_2` FOREIGN KEY (`call_status`) REFERENCES `lead_call_status` (`id`),
  CONSTRAINT `opportunity_ibfk_3` FOREIGN KEY (`sales_agent`) REFERENCES `sales_agent` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opportunity`
--

LOCK TABLES `opportunity` WRITE;
/*!40000 ALTER TABLE `opportunity` DISABLE KEYS */;
INSERT INTO `opportunity` VALUES (1,'Changed Opportunity 1','test1@example.com','8951358657',NULL,'2022-01-01 00:00:00',2,8,3),(2,'Opportunity 2','test2@example.com','2345678901',NULL,'2022-01-02 00:00:00',2,6,2),(3,'Opportunity 3','test3@example.com','3456789012',NULL,'2022-01-03 00:00:00',2,11,3),(4,'Opportunity 4','test4@example.com','4567890123',NULL,'2022-01-04 00:00:00',2,11,1),(5,'Opportunity 5','test5@example.com','5678901234',NULL,'2022-01-05 00:00:00',2,11,2);
/*!40000 ALTER TABLE `opportunity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `opportunity_status`
--

DROP TABLE IF EXISTS `opportunity_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opportunity_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `color_code` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opportunity_status`
--

LOCK TABLES `opportunity_status` WRITE;
/*!40000 ALTER TABLE `opportunity_status` DISABLE KEYS */;
INSERT INTO `opportunity_status` VALUES (1,'No Show',NULL),(2,'Sale',NULL),(3,'No Sale',NULL),(4,'Follow up',NULL);
/*!40000 ALTER TABLE `opportunity_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales_agent`
--

DROP TABLE IF EXISTS `sales_agent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales_agent` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `color_code` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales_agent`
--

LOCK TABLES `sales_agent` WRITE;
/*!40000 ALTER TABLE `sales_agent` DISABLE KEYS */;
INSERT INTO `sales_agent` VALUES (1,'Jerry',NULL),(2,'Avinash',NULL),(3,'Santosh',NULL),(4,'Self',NULL);
/*!40000 ALTER TABLE `sales_agent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `templates`
--

DROP TABLE IF EXISTS `templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `active` bit(1) NOT NULL,
  `template_text` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `templates`
--

LOCK TABLES `templates` WRITE;
/*!40000 ALTER TABLE `templates` DISABLE KEYS */;
INSERT INTO `templates` VALUES (1,'new_register',1,'Hi there {name} you have an appointment with {sales_person}. See you there {name}'),(3,'new_lead',1,'Hi Lead'),(4,'Saturday_Reminder',1,'{name}, Happy Saturday! Use the weekend to explore Generative AI through our concise webinar training video. Webinar covers Generative AI roadmap and job opportunities for aspiring GenAI developers/architect\r\nWatch this webinar training  here: https://bit.ly/3 - Jerry Kurian');
/*!40000 ALTER TABLE `templates` ENABLE KEYS */;
UNLOCK TABLES;

INSERT INTO configs (name, value) VALUES ('max_possible_score', '10');

INSERT INTO max_scores (score_name, score_value, category) VALUES
('Salary Growth', 1, 'challenge'),
('Promotion', 1, 'challenge'),
('Unable to get into a high-growth product company', 1, 'challenge'),
('Lack of relevant skills', 1, 'challenge'),
('RIGHT NOW - I want to get started immediately.', 3, 'urgency'),
('WITHIN 90 DAYS - I have other things to attend to first.', 1, 'urgency'),
('MORE THAN 90 DAYS - I want to do this eventually, but I''m not sure when.', 0, 'urgency'),
('15-25 Lacks', 2, 'salary'),
('26-40 Lacks', 3, 'salary'),
('40+ Lacks', 1, 'salary'),
('50% Increment', 1, 'salary_expectation'),
('100% Increment', 2, 'salary_expectation'),
('As per market salary', 1, 'salary_expectation'),
('I have plenty of cash and credit to invest in growing my career (Rs 1 Lakh or more)', 3, 'financial_status'),
('I''m living paycheck-to-paycheck, so getting the funds together to grow this career may be a challenge, but possible if that is what is needed.', 2, 'financial_status'),
('Money is a constant source of stress - I don''t have any funds, or credit at all, and I want to keep my career exactly where it''s at.', 0, 'financial_status'),
('Yes', 1, 'availability'),
('No (Please change the date/time if you won''t be available)', 0, 'availability');

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-02-29 10:40:05
update lead_call_status set text_color="#f8f8f8";
update lead_call_status set text_color="#131211" where id=1 or id=3 or id=5 or id=9 or id=10;
update lead_call_status set text_color="#131211" where id=1 or id=3 or id=5 or id=9 or id=10 or id=11;
update sales_agent set text_color="#f8f8f8";
update opportunity_status set text_color="#f8f8f8" where id<>4;

