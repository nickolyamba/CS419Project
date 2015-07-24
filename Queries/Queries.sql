####################### Pagination #1 ######################
# http://sqlperformance.com/2015/01/t-sql-queries/pagination-with-offset-fetch
SELECT * FROM company 
ORDER BY id ASC
OFFSET 1 FETCH NEXT 2 ROWS ONLY

SELECT * FROM company 
ORDER BY id ASC OFFSET 1 LIMIT 2

####################### List All Columns ######################
SELECT column_name from information_schema.columns 
WHERE table_name='company';

####################### List All Tables ######################
SELECT table_name 
FROM information_schema.tables 
WHERE table_type = 'BASE TABLE' 
    AND table_schema = 'public' 
ORDER BY table_type, table_name

####################### Company ######################
CREATE TABLE COMPANY(
   ID  SERIAL PRIMARY KEY,
   NAME           TEXT      NOT NULL,
   AGE            INT       NOT NULL,
   ADDRESS        CHAR(50),
   SALARY         REAL
);

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ( 'Paul', 32, 'California', 20000.00 );

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('Allen', 25, 'Texas', 15000.00 );

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('Teddy', 23, 'Norway', 20000.00 );

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ( 'Mark', 25, 'Rich-Mond ', 65000.00 );

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ( 'David', 27, 'Texas', 85000.00 );


INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ( 'Kim', 22, 'South-Hall', 45000.00 );

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ( 'James', 24, 'Houston', 10000.00 );

####################### Supplier ######################
CREATE TABLE SUPPLIER (
  suppID SERIAL PRIMARY KEY,
  name CHAR(255) NOT NULL,
  website CHAR(255) DEFAULT NULL,
  phone CHAR(50) DEFAULT NULL
);

INSERT INTO supplier (name, website, phone) VALUES 
('Aldrich','www.aldrich.ru','510-564-5678'),
('VWR','www.vwr.com','123-456-9875'),
('McMaster','www.mcmaster.com','925-123-6547'),
('Etsy','www.etsy.com','456-894-4561'),
('Intel','www.intel.com','645-54-43543'),
('Amazon','www.amazon.com','432-543-4343'),
('Ebay','www.ebay.com','945-456-4564');


