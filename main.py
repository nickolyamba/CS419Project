#!/usr/bin/python

import npyscreen, curses

import datetime
from math import floor
from decimal import Decimal
from threading import Timer
import time

from mysqlDb import MysqlDB
from postgreDb import PostgreDB
from column import Column
#from alchemyLib import Alchemy

# time in sec of showing 
# feedback message to a user
FEEDBACK_TIMEOUT = 6


'''*********************************************************
   Class GridSettings inherits object
   
   Purpose:  Save current GridView pagination settings + table_name
*********************************************************'''
class GridSettings(object):
	def __init__ (self):
		self.limit = 5
		self.sort_direction = 'ASC'
		self.offset = 0
		self.table = ''
		self.sort_column = ''
		
		self.columns_list = []
		# contains all the fetched data (up to 10 rows of data)
		self.rows = []
		#location of the currently edited cell
		self.edit_cell = []
		# database engine type
		self.db_type = ''
		self.row_count = 0
		


'''**************************************************
   Class MyGrid inherits GridColTitles class
   
   Purpose:  display data from database as greed,
    visualazing a table in database
**************************************************'''
class MyGrid(npyscreen.GridColTitles):
    def custom_print_cell(self, actual_cell, cell_display_value):
        pass


'''**************************************************
   Class DBList inherits MultiLineAction class
   
   Purpose:  display list of actions that can be performed on 
   the table, manages action on select
**************************************************'''
class DBList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(DBList, self).__init__(*args, **keywords)

    def display_value(self, value):
        return "%s" % value
    
    def actionHighlighted(self, act_on_this, keypress):
		# get name of selected option
		selection = act_on_this
		if selection == 'MySQL':
			self.parent.parentApp.myGridSet.db_type = 'MySQL'
			self.parent.parentApp.switchForm('TableSelect')
		elif selection == 'PostgreSQL':
			self.parent.parentApp.myGridSet.db_type = 'PostgreSQL'
			self.parent.parentApp.switchForm('TableSelect')
		elif selection == 'Exit Application':
			self.parent.parentApp.exit_application()
		else:
			self.parent.parentApp.switchForm(None)
		
		
'''**************************************************
   Class DBSelect inherits ActionForm class
   
   Purpose:  Container for displaying of the dynamic list
**************************************************'''
class DBSelectForm(npyscreen.ActionFormMinimal):
	# Create Widgets
	OK_BUTTON_TEXT = "Exit"
	def create(self):
		self.action = self.add(DBList, max_height=3,
									    name='Select Database Engine',
										values = ['PostgreSQL', 'MySQL', 'Exit Application'],
										scroll_exit = True)
		self.nextrely += 1
		
		# define exit on Esc
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.parentApp.exit_application
		
	def on_ok(self):
		self.parentApp.switchForm(None)
		self.parentApp.switchFormNow()

		
'''**************************************************
   Class TableList inherits MultiLineAction class
   
   Purpose:  display list of tables as list and defines an action
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
		
		# reset Main App Form objects
		del self.parent.parentApp.myGridSet.columns_list [:]
		self.parent.parentApp.myGridSet.rows = ()
		self.parent.parentApp.myGridSet.sort_column = ''
		self.parent.parentApp.myGridSet.offset = 0
		self.parent.parentApp.myGridSet.row_count = 0
		self.parent.parentApp.myGridSet.limit = 5
		
		#del self.parent.parentApp.myGridSet
		#self.parent.parentApp.myGridSet = GridSettings()
		#del self.parent.parentApp.selTableF
		#self.parent.parentApp.selTableF = self.parent.parentApp.addForm('TableSelect', TableListDisplay, name='Select Table')
		del self.parent.parentApp.tabMenuF
		self.parent.parentApp.tabMenuF = self.parent.parentApp.addForm('Menu', TableMenuForm)
		del self.parent.parentApp.GridSetF
		self.parent.parentApp.GridSetF = self.parent.parentApp.addForm('GridSet', GridSetForm, name='Pagination Settings')
		
		# save the name of selected table in settings object
		self.parent.parentApp.myGridSet.table = selectedTableName
		# initialize TableMenuForm object attributes and switch to TableMenuForm
		self.parent.parentApp.getForm('Menu').table_name = selectedTableName
		self.parent.parentApp.switchForm('Menu')


'''**************************************************
   Class TableListDisplay inherits FormMutt class
   
   Purpose:  Container Form for displaying of the dynamic list
