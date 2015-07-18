#!/usr/bin/python
import npyscreen

class myEmployeeForm(npyscreen.Form):
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

def myFunction(*args):
    F = myEmployeeForm(name = "New Employee")
    F.edit()
    return "Created record for " + F.myName.value

if __name__ == '__main__':
    print npyscreen.wrapper_basic(myFunction)
