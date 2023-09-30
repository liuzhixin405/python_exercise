-- Active: 1696060028456@@127.0.0.1@3306
use `spider`;

drop table if EXISTS `tb_top_movie`;

create table `tb_top_movie` (
    `mov_id` int UNSIGNED AUTO_INCREMENT COMMENT 'No',
    `title` varchar(50) not null COMMENT 'title',
    `rating` DECIMAL(3,1) not null COMMENT 'score',
    `subject` varchar(200) DEFAULT '' COMMENT 'subject',
    PRIMARY key (`mov_id`)
    ) engine=innodb COMMENT='TopMovie250'