**************************************************'''
class TableListDisplay(npyscreen.ActionFormMinimal):
	OK_BUTTON_TEXT = "Back"
	# Create Widgets
	def create(self):
		self.action = self.add(TableList,
										name='Select Table',
										scroll_exit = True)
		#self.nextrely += 1
		
		# define action on Esc
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.on_ok
		
	def beforeEditing(self):
		self.update_list()
	
	# populate wMain.values with list of tables in the database
	def update_list(self):
		if self.parentApp.myGridSet.db_type == 'PostgreSQL':
			self.action.values = self.parentApp.postgreDb.list_all_tables()
		else:
			self.action.values = self.parentApp.mySQLDb.list_all_tables()		
		
	def on_ok(self):
		self.parentApp.switchForm('MAIN')
		self.parentApp.switchFormNow()


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
		elif selection == 'Select Another Table':
			self.parent.parentApp.switchForm('TableSelect')
		elif selection == 'Exit Application':
			self.parent.parentApp.tabMenuF.exit_application()
		else:
			self.parent.parentApp.switchForm(None)

		
'''**************************************************
   Class TableMenuForm inherits ActionForm class
   
   Purpose:  Displays main table menu and grid
**************************************************'''													
class TableMenuForm(npyscreen.ActionFormV2WithMenus):
	# set screen redirection based on user choice
	CANCEL_BUTTON_TEXT = "Back"
	def afterEditing(self):
		if self.timer:
			self.timer.cancel()# cancel timer
	
	# Create Widgets
	def create(self):
		self.timer = None
		self.nextrely += 1
		self.action = self.add(TableOptionList, max_height=4,
									    name='Select Action',
										values = ['Add Row', 'Pagination Settings', 'Select Another Table', 'Exit Application'],
										scroll_exit = True
										 # Let the user move out of the widget by pressing 
										# the down arrow instead of tab.  Try it without to see the difference.
										)
		self.nextrely += 1
		
		# feedback textbox
		self.feedback = self.add(npyscreen.MultiLineEdit, editable = False, name = ' ', relx = 15, begin_entry_at = 1, max_height=4)
		#self.nextrely += 1
		
		# buttons
		self.bn_first_page = self.add(npyscreen.ButtonPress, name = "<< First", max_height=1, relx = 23)
		self.bn_first_page.whenPressed = self.redrawFirstPage # button press handler
		self.nextrely += -1 #widget stays at the same line 
		
		self.bn_prev = self.add(npyscreen.ButtonPress, name = "< Prev", max_height=1, relx = 35)
		self.bn_prev.whenPressed = self.redrawPrev # button press handler
		self.nextrely += -1 # widget stays at the same line 
		
		self.bn_next = self.add(npyscreen.ButtonPress, name = "Next >", max_height=1, relx = 45)
		self.bn_next.when_pressed_function = self.redrawNext # button press handler
		self.nextrely += -1 # widget stays at the same line 
		
		self.bn_last_page = self.add(npyscreen.ButtonPress, name = "Last >>", max_height=1, relx = 55)
		self.bn_last_page.whenPressed = self.redrawLastPage # button press handler
		# move one line down from  the previous form
		self.nextrely += 1
		
		self.m1 = self.add_menu(name="Main Menu", shortcut="^M")
		self.m1.addItemsFromList([
            ("Edit Row", self.set_edit_form, "^E"),
            ("Delete Row", self.confirm_delete, "^D"),
            ("Exit Menu", self.exit_menu, "^Q"),
        ])

		# create Grid widget  and setup handler for Enter btn press
		self.myGrid =  self.add(MyGrid, col_titles = [], select_whole_line = True)
		# set grid handler for Enter press. source: https://goo.gl/e9wkYu
		self.myGrid.add_handlers({curses.ascii.LF: self.root_menu})

		# define exit on Esc
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.on_cancel
	
	def exit_menu(self):
		self.h_exit_escape(None)
	
	# called on Delete press in popup menu
	def confirm_delete(self):
		# http://npyscreen.readthedocs.org/messages.html?highlight=yes_no#selectFile
		isDelete = npyscreen.notify_yes_no("Confirm to delete the row?", title="Confirm Deletion", form_color='STANDOUT', wrap=True, editw = 0)
		if isDelete:
			# dict for where clause of SQL statement (contains primary key:value pairs)
			where_dict = {} 
			row_num = self.myGrid.edit_cell[0]
			for col, col_value in zip(self.parentApp.myGridSet.columns_list, self.myGrid.values[row_num]):
				if  col.primary_key:
					where_dict[col.name] = col_value
			# delete row
			if self.parentApp.myGridSet.db_type == 'PostgreSQL':
				del_row_data, isSuccess = self.parentApp.postgreDb.delete_record(self.parentApp.myGridSet.table, where_dict)
			else:
				del_row_data, isSuccess = self.parentApp.mySQLDb.delete_record(self.parentApp.myGridSet.table, where_dict)
			# give feedback
			if isSuccess:
				del_data_dict = {}
				for col, col_value in zip(self.parentApp.myGridSet.columns_list, del_row_data):
					del_data_dict[col.name] = col_value
				self.feedback.value  = "Deleted succesfully. " + str(del_data_dict).strip("{}'\0")
				self.feedback.color = 'SAFE'
				# update myGrid and screen
				self.update_grid()
			else:
				self.feedback.value  = str(del_row_data)
				self.feedback.color = 'ERROR'
			# make feedback visible
			self.feedback.hidden = False
			self.display()
			# set times to hide the feedback
			t = Timer(FEEDBACK_TIMEOUT, self.hideFeedback)
			t.start()
			
	def update_grid(self):
		# reset Grid
		self.limit = self.parentApp.myGridSet.limit
		# reset offset and update it
		#self.parentApp.myGridSet.offset = 0
		self.offset = self.parentApp.myGridSet.offset
		# update sorting order and column to sort on
		self.sort_direction = self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		if self.sort_column == '':
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		# reset Grid
		del self.myGrid.values [:]
		# query rows from database to populate grid
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.parentApp.myGridSet.rows = self.rows
	
	def hideFeedback(self):
		self.feedback.hidden = True
		self.display()
	
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
		if new_offset <= self.parentApp.myGridSet.row_count:
			self.parentApp.myGridSet.offset = new_offset
		#self.parentApp.myGridSet.offset = new_offset
		self.offset = self.parentApp.myGridSet.offset
		# update sorting order and column to sort on
		self.sort_direction = self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.columns_list[0].name
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.fetch_rows()
		
		for row in self.rows:
			self.myGrid.values.append(row)
		self.parentApp.myGridSet.rows = self.rows
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
				self.sort_column = self.columns_list[0].name
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.parentApp.myGridSet.rows = self.rows
		self.display()
		
	def redrawFirstPage(self):
			self.limit = self.parentApp.myGridSet.limit
			self.offset = 0
			self.parentApp.myGridSet.offset = self.offset
			self.sort_direction =  self.parentApp.myGridSet.sort_direction
			self.sort_column = self.parentApp.myGridSet.sort_column
			# when called with default settings
			if self.sort_column == '':
					self.sort_column = self.parentApp.myGridSet.columns_list[0].name
			self.myGrid.values = []
			self.fetch_rows()
			for row in self.rows:
				self.myGrid.values.append(row)
			self.display()
		
	def redrawLastPage(self):
		self.limit = self.parentApp.myGridSet.limit
		page_count = int(floor(self.parentApp.myGridSet.row_count /self.limit))
		self.offset = page_count * self.parentApp.myGridSet.limit
		self.parentApp.myGridSet.offset = self.offset
		self.sort_direction =  self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		self.myGrid.values = []
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
		
	def beforeEditing(self):
		# if were able to set value for self.selectTable
		#self.parentApp.resetHistory()
		if self.table_name:
			self.name = "Table '%s'" % self.table_name
			
			#self.feedback.value =  self.parentApp.myGridSet.db_type
			
			# Get list of Column objects when the page is opened for the first time
			# Otherwise, just update the grid values
			if not self.parentApp.myGridSet.columns_list or self.parentApp.myGridSet.table != self.table_name:
				if self.parentApp.myGridSet.db_type == 'PostgreSQL':
					self.columns_list, self.row_count = self.parentApp.postgreDb.list_columns(self.table_name)
				else:
					self.columns_list, self.row_count = self.parentApp.mySQLDb.list_columns(self.table_name)
				# Save Table properties in the myGridSet
				self.parentApp.myGridSet.columns_list = []
				for col in self.columns_list:
					self.parentApp.myGridSet.columns_list.append(col)
				# add column titles to the Grid
				self.myGrid.col_titles  = []
				for col in self.columns_list:
					self.myGrid.col_titles.append(col.name)
			
			self.parentApp.myGridSet.row_count =  self.row_count
			#self.feedback.value = str(self.parentApp.myGridSet.row_count)
			#self.display()
			
			# update query params from GridSettings object
			self.limit = self.parentApp.myGridSet.limit
			self.offset = self.parentApp.myGridSet.offset
			self.sort_direction = self.parentApp.myGridSet.sort_direction
			self.sort_column = self.parentApp.myGridSet.sort_column
			# when called with default settings
			if self.sort_column == '':
				self.sort_column = self.columns_list[0].name
			
			# populate the grid by fetching data from database
			self.myGrid.values = []
			self.rows = []
			self.myGrid.default_column_number = 5
			if self.columns_list:
				self.fetch_rows()
			# populate the grid
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
	
	def fetch_rows(self):
		if self.parentApp.myGridSet.db_type == 'PostgreSQL':
			self.rows = self.parentApp.postgreDb.list_records(self.table_name, self.sort_column, self.sort_direction, self.offset, self.limit)
		else:
			self.rows = self.parentApp.mySQLDb.list_records(self.table_name, self.sort_column, self.sort_direction, self.offset, self.limit)
		
	def exit_application(self):
		self.parentApp.switchForm(None)
		self.parentApp.switchFormNow()
	
	def on_cancel(self):
		self.parentApp.switchForm('TableSelect')
		self.parentApp.switchFormNow()


'''*********************************************************
   Class AddRowForm inherits ActionForm class
   
   Purpose:  Reponsible for adding a new row to the given table
