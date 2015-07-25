#!/usr/bin/python

'''**************************************
# Name: Nikolay Goncharenko, Rory Bresnahan
# Email: goncharn@onid.oregonstate.edu
# Class: CS419 - Capstone Project
# Assignment: Python Ncurses UI for 
# MySQL/PostgreSQL Database Management
**************************************'''

import npyscreen, curses
import random
import psycopg2
from psycopg2.extensions import AsIs
import sys

# $mysqli = new mysqli("oniddb.cws.oregonstate.edu", "goncharn-db", $myPassword, "goncharn-db");
#limit = 3
#sort_direction = 'ASC'
#offset = 0
#paramstyle = 'format'
#table = ''

'''**************************************************
* Class Database inherits object class
*
* Purpose:  Connect to the database and query it
**************************************************'''
class Database(object):
	def __init__ (self):
		try:
			self.conn = psycopg2.connect("dbname='muepyavy' user='muepyavy' host='babar.elephantsql.com' password='EQoh7fJJNxK-4ag4SNUIYwzzWqTVzj-8'")
		except psycopg2.DatabaseError, e:
			if self.conn:
				self.conn.rollback()
			print 'Error %s' % e
			sys.exit(1)
		#return  conn;
		
	# returns list of all tables in the database	
	def list_all_tables(self):
		cur = self.conn.cursor()
		cur.execute("SELECT table_name FROM information_schema.tables \
							WHERE \
								table_type = 'BASE TABLE' AND table_schema = 'public' \
							ORDER BY table_type, table_name")
		tables = cur.fetchall()
		cur.close()
		return tables
		
	# returns list of all column names in the table	
	def list_columns(self, table_name):
		columns_list = []
		cur = self.conn.cursor()
		cur.execute("SELECT column_name from information_schema.columns \
										WHERE table_name = %s;", (table_name,))
		columns_tuple = cur.fetchall()
		cur.close()
		# traverese tuple of tuples to list of strings
		for col in columns_tuple:
			col = list(col)
			col[0] = col[0].strip("(),'")
			columns_list.append(col[0])
		return columns_list
		
	def list_records(self, table_name, sort_column, sort_direction, offset, limit):
		cur = self.conn.cursor()
		cur.execute("SELECT * from %s ORDER BY %s %s OFFSET %s LIMIT %s;", 
						(AsIs(table_name), AsIs(sort_column), AsIs(sort_direction), offset, limit))
		rows = cur.fetchall()
		return rows
	
	def closeConn(self):
		self.conn.close()
'''
    def add_record(self, last_name = '', other_names='', email_address=''):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('INSERT INTO records(last_name, other_names, email_address) \
                    VALUES(?,?,?)', (last_name, other_names, email_address))
        db.commit()
        c.close()
    
    def update_record(self, record_id, last_name = '', other_names='', email_address=''):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('UPDATE records set last_name=?, other_names=?, email_address=? \
                    WHERE record_internal_id=?', (last_name, other_names, email_address, \
                                                        record_id))
        db.commit()
        c.close()    

    def delete_record(self, record_id):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('DELETE FROM records where record_internal_id=?', (record_id,))
        db.commit()
        c.close()    
    
    def list_all_records(self, ):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT * from records')
        records = c.fetchall()
        c.close()
        return records
    
    def get_record(self, record_id):
        db = sqlite3.connect(self.dbfilename)
        c = db.cursor()
        c.execute('SELECT * from records WHERE record_internal_id=?', (record_id,))
        records = c.fetchall()
        c.close()
        return records[0]
'''

'''**************************************************
   Class MyGrid inherits GridColTitles class
   
   Purpose:  display data from database as greed,
    visualazing a table in database
**************************************************'''
class MyGrid(npyscreen.GridColTitles):
    # You need to override custom_print_cell to manipulate how
    # a cell is printed. In this example we change the color of the
    # text depending on the string value of cell.
    def custom_print_cell(self, actual_cell, cell_display_value):
        if cell_display_value =='FAIL':
           actual_cell.color = 'DANGER'
        elif cell_display_value == 'PASS':
           actual_cell.color = 'GOOD'
        else:
           actual_cell.color = 'DEFAULT'


