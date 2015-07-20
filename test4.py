#!/usr/bin/python
import npyscreen, curses
import random

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
		   
class selectTableForm(npyscreen.Form):
	def afterEditing(self):
			self.parentApp.getForm('Menu').value = self.table.get_selected_objects()
			self.parentApp.setNextForm('Menu')
	
	def create(self):
		self.table = self.add(npyscreen.TitleSelectOne, max_height=3,
																		name='Select Table',
																		values = ['Table 1', 'Table 2', 'Table 3'],
																		scroll_exit = True
																		 # Let the user move out of the widget by pressing 
																		# the down arrow instead of tab.  Try it without to see the difference.
																		)
		tableName = self.table.value
		#self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_application
		
	def exit_application(self):
		curses.beep()
		self.parentApp.setNextForm(None)
		self.editing = False


class tableMenuForm(npyscreen.Form):
	def afterEditing(self):
		if self.action.value == 'Add Row':
			self.parentApp.setNextFormPrevious()
		else:
			self.parentApp.setNextForm(None)
		#self.parentApp.setNextFormPrevious()
	
	def create(self):
		self.value = None
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
		if self.value:
			self.name = "Table id : %s" % self.value
		else:
			self.name = "New Record"
			
		#return self.action.value;
		#self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.exit_application
		
	def exit_application(self):
		curses.beep()
		self.parentApp.setNextForm(None)
		self.editing = False

class MyApplication(npyscreen.NPSAppManaged):
    def onStart(self):
		selTableForm = self.addForm('MAIN', selectTableForm, name='Select Table')
		tabMenuForm = self.addForm('Menu', tableMenuForm, name='Table Menu')
		
		return selTableForm.table.value

if __name__ == '__main__':
    TestApp = MyApplication().run()
    print TestApp