*********************************************************'''
class AddRowForm(npyscreen.ActionForm):
	def afterEditing(self):
		# if timer is set, cancel
		if self.timer:
			self.timer.cancel()# cancel timer
		self.parentApp.setNextFormPrevious()
	
	def create(self):
		# http://stackoverflow.com/questions/4010840
	 	# SQL Alchemy version - working
		'''
		self.datatable = self.parentApp.alchemy.get_datatable(self.parentApp.myGridSet.table)
		for c in self.datatable.c:
			k = str(c).split('.')
			col_name = k[1]
			col_type = str(c.type)
			isNull = "NULL DEF" if c.nullable  else "NOT NULL"
			if  c.primary_key:
				isNull = "PRIM KEY"
			self.dict[col_name] = self.add(npyscreen.TitleText, name = col_name + " " + col_type + " "+isNull, begin_entry_at = 30) 
		'''
		self.timer = None
		self.prim_key_list = []
		# generate dict to hold widget objects
		self.dict = {}
		for col in self.parentApp.myGridSet.columns_list:
			if col.charLen:
				max_chars =  "("+str(col.charLen)+")"
			else:
				max_chars = ''
			if col.precision:
				precision = "("+str(col.precision)+")" 
			else:
				precision = ''
			if  col.primary_key:
				isNull = "PRIM KEY"
				self.prim_key_list.append(col.name)
			else:
				isNull = col.nullable
			self.dict[col.name] = self.add(npyscreen.TitleText, name = col.name + " " +  col.type.upper() + 
				max_chars + precision + " " + isNull, begin_entry_at = 35)
		
		# move one line down from  the previous form
		self.nextrely += 1
		
		# buttons
		self.bn_add = self.add(npyscreen.ButtonPress, name = "Add Row", max_height=1, relx = 15)
		self.bn_add.whenPressed = self.addRow # button press handler
		#self.nextrely += 1
		
		self.feedback = self.add(npyscreen.MultiLineEdit, editable = False, name = ' ', hidden = False, relx = 15, begin_entry_at = 1, max_height=4)
		self.nextrely += 1
		
		self.bn_first_page = self.add(npyscreen.ButtonPress, name = "<< First", max_height=1, relx = 23)
		self.bn_first_page.whenPressed = self.redrawFirstPage # button press handler
		self.nextrely += -1 #widget stays at the same line 
		
		self.bn_prev = self.add(npyscreen.ButtonPress, name = "< Prev", max_height=1, relx = 35)
		self.bn_prev.whenPressed = self.redrawPrev # button press handler
		self.nextrely += -1 # widget stays at the same line 
		
		self.bn_next = self.add(npyscreen.ButtonPress, name = "Next >", max_height=1, relx = 45)
		self.bn_next.when_pressed_function = self.redrawNext # button press handler
		self.nextrely += -1 # widget stays at the same line 
		
		self.bn_last_page = self.add(npyscreen.ButtonPress, name = "Last >>", max_height=1, relx = 55)
		self.bn_last_page.whenPressed = self.redrawLastPage # button press handler
		self.nextrely += 1 
		
		# create Grid widget
		self.myGrid =  self.add(MyGrid, col_titles = [], select_whole_line = True)
		
		# define return on prev form on Esc
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_form
	
	def beforeEditing(self):
		# display cached Grid
		self.myGrid.values = []
		self.myGrid.col_titles = []
		row = []
		for col in self.parentApp.myGridSet.columns_list:
			self.myGrid.col_titles.append(col.name)
		for row in self.parentApp.myGridSet.rows:
			self.myGrid.values.append(row)
		''' for debuging
		list = []
		for col in self.parentApp.myGridSet.columns_list:
			list.append(col.name)
		self.feedback.value = str(list)
		'''
	
	def addRow(self):
		col_dict = {}
		# if user entered value primary key value
		if self.dict[self.prim_key_list[0]].value:
			for col in self.parentApp.myGridSet.columns_list:
				value = self.parentApp.cast_string(str(col.type),  self.dict[col.name].value)
				if value != None or col.nullable != 'NULL':
					col_dict[col.name] = value
		# user doesn't enter value for primary key
		# implement autoincreament
		else:
			for col in self.parentApp.myGridSet.columns_list:
				if col.name != self.prim_key_list[0]:
					value = self.parentApp.cast_string(col.type,  self.dict[col.name].value)
					if value != None or col.nullable != 'NULL':
						col_dict[col.name] = value
		#self.feedback.value = str(col_dict)
		# add row
		
		if self.parentApp.myGridSet.db_type == 'PostgreSQL':
			self.row_id, isSuccess = self.parentApp.postgreDb.add_record(self.parentApp.myGridSet.table, col_dict, self.prim_key_list[0])
		else:
			self.row_id, isSuccess = self.parentApp.mySQLDb.add_record(self.parentApp.myGridSet.table, col_dict, self.prim_key_list[0])
		# give feedback
		if isSuccess:
			id_dict = {}
			self.feedback.value  = "Added Row. " + self.prim_key_list[0] + ": " + str(self.row_id)
			self.feedback.color = 'SAFE'
			# add 1 to row counter
			self.parentApp.myGridSet.row_count = self.parentApp.myGridSet.row_count + 1
			# reset textbox values
			for col in self.parentApp.myGridSet.columns_list:
				self.dict[col.name].value = ''
			# update myGrid and screen
			self.update_grid()
		else:
			self.feedback.value  = str(self.row_id)
			self.feedback.color = 'ERROR'
		
		# make feedback visible
		self.feedback.hidden = False
		self.display()
		if self.timer:
			self.timer.cancel()
		# set times to hide the feedback
		self.timer = Timer(FEEDBACK_TIMEOUT, self.hideFeedback)
		self.timer.start()
	
	def update_grid(self):
		# reset Grid
		self.limit = self.parentApp.myGridSet.limit
		# reset offset and update it
		self.parentApp.myGridSet.offset = 0
		self.parentApp.myGridSet.sort_direction = 'DESC'
		self.offset = self.parentApp.myGridSet.offset
		# update sorting order and column to sort on
		self.sort_direction = self.parentApp.myGridSet.sort_direction
		self.parentApp.myGridSet.sort_column = self.prim_key_list[0]
		self.sort_column = self.parentApp.myGridSet.sort_column
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
	
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
		# not more than row count
		if new_offset <= self.parentApp.myGridSet.row_count:
			self.parentApp.myGridSet.offset = new_offset
		self.offset = self.parentApp.myGridSet.offset
		# update sorting order and column to sort on
		self.sort_direction = self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.fetch_rows()
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
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
		
	def redrawFirstPage(self):
		self.limit = self.parentApp.myGridSet.limit
		self.offset = 0
		self.parentApp.myGridSet.offset = self.offset
		self.sort_direction =  self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		self.myGrid.values = []
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
		
	def redrawLastPage(self):
		self.limit = self.parentApp.myGridSet.limit
		page_count = int(floor(self.parentApp.myGridSet.row_count /self.limit))
		self.offset = page_count * self.parentApp.myGridSet.limit
		self.parentApp.myGridSet.offset = self.offset
		self.sort_direction =  self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		self.myGrid.values = []
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
	
	def fetch_rows(self):
		if self.parentApp.myGridSet.db_type == 'PostgreSQL':
			self.rows = self.parentApp.postgreDb.list_records(self.parentApp.myGridSet.table, self.sort_column, self.sort_direction, self.offset, self.limit)
		else:
			self.rows = self.parentApp.mySQLDb.list_records(self.parentApp.myGridSet.table, self.sort_column, self.sort_direction, self.offset, self.limit)
		
	def hideFeedback(self):
		self.feedback.hidden = True
		self.display()
	
	def exit_form(self):
		self.parentApp.setNextFormPrevious()
		self.parentApp.switchFormNow()


'''*********************************************************
   Class EditRowForm inherits ActionForm class
   
   Purpose:  Reponsible for editing a selected row in the given table
