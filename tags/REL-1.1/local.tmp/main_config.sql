SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `main_config`
-- ----------------------------
DROP TABLE IF EXISTS `main_config`;
CREATE TABLE `main_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `config_name` varchar(50) NOT NULL,
  `config_value` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of main_config
-- ----------------------------
INSERT INTO `main_config` VALUES ('1', 'company', '<enter company name>');
INSERT INTO `main_config` VALUES ('2', 'greeting_new', 'we are currently experiencing a service issue that is impacting one or more production services.  We are actively working to resolve this issue and will update you as progress is made on a resolution.  All known information about this incident is listed below.');
INSERT INTO `main_config` VALUES ('3', 'greeting_update', 'the purpose of this message is to update you on the status of a service issue that has impacted one or more production services.  All known information about this incident is listed below.');
INSERT INTO `main_config` VALUES ('4', 'email_to', '<enter recipient email address>');
INSERT INTO `main_config` VALUES ('5', 'email_from', '<enter from email address>');
INSERT INTO `main_config` VALUES ('6', 'email_subject', 'Incident Notification');
INSERT INTO `main_config` VALUES ('7', 'maintenance', 'none');
INSERT INTO `main_config` VALUES ('9', 'page_to', '<enter pager email address>');
INSERT INTO `main_config` VALUES ('10', 'message_success', 'Your message has been successfully processed.  Our Engineers will be in touch.');
INSERT INTO `main_config` VALUES ('11', 'message_error', 'There was an error processing your message.  Please contact your system administrator.');

