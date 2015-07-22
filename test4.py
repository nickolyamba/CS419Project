#!/usr/bin/python
import npyscreen, curses
import random
import psycopg2

# $mysqli = new mysqli("oniddb.cws.oregonstate.edu", "goncharn-db", $myPassword, "goncharn-db");
rowNumber = 5

class Database(object):
	def list_all_tables(self):
		try:
			conn = psycopg2.connect("dbname='muepyavy' user='muepyavy' host='babar.elephantsql.com' password='EQoh7fJJNxK-4ag4SNUIYwzzWqTVzj-8'")
		except:
			print "I am unable to connect to the database"
		
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
		

class TableListDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = TableList
    def beforeEditing(self):
        self.update_list()
    
    def update_list(self):
        self.wMain.values = self.parentApp.myDatabase.list_all_tables()
        self.wMain.display()


class SelectTableForm(npyscreen.Form):
	def afterEditing(self):
			selectedTableName = self.table.get_selected_objects()[0]
			self.parentApp.getForm('Menu').selectTable = selectedTableName
			self.parentApp.setNextForm('Menu')
	
	def create(self):
		self.table = self.add(npyscreen.TitleSelectOne, max_height=3,
													name='Select Table',
													values = ['Table 1', 'Table 2', 'Table 3'],
													scroll_exit = True)

													
class TableMenuForm(npyscreen.Form):
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
	
	def create(self):
		self.selectTable = None
		self.rowNum = self.add(npyscreen.TitleText, name='Rows: ', value = str(rowNumber))
		#rowNumber = int(str(self.rowNum.value))
		self.action = self.add(npyscreen.TitleSelectOne, max_height=5,
																		name='Select Action',
																		values = ['Next Page', 'Prev Page', 'Add Row', 'Edit Row', 'Delete Row'],
																		scroll_exit = True
																		 # Let the user move out of the widget by pressing 
																		# the down arrow instead of tab.  Try it without to see the difference.
																		)
		# move one line down from  the previous form
		self.nextrely += 1
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


class AddRowForm(npyscreen.Form):
	def afterEditing(self):
		self.parentApp.setNextFormPrevious()
	
	def create(self):
		self.value = None
		self.wgLastName   = self.add(npyscreen.TitleText, name = "Last Name:",)
		self.wgOtherNames = self.add(npyscreen.TitleText, name = "Other Names:")
		self.wgEmail      = self.add(npyscreen.TitleText, name = "Email:")


class MyApplication(npyscreen.NPSAppManaged):
    def onStart(self):
		self.myDatabase = Database()
		selTableF = self.addForm('MAIN', TableListDisplay, name='Select Table')
		tabMenuF = self.addForm('Menu', TableMenuForm, name='Table Menu')
		addRowF = self.addForm('Add Row', AddRowForm, name='Add Row')

if __name__ == '__main__':
    TestApp = MyApplication().run()
    print TestApp