'''**************************************************
   Class TableList inherits MultiLineAction class
   
   Purpose:  display list of tables as list and define an action
   when one of the tables is selected 
**************************************************'''
class TableList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(TableList, self).__init__(*args, **keywords)

    def display_value(self, value):
        return "%s" % (value[0])
    
    def actionHighlighted(self, act_on_this, keypress):
		# get value of selected table
		selectedTableName = act_on_this[0]
		# save the name of selected table in settings object
		self.parent.parentApp.myGridSet.table = selectedTableName
		# initialize TableMenuForm object attributes and switch to TableMenuForm
		self.parent.parentApp.getForm('Menu').selectTable = selectedTableName
		self.parent.parentApp.getForm('Menu').sort_direction = self.parent.parentApp.myGridSet.sort_direction
		self.parent.parentApp.getForm('Menu').offset = self.parent.parentApp.myGridSet.offset
		self.parent.parentApp.getForm('Menu').limit = self.parent.parentApp.myGridSet.limit
		self.parent.parentApp.switchForm('Menu')
		
'''**************************************************
   Class TableListDisplay inherits FormMutt class
   
   Purpose:  Container for displaying of the dynamic list
**************************************************'''
class TableListDisplay(npyscreen.FormMutt):
	
	# type of widget to be displayed
	MAIN_WIDGET_CLASS = TableList
	MAIN_WIDGET_CLASS_START_LINE = 2
	STATUS_WIDGET_X_OFFSET = 5
	
	def beforeEditing(self):
		self.update_list()
	
	def update_list(self):
		self.wStatus1.value =  ' Select Table From List   '
		self.wMain.values = self.parentApp.myDatabase.list_all_tables()
		self.wMain.relx= 3
		self.wMain.display()


'''**************************************************
   Class TableMenuForm inherits ActionForm class
   
   Purpose:  Displays main table menu and grid
**************************************************'''													
class TableMenuForm(npyscreen.ActionForm):
	# set screen redirection based on user choice
	#selectTable = None
	#columns_list = []
	isExit = False
	
	def afterEditing(self):
		if self.isExit == True:
			self.parentApp.switchForm(None)
		else:
			if len(self.action.get_selected_objects()) > 0:
				selection = self.action.get_selected_objects()[0]
				if selection == 'Add Row':
					self.parentApp.setNextForm('Add Row')
				elif selection == 'Edit Row':
					self.parentApp.setNextForm('Edit Row')
				elif selection == 'Delete Row':
					self.parentApp.setNextForm('Delete Row')
				elif selection == 'Pagination Settings':
					self.parentApp.setNextForm('GridSet')
				else:
					self.parentApp.switchForm(None)
			#self.parentApp.setNextFormPrevious()
	
	# Create Widgets
	def create(self):
		#self.tableName = self.add(npyscreen.TitleText, name='Table Name: ')
		#self.tableName2 = self.add(npyscreen.TitleText, name='Table Name2: ', value = str(self.tableName))
		self.nextrely += 1
		self.action = self.add(npyscreen.TitleSelectOne, max_height=6,
									    name='Select Action',
										values = ['Add Row', 'Edit Row', 'Delete Row', 'Pagination Settings'],
										scroll_exit = True
										 # Let the user move out of the widget by pressing 
										# the down arrow instead of tab.  Try it without to see the difference.
										)
		self.nextrely += 2
		self.nextrelx += 15
		# buttons
		self.bn_prev = self.add(npyscreen.ButtonPress, name = "Prev")
		self.bn_prev.whenPressed = self.redrawPrev
		
		self.nextrely += -1
		self.nextrelx += 20
		self.bn_next = self.add(npyscreen.ButtonPress, name = "Next")
		self.bn_next.whenPressed = self.redrawNext
	
		self.nextrelx += -35
		self.nextrely += 1
		# move one line down from  the previous form
		
	def redrawNext(self):
		# intialize query attributes from settings object
		self.limit = self.parentApp.myGridSet.limit
		# update offset
		new_offset = self.parentApp.myGridSet.offset + self.limit
		self.parentApp.myGridSet.offset = new_offset
		self.offset = self.parentApp.myGridSet.offset
		self.sort_direction = sort_direction = self.parentApp.myGridSet.sort_direction
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.rows = self.parentApp.myDatabase.list_records(self.selectTable, self.columns_list[0], self.sort_direction, self.offset, self.limit)
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
		
	def redrawPrev(self):
		# intialize query attributes from settings object
		self.limit = self.parentApp.myGridSet.limit
		# update offset
		new_offset = self.parentApp.myGridSet.offset - self.limit
		if new_offset < 0:
			self.parentApp.myGridSet.offset = 0
		else:
			self.parentApp.myGridSet.offset = new_offset
		self.offset = self.parentApp.myGridSet.offset
		self.sort_direction = sort_direction = self.parentApp.myGridSet.sort_direction
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.rows = self.parentApp.myDatabase.list_records(self.selectTable, self.columns_list[0], self.sort_direction, self.offset, self.limit)
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
		
	def beforeEditing(self):
		# if were able to set value for self.selectTable
		if self.selectTable:
			self.name = "Table '%s'" % self.selectTable

			# Create MyGrid Widget object
			# fetch columns names into columns_list
			self.columns_list = self.parentApp.myDatabase.list_columns(self.selectTable)
			
			self.myGrid =  self.add(MyGrid, col_titles = self.columns_list, select_whole_line = True)
			
			# populate the grid
			self.myGrid.values = []
			self.myGrid.default_column_number = 5
			
			self.rows = self.parentApp.myDatabase.list_records(self.selectTable, self.columns_list[0], self.sort_direction, self.offset, self.limit)
			for row in self.rows:
				self.myGrid.values.append(row)
			
		else:
			self.name = "Error transfering data from Screen #1 to #2!"
		
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_application
		
	def exit_application(self):
		#curses.beep()
		self.isExit = True
		self.parentApp.switchForm(None)
		self.editing = False


