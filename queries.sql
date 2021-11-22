CREATE DATABASE IF NOT EXISTS `BITCOIN_TRANSACTION` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

USE BITCOIN_TRANSACTION;

-- Complete
CREATE TABLE IF NOT EXISTS `USERS` (
	`ClientId` int(11) NOT NULL AUTO_INCREMENT,
    `UserName` varchar(100) NOT NULL,
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
    `TotalAmount` FLOAT(10) NOT NULL, -- Bticoin amt + Fiat currency
	`FiatCurrecy` FLOAT(10) NOT NULL, -- $ amount
    PRIMARY KEY(`ClientId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId)
)Engine=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

Select * from Users;

-- Complete
CREATE TABLE IF NOT EXISTS `BITCOIN` (
	`ClientId` int(11) NOT NULL,
    `BitCoinType` varchar(100) NOT NULL,
    `Units` int(11) NOT NULL,
    PRIMARY KEY(`ClientId`,`BitCoinType`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId)
)Engine=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Complete
CREATE TABLE IF NOT EXISTS `TRANSACTION` (
	`ClientId` int(11) NOT NULL, -- Who is initiating the transaction
    `TransactionId` varchar(100) NOT NULL,
    `TransactionType` varchar(10) NOT NULL, -- Buy or sell
	`Date` TIMESTAMP NOT NULL,
	`CommisionPaid` FLOAT(10) NOT NULL,
    `CommisionType` varchar(10) NOT NULL,
    `RecipientId` varchar(10) NOT NULL,
    `Status` varchar(20) NOT NULL,
    PRIMARY KEY (`TransactionId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId)
)Engine=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO `Transaction` (`ClientId`,`TransactionId`,`TransactionType`, `Date`, `CommisionPaid`, `CommisionType`, `RecipientId`, `Status`) 
VALUES (19, 'random1', 'BUY', now(), 3500, 'Currency', 20, 'pending');

INSERT INTO `Transaction` (`ClientId`,`TransactionId`,`TransactionType`, `Date`, `CommisionPaid`, `CommisionType`, `RecipientId`, `Status`) 
VALUES (20, 'random2', 'BUY', now(), 5500, 'Currency', 22, 'pending');

INSERT INTO `Transaction` (`ClientId`,`TransactionId`,`TransactionType`, `Date`, `CommisionPaid`, `CommisionType`, `RecipientId`, `Status`) 
VALUES (20, 'random3', 'BUY', now(), 5500, 'Currency', 24, 'completed');

INSERT INTO `Transaction` (`ClientId`,`TransactionId`,`TransactionType`, `Date`, `CommisionPaid`, `CommisionType`, `RecipientId`, `Status`) 
VALUES (19, 'random5', 'BUY', now(), 5500, 'Currency', 23, 'completed');


Select * from Address;
SELECT * FROM Transaction WHERE ClientId=19 AND DATE < NOW() ORDER BY DATE ASC;
Select * from Users;
SELECT * FROM Address;


-- INSERT INTO `USERS` (`UserName`,`Password`,`Phone`, `Email`, `Type`) VALUES ('Admin', '@dm1n', '4699272570','iamadmin@gmail.com', 'admin');

-- INSERT INTO `USERS` (`UserName`,`Password`,`Phone`, `Email`, `Type`) VALUES ('Trader_two', 'trader@2', '4699252577','iamtradertwo@gmail.com', 'trader');

-- GRANT ALL ON BITCOIN_TRANSACTION.* TO 'root'@'localhost';


