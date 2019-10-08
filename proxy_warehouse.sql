/*
 Navicat MySQL Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80011
 Source Host           : localhost:3306
 Source Schema         : proxy_warehouse

 Target Server Type    : MySQL
 Target Server Version : 80011
 File Encoding         : 65001

 Date: 06/10/2019 17:15:15
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for proxy_info
-- ----------------------------
DROP TABLE IF EXISTS `proxy_info`;
CREATE TABLE `proxy_info`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `proxy_ip` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `proxy_port` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `addr` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `enqueue` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `proxy_ip`(`proxy_ip`, `proxy_port`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3891 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for usage_log
-- ----------------------------
DROP TABLE IF EXISTS `usage_log`;
CREATE TABLE `usage_log`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `proxy_id` int(11) NOT NULL,
  `target_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `start_time` timestamp(0) NULL DEFAULT NULL,
  `elapsed_time` float(10, 3) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `usage_proxy`(`proxy_id`) USING BTREE,
  CONSTRAINT `usage_proxy` FOREIGN KEY (`proxy_id`) REFERENCES `proxy_info` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 11202 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- View structure for high_availability_proxy
-- ----------------------------
DROP VIEW IF EXISTS `high_availability_proxy`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `high_availability_proxy` AS select `usage_log`.`proxy_id` AS `proxy_id`,`proxy_info`.`proxy_ip` AS `proxy_ip`,`proxy_info`.`proxy_port` AS `proxy_port`,count(`usage_log`.`proxy_id`) AS `number_of_successful`,avg(`usage_log`.`elapsed_time`) AS `avg_elapsed`,`t`.`number_of_use` AS `number_of_use` from ((`usage_log` join (select `usage_log`.`proxy_id` AS `proxy_id`,count(`usage_log`.`proxy_id`) AS `number_of_use` from `usage_log` group by `usage_log`.`proxy_id`) `t`) join `proxy_info`) where ((`usage_log`.`elapsed_time` > 0) and (`t`.`proxy_id` = `usage_log`.`proxy_id`) and (`usage_log`.`proxy_id` = `proxy_info`.`id`)) group by `usage_log`.`proxy_id` order by (count(`usage_log`.`proxy_id`) / `t`.`number_of_use`) desc,avg(`usage_log`.`elapsed_time`),`t`.`number_of_use`;

-- ----------------------------
-- Procedure structure for Insert_proxy
-- ----------------------------
DROP PROCEDURE IF EXISTS `Insert_proxy`;
delimiter ;;
CREATE PROCEDURE `Insert_proxy`(IN `proxy_ip` varchar(15),IN `proxy_port` varchar(15),IN `proxy_addr` varchar(15))
BEGIN
	#Routine body goes here...
	declare a int default 1;
	select count(id)+1 into a from proxy_info;
	insert into proxy_info(id, proxy_ip, proxy_port, addr)
	VALUES(a, proxy_ip, proxy_port, proxy_addr);
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for Select_HIA
-- ----------------------------
DROP PROCEDURE IF EXISTS `Select_HIA`;
delimiter ;;
CREATE PROCEDURE `Select_HIA`(IN `amount` int)
BEGIN
	#Routine body goes here...
	select proxy_id, proxy_ip, proxy_port
	from high_availability_proxy
	limit amount;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for Select_rarely_used
-- ----------------------------
DROP PROCEDURE IF EXISTS `Select_rarely_used`;
delimiter ;;
CREATE PROCEDURE `Select_rarely_used`(IN `amount` int,IN `i_interval` int)
BEGIN
	#Routine body goes here...
SELECT
	proxy_info.id,
	proxy_info.proxy_ip,
	proxy_info.proxy_port 
FROM
	proxy_info 
WHERE
	proxy_info.id NOT IN ( SELECT proxy_id FROM usage_log )
	UNION ALL
		(
	SELECT
		proxy_info.id,
		proxy_info.proxy_ip,
		proxy_info.proxy_port 
	FROM
		proxy_info,
		usage_log 
	WHERE
		proxy_info.id = usage_log.proxy_id 
	GROUP BY
		proxy_info.id 
	HAVING
		UNIX_TIMESTAMP(
			NOW()) - UNIX_TIMESTAMP(
		max( usage_log.start_time )) > i_interval
	ORDER BY
	max( usage_log.start_time )) limit amount;
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
