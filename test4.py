#!/usr/bin/python

'''**************************************
# Name: Nikolay Goncharenko, Rory Bresnahan
# Email: goncharn@onid.oregonstate.edu
# Class: CS419 - Capstone Project
# Assignment: Python Ncurses UI for 
# MySQL/PostgreSQL Database Management
**************************************'''

import npyscreen, curses
import psycopg2
from psycopg2.extensions import AsIs
import sys

# http://stackoverflow.com/questions/2146705/select-datatype-of-the-field-in-postgres - datatypes fields
# $mysqli = new mysqli("oniddb.cws.oregonstate.edu", "goncharn-db", $myPassword, "goncharn-db");

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
		
	def add_record(self, table_name, sort_column, sort_direction, offset, limit):
		cur = self.conn.cursor()
		try:
			cur.execute()
		except:
			cur.rollback()
	
	def closeConn(self):
		self.conn.close()

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
		self.sort_column = ''
		self.columns_list = []
		self.rows = []
		self.edit_cell = []


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
        pass

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
		# get name of selected table
		selectedTableName = act_on_this[0]
		# save the name of selected table in settings object
		self.parent.parentApp.myGridSet.table = selectedTableName
		# initialize TableMenuForm object attributes and switch to TableMenuForm
		self.parent.parentApp.getForm('Menu').table_name = selectedTableName
		self.parent.parentApp.switchForm('Menu')

		
'''**************************************************
   Class TableListDisplay inherits FormMutt class
   
   Purpose:  Container for displaying of the dynamic list
**************************************************'''
class TableListDisplay(npyscreen.FormMutt):
	
	# type of widget to be displayed
	MAIN_WIDGET_CLASS = TableList
	# position of main_widget and status widget
	MAIN_WIDGET_CLASS_START_LINE = 2
	STATUS_WIDGET_X_OFFSET = 5
	
	def beforeEditing(self):
		self.update_list()
	
	# populate wMain.values with list of tables in the database
	def update_list(self):
		self.wStatus1.value =  ' Select Table From List   '
		self.wMain.values = self.parentApp.myDatabase.list_all_tables()
		self.wMain.relx= 3
		self.wMain.display()


'''**************************************************
   Class TableOptionList inherits MultiLineAction class
   
   Purpose:  display list of actions that can be performed on 
   the table
**************************************************'''
class TableOptionList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(TableOptionList, self).__init__(*args, **keywords)

    def display_value(self, value):
        return "%s" % (value)
    
    def actionHighlighted(self, act_on_this, keypress):
		# get name of selected option
		selection = act_on_this
		if selection == 'Add Row':
			self.parent.parentApp.switchForm('Add Row')
		elif selection == 'Edit Row':
			self.parent.parentApp.switchForm('Edit Row')
		elif selection == 'Delete Row':
			self.parent.parentApp.switchForm('Delete Row')
		elif selection == 'Pagination Settings':
			self.parent.parentApp.GridSetF.columns_list = self.parent.parentApp.tabMenuF.columns_list
			self.parent.parentApp.switchForm('GridSet')
		elif selection == 'Exit Application':
			self.parent.parentApp.tabMenuF.exit_application()
		else:
			self.parent.parentApp.switchForm()

		
