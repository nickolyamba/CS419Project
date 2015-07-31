
####################### Get Primary and it's type ######################
SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type
FROM   pg_index i
JOIN   pg_attribute a ON a.attrelid = i.indrelid
                     AND a.attnum = ANY(i.indkey)
WHERE  i.indrelid = 'company'::regclass
AND    i.indisprimary;

####################### AutoVacuuming #################################
# http://www.postgresonline.com/journal/archives/139-Enable-and-Disable-Vacuum-per-table.html
# https://lob.com/blog/supercharge-your-postgresql-performance/
--disable auto vacuum
ALTER TABLE sometable SET (
  autovacuum_enabled = false, toast.autovacuum_enabled = false
);

--enable auto vacuum
ALTER TABLE sometable SET (
  autovacuum_enabled = true, toast.autovacuum_enabled = true
);

ALTER TABLE table_name SET (autovacuum_vacuum_scale_factor = 0.0);  
ALTER TABLE table_name SET (autovacuum_vacuum_threshold = 5000);  
ALTER TABLE table_name SET (autovacuum_analyze_scale_factor = 0.0);  
ALTER TABLE table_name SET (autovacuum_analyze_threshold = 5000);

# number of rows:
SELECT reltuples FROM pg_class WHERE oid = 'public.company'::regclass;  
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

INSERT INTO employee (emp_name, dep_id)
            VALUES ('dilbert', 1) RETURNING emp_id;

emp_id
------
  1

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('Paul', 32, 'California', 20000.00);

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('Allen', 25, 'Texas', 15000.00);

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('Teddy', 23, 'Norway', 20000.00);

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('Mark', 25, 'Rich-Mond ', 65000.00);

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('David', 27, 'Texas', 85000.00);

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('Kim', 22, 'South-Hall', 45000.00);

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('James', 24, 'Houston', 10000.00);

INSERT INTO COMPANY (NAME,AGE,ADDRESS,SALARY)
VALUES ('Michael', 37, 'Berkeley', 38000.00), 
('Zigmund', 21, 'Oakland', 45000.00),
('Ying', 22, 'San Pablo', 45000.00),
('Cristle', 25, 'Daily City', 70000.00),
('Rachel', 35, 'San Bernandino', 35000.00),
('Nick', 24, 'Carmel', 15000.00);
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


