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
  `display` varchar(8) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=21 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_config`
--

LOCK TABLES `main_config` WRITE;
/*!40000 ALTER TABLE `main_config` DISABLE KEYS */;
INSERT INTO `main_config` VALUES (1,'company','Company Name','test','','string'),(2,'greeting_new','Greeting - New','we are currently experiencing a service issue that is impacting one or more production services.  We are actively working to resolve this issue and will update you as progress is made on a resolution.  All known information about this incident is listed below.','','string'),(3,'greeting_update','Greeting - Update','the purpose of this message is to update you on the status of a service issue that has impacted one or more production services.  All known information about this incident is listed below.','','string'),(4,'email_to','Email To','','','string'),(5,'email_from','Email From','','','string'),(6,'email_subject','Email Subject','Incident Notification','','string'),(7,'maintenance','Maintenance Notification','none','','string'),(9,'page_to','Page To','','','string'),(10,'message_success','Message Success','Your message has been successfully processed.  Our Engineers will be in touch.','','string'),(11,'message_error','Message Error','There was an error processing your message.  Please contact your system administrator.','','string'),(12,'escalation','Escalation Path','THERE IS CURRENTLY NO ESCALATION PATH DEFINED.','','string'),(13,'report_incident_help','Help - Report Incident','When reporting an incident, please be mindful of the following guidelines:<br><br>\r\n<li>Enter your full name and email address in the fields provided.\r\n<li>Provide as much information as possible in the <b>Brief Incident Description</b> field.\r\n<li>The <b>Brief Incident Description</b> will be sent immediately to the 24x7 oncall engineer.\r\n<li>Additional information may be provided about the incident, which will be made available to the 24x7 team.\r\n<li>If an incident is confirmed by the oncall engineer, the dashboard will be updated.\r\n','','string'),(14,'create_incident_help','Help - Create Incident','When submitting a new incident, the following guidelines should be followed:\r\n<li>A description must be provided\r\n<li>A date and time must be provided (use the date the incident began)\r\n<li>At least one service must be selected\r\n<li>To broadcast a message about the incident, select the \"Broadcast Email\" checkbox.\r\n','','string'),(15,'logo_display','Display Logo','0','','boolean'),(16,'logo_url','Display Logo Url','','','string'),(17,'nav_display','Display Nav','1','','boolean'),(18,'contacts_display','Display Contacts','1','','boolean'),(19,'report_incident_display','Display Report Incident','1','','boolean'),(20,'notify','Notify','1','','boolean');
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

-- Dump completed on 2013-03-07 11:51:47