'''**************************************************
   Class TableMenuForm inherits ActionForm class
   
   Purpose:  Displays main table menu and grid
**************************************************'''													
class TableMenuForm(npyscreen.ActionFormV2WithMenus):
	# set screen redirection based on user choice
	def afterEditing(self):
		pass
	
	# Create Widgets
	def create(self):
		self.nextrely += 1
		self.action = self.add(TableOptionList, max_height=6,
									    name='Select Action',
										values = ['Add Row', 'Pagination Settings', 'Exit Application'],
										scroll_exit = True
										 # Let the user move out of the widget by pressing 
										# the down arrow instead of tab.  Try it without to see the difference.
										)
		# buttons
		self.bn_prev = self.add(npyscreen.ButtonPress, name = "Prev", max_height=1, relx = 20)
		self.bn_prev.whenPressed = self.redrawPrev # button press handler
		
		self.nextrely += -1 # 2nd widget stays at the same line 
		self.bn_next = self.add(npyscreen.ButtonPress, name = "Next", max_height=1, relx = 30)
		self.bn_next.whenPressed = self.redrawNext # button press handler
	    
		# move one line down from  the previous form
		self.nextrely += 1
		
		self.m1 = self.add_menu(name="Main Menu", shortcut="^M")
		self.m1.addItemsFromList([
            ("Edit Row", self.set_edit_form, "^E"),
            ("Delete Row", self.confirm_delete, "^D"),
            #("Exit Application", self.exit_application, "^Q"),
        ])

		# create Grid widget  and setup handler for Enter btn press
		self.myGrid =  self.add(MyGrid, col_titles = [], select_whole_line = True)
		# set grid handler for Enter press. source: https://goo.gl/e9wkYu
		grid_handler = {curses.ascii.LF: self.root_menu}
		self.myGrid.add_handlers(grid_handler)

		# define exit on Esc
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_application

	# called on Delete press in popup menu
	def confirm_delete(self):
		# http://npyscreen.readthedocs.org/messages.html?highlight=yes_no#selectFile
		isDelete = npyscreen.notify_yes_no("Confirm to delete the row?", title="Confirm Deletion", form_color='STANDOUT', wrap=True, editw = 0)
		if isDelete == True:
			pass
		else:
			pass
	
	# called on Edit press in popup menu
	def set_edit_form(self):
		self.parentApp.myGridSet.edit_cell = self.myGrid.edit_cell
		self.parentApp.switchForm('Edit Row')
		self.parentApp.switchFormNow()
	
	'''**************************************************************************
	Function redrawNext

	Purpose:  Handler for "Next Button".  
	Implements Next Pagination by fetching next range of records from the database
	***************************************************************************'''			
	def redrawNext(self):
		# intialize query attributes from settings object
		self.limit = self.parentApp.myGridSet.limit
		# update offset
		new_offset = self.parentApp.myGridSet.offset + self.limit
		self.parentApp.myGridSet.offset = new_offset
		self.offset = self.parentApp.myGridSet.offset
		# update sorting order and column to sort on
		self.sort_direction = self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.columns_list[0]
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.rows = self.parentApp.myDatabase.list_records(self.table_name, self.sort_column, self.sort_direction, self.offset, self.limit)
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
	
	'''**************************************************************************
	Function redrawPrev

	Purpose:  Handler for "Prev Button".  
	Implements Previous Pagination by fetching previous range of records from the database
	***************************************************************************'''		
	def redrawPrev(self):
		# intialize query attributes from settings object
		self.limit = self.parentApp.myGridSet.limit
		# update offset
		new_offset = self.parentApp.myGridSet.offset - self.limit
		# don't allow to fetch for negative row numbers
		if new_offset < 0:
			self.parentApp.myGridSet.offset = 0
		else:
			self.parentApp.myGridSet.offset = new_offset
		self.offset = self.parentApp.myGridSet.offset
		self.sort_direction =  self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.columns_list[0]
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.rows = self.parentApp.myDatabase.list_records(self.table_name, self.sort_column, self.sort_direction, self.offset, self.limit)
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
		
	def beforeEditing(self):
		# if were able to set value for self.selectTable
		if self.table_name:
			self.name = "Table '%s'" % self.table_name#self.selectTable
			
			self.columns_list = self.parentApp.myDatabase.list_columns(self.table_name)
			self.myGrid.col_titles = self.columns_list
			self.parentApp.myGridSet.columns_list = self.columns_list
			
			# update query params from GridSettings object
			self.limit = self.parentApp.myGridSet.limit
			self.offset = self.parentApp.myGridSet.offset
			self.sort_direction = self.parentApp.myGridSet.sort_direction
			self.sort_column = self.parentApp.myGridSet.sort_column
			# when called with default settings
			if self.sort_column == '':
				self.sort_column = self.columns_list[0]
			
			# populate the grid by fetching data from database
			self.myGrid.values = []
			self.rows = []
			self.myGrid.default_column_number = 5
			if len(self.columns_list) > 0:
				self.rows = self.parentApp.myDatabase.list_records(self.table_name, self.sort_column, self.sort_direction, self.offset, self.limit)
				
			for row in self.rows:
				# clean up values from white spaces
				for column in row:
					#if isinstance(column, basestring):
					column = str(column).rstrip('')
				self.myGrid.values.append(row)
			
			# cache data  in the GridSetting (allow to cache) since we don't query large amount
			# of data.We limit querying and showing no more than 10 records per page
			self.parentApp.myGridSet.rows = self.rows
		
		else:
			self.name = "Error transfering data from Screen #1 to #2!"	
		
	def exit_application(self):
		self.parentApp.switchForm(None)
		self.parentApp.switchFormNow()
	
	def on_cancel(self):
		self.parentApp.switchForm('MAIN')
		self.parentApp.switchFormNow()


