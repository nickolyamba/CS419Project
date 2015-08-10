#!/usr/bin/python

import exceptions
import sys
import MySQLdb
import itertools
from column import Column

'''**************************************************
* Class MysqlDB inherits object class
*
* Purpose:  Connect to the database, define, and i
* 					implements queries
**************************************************'''
class MysqlDB(object):
	# connect to DB when application is started and DB object is initialized
	def __init__ (self):
		try:
			self.db = MySQLdb.Connection(host="sql3.freesqldatabase.com", user="sql386176", 
				passwd="yD1!wG7%", db="sql386176")
		except MySQLdb.Error, ex:
			print 'Error  %s' % ex
			sys.exit(1)
	
	
	# returns list of all tables in the database	
	def list_all_tables(self):
		cur = self.db.cursor()
		cur.execute("SELECT table_name FROM information_schema.tables \
							WHERE \
								table_type = 'base table' AND table_schema = 'sql386176' \
							ORDER BY table_name")
		tables = cur.fetchall()
		cur.close()
		return tables
	
	
	# returns list of all column names in the table	
	def list_columns(self, table_name):
		columns_list = []
		cur = self.db.cursor()
		# get lists of column_name, type, charLen for CHAR, precision for numeric entries, nullable
		query_string = "SELECT column_name, data_type, character_maximum_length, numeric_precision, \
										is_nullable from information_schema.columns WHERE table_name = %s;"
		cur.execute(query_string, (table_name,))
		columns_tuple = cur.fetchall()
		
		# http://stackoverflow.com/questions/12379221
		cur.execute("SELECT k.COLUMN_NAME \
			FROM information_schema.table_constraints t \
			INNER JOIN information_schema.key_column_usage k \
			USING ( constraint_name, table_schema, table_name )  \
			WHERE t.constraint_type =  'PRIMARY KEY' \
			AND t.table_name = %s;",  (table_name,))
		# fetch list of primary keys	
		columns_prim_tuple = cur.fetchall()
		
		#http://www.tocker.ca/2013/05/02/fastest-way-to-count-rows-in-a-table.html
		#cur.execute("SELECT TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = %s",  (table_name,))
		cur.execute("SELECT COUNT(*) FROM {0}".format (table_name))
		
		row_count = cur.fetchone()
		
		cur.close()
		
		# traverese tuple of tuples to list of strings
		# http://stackoverflow.com/questions/1663807
		for col, col_prim in itertools.izip_longest(columns_tuple, columns_prim_tuple):
			# create Column object
			column = Column()
			# convert tuple item into string
			col = list(col)
			col[0] = col[0].strip("(),'")
			
			# col_prim is None, do not append assign None
			if col_prim:
				col_prim = list(col_prim)
				col_prim[0] = col_prim[0].strip("(),'")
				column.primary_key = col_prim[0]
			else:
				column.primary_key = ''
			
			# populate column object
			column.name = col[0]
			column.type = col[1]
			column.charLen = col[2]
			column.precision = col[3]
			column.nullable = "NULL" if col[4] == "YES" else "NOT NULL"
			columns_list.append(column)
		
		return columns_list, row_count[0]
	
	
	def list_records(self, table_name, sort_column, sort_direction, offset, limit):
		cur = self.db.cursor()
		query_string = "SELECT * from `{0}` ORDER BY {1} {2} LIMIT {3}, {4};" .format(table_name, sort_column, sort_direction, offset, limit)
		cur.execute(query_string)
		rows = cur.fetchall()
		return rows
	
	
	def add_record(self, table_name, col_dict, id_column):
		new_row_id = 0
		cur = self.db.cursor()
		# get column names and values from the dictionary
		# http://stackoverflow.com/questions/29461933
		columns = col_dict.keys()
		values = tuple(col_dict[column] for column in columns)
		# http://stackoverflow.com/questions/16253938
		query  = "INSERT INTO {0} ({1}) VALUES ({2})".format(table_name, ', '.join(columns), ', '.join(["%s"]*len(columns)))
		try:
			cur.execute(query, values)
			new_row_id = cur.lastrowid
			self.db.commit()
		except MySQLdb.Error, ex:
			self.db.rollback()
			return str(ex), False
		return new_row_id, True
	
	
	def edit_record(self, table_name, set_dict, where_dict):
		cur = self.db.cursor()
		# create tuple containing values
		data_list =  set_dict.values() + where_dict.values()
		
		# http://stackoverflow.com/questions/11517106
		query  = 'UPDATE {0} SET {1} WHERE {2} LIMIT 1'.format(table_name, 
																										', '.join('{0}=%s'.format(col) for col in set_dict), 
																								' AND '.join('{0}=%s'.format(col) for col in where_dict))
		try:
			cur.execute(query, data_list)
			self.db.commit()
			edited_row_id = cur.lastrowid
		except MySQLdb.Error, ex:
			self.db.rollback()
			return str(ex), False
		
		return True
		
	def delete_record(self, table_name, where_dict):
		cur = self.db.cursor()
		deleted_row = ['row has been deleted']
		data_list =  where_dict.values()
		
		query  = 'DELETE FROM {0} WHERE {1}'.format(table_name, ' AND '.join('{0}=%s'.format(col) for col in where_dict))
		try:
			cur.execute(query, data_list)
			self.db.commit()
			#deleted_row = cur.fetchone()
		except MySQLdb.Error, ex:
			self.db.rollback()
			return str(ex), False
			
		return deleted_row, True
		
		
	def closeConn(self):
		self.db.close()