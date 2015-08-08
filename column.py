#!/usr/bin/python

'''**************************************
# Name: Nikolay Goncharenko, Rory Bresnahan
# Email: goncharn@onid.oregonstate.edu
# Class: CS419 - Capstone Project
# Assignment: Python Ncurses UI for 
# MySQL/PostgreSQL Database Management
**************************************'''

'''*********************************************************
Class Column inherits object

Purpose:  Save a column properties to used in the program
*********************************************************'''
class Column(object):
	def __init__ (self):
		name = ''
		type = ''
		charLen = ''
		precision = ''
		nullable = ''
		primary_key = ''
