CREATE DATABASE IF NOT EXISTS `BITCOIN_TRANSACTION` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

USE BITCOIN_TRANSACTION;

-- Complete
CREATE TABLE IF NOT EXISTS `USERS` (
	`ClientId` int(11) NOT NULL AUTO_INCREMENT,
    `UserName` varchar(100) NOT NULL,
    `FirstName` varchar(100) NOT NULL,
    `LastName` varchar(100) NOT NULL,
    `Password` varchar(100) NOT NULL,
	`Phone` varchar(100) NOT NULL,
	`Email` varchar(100) NOT NULL,
	`Type` varchar(100) NOT NULL, -- admin, trader, user:(gold, silver)
    PRIMARY KEY(`ClientId`)
)Engine=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Complete
CREATE TABLE IF NOT EXISTS `ADDRESS` (
	`ClientId` int(11) NOT NULL,
    `StreetAddress` varchar(100) NOT NULL,
    `City` varchar(100) NOT NULL,
	`State` varchar(100) NOT NULL,
	`ZipCode` int(11) NOT NULL,
    PRIMARY KEY(`ClientId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId)
)Engine=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- Complete
CREATE TABLE IF NOT EXISTS `ACC_DETAILS` (
	`ClientId` int(11) NOT NULL,
	`FiatCurrency` FLOAT(10) NOT NULL, -- $ amount
    PRIMARY KEY(`ClientId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId)
)Engine=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

Select * from ACC_DETAILS;

-- Complete
CREATE TABLE IF NOT EXISTS `BITCOIN` (
	`ClientId` int(11) NOT NULL,
    `Units` Float(10) NOT NULL,
    PRIMARY KEY(`ClientId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId)
)Engine=InnoDB DEFAULT CHARSET=utf8;

-- Complete
CREATE TABLE IF NOT EXISTS `TRANSACTION` (
	`ClientId` int(11) NOT NULL, -- Who is initiating the transaction
    `TransactionId` varchar(100) NOT NULL,
    `TransactionType` varchar(10) NOT NULL, -- Buy or sell
	`Date` TIMESTAMP NOT NULL,
	`CommisionPaid` FLOAT(10) NOT NULL,
    `CommisionType` FLOAT(10) NOT NULL,
    `RecipientId` int(10) NOT NULL,
    `BitCoinAmount` FLOAT(10) NOT NULL,
    `Status` varchar(20) NOT NULL,
    `CommissionRateType` varchar(50) NOT NULL,
    PRIMARY KEY (`TransactionId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId)
)Engine=InnoDB DEFAULT CHARSET=utf8;

-- Complete
CREATE TABLE IF NOT EXISTS `SELLER` (
	`ClientId` int(11) NOT NULL,
    `Units` Float(10) NOT NULL,
	`Date` TIMESTAMP NOT NULL,
	`CommisionPaid` FLOAT(10) NOT NULL,
    `CommisionType` FLOAT(10) NOT NULL,
    `CommissionRateType` varchar(50) NOT NULL,
    PRIMARY KEY(`ClientId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId)
)Engine=InnoDB DEFAULT CHARSET=utf8;


Select * from Transaction;
select *
from seller;

-- INSERT INTO `USERS` (`UserName`, `FirstName`, `LastName`,`Password`,`Phone`, `Email`, `Type`)
-- VALUES ('Admin', 'first_admin', 'last_admin', '@dm1n', '4699272570','iamadmin@gmail.com', 'admin');

INSERT INTO `USERS` (`UserName`, `FirstName`, `LastName`,`Password`,`Phone`, `Email`, `Type`) 
VALUES ('Trader_two', 'second_trader', 'second_trader', 'trader@2', '4696053013','iamtradertwo@gmail.com', 'trader');

-- GRANT ALL ON BITCOIN_TRANSACTION.* TO 'root'@'localhost';

INSERT INTO `Transaction` (`ClientId`,`TransactionId`,`TransactionType`, `Date`, `CommisionPaid`, `CommisionType`, `RecipientId`, `BitCoinAmount`,`Status`) 
VALUES (5, 'random1', 'BUY', now(), 3992.972, 7, 7, '1','pending');

Select * from ACC_DETAILS;


Select * from TRANSACTION;
Select * from Seller;


select * from BITCOIN;
INSERT INTO `Transaction` (`ClientId`,`TransactionId`,`TransactionType`, `Date`, `CommisionPaid`, `CommisionType`, `RecipientId`, `BitCoinAmount`,`Status`) 
VALUES (7, 'random9', 'BUY', now(), 3500, 5, 8, '2','pending');

INSERT INTO `Transaction` (`ClientId`,`TransactionId`,`TransactionType`, `Date`, `CommisionPaid`, `CommisionType`, `RecipientId`, `Status`) 
VALUES (6, 'random2', 'BUY', now(), 5500, 'Currency', 7, 'pending');

INSERT INTO `Transaction` (`ClientId`,`TransactionId`,`TransactionType`, `Date`, `CommisionPaid`, `CommisionType`, `RecipientId`, `Status`) 
VALUES (5, 'random3', 'BUY', now(), 5500, 'Currency', 8, 'completed');

INSERT INTO `Transaction` (`ClientId`,`TransactionId`,`TransactionType`, `Date`, `CommisionPaid`, `CommisionType`, `RecipientId`, `Status`) 
VALUES (5, 'random5', 'BUY', now(), 5500, 'Currency', 9, 'completed');

Select * from T;

Select * from users;

select *
from Transaction;
