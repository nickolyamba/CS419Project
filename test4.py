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

# $mysqli = new mysqli("oniddb.cws.oregonstate.edu", "goncharn-db", $myPassword, "goncharn-db");
rowNumber = 5

'''**************************************************
* Class Database inherits object class
*
* Purpose:  Connect to the database and query it
**************************************************'''
class Database(object):
	def list_all_tables(self):
		try:
			conn = psycopg2.connect("dbname='muepyavy' user='muepyavy' host='babar.elephantsql.com' password='EQoh7fJJNxK-4ag4SNUIYwzzWqTVzj-8'")
		except:
			print "I am unable to connect to the database"
		
		# fetch list of the tables in the database
		cursor = conn.cursor()
		cursor.execute("SELECT table_name FROM information_schema.tables \
							WHERE \
								table_type = 'BASE TABLE' AND table_schema = 'public' \
							ORDER BY table_type, table_name")
		tables = cursor.fetchall()
		cursor.close()
		return tables
	
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
        #self.parent.parentApp.getForm('EDITRECORDFM').value = act_on_this[0]
        #parent.parentApp.switchForm('EDITRECORDFM')
		selectedTableName = act_on_this[0]
		self.parent.parentApp.getForm('Menu').selectTable = selectedTableName
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
	def afterEditing(self):
		selection = self.action.get_selected_objects()[0]
		if selection == 'Add Row':
			self.parentApp.setNextForm('Add Row')
		elif selection == 'Edit Row':
			self.parentApp.setNextForm('Edit Row')
		elif selection == 'Delete Row':
			self.parentApp.setNextForm('Delete Row')
		elif selection == 'Next Page':
			self.parentApp.setNextForm('Next Page')
		elif selection == 'Prev Page':
			self.parentApp.setNextForm('Prev Page')
		else:
			self.parentApp.setNextForm(None)
		#self.parentApp.setNextFormPrevious()
	
	# Create Widgets
	def create(self):
		self.selectTable = None
		self.rowNum = self.add(npyscreen.TitleText, name='Rows: ', value = str(rowNumber))
		self.action = self.add(npyscreen.TitleSelectOne, max_height=5,
																		name='Select Action',
																		values = ['Next Page', 'Prev Page', 'Add Row', 'Edit Row', 'Delete Row'],
																		scroll_exit = True
																		 # Let the user move out of the widget by pressing 
																		# the down arrow instead of tab.  Try it without to see the difference.
																		)
		# move one line down from  the previous form
		self.nextrely += 1
		# Create MyGrid Widget object
		self.myGrid =  self.add(MyGrid, col_titles = ['1','2','3','4'])
		# populate the grid
		self.myGrid.values = []
		for x in range(rowNumber):
			row = []
			for y in range(4):
				if bool(random.getrandbits(1)):
					row.append("PASS")
				else:
					row.append("FAIL")
			self.myGrid.values.append(row)
	
	def beforeEditing(self):
		if self.selectTable:
			self.name = "%s" % self.selectTable
		else:
			self.name = "New Record"
			
		#return self.action.value;
		#self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_application
		
	def exit_application(self):
		curses.beep()
		self.parentApp.setNextForm(None)
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


'''**************************************************
   Class MyApplication inherits NPSAppManaged class
   
   Purpose:  Manages  flow between application screens.
	It's a main app environment
**************************************************'''
class MyApplication(npyscreen.NPSAppManaged):
    def onStart(self):
		self.myDatabase = Database()
		selTableF = self.addForm('MAIN', TableListDisplay, name='Select Table')
		tabMenuF = self.addForm('Menu', TableMenuForm, name='Table Menu')
		addRowF = self.addForm('Add Row', AddRowForm, name='Add Row')

if __name__ == '__main__':
    TestApp = MyApplication().run()
    print TestApp
