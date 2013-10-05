SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `main_config_email`
-- ----------------------------
DROP TABLE IF EXISTS `main_config_email`;
CREATE TABLE `main_config_email` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `enabled` tinyint(1) NOT NULL,
  `email_format` tinyint(1) NOT NULL,
  `from_address` varchar(100) NOT NULL,
  `text_pager` varchar(100) NOT NULL,
  `incident_greeting` varchar(1000) NOT NULL,
  `incident_update` varchar(1000) NOT NULL,
  `maintenance_greeting` varchar(1000) NOT NULL,
  `maintenance_update` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of main_config_email
-- ----------------------------
INSERT INTO `main_config_email` VALUES ('1', '1', '0', '', '', 'test', 'test', 'test', 'test');

-- ----------------------------
-- Table structure for `main_config_escalation`
-- ----------------------------
DROP TABLE IF EXISTS `main_config_escalation`;
CREATE TABLE `main_config_escalation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `enabled` tinyint(1) NOT NULL,
  `instructions` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of main_config_escalation
-- ----------------------------
INSERT INTO `main_config_escalation` VALUES ('1', '1', 'If you reported an incident via the <a href=\"/report\">report incident</a> link and have not received confirmation that our engineers are investigating the problem, please follow the below escalation path. If you are unable to make contact, please leave a voice message, wait 5 minutes for a response, and escalate to the next contact on the list.');

-- ----------------------------
-- Table structure for `main_config_ireport`
-- ----------------------------
DROP TABLE IF EXISTS `main_config_ireport`;
CREATE TABLE `main_config_ireport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `enabled` tinyint(1) NOT NULL,
  `email_enabled` tinyint(1) NOT NULL,
  `instructions` varchar(500) NOT NULL,
  `submit_message` varchar(500) NOT NULL,
  `upload_enabled` tinyint(1) NOT NULL,
  `upload_path` varchar(500) NOT NULL,
  `file_size` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of main_config_ireport
-- ----------------------------
INSERT INTO `main_config_ireport` VALUES ('1', '1', '0', 'Please be as descriptive as possible', 'Thank you for your support!\r\n\r\nWe\'ll be in touch!', '0', '', '1');

-- ----------------------------
-- Table structure for `main_config_logo`
-- ----------------------------
DROP TABLE IF EXISTS `main_config_logo`;
CREATE TABLE `main_config_logo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(1000) NOT NULL,
  `logo_enabled` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of main_config_logo
-- ----------------------------
INSERT INTO `main_config_logo` VALUES ('1', 'http://www.test.com/logo.png', '1');

-- ----------------------------
-- Table structure for `main_config_message`
-- ----------------------------
DROP TABLE IF EXISTS `main_config_message`;
CREATE TABLE `main_config_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `main` varchar(1000) NOT NULL,
  `main_enabled` tinyint(1) NOT NULL,
  `alert` varchar(1000) NOT NULL,
  `alert_enabled` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of main_config_message
-- ----------------------------
INSERT INTO `main_config_message` VALUES ('1', 'This dashboard displays status information for all critical services. The dashboard will be updated whenever status information for any service changes. Please check back here at any time to obtain current status information.<br><br>To report a problem with a service, please use the <a href=\"/report\">report incident</a> link. If you have reported an incident and have not received a response, please <a href=\"/escalation\">escalate</a> the issue.', '1', 'We are currently experiencing a level 1 issue.  Baten down the hatches.', '0');

-- ----------------------------
-- Table structure for `main_config_systemurl`
-- ----------------------------
DROP TABLE IF EXISTS `main_config_systemurl`;
CREATE TABLE `main_config_systemurl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(1000) NOT NULL,
  `url_enabled` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of main_config_systemurl
-- ----------------------------
INSERT INTO `main_config_systemurl` VALUES ('1', '/foo/bar1', '1');

-- ----------------------------
-- Table structure for `main_status`
-- ----------------------------
DROP TABLE IF EXISTS `main_status`;
CREATE TABLE `main_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `status` (`status`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of main_status
-- ----------------------------
INSERT INTO `main_status` VALUES ('1', 'planning');
INSERT INTO `main_status` VALUES ('2', 'open');
INSERT INTO `main_status` VALUES ('3', 'closed');
INSERT INTO `main_status` VALUES ('4', 'started');
INSERT INTO `main_status` VALUES ('5', 'completed');

-- ----------------------------
-- Table structure for `main_type`
-- ----------------------------
DROP TABLE IF EXISTS `main_type`;
CREATE TABLE `main_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `type` (`type`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of main_type
-- ----------------------------
INSERT INTO `main_type` VALUES ('1', 'incident');
INSERT INTO `main_type` VALUES ('2', 'maintenance');