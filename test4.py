#!/usr/bin/python
import npyscreen, curses
import random

# $mysqli = new mysqli("oniddb.cws.oregonstate.edu", "goncharn-db", $myPassword, "goncharn-db");
rowNumber = 5
tableName = ''

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
		selTableF = self.addForm('MAIN', SelectTableForm, name='Select Table')
		tabMenuF = self.addForm('Menu', TableMenuForm, name='Table Menu')
		addRowF = self.addForm('Add Row', AddRowForm, name='Add Row')
		
		return selTableF.table.value

if __name__ == '__main__':
    TestApp = MyApplication().run()
    print TestApp
