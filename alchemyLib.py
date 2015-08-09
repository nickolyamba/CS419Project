#!/usr/bin/python

#import exceptions
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker


'''**************************************************
* Class Alchemy obj inherits object class
*
* Purpose:  Connect to the database and insert, delete data
**************************************************'''
class Alchemy(object):
	def __init__ (self):
		self.engine =  create_engine("postgresql://muepyavy:EQoh7fJJNxK-4ag4SNUIYwzzWqTVzj-8@babar.elephantsql.com/muepyavy")
	
	def get_datatable(self, table_name):
		metadata = MetaData()
		metadata.reflect(self.engine, only=[table_name])
		datatable = metadata.tables[table_name]
		return datatable
		
	def insert(self, dict):
		conn = engine.connect()
		stmt = datatable.insert().values(dict)
		conn.execute(stmt)
		conn.close()