'''*********************************************************
   Class AddRowForm inherits ActionForm class
   
   Purpose:  Reponsible for adding a new row to the given table
*********************************************************'''
class AddRowForm(npyscreen.ActionForm):
	def afterEditing(self):
		self.parentApp.setNextFormPrevious()
	
	def create(self):
		# generate dict to hold widget objects
		# http://stackoverflow.com/questions/4010840
		self.dict = {}
		count = 0
		for column in self.parentApp.myGridSet.columns_list:
			count = count + 1
			self.dict["column"+ str(count)] = self.add(npyscreen.TitleText, name = column)
		
		# move one line down from  the previous form
		self.nextrely += 1
		
		# buttons
		self.bn_prev = self.add(npyscreen.ButtonPress, name = "Prev", max_height=1, relx = 20)
		self.bn_prev.whenPressed = self.parentApp.tabMenuF.redrawPrev # button press handler
		
		self.nextrely += -1 # 2nd widget stays at the same line 
		self.bn_next = self.add(npyscreen.ButtonPress, name = "Next", max_height=1, relx = 30)
		self.bn_next.whenPressed =self.parentApp.tabMenuF.redrawNext # button press handler
		
		# create Grid widget
		self.myGrid =  self.add(MyGrid, col_titles = [], select_whole_line = True)
		
		# define return on prev form on Esc
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_form
	
	def beforeEditing(self):
			# display cached Grid
			self.myGrid.values = []
			row = []
			self.myGrid.col_titles = self.parentApp.myGridSet.columns_list
			for row in self.parentApp.myGridSet.rows:
				self.myGrid.values.append(row)
	
	def exit_form(self):
		self.parentApp.setNextFormPrevious()
		self.parentApp.switchFormNow()

'''*********************************************************
   Class EditRowForm inherits ActionForm class
   
   Purpose:  Reponsible for editing a selected row in the given table
*********************************************************'''
class EditRowForm(npyscreen.ActionForm):
	def afterEditing(self):
		self.parentApp.setNextFormPrevious()
	
	def create(self):
		# generate dict to hold widget objects
		# http://stackoverflow.com/questions/4010840
		self.dict = {}
		count = 0
		for column in self.parentApp.myGridSet.columns_list:
			#count = count + 1
			#self.dict["column"+ str(count)] = self.add(npyscreen.TitleText, name = column)
			if column is not self.parentApp.myGridSet.columns_list[0]:
				self.dict[str(column)] = self.add(npyscreen.TitleText, name = str(column))
		
		# move one line down from  the previous form
		self.nextrely += 1
		
		# buttons
		self.bn_prev = self.add(npyscreen.ButtonPress, name = "Prev", max_height=1, relx = 20)
		self.bn_prev.whenPressed = self.parentApp.tabMenuF.redrawPrev # button press handler
		
		self.nextrely += -1 # 2nd widget stays at the same line 
		self.bn_next = self.add(npyscreen.ButtonPress, name = "Next", max_height=1, relx = 30)
		self.bn_next.whenPressed =self.parentApp.tabMenuF.redrawNext # button press handler
		
		# create Grid widget
		self.myGrid =  self.add(MyGrid, col_titles = [], select_whole_line = True)
		
		# define return on prev form on Esc
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_form
	
	def beforeEditing(self):
			'''
			count = 0
			for column in self.parentApp.myGridSet.columns_list:
				count = count + 1
				self.dict["column"+ str(count)].value = self.column_values[count-1]
			'''
			# display cached Grid
			self.myGrid.values = []
			row = []
			self.myGrid.col_titles = self.parentApp.myGridSet.columns_list
			for row in self.parentApp.myGridSet.rows:
				self.myGrid.values.append(row)
			
			# set current values of the columns
			'''
			
			row_num = self.parentApp.myGridSet.edit_cell[0]
			self.dict["column" + str(count)].value = str(self.parentApp.myGridSet.rows[row_num][count-1])
			count += count
			self.dict["column" + str(count)].value = str(self.parentApp.myGridSet.rows[row_num][count-1])
			'''
			row_num = self.parentApp.myGridSet.edit_cell[0]
			count = 1
			for column in self.parentApp.myGridSet.columns_list:
				
				if column is not self.parentApp.myGridSet.columns_list[0]:
					count = count + 1
					self.dict[str(column)].value = str(self.parentApp.myGridSet.rows[row_num][count-1])
	
	def exit_form(self):
		self.parentApp.setNextFormPrevious()
		self.parentApp.switchFormNow()

