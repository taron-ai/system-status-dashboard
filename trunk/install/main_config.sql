-- MySQL dump 10.13  Distrib 5.1.67, for redhat-linux-gnu (i386)
--
-- Host: localhost    Database: ssd
-- ------------------------------------------------------
-- Server version	5.1.67

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `main_config`
--

DROP TABLE IF EXISTS `main_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `config_name` varchar(50) NOT NULL,
  `friendly_name` varchar(50) NOT NULL,
  `config_value` varchar(1000) NOT NULL,
  `description` varchar(500) NOT NULL,
  `category` varchar(15) NOT NULL,
  `display` varchar(8) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=34 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_config`
--

LOCK TABLES `main_config` WRITE;
/*!40000 ALTER TABLE `main_config` DISABLE KEYS */;
INSERT INTO `main_config` VALUES (1,'recipient_name','Recipient Name','','The name that emails sent from SSD will be addressed to (usually the company name).','email_text','string'),(2,'greeting_incident_new','Greeting - Incident New','we are currently experiencing a service issue that is impacting one or more production services.  We are actively working to resolve this issue and will update you as progress is made on a resolution.  All known information about this incident is listed below.','The greeting that will accompany email messages about new incidents','email_text','string'),(3,'greeting_incident_update','Greeting - Incident Update','the purpose of this message is to update you on the status of a service issue that has impacted one or more production services.  All known information about this incident is listed below.','The greeting that will accompany email updates about existing incidents.','email_text','string'),(4,'recipient_incident','Recipient - Incident','','The email address that will receive incident notification emails.','email_addresses','string'),(5,'email_from','Sender Address','','The email address that email messages from SSD will be sent from.','email_addresses','string'),(6,'email_subject_incident','Subject - Incident','Incident Notification','The subject of email messages sent about incidents.','email_text','string'),(7,'alert','Alert Message','This is a test of the emergency broadcast system.','An optional message that will be prominently displayed on the SSD homepage.','notifications','string'),(9,'recipient_pager','Recipient - Pager','','The email address that will receive user generated incident notifications.  These messages will be constrained to 160 characters.','email_addresses','string'),(10,'message_success','Message Success','Your message has been successfully processed.  Our Engineers will be in touch.','The success message that will be displayed to a user who has submitted an incident report.','email_text','string'),(11,'message_error','Message Error','There was an error processing your message.  Please contact your system administrator.','The error message that will be displayed when a user submits an incident report but an error was encountered in processing the email.','email_text','string'),(12,'escalation','Escalation Path','THERE IS CURRENTLY NO ESCALATION PATH DEFINED.','','','string'),(13,'instr_report_incident','Instructions - Report Incident','When reporting an incident, please be mindful of the following guidelines:<br><br>\r\n<li>Enter your full name and email address in the fields provided.\r\n<li>Provide as much information as possible in the <b>Brief Incident Description</b> field.\r\n<li>The <b>Brief Incident Description</b> will be sent immediately to the 24x7 oncall engineer.\r\n<li>Additional information may be provided about the incident, which will be made available to the 24x7 team.\r\n<li>If an incident is confirmed by the oncall engineer, the dashboard will be updated.\r\n','Instructions that will optionally be displayed on the report incident screen.','notifications','string'),(14,'instr_create_incident','Instructions - Create Incident','When submitting a new incident, the following guidelines should be followed:\r\n<li>A description must be provided\r\n<li>A date and time must be provided (use the date the incident began)\r\n<li>At least one service must be selected\r\n<li>To broadcast a message about the incident, select the \"Broadcast Email\" checkbox.\r\n','Instructions that will optionally be displayed on the create incident page.','notifications','string'),(15,'logo_display','Display Company Logo','1','Whether or not to display a company logo.','functionality','boolean'),(16,'logo_url','Company Logo Url','http://www.babycenter.com/images/logos/logo_pin_263x85.png','The company logo to display','urls','string'),(17,'nav_display','Display Navigation Header','1','Whether or not to display the navigation header.','functionality','boolean'),(18,'contacts_display','Display Contacts','1','Whether or not to display the contacts link in the navigation header.','functionality','boolean'),(19,'report_incident_display','Display Report Incident','1','Whether or not to display the report incident link in the navigation header','functionality','boolean'),(20,'notify','Notify','1','Whether or not to enable email notifications.','functionality','boolean'),(21,'display_sched_maint_instr','Display Scheduled Maintenance Instructions','0','Instructions that will optinally be displayed on the schedule maintenance page.','notifications','boolean'),(22,'instr_sched_maint','Instructions - Scheduled Maintenance','nothing','Whether or not to display the scheduled maintenance help.','notifications','string'),(23,'recipient_maintenance','Recipient - Maintenance','toma@babycenter.com','The email address that will receive maintenance notification emails.','email_addresses','string'),(33,'file_upload_size','Maximum File Upload Size','1024','The maximum size (in bytes) allowed for user uploaded screenshots','file_uploads',''),(24,'email_subject_maintenance','Subject - Maintenance','Maintenance Notification','The subject line for maintenance notifications','email_text','string'),(25,'greeting_maintenance_new','Greeting - Maintenance New','We will be performing scheduled maintenance','The greeting that will accompany email messages about new maintenance notifications','email_text','string'),(26,'greeting_maintenance_update','Greeting - Maintenance Update','Update on scheduled maintenance','The greeting that will accompany email messages about existing maintenances','email_text','string'),(27,'ssd_url','SSD URL','http://status.babycenter.com','The SSD url that will be displayed on communication sent from this SSD instance','urls','string'),(28,'enable_uploads','Incident Report File Uploads','1','Whether or not to allow users to upload screenshots when reporting incidents','file_uploads','boolean'),(29,'upload_path','Incident Report Upload Path','','The path on the local (or shared) filesystem where image uploads will be saved (must be writeable by the user running the Apache webserver)','file_uploads','string'),(30,'display_alert','Display Alert Message','0','Whether or not to display the alert message on the SSD homepage','notifications','boolean'),(31,'display_report_incident_instr','Display Report Incident Instructions','0','Instructions that will optinally be displayed on the report incident page.','notifications','boolean'),(32,'display_create_incident_instr','Display Create Incident Instructions','0','Instructions that will optinally be displayed on the create incident page.','notifications','boolean');
/*!40000 ALTER TABLE `main_config` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-04-04 17:55:59