*********************************************************'''
class EditRowForm(npyscreen.ActionForm):
	def afterEditing(self):
		# if timer is set, cancel
		if self.timer:
			self.timer.cancel()
		self.parentApp.setNextFormPrevious()
	
	def create(self):
		self.timer = None
		self.edit_from_self = False
		self.prim_key_list = []
		# generate dict to hold widget objects
		self.dict = {}
		for col in self.parentApp.myGridSet.columns_list:
			if col.charLen:
				max_chars =  "("+str(col.charLen)+")"
			else:
				max_chars = ''
			if col.precision:
				precision = "("+str(col.precision)+")" 
			else:
				precision = ''
			if  col.primary_key:
				isNull = "PRIM KEY" # since if primary, then NOT NULL
				self.prim_key_list.append(col.name)
			else:
				isNull = col.nullable
			self.dict[col.name] = self.add(npyscreen.TitleText, name = col.name + " " +  col.type.upper() + 
				max_chars + precision + " " + isNull, begin_entry_at = 35)
		
		# move one line down from  the previous form
		self.nextrely += 1
		
		# buttons
		self.bn_edit = self.add(npyscreen.ButtonPress, name = "Edit Row", max_height=1, relx = 25)
		self.bn_edit.whenPressed = self.editRow # button press handler
		#self.nextrely += 1
		
		# feedback textbox
		self.feedback = self.add(npyscreen.MultiLineEdit, editable = False, hidden = False, name = ' ', relx = 15, begin_entry_at = 1, max_height=4)
		self.nextrely += 1
		
		self.bn_first_page = self.add(npyscreen.ButtonPress, name = "<< First", max_height=1, relx = 23)
		self.bn_first_page.whenPressed = self.redrawFirstPage # button press handler
		self.nextrely += -1 #widget stays at the same line 
		
		self.bn_prev = self.add(npyscreen.ButtonPress, name = "< Prev", max_height=1, relx = 35)
		self.bn_prev.whenPressed = self.redrawPrev # button press handler
		self.nextrely += -1 # widget stays at the same line 
		
		self.bn_next = self.add(npyscreen.ButtonPress, name = "Next >", max_height=1, relx = 45)
		self.bn_next.when_pressed_function = self.redrawNext # button press handler
		self.nextrely += -1 # widget stays at the same line 
		
		self.bn_last_page = self.add(npyscreen.ButtonPress, name = "Last >>", max_height=1, relx = 55)
		self.bn_last_page.whenPressed = self.redrawLastPage # button press handler
		self.nextrely += 1 
		
		# create Grid widget
		self.myGrid =  self.add(MyGrid, col_titles = [], select_whole_line = True)
		self.myGrid.add_handlers({curses.ascii.LF : self.edit_another_row})
		
		# define return on prev form on Esc
		self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_form
	
	def edit_another_row(self, *args, **keywords):
		self.edit_from_self = True
		# set current values of the fields
		self.row_num = self.myGrid.edit_cell[0]
		for col, col_value in zip(self.parentApp.myGridSet.columns_list, self.myGrid.values[self.row_num]):
			self.dict[col.name].value = str(col_value)
		self.display()
	
	def beforeEditing(self):
		# display cached Grid
		# reset attributes
		self.edit_from_self = False
		self.myGrid.values = []
		self.myGrid.col_titles = []
		row = []
		for col in self.parentApp.myGridSet.columns_list:
			self.myGrid.col_titles.append(col.name)
		for row in self.parentApp.myGridSet.rows:
			self.myGrid.values.append(row)
		
		# set current values of the fields
		self.row_num = self.parentApp.myGridSet.edit_cell[0]
		for col, col_value in zip(self.parentApp.myGridSet.columns_list, self.parentApp.tabMenuF.myGrid.values[self.row_num]):
			self.dict[col.name].value = str(col_value).rstrip(' ') # strip off white spaces
	
	def editRow(self):
		col_dict = {} # dict containing changed columns
		where_dict = {} # dict containing primary keys
		# if edited value selected in  self.parentApp.tabMenuF.myGrid
		if not self.edit_from_self:
			for col, col_value in zip(self.parentApp.myGridSet.columns_list, self.parentApp.tabMenuF.myGrid.values[self.row_num]):
					if self.dict[col.name].value != str(col_value):
						col_dict[col.name] = self.parentApp.cast_string(str(col.type),  self.dict[col.name].value)
					if col.name in self.prim_key_list:
						where_dict[col.name] = col_value
			#self.feedback.value = str(col_dict)
			self.feedback.hidden = False
			self.display()
		# if edited from inside (self.myGrid) via calling edit_another_row(self)
		else:
			for col, col_value in zip(self.parentApp.myGridSet.columns_list, self.myGrid.values[self.row_num]):
					if self.dict[col.name].value != str(col_value):
						col_dict[col.name] = self.parentApp.cast_string(str(col.type),  self.dict[col.name].value)
					if col.name in self.prim_key_list:
						where_dict[col.name] = col_value

		
		# edit row
		if self.parentApp.myGridSet.db_type == 'PostgreSQL':
			row_id, isSuccess = self.parentApp.postgreDb.edit_record(self.parentApp.myGridSet.table, col_dict, where_dict)
		else:
			isSuccess = self.parentApp.mySQLDb.edit_record(self.parentApp.myGridSet.table, col_dict, where_dict)
		# give feedback
		if isSuccess:
			if self.parentApp.myGridSet.db_type == 'PostgreSQL':
				self.feedback.value  = "Row has been edited  succesfully. Returned: " + str(self.prim_key_list) + " = " + str(row_id)
			else:
				self.feedback.value  = "Row has been edited  succesfully."
			self.feedback.color = 'SAFE'
			# update myGrid and screen
			self.update_grid()
		else:
			self.feedback.value  = str(row_id)
			self.feedback.color = 'ERROR'
		# make feedback visible
		self.feedback.hidden = False
		self.display()
		# set time to hide the feedback
		# if timer is set, cancel
		if self.timer:
			self.timer.cancel()
		self.timer = Timer(FEEDBACK_TIMEOUT, self.hideFeedback)
		self.timer.start()
	
	def update_grid(self):
		# reset Grid
		self.limit = self.parentApp.myGridSet.limit
		# reset offset and update it
		#self.parentApp.myGridSet.offset = 0
		self.offset = self.parentApp.myGridSet.offset
		# update sorting order and column to sort on
		self.sort_direction = self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		if self.sort_column == '':
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		# reset Grid
		del self.myGrid.values [:]
		# query rows from database to populate grid
		#self.rows = self.parentApp.postgreDb.list_records(self.parentApp.myGridSet.table, self.sort_column, self.sort_direction, self.offset, self.limit)
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.parentApp.myGridSet.rows = self.rows
	
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
		# new offset <= row_count
		if new_offset <= self.parentApp.myGridSet.row_count:
			self.parentApp.myGridSet.offset = new_offset
		self.offset = self.parentApp.myGridSet.offset
		# update sorting order and column to sort on
		self.sort_direction = self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		#self.rows = self.parentApp.postgreDb.list_records(self.parentApp.myGridSet.table, self.sort_column, self.sort_direction, self.offset, self.limit)
		self.fetch_rows()
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
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		# reset Grid
		self.myGrid.values = []
		# query rows from database to populate grid
		#self.rows = self.parentApp.postgreDb.list_records(self.parentApp.myGridSet.table, self.sort_column, self.sort_direction, self.offset, self.limit)
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
		
	def redrawFirstPage(self):
		self.limit = self.parentApp.myGridSet.limit
		self.offset = 0
		self.parentApp.myGridSet.offset = self.offset
		self.sort_direction =  self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		self.myGrid.values = []
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
		
	def redrawLastPage(self):
		self.limit = self.parentApp.myGridSet.limit
		page_count = int(floor(self.parentApp.myGridSet.row_count /self.limit))
		self.offset = page_count * self.parentApp.myGridSet.limit
		self.parentApp.myGridSet.offset = self.offset
		self.sort_direction =  self.parentApp.myGridSet.sort_direction
		self.sort_column = self.parentApp.myGridSet.sort_column
		# when called with default settings
		if self.sort_column == '':
				self.sort_column = self.parentApp.myGridSet.columns_list[0].name
		self.myGrid.values = []
		self.fetch_rows()
		for row in self.rows:
			self.myGrid.values.append(row)
		self.display()
		
	def fetch_rows(self):
		if self.parentApp.myGridSet.db_type == 'PostgreSQL':
			self.rows = self.parentApp.postgreDb.list_records(self.parentApp.myGridSet.table, self.sort_column, self.sort_direction, self.offset, self.limit)
		else:
			self.rows = self.parentApp.mySQLDb.list_records(self.parentApp.myGridSet.table, self.sort_column, self.sort_direction, self.offset, self.limit)
	
	def hideFeedback(self):
		self.feedback.hidden = True
		self.display()
	
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
		self.parentApp.setNextFormPrevious()
	
	def create(self):
		self.limitWidget = self.add(npyscreen.TitleText, name='Rows per page: ', begin_entry_at = 21, value = str(self.parentApp.myGridSet.limit))
		self.nextrely += 1
		self.offsetWidget = self.add(npyscreen.TitleText, name='Start at row #:', begin_entry_at = 21, value = str(self.parentApp.myGridSet.offset + 1))
		self.nextrely += 1
		self.columnWidget = self.add(npyscreen.TitleSelectOne, max_height=5,
									    name='Order by',
										scroll_exit = True
										)
		self.nextrely += 1
		self.sortDirWidget = self.add(npyscreen.TitleSelectOne, max_height=6,
									    name='Sort',
										values = ['ASC', 'DESC'],
										scroll_exit = True
										)

	def beforeEditing(self):
		if self.columns_list:
			del self.columnWidget.values [:]
			# populate with column names
			for col in self.columns_list:
				self.columnWidget.values.append(col.name)
			# set default settings
			self.columnWidget.value = 0
			self.sortDirWidget.value = 0
	
	def on_ok(self):
		# limit number of rows per page to ten
		if int(self.limitWidget.value) <= 10 and int(self.limitWidget.value) >= 1:
			self.parentApp.myGridSet.limit = int(self.limitWidget.value)
		else:
			self.parentApp.myGridSet.limit = 10
		self.parentApp.myGridSet.offset = int(self.offsetWidget.value) - 1
		self.parentApp.myGridSet.sort_direction = self.sortDirWidget.get_selected_objects()[0]
		self.parentApp.myGridSet.sort_column = self.columnWidget.get_selected_objects()[0]
		

'''**************************************************
   Class MyApplication inherits NPSAppManaged class
   
   Purpose:  Manages  flow between application screens.
				 It's a main app environment