'''*********************************************************
   Class GridSetForm inherits ActionForm class
   
   Purpose:  Reponsible for changing global Grid Settings: 
    - num rows per page to show
	- starting row
	- column to sort on
	- sorting direction: ASC or DESC
*********************************************************'''
class GridSetForm(npyscreen.ActionForm):
	def afterEditing(self):
		self.parentApp.myGridSet.limit = int(self.limitWidget.value)
		self.parentApp.myGridSet.offset = int(self.offsetWidget.value)
		self.parentApp.myGridSet.sort_direction = self.sortDirWidget.get_selected_objects()[0]
		self.parentApp.myGridSet.sort_column = self.columnWidget.get_selected_objects()[0]
		self.parentApp.setNextFormPrevious()
	
	def create(self):
		self.limitWidget = self.add(npyscreen.TitleText, name='Rows per page: ', begin_entry_at = 21, value = str(self.parentApp.myGridSet.limit))
		self.nextrely += 1
		self.offsetWidget = self.add(npyscreen.TitleText, name='Start at row #:', begin_entry_at = 21, value = str(self.parentApp.myGridSet.offset))
		self.nextrely += 1
		self.columnWidget = self.add(npyscreen.TitleSelectOne, max_height=5,
									    name='Order by',
										#values = [],
										scroll_exit = True
										 # Let the user move out of the widget by pressing 
										# the down arrow instead of tab.  Try it without to see the difference.
										)
		self.nextrely += 1
		self.sortDirWidget = self.add(npyscreen.TitleSelectOne, max_height=6,
									    name='Sort',
										values = ['ASC', 'DESC'],
										scroll_exit = True
										 # Let the user move out of the widget by pressing 
										# the down arrow instead of tab.  Try it without to see the difference.
										)

	def beforeEditing(self):
		if self.columns_list:
			self.columnWidget.values = self.columns_list
			

'''**************************************************
   Class MyApplication inherits NPSAppManaged class
   
   Purpose:  Manages  flow between application screens.
				 It's a main app environment
**************************************************'''
class MyApplication(npyscreen.NPSAppManaged):
	add_row_count = 0 # count number of calls to Add Row Form
	edit_row_count = 0 # count number of calls to Edit Row Form
	def onStart(self):
		self.myDatabase = Database()
		self.myGridSet = GridSettings()
		self.selTableF = self.addForm('MAIN', TableListDisplay, name='Select Table')
		self.tabMenuF = self.addForm('Menu', TableMenuForm)
		self.GridSetF = self.addForm('GridSet', GridSetForm, name='Pagination Settings')
	
	'''**************************************************************************
	Function onInMainLoop()

	Purpose:  It is called when swithing between forms
	***************************************************************************'''	
	def onInMainLoop(self):
		# when app leavs Table Menu Form (obj tabMenuF)
		# for the first time, create Add Row form
		if self.NEXT_ACTIVE_FORM == 'Add Row':
			self.add_row_count = self.add_row_count + 1
			if self.add_row_count == 1:
				self.addRowF = self.addForm('Add Row', AddRowForm, name='Add Row')
		
		# when app leavs Table Menu Form (obj tabMenuF)
		# for the first time, create Edit Row form
		if self.NEXT_ACTIVE_FORM == 'Edit Row':
			self.edit_row_count = self.edit_row_count + 1
			if self.edit_row_count == 1:
				self.editRowF = self.addForm('Edit Row', EditRowForm, name='Edit Row')
	
	def onCleanExit(self):
		self.myDatabase.closeConn()
	
	'''**************************************************************************
	Function redrawNext

	Purpose:  Handler for "Next Button".  
	Implements Next Pagination by fetching next range of records from the database
	***************************************************************************'''			
	def redrawNext(self):
		# intialize query attributes from settings object
		self.limit = self.parentApp.myGridSet.limit
		# update offset
		new_offset = self.parentApp.myGridSet.offset + self.limit
		self.parentApp.myGridSet.offset = new_offset
		self.offset = self.parentApp.myGridSet.offset
		# update sorting order and column to sort on
		self.sort_direction = self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.columns_list[0]
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.rows = self.parentApp.myDatabase.list_records(self.table_name, self.sort_column, self.sort_direction, self.offset, self.limit)
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
	
	
	'''**************************************************************************
	Function redrawPrev

	Purpose:  Handler for "Prev Button".  
	Implements Previous Pagination by fetching previous range of records from the database
	***************************************************************************'''		
	def redrawPrev(self, obj):
		# intialize query attributes from settings object
		table_name = self.myGridSet.table
		limit = self.myGridSet.limit
		# update offset
		new_offset = self.myGridSet.offset - limit
		# don't allow to fetch for negative row numbers
		if new_offset < 0:
			self.myGridSet.offset = 0
		else:
			self.myGridSet.offset = new_offset
		offset = self.myGridSet.offset
		sort_direction =  self.myGridSet.sort_direction
		sort_column = self.myGridSet.sort_column
		# when called with default settings
		if sort_column == '':
				if len(self.myGridSet.columns_list) > 0:
					sort_column = self.myGridSet.columns_list[0]
		# query rows from database to populate grid
		obj.myGrid.values = []
		rows = self.myDatabase.list_records(table_name, sort_column, sort_direction, offset, limit)
		for row in rows:
			obj.myGrid.values.append(row)
		obj.display()

if __name__ == '__main__':
    MyApplication().run()
    print 'Exited From the App'
