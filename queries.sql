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
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId) ON DELETE CASCADE
)Engine=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- Complete
CREATE TABLE IF NOT EXISTS `ACC_DETAILS` (
	`ClientId` int(11) NOT NULL,
	`FiatCurrency` FLOAT(10) NOT NULL, -- $ amount
    PRIMARY KEY(`ClientId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId) ON DELETE CASCADE
)Engine=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Complete
CREATE TABLE IF NOT EXISTS `BITCOIN` (
	`ClientId` int(11) NOT NULL,
    `Units` Float(10) NOT NULL,
    PRIMARY KEY(`ClientId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId) ON DELETE CASCADE
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
    `TraderId` int(11), 
    PRIMARY KEY (`TransactionId`),
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId) ON DELETE CASCADE
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
    FOREIGN KEY (ClientId) REFERENCES USERS(ClientId) ON DELETE CASCADE
)Engine=InnoDB DEFAULT CHARSET=utf8;

-- GRANT ALL ON BITCOIN_TRANSACTION.* TO 'root'@'localhost';
INSERT INTO Users(UserName, FirstName, LastName, Password, Phone, Email, Type) VALUES('Admin', 'first_admin','last_admin',
 'gAAAAABhrThfm9QYGMSzwSd2KBsuGHkczMrE6ntkkiLC72RN5RbIp-xj2g3Sej9dlFfh3Oeo-QCDTCN4LDRxf5XA24ZjA7PHAQ==', 4699272570, 'iamadmin@gmail.com',
 'admin');

INSERT INTO Users(UserName, FirstName, LastName, Password, Phone, Email, Type) VALUES('Trader_one', 'first_trader','first_trader',
 'gAAAAABhrTgTwWOsuXpqPBdk2jaeDYJNRUKSMfxP7La1jjH7mo1v9PQoFlVa7UJ3icRfIkkLtSuBviCa-sVxBbY_o73vi688Xw==', 4699252577, 'iamtradertwo@gmail.com',
 'trader');

 INSERT INTO Users(UserName, FirstName, LastName, Password, Phone, Email, Type) VALUES('Trader_two', 'second_trader','second_trader',
 'gAAAAABhrTgrWXPWN_0j__PbN3-uzmmO4ywBT6dGgYjjy_ka9-BJoUewK9klB260q1uj8JpEu2DefPCUakAU_KZlND1XxZfaSA==', 4696053013, 'iamtradertwo@gmail.com',
 'trader');