'''*********************************************************
   Class AddRowForm inherits ActionForm class
   
   Purpose:  Reponsible for adding a new row to the given table
*********************************************************'''
class AddRowForm(npyscreen.ActionForm):
	def afterEditing(self):
		self.parentApp.setNextFormPrevious()
	# It's just prototype, non-dynamic
	def create(self):
		self.value = None
		self.wgLastName   = self.add(npyscreen.TitleText, name = "Last Name:",)
		self.wgOtherNames = self.add(npyscreen.TitleText, name = "Other Names:")
		self.wgEmail      = self.add(npyscreen.TitleText, name = "Email:")


'''*********************************************************
   Class GridSettings inherits object
   
   Purpose:  Save current GridView pagination settings + table_name
*********************************************************'''
class GridSettings(object):
	def __init__ (self):
		self.limit = 3
		self.sort_direction = 'ASC'
		self.offset = 0
		self.table = ''
		self.column = ''


# Form containing pagination settings
class GridSetForm(npyscreen.ActionForm):
	def afterEditing(self):
		self.parentApp.setNextFormPrevious()
	
	def create(self):
		self.limitWidget = self.add(npyscreen.TitleText, name='Rows per page: ', value = str(self.parentApp.myGridSet.limit))
		self.offsetWidget = self.add(npyscreen.TitleText, name='Start at row #:', value = str(self.parentApp.myGridSet.offset))
		self.columnWidget = self.add(npyscreen.TitleSelectOne, max_height=5,
									    name='Order by',
										values = ['1', '2'],#self.parentApp.tabMenuF.columns_list,
										scroll_exit = True
										 # Let the user move out of the widget by pressing 
										# the down arrow instead of tab.  Try it without to see the difference.
										)
		
		self.sortDirWidget = self.add(npyscreen.TitleSelectOne, max_height=6,
									    name='Sort',
										values = ['ASC', 'DESC'],
										scroll_exit = True
										 # Let the user move out of the widget by pressing 
										# the down arrow instead of tab.  Try it without to see the difference.
										)


'''**************************************************
   Class MyApplication inherits NPSAppManaged class
   
   Purpose:  Manages  flow between application screens.
				 It's a main app environment
**************************************************'''
class MyApplication(npyscreen.NPSAppManaged):
	def onStart(self):
		self.myDatabase = Database()
		self.myGridSet = GridSettings()
		self.selTableF = self.addForm('MAIN', TableListDisplay, name='Select Table')
		self.tabMenuF = self.addForm('Menu', TableMenuForm, name='Table Menu')
		self.addRowF = self.addForm('Add Row', AddRowForm, name='Add Row')
		self.GridSetF = self.addForm('GridSet', GridSetForm, name='Pagination Settings')
	
	
	def onCleanExit(self):
		self.myDatabase.closeConn()

if __name__ == '__main__':
    MyApplication().run()
    print 'Exited From the App'