**************************************************'''
class MyApplication(npyscreen.NPSAppManaged):
	add_row_count = 0 # count number of calls to Add Row Form
	edit_row_count = 0 # count number of calls to Edit Row Form
	def onStart(self):
		self.postgreDb = PostgreDB()
		#self.alchemy = Alchemy() # works well, but too slow
		self.myGridSet = GridSettings()
		self.selDbF = self.addForm('MAIN', DBSelectForm, name = 'Select PostgreDB Engine')
		self.selTableF = self.addForm('TableSelect', TableListDisplay, name='Select Table')
		self.tabMenuF = self.addForm('Menu', TableMenuForm)
		self.GridSetF = self.addForm('GridSet', GridSetForm, name='Pagination Settings')
	
	'''**************************************************************************
	Function onInMainLoop()

	Purpose:  It is called when swithing between forms
	***************************************************************************'''	
	def onInMainLoop(self):
		# when app leavs Table Menu Form (obj tabMenuF)
		# create Add Row form
		# Delete the older version since widgets might be different
		if self.NEXT_ACTIVE_FORM == 'Add Row':
			self.add_row_count = self.add_row_count + 1
			#if self.add_row_count == 1:
			if hasattr(self, 'addRowF'):
				del self.addRowF
			self.addRowF = self.addForm('Add Row', AddRowForm, name='Add Row')
		
		# when app leavs Table Menu Form (obj tabMenuF)
		# create Edit Row form. 
		# Delete the older version since widgets might be different
		elif self.NEXT_ACTIVE_FORM == 'Edit Row':
			self.edit_row_count = self.edit_row_count + 1
			#if self.edit_row_count == 1:
			if hasattr(self, 'editRowF'):
				del self.editRowF
			self.editRowF = self.addForm('Edit Row', EditRowForm, name='Edit Row')
		
		elif self.NEXT_ACTIVE_FORM == 'TableSelect':
			if self.myGridSet.db_type == 'MySQL':
				self.mySQLDb = MysqlDB()
			
		'''
		elif self.NEXT_ACTIVE_FORM == 'Menu':
			del self.myGridSet.columns_list [:]
			self.myGridSet.rows = ()
		'''
	def onCleanExit(self):
		self.postgreDb.closeConn()
		
	'''**************************************************************************
	Function cast_string()

	Purpose:  # Cast Python string to corresponding to DB type Python data type
	***************************************************************************'''			
	# http://www.psycopg.org/psycopg/docs/usage.html#adaptation-of-python-values-to-sql-types
	def cast_string(self, data_type, string_val):
		value = None
		if not string_val:
			#self.addRowF.feedback.value = "None chosen"
			return None
		if data_type == "text" or data_type == "char" or data_type == "varchar":
			value = string_val
		elif data_type == 'smallint' or data_type == 'integer' or data_type == 'int':
			value = int(string_val)
		elif data_type == 'bigint' :
			value = long(string_val)
		elif data_type == 'real' or data_type == 'double':
			value = float(string_val)
		elif data_type == 'numeric':
			value = Decimal(string_val)
		elif data_type == 'bool':
			value = True if string_val == 'True' else False
		elif data_type == 'bytea':
			value = buffer(string_val)
		elif data_type == 'date':
			value = datetime.datetime.strptime(string_val, "%m/%d/%Y").date()
		elif data_type == 'time':
			value = datetime.datetime.strptime(string_val, '%H:%M:%S').time()
		elif data_type == 'datetime':
			value = datetime.datetime.strptime(string_val, '%Y/%m/%d %H:%M:%S')
		elif data_type == 'timestamp':
			value = "TIMESTAMP " + string_val
			#self.editRowF.feedback.value = "DataType = "+ data_type + " Value:" + value
			#self.editRowF.feedback.hidden = False
			#self.editRowF.display()
		
		return value
		
	def exit_application(self):
		self.switchForm(None)
		self.switchFormNow()

if __name__ == '__main__':
    MyApplication().run()
    print 'Exited From the App'
