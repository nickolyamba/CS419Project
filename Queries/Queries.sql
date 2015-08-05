
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
SELECT column_name, data_type from information_schema.columns 
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

##################### Chemical ######################

CREATE TABLE Chemical(
	chemID SERIAL NOT NULL,
	name TEXT NOT NULL UNIQUE,
	molWeight REAL,
	suppID integer,
	CONSTRAINT pk_chemID PRIMARY KEY (chemID),
	CONSTRAINT fk_suppID FOREIGN KEY (suppID)
	REFERENCES supplier(suppID) ON DELETE CASCADE
);

INSERT INTO chemical (name, molWeight, suppID) VALUES
('Lithium Sulfide',45.95, 1),
('NewChemical',60,1),
('VeryNewChem',65.5, 1),
('Lithium Carbonate',65.32,2),
('Lithium Something',56,3),
('Crabonate Somth',64,4),
('1,3-Dioxolane',74.08,1),
('Acetone',58.08,7),
('Ammonium Chloride',53.49,6),
('1,2-Dimethoxyethane (DME)',90.12,1),
('Dimethyl Carbonate (DMC)',90.08,2),
('Ethylene Carbonate (EC)',88.06,3),
('Lithium Chloride',42.39,5);

(36,'Lithium Nitrate','7790-69-4',68.95,2.3800,NULL),
(37,'Water Deionized','7732-18-5',18.02,1.0000,NULL),
(13,'Lithium Malonate','4564-456',50,1.3000,'comment #1'),
(14,'Lithium Phosphate','456-987',65,1.2300,'comment #5'),
(15,'Lithium Hydroxide','456654-78',68,3.2100,'comment #17'),
(22,'Sulfur','456-312',32.07,2.0100,''),
(23,'Lithium','123-312',7.98,2.1000,''),
(24,'Novel Chem','456-456',35,1.0200,''),
(25,'Chemical#5','456-645',54.45,1.1000,'');


##################### Solution ######################

CREATE TABLE Solution(
  solutionID SERIAL NOT NULL,
  name TEXT NOT NULL,
  CONSTRAINT pk_soluID PRIMARY KEY (solutionID)
);

INSERT INTO solution (name) VALUES
('12M S as Li2S5 in water'),
('1M LiTFSI in 1,3-Dioxolane'),
('1M LiTFSI in EC:DMC (1:1)'),
('1M LiTFSI in EC:DMC (1:1)'),
('LiCl + NH4Cl in Dioxolane'),
('1M Barium Cholride in water'),
('2M Lithium Hydroxide in water'),
('3M Li2S4 in water'),
('3M Li2S4 in water-org solvent'),
('1M Aluminum Sulfate in water')
('12M S as Li2S5 in ethanol'),
('1M LiTFSI in hydrozine'),
('1M LiTFSI in ethylamine'),
('1M LiTFSI in water)');

##################### ChemSolution ######################

CREATE TABLE chem_solu(
  chemID integer NOT NULL REFERENCES chemical(chemID) ON UPDATE CASCADE ON DELETE CASCADE,
  solutionID integer NOT NULL REFERENCES solution(solutionID) ON UPDATE CASCADE ON DELETE CASCADE,
  volume numeric NOT NULL DEFAULT 1,
  CONSTRAINT pk_chem_solu PRIMARY KEY (chemID, solutionID)
);

INSERT INTO chem_solu (chemID, solutionID, volume) VALUES
(1, 1, 2),
(1, 2, 10),
(1, 3, 20),
(1, 4, 16),
(1, 5, 20),
(1, 6, 25),
(1, 7, 16),
(1, 8, 14),
(1, 9, 2),
(7, 2, 5),
(7, 3, 79),
(9, 3, 25),
(13, 1, 32),
(22, 1, 45),
(25, 3, 56),
(27, 3, 2),
(26, 6, 21),
(4, 2, 4),
(7, 4, 98);