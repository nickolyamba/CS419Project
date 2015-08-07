#!/usr/bin/python

'''**************************************
# Name: Nikolay Goncharenko, Rory Bresnahan
# Email: goncharn@onid.oregonstate.edu
# Class: CS419 - Capstone Project
# Assignment: Python Ncurses UI for 
# MySQL/PostgreSQL Database Management
**************************************'''
import exceptions
import sys
import MySQLdb


'''**************************************************
* Class Database inherits object class
*
* Purpose:  Connect to the database and query it
**************************************************'''
class MysqlDB(object):
	def __init__ (self):
		try:
			self.db =MySQLdb.Connection(host="sql3.freesqldatabase.com", user="sql386176", 
				passwd="yD1!wG7%", db="sql386176")
		except Error, e:
			print 'Error %s' % e
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
		query_string = "SELECT column_name, data_type, character_maximum_length, numeric_precision, is_nullable from information_schema.columns \
										WHERE table_name = %s;"
		cur.query(query_string, (table_name,))
		columns_tuple = cur.fetchall()
		
		# SHOW COLUMNS FROM address
		cur.execute("SELECT a.attname FROM  pg_index i \
			JOIN  pg_attribute a ON a.attrelid = i.indrelid \
			AND a.attnum = ANY(i.indkey) \
			WHERE  i.indrelid = %s::regclass \
			AND  i.indisprimary;",  (table_name,))
			
		columns_prim_tuple = cur.fetchall()
		
		cur.close()
		# traverese tuple of tuples to list of strings
		# http://stackoverflow.com/questions/1663807
		for col, col_prim in itertools.izip_longest(columns_tuple, columns_prim_tuple):
			# create Column object
			column = Column()
			
			col = list(col)
			col[0] = col[0].strip("(),'")
			
			# col_prim is None, do not append, assign None
			if col_prim:
				col_prim = list(col_prim)
				col_prim[0] = col_prim[0].strip("(),'")
				column.primary_key = col_prim[0]
			else:
				column.primary_key = ''
			
			column.name = col[0]
			column.type = col[1]
			column.charLen = col[2]
			column.precision = col[3]
			column.nullable = "NULL" if col[4] == "YES" else "NOT NULL"
			columns_list.append(column)
			
		return columns_list
	
	
	def list_records(self, table_name, sort_column, sort_direction, offset, limit):
		cur = self.db.cursor()
		cur.execute("SELECT * from %s ORDER BY %s %s OFFSET %s LIMIT %s;", 
						(AsIs(table_name), AsIs(sort_column), AsIs(sort_direction), offset, limit))
		rows = cur.fetchall()
		return rows
	
	
	def add_record(self, table_name, dict, id_column):
		new_row_id = 0
		cur = self.db.cursor()
		# get column names and values from the dictionary
		# http://stackoverflow.com/questions/29461933
		columns = dict.keys()
		values = [dict[column] for column in columns]
		
		query  = 'INSERT INTO %s (%s) VALUES %s RETURNING %s'
		try:
			cur.execute(query, (AsIs(table_name), AsIs(', '.join(columns)), tuple(values), AsIs(id_column)))
			new_row_id = cur.fetchone()[0]
			self.db.commit()
		except Exception, ex:
			self.db.rollback()
			#http://stackoverflow.com/questions/610883
			if hasattr(ex, 'pgerror'): 
				return ex.pgerror, False
			else:
				return str(ex), False
		return new_row_id, True
	
	
	def edit_record(self, table_name, set_dict, where_dict):
		edited_row_id = 0
		cur = self.db.cursor()
		# create tuple containing values
		#return_dict = {}
		#for x in where_dict.keys(): return_dict[x] = AsIs(x)
		table_dict = {'table': AsIs(table_name)}
		data_list = table_dict.values() + set_dict.values() + where_dict.values()
		
		# http://stackoverflow.com/questions/11517106
		query  = 'UPDATE %s SET {0} WHERE {1} RETURNING {2}'.format(', '.join('{0}=%s'.format(col) for col in set_dict), 
																								' AND '.join('{0}=%s'.format(col) for col in where_dict),
																								', '.join('{0}'.format(AsIs(col)) for col in where_dict))
		try:
			cur.execute(query, data_list)
			self.db.commit()
			edited_row_id = cur.fetchone()
		except Exception, ex:
			self.db.rollback()
			if hasattr(ex, 'pgerror'): 
				return ex.pgerror, False
			else:
				return str(ex), False
		
		return edited_row_id, True
		
	def delete_record(self, table_name, where_dict):
		cur = self.db.cursor()
		
		deleted_row = []
		table_name = AsIs(table_name)
		table_dict = {'table': table_name}
		data_list =  table_dict.values() + where_dict.values()
		
		query  = 'DELETE FROM %s WHERE {0} RETURNING *'.format(' AND '.join('{0}=%s'.format(col) for col in where_dict))
		try:
			cur.execute(query, data_list)
			self.db.commit()
			deleted_row = cur.fetchone()
		except Exception, ex:
			self.db.rollback()
			if hasattr(ex, 'pgerror'): 
				return ex.pgerror, False
			else:
				return str(ex), False
			
		return deleted_row, True
		
		
	def closeConn(self):
		self.db.close()