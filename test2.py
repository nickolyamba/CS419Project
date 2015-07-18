#!/usr/bin/python
import npyscreen

class myEmployeeForm(npyscreen.Form):
	def afterEditing(self):
		self.parentApp.setNextForm(None)
	
	def create(self):
		self.myName        = self.add(npyscreen.TitleText, name='Name')
		self.myDepartment = self.add(npyscreen.TitleSelectOne, max_height=3,
																		name='Department',
																		values = ['Department 1', 'Department 2', 'Department 3'],
																		scroll_exit = True
																		 # Let the user move out of the widget by pressing 
																		# the down arrow instead of tab.  Try it without to see the difference.
																		)
		self.myDate        = self.add(npyscreen.TitleDateCombo, name='Date Employed')

class MyApplication(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', myEmployeeForm, name='New Employee')

if __name__ == '__main__':
    TestApp = MyApplication().run()
    print "All objects, baby."
