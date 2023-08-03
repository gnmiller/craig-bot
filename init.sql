DROP DATABASE IF EXISTS `craig-bot`;
CREATE DATABASE IF NOT EXISTS `craig-bot`;
use `craig-bot`;
CREATE TABLE IF NOT EXISTS `guilds` (
		`guild_id` VARCHAR(64) NOT NULL UNIQUE,
		`guild_name` VARCHAR(65),
		`added` DATE DEFAULT (CURRENT_DATE),
		`uniq_id` INTEGER AUTO_INCREMENT,
		PRIMARY KEY (`uniq_id`) );
                    
CREATE TABLE IF NOT EXISTS `opts` (
		`guild_id` VARCHAR(64),
		`opt_name` VARCHAR(32),
		`opt_val` VARCHAR(128),
		`set_by` VARCHAR(64),
		UNIQUE KEY `opts_id` (opt_name,guild_id)
);
                    
CREATE TABLE IF NOT EXISTS `open_ai` (
		`guild_id` VARCHAR(64),
		`user_id` INTEGER,
		`model` VARCHAR(32),
		`prompt` VARCHAR(1024),
		`date` DATE DEFAULT (CURRENT_DATE)
);
                    
CREATE TABLE IF NOT EXISTS auth_user (
		`guild_id` VARCHAR(64),
		`user_id` VARCHAR(64),
		`added_by` VARCHAR(64),
		`date` DATE DEFAULT (CURRENT_DATE),
		`role` VARCHAR(64),
		UNIQUE KEY `auth_id` (`guild_id`,`user_id`)
);
                        
CREATE TABLE IF NOT EXISTS auth_roles (
		`guild_id` VARCHAR(64),
		`role_id` VARCHAR(64),
		`added_by` VARCHAR(64),
		`date` DATE DEFAULT (CURRENT_DATE),
		`role` VARCHAR(64),
		UNIQUE KEY `auth_id` (`guild_id`,`role_id`)
);

CREATE TABLE IF NOT EXISTS dice_data (
        `id` INTEGER PRIMARY KEY AUTO_INCREMENT UNIQUE,
        `guild_id` VARCHAR(64),
		`user_id` VARCHAR(64),
        `num_sides` INTEGER,
        `result` INTEGER
);            
