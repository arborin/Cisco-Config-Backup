from tkinter import *
from tkinter import ttk
import datetime
import sqlite3
import time
import paramiko
from tabulate import tabulate
from threading import Thread
import pyperclip
from tkinter import messagebox


class Database:
	def __init__(self):
		self.conn = sqlite3.connect('device.db', check_same_thread=False)
		# self.conn = sqlite3.connect('device_db')
		self.c = self.conn.cursor()

		cr_tree_tbl = """CREATE TABLE IF NOT EXISTS list(
		ID INTEGER PRIMARY KEY AUTOINCREMENT,
		NAME CHAR(50),
			IP CHAR(50),
			CAT INTEGER,
			USER CHAR(50),
			PASS CHAR(50),
			ENABLE CHAR(50)
		);
		"""
		self.c.execute(cr_tree_tbl)

		cr_tftp_server = """
			CREATE TABLE IF NOT EXISTS tftp(
			ID INTEGER PRIMARY KEY AUTOINCREMENT,
			name CHAR(30),
				IP CHAR(50),
				DESC TEXT
			);
		"""
		self.c.execute(cr_tftp_server)
		
		cr_command_tbl = """
			CREATE TABLE IF NOT EXISTS command(
			ID INTEGER PRIMARY KEY AUTOINCREMENT,
			command CHAR(30)
			);
		"""
		self.c.execute(cr_command_tbl)
		
		cr_conf_tbl = """
			CREATE TABLE IF NOT EXISTS config(
			ID INTEGER PRIMARY KEY AUTOINCREMENT,
			dev_id INTEGER,
			date CHAR(50),
			config TEXT
			);
		"""

		self.c.execute(cr_conf_tbl)

	def insert(self, query):
		self.c.execute(query)
		self.conn.commit()

	def select(self, query):
		self.conn.commit()
		self.c.execute(query)
		return self.c.fetchall()


class MainApp:
	def __init__(self, master):
		self.db = Database()
		self.master = master


		w = 1500     # width for the Tk root
		h = 800     # height for the Tk root


		ws = self.master.winfo_screenwidth() # width of the screen
		hs = self.master.winfo_screenheight() # height of the screen

		# calculate x and y coordinates for the Tk self.master window
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)

		# set the dimensions of the screen
		# and where it is placed
		self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

		# self.master.geometry('1500x800+100+100')
		self.master.title('Cisco Config Backup')
		self.initUI(master)
		self.write_log('READY', 'INFO')# scrollbar = Scrollbar(self.master)# scrollbar.pack(side = RIGHT, fill = Y)# self.backup_frame.pack(fill = BOTH, expand = True)

	def write_log(self, message, mtype):
		today = datetime.datetime.now()
		format = "%d/%m/%Y %H:%M:%S"
		s = today.strftime(format)# log_type = 'INFO'
		last = self.log.index('end')
		self.log.config(state = 'normal')
		self.log.insert('{}'.format(last), '{} \t\t\t[{}]\t\t\t{}\n'.format(s, mtype, message))
		self.log.see(END)
		self.log.config(state = 'disabled')

	def write_command_line(self, output):
		self.log.config(state = 'normal')
		self.log.delete('1.0', END)
		self.log.config(state = 'normal')
		self.log.insert('1.0', '=' * 100 +'\n' + '{}'.format(output) + '\n' + '=' * 100 + '\n')
		# self.log.see(END)
		self.log.config(state = 'disabled')
		
	def log_details(self, output):
		self.log.config(state = 'normal')
		self.log.delete('1.0', END)
		self.log.config(state = 'normal')
		self.log.insert('1.0', '{}'.format(output) + '\n')
		# self.log.see(END)
		self.log.config(state = 'disabled')
		
	def save_cat(self, root):
		self.cat = self.category.get()
		if self.cat:
			ins_cat = "INSERT INTO list (NAME) VALUES ('{}')".format(self.cat)
			self.db.insert(ins_cat)

			self.select_cat = "SELECT id, name FROM list WHERE name = '{}'".format(self.cat)
			self.cat = self.db.select(self.select_cat)

			for row in self.cat:
				self.treeview.insert('', '{}'.format(row[0]), '{}'.format(row[0]), text = '{}'.format(row[1]))

			self.write_log('ADD NEW CATEGORY - {}'.format(self.cat[0][1]), 'INFO')
			root.destroy()
		else :
			self.write_log("Category is empty!", "WARNING")
		root.destroy()

	def new_category(self):
		self.popup = Toplevel(self.master)
		self.popup.title('New cat')
		sw = self.popup.winfo_screenwidth()
		sh = self.popup.winfo_screenheight()
		w = 100
		h = 300
		self.popup.geometry('{}x{}+{}+{}'.format(h, w, int(sw/2-w/2), int(sh/2-h/2)))
		# self.popup.geometry('300x100+200+200')
		self.popup.resizable(False, False)
		self.name = Label(self.popup, text = "Category Name")
		self.name.grid(row = 0, column = 0, padx = 10, pady = 10)
		self.category = Entry(self.popup, width = 20)
		self.category.grid(row = 0, column = 1, columnspan = 2)
		self.cancel = ttk.Button(self.popup, text = 'Cancel', command = lambda: self.popup.destroy())
		self.cancel.grid(row = 1, column = 1, sticky = 'e')
		self.save = ttk.Button(self.popup, text = 'Save', command = lambda: self.save_cat(self.popup))
		self.save.grid(row = 1, column = 2, sticky = 'e')
	
	def edit_cat_selection(self,event):
		self.value_of_combo = self.cb.get()

		self.select_cat = "SELECT id FROM list WHERE name='{}'".format(self.value_of_combo)
		self.cat_id = self.db.select(self.select_cat)
		self.id.configure(text=self.cat_id[0][0])
	
	# def update_dev(self, root):
	# 	self.cat = self.cb.get()
	# 	self.id = int(self.id.cget('text'))
		
	# 	if self.cat:
	# 		ins_cat = "UPDATE list SET name = '{}' WHERE ID = {};".format(self.cat, self.id)

	# 		root.destroy()
	# 	else :
	# 		self.write_log("Category is empty!", "WARNING")
	# 	root.destroy()

	def update_cat(self, root):
		self.cat = self.cb.get()
		self.id = int(self.id.cget('text'))
		print(self.cat, self.id)
		if self.cat:
			ins_cat = "UPDATE list SET name = '{}' WHERE ID = {};".format(self.cat, self.id)
			self.db.insert(ins_cat)
			self.treeview.delete(*self.treeview.get_children())
			self.get_tree_view()
			root.destroy()
		else :
			self.write_log("Category is empty!", "WARNING")
		root.destroy()

	def delete_cat(self, root):
		cat = self.cb.get()
		id = int(self.id.cget('text'))
		
		print(cat, id)
		
		if self.cat:
			select_cat = "SELECT id from list WHERE cat = {};".format(id)

			cat_result = self.db.select(select_cat)
			print(cat_result)

			if len(cat_result)>0:
				messagebox.showinfo("Info", "Category contain devices!")
			else:
				del_dev = "DELETE FROM list WHERE id = '{}'".format(id)
				self.db.select(del_dev)
			
			self.treeview.delete(*self.treeview.get_children())
			self.get_tree_view()
			root.destroy()
		else :
			self.write_log("Category is empty!", "WARNING")
		root.destroy()

	def update_dev(self, root):
		
		id = int(self.id.get())
		cat = self.cb.get()
		name = self.name.get()
		ip_add = self.ip_add.get()
		user_name = self.user_name.get()
		user_pswd = self.user_pswd.get()
		user_enpswd = self.user_enpswd.get()
		
		print("{} {} {} {} {} {} {}".format(id, cat, name, ip_add, user_name, user_pswd, user_enpswd))


		self.select_cat = "SELECT id FROM list WHERE name='{}'".format(cat)
		cat_result = self.db.select(self.select_cat)
		cat_id = cat_result[0][0]
		
		if self.cat:
			update_dev = """UPDATE list SET cat = '{}', 
											name = '{}', 
											ip = '{}', 
											user = '{}', 
											pass = '{}', 
											enable = '{}' 
							 WHERE ID = {};""".format(cat_id, name, ip_add, user_name, user_pswd, user_enpswd, id)
			print(update_dev)
			self.db.insert(update_dev)
			self.treeview.delete(*self.treeview.get_children())
			self.get_tree_view()
			
			root.destroy()
		else :
			self.write_log("Category is empty!", "WARNING")
		root.destroy()
	
	def edit_category(self):
		self.popup = Toplevel(self.master)
		self.popup.title('Edit category')
		sw = self.popup.winfo_screenwidth()
		sh = self.popup.winfo_screenheight()
		w = 100
		h = 300
		self.popup.geometry('{}x{}+{}+{}'.format(h, w, int(sw/2-w/2), int(sh/2-h/2)))
		self.popup.resizable(False, False)

		self.name = Label(self.popup, text = "Category")
		self.name.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'e')

		choice_var = StringVar()
		self.select_dev = "SELECT id, cat, name, ip FROM list WHERE cat is null"
		self.dev = self.db.select(self.select_dev)
		self.cat = []

		for row in self.dev:
			self.cat.append(row[2])

		self.cb = ttk.Combobox(self.popup)
		self.cb.config(width = "18")
		self.cb['values'] = self.cat
		self.cb.grid(row = 0, column = 1, padx = 10, pady = 10, columnspan = 2, sticky = 'e')
		self.cb.bind("<<ComboboxSelected>>", self.edit_cat_selection)
		self.id = Label(self.popup, text = "ID")
		# self.id.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = 'e')
		
		
		# self.delete = ttk.Button(self.popup, text = 'Delete', command = lambda: self.popup.destroy())
		self.delete = ttk.Button(self.popup, text = 'Delete', command = lambda: self.delete_cat(self.popup))
		self.delete.grid(row = 6, column = 1, sticky = 'e')

		self.update = ttk.Button(self.popup, text = 'Update Dev', command = lambda: self.update_cat(self.popup))
		self.update.grid(row = 6, column = 2, sticky = 'e')
		
	
	def close_program(self):
		self.master.destroy()
	
	def about_as(self):
		self.popup = Toplevel(self.master)
		self.popup.title('About as')
		sw = self.popup.winfo_screenwidth()
		sh = self.popup.winfo_screenheight()
		w = 100
		h = 300
		self.popup.geometry('{}x{}+{}+{}'.format(h, w, int(sw/2-w/2), int(sh/2-h/2)))
		# self.popup.geometry('300x100+200+200')
		self.popup.resizable(False, False)
		self.title = Label(self.popup, text = "This program makes cisco config backups").pack()
		self.name = Label(self.popup, text = "Nika Kobaidze").pack()
		self.date = Label(self.popup, text = "2016").pack()


	def delete_dev(self, root):
		id = int(self.id.get())
		
		del_dev = "DELETE FROM list WHERE id = '{}'".format(id)
		self.db.select(del_dev)

		self.write_log('DEVICE DELETED, ID: - {}'.format(id), 'INFO')

		self.treeview.delete(*self.treeview.get_children())
		self.get_tree_view()	
		root.destroy()


	def save_dev(self, root):
		cat = self.cb.get()
		dev_name = self.name.get()
		ip = self.ip_add.get()
		uname = self.user_name.get()
		pswd = self.user_pswd.get()
		enpswd = self.user_enpswd.get()
		cat_id = ''
		
		
		if cat and dev_name:
			self.select_dev = "SELECT id FROM list WHERE name = '{}'".format(dev_name)
			self.id = self.db.select(self.select_dev)
			if self.id:
				self.write_log("NAME {} IS ALREADY EXSISTS!".format(dev_name), "WARNING")
			else:
				self.select_cat = "SELECT id FROM list WHERE name = '{}'".format(cat)
				self.id = self.db.select(self.select_cat)
				for row in self.id:
					cat_id = row[0]
					
				ins_dev = "INSERT INTO list (NAME, IP, USER, PASS, CAT, ENABLE) VALUES ('{}','{}','{}','{}','{}','{}')".format(dev_name, ip, uname, pswd, cat_id, enpswd)
				self.db.insert(ins_dev)
	
				self.select_dev = "SELECT id, cat, name, ip FROM list WHERE name = '{}'".format(dev_name)
				self.dev = self.db.select(self.select_dev)
	
				for row in self.dev:
					self.treeview.insert('{}'.format(row[1]), '{}'.format(row[0]), '{}'.format(row[0]), text = '{}'.format(row[2]))
				self.treeview.set(row[0], '#1', row[3])
	
				self.write_log('ADD NEW DEVICE - {}'.format(dev_name), 'INFO')
				self.update_stats()
				root.destroy()
		else :
			self.write_log("CATEGORY OR NAME IS EMPTY!", "WARNING")
		root.destroy()

	def edit_device(self):
		device_id = format(self.v_id.cget("text"))

		if device_id.isdigit():
			self.popup = Toplevel(self.master)
			self.popup.title("Edit Device")
			sw = self.popup.winfo_screenwidth()
			sh = self.popup.winfo_screenheight()
			w = 300
			h = 300
			self.popup.geometry('{}x{}+{}+{}'.format(h, w, int(sw/2-w/2), int(sh/2-h/2)))
			self.popup.resizable(False, False)

			id = self.v_id.cget('text')
			ip = self.v_ip.cget("text")
			device = self.v_dname.cget("text")
			user = self.v_uname.cget("text")
			psw = self.v_pass.cget("text")
			enable = self.en_pass.cget("text")
			cat = self.v_cat.cget("text")
			
			self.name = Label(self.popup, text = "Category")
			self.name.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'e')

			choice_var = StringVar()
			self.select_dev = "SELECT id, cat, name, ip FROM list WHERE cat is null"
			self.dev = self.db.select(self.select_dev)
			self.cat = []

			for row in self.dev:
				self.cat.append(row[2])

			

			self.cb = ttk.Combobox(self.popup)
			self.cb.config(width = "18")
			self.cb['values'] = self.cat
			self.cb.insert(0, cat)
			self.cb.grid(row = 0, column = 1, padx = 10, pady = 10, columnspan = 2, sticky = 'e')

			self.device = Label(self.popup, text = "Device")
			self.device.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = 'e')
			self.name = Entry(self.popup, width = 20)
			self.name.insert(0, device)
			self.name.grid(row = 1, column = 1, columnspan = 2)

			self.ip = Label(self.popup, text = "Ip")
			self.ip.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = 'e')
			self.ip_add = Entry(self.popup, width = 20)
			self.ip_add.insert(0, ip)
			self.ip_add.grid(row = 2, column = 1, columnspan = 2)

			self.user = Label(self.popup, text = "User")
			self.user.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = 'e')
			self.user_name = Entry(self.popup, width = 20)
			self.user_name.insert(0, user)
			self.user_name.grid(row = 3, column = 1, columnspan = 2)

			self.pswd = Label(self.popup, text = "SSH Passwd")
			self.pswd.grid(row = 4, column = 0, padx = 10, pady = 10, sticky = 'e')
			self.user_pswd = Entry(self.popup, width = 20)
			self.user_pswd.insert(0, psw)
			self.user_pswd.grid(row = 4, column = 1, columnspan = 2)
			
			self.enpswd = Label(self.popup, text = "Enable Passwd")
			self.enpswd.grid(row = 5, column = 0, padx = 10, pady = 10, sticky = 'e')
			self.user_enpswd = Entry(self.popup, width = 20)
			self.user_enpswd.insert(0, enable)
			self.user_enpswd.grid(row = 5, column = 1, columnspan = 2)
			
			# self.cancel = ttk.Button(self.popup, text = 'Delete', command = lambda: self.popup.destroy())
			self.cancel = ttk.Button(self.popup, text = 'Delete', command = lambda: self.delete_dev(self.popup))
			self.cancel.grid(row = 6, column = 1, sticky = 'e')

			self.save = ttk.Button(self.popup, text = 'Update', command = lambda: self.update_dev(self.popup))
			self.save.grid(row = 6, column = 2, sticky = 'e')

			# ID HIDDEN
			self.id = Entry(self.popup, width = 20)
			self.id.insert(0, id)
			self.id.grid(row = 7, column = 1, padx = 10, pady = 10, columnspan = 2, sticky = 'e')
		else:
			messagebox.showinfo("Info", "Please select device")
		

		


	def new_device(self):

		self.popup = Toplevel(self.master)
		self.popup.title('New Device')
		sw = self.popup.winfo_screenwidth()
		sh = self.popup.winfo_screenheight()
		w = 300
		h = 300
		self.popup.geometry('{}x{}+{}+{}'.format(h, w, int(sw/2-w/2), int(sh/2-h/2)))
		self.popup.resizable(False, False)

		self.name = Label(self.popup, text = "Category")
		self.name.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'e')

		choice_var = StringVar()
		self.select_dev = "SELECT id, cat, name, ip FROM list WHERE cat is null"
		self.dev = self.db.select(self.select_dev)
		self.cat = []

		for row in self.dev:
			self.cat.append(row[2])

		self.cb = ttk.Combobox(self.popup)
		self.cb.config(width = "18")
		self.cb['values'] = self.cat
		self.cb.grid(row = 0, column = 1, padx = 10, pady = 10, columnspan = 2, sticky = 'e')

		self.device = Label(self.popup, text = "Device")
		self.device.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = 'e')
		self.name = Entry(self.popup, width = 20)
		self.name.grid(row = 1, column = 1, columnspan = 2)

		self.ip = Label(self.popup, text = "Ip")
		self.ip.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = 'e')
		self.ip_add = Entry(self.popup, width = 20)
		self.ip_add.grid(row = 2, column = 1, columnspan = 2)

		self.user = Label(self.popup, text = "User")
		self.user.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = 'e')
		self.user_name = Entry(self.popup, width = 20)
		self.user_name.grid(row = 3, column = 1, columnspan = 2)

		self.pswd = Label(self.popup, text = "SSH Passwd")
		self.pswd.grid(row = 4, column = 0, padx = 10, pady = 10, sticky = 'e')
		self.user_pswd = Entry(self.popup, width = 20)
		self.user_pswd.grid(row = 4, column = 1, columnspan = 2)
		
		self.enpswd = Label(self.popup, text = "Enable Passwd")
		self.enpswd.grid(row = 5, column = 0, padx = 10, pady = 10, sticky = 'e')
		self.user_enpswd = Entry(self.popup, width = 20)
		self.user_enpswd.grid(row = 5, column = 1, columnspan = 2)
		
		self.cancel = ttk.Button(self.popup, text = 'Cancel', command = lambda: self.popup.destroy())
		self.cancel.grid(row = 6, column = 1, sticky = 'e')

		self.save = ttk.Button(self.popup, text = 'Save', command = lambda: self.save_dev(self.popup))
		self.save.grid(row = 6, column = 2, sticky = 'e')

	def save_tftp(self, root):
		tftp = self.tftp_ip_add.get()

		ins_tftp = "INSERT INTO tftp (IP) VALUES ('{}')".format(tftp)
		self.db.insert(ins_tftp)
		self.update_stats()
		self.write_log('ADD NEW TFTP SERVER - {}'.format(tftp), 'INFO')
		root.destroy()

	def new_tftp(self):
		self.popup = Toplevel(self.master)
		self.popup.title('New TFTP')
		sw = self.popup.winfo_screenwidth()
		sh = self.popup.winfo_screenheight()
		w = 100
		h = 300
		self.popup.geometry('{}x{}+{}+{}'.format(h, w, int(sw/2-w/2), int(sh/2-h/2)))
		self.popup.resizable(False, False)

		self.name = Label(self.popup, text = "Server IP")
		self.name.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'e')

		self.tftp_ip_add = Entry(self.popup, width = 20)
		self.tftp_ip_add.grid(row = 0, column = 1, columnspan = 2)

		self.cancel = ttk.Button(self.popup, text = 'Cancel', command = lambda: self.popup.destroy())
		self.cancel.grid(row = 5, column = 1, sticky = 'e')

		self.save = ttk.Button(self.popup, text = 'Save', command = lambda: self.save_tftp(self.popup))
		self.save.grid(row = 5, column = 2, sticky = 'e')
	

	def save_command(self, root):
		new_command = self.command.get()

		command_query = "INSERT INTO command (command) VALUES ('{}')".format(new_command)
		self.db.insert(command_query)
		self.update_stats()
		self.write_log('ADD NEW COMMAND {}'.format(new_command), 'INFO')
		root.destroy()
		

	def new_command(self):
		self.popup = Toplevel(self.master)
		self.popup.title('New Command')
		sw = self.popup.winfo_screenwidth()
		sh = self.popup.winfo_screenheight()
		w = 100
		h = 300
		self.popup.geometry('{}x{}+{}+{}'.format(h, w, int(sw/2-w/2), int(sh/2-h/2)))
		self.popup.resizable(False, False)

		self.name = Label(self.popup, text = "Command")
		self.name.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'e')

		self.command = Entry(self.popup, width = 20)
		self.command.grid(row = 0, column = 1, columnspan = 2)

		self.cancel = ttk.Button(self.popup, text = 'Cancel', command = lambda: self.popup.destroy())
		self.cancel.grid(row = 5, column = 1, sticky = 'e')

		self.save = ttk.Button(self.popup, text = 'Save', command = lambda: self.save_command(self.popup))
		self.save.grid(row = 5, column = 2, sticky = 'e')


	def newselection(self, event):
		self.date_cb.set('')
		self.value_of_combo = self.conf_cb.get()
		print(self.value_of_combo)
		self.write_log('{} SELECTED'.format(self.value_of_combo), 'INFO')
		self.select_dev = "SELECT id FROM list WHERE name='{}'".format(self.value_of_combo)
		self.dev_id = self.db.select(self.select_dev)
		print(self.dev_id[0][0])
		self.select_dev = "SELECT id,date,config FROM config WHERE dev_id='{}'".format(self.dev_id[0][0])
		self.select_dev = self.db.select(self.select_dev)
		self.date = []
		for raw in self.select_dev:
			self.date.append(raw[1])
		print(self.date)
		self.date_cb['values'] = self.date
		print(self.value_of_combo)
	

	def selectNode(self, event):
		item = self.treeview.selection()

		self.dev_name = self.treeview.item(item, "text")
		self.select_dev = "SELECT l.name, l.ip, l.cat, l.user, l.pass, l.id, l.enable, l2.name FROM list l LEFT join list l2 ON l.cat=l2.id  WHERE l.name='{}'".format(self.dev_name)
		self.dev = self.db.select(self.select_dev)

		print(self.dev)
		for row in self.dev:
			if row[2]:
				try:
					self.write_log('SELECT {} {} {}'.format(row[0], row[1], row[3]), 'INFO')
					self.v_dname.config(text = "temp")
					self.v_dname.config(text = '{}'.format(row[0]))
					self.v_ip.config(text = '{}'.format(row[1]))
					self.v_uname.config(text = '{}'.format(row[3]))
					self.v_pass.config(text = '{}'.format(row[4]))
					self.v_id.config(text = '{}'.format(row[5]))
					self.en_pass.config(text = '{}'.format(row[6]))
					self.v_cat.config(text = '{}'.format(row[7]))
					
				except:
					pass


	def set_backup_date(self):
		self.date_cb.set('')
		self.date_cb['values'] = []
		self.dev_name = self.v_dname.cget('text')
		print(self.dev_name)
		if self.dev_name == "-----":
			pass
		else:
			# self.write_log('{} SELECTED'.format(self.dev_name), 'INFO')
			self.select_dev = "SELECT id FROM list WHERE name='{}'".format(self.dev_name)
			self.dev_id = self.db.select(self.select_dev)
			if self.dev_id:
				print(self.dev_id[0][0])
		
				self.select_dev = "SELECT id, date, config FROM config WHERE dev_id='{}'".format(self.dev_id[0][0])
				self.select_dev = self.db.select(self.select_dev)
				self.date = []
				for raw in self.select_dev:
					self.date.append(raw[1])
				print(self.date)
				self.date_cb['values'] = self.date
				print(self.dev_name)
	

	def update_dev_list(self):
		self.select_dev = "SELECT id, cat, name, ip FROM list WHERE cat not null"
		self.dev = self.db.select(self.select_dev)
		self.cat = []
		for row in self.dev:
			self.cat.append(row[2])
		self.conf_cb['values'] = self.cat
	

	def update_fttp_list(self):
		self.tftp_query = "SELECT ip FROM tftp"
		self.temp = self.db.select(self.tftp_query)
		self.server_list = []
		for row in self.temp:
			self.server_list.append(row[0])
		self.cb_tftp['values'] = self.server_list
	

	def update_command_list(self):
		self.command_query = "SELECT command FROM command"
		self.temp = self.db.select(self.command_query)
		self.command_list = []
		for row in self.temp:
			self.command_list.append(row[0])
		self.cb_command['values'] = self.command_list


	def makeConfigBackup(self):
		self.write_log('BACKUP THREAD', 'WARNING')
		t = Thread(target=self.make_backup_thread)
		t.start()
			
			
	def make_backup_thread(self):
		self.write_log('BACKUP FUNCTION RUN', 'WARNING')
		id = self.v_id.cget('text')
		ip = self.v_ip.cget("text")
		user = self.v_uname.cget("text")
		psw = self.v_pass.cget("text")
		enable = self.en_pass.cget("text")
		print(ip, user, psw)
		if ip == "-----":
			self.write_log('SELECT DEVICE', 'WARNING')
		else :
			# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
			try:
				remote_conn_pre = paramiko.SSHClient()
				remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())# remote_conn_pre.connect("192.168.164.5", username = "admin", password = "123456", look_for_keys = False, allow_agent = False)
				remote_conn_pre.connect("{}".format(ip), username = "{}".format(user), password = "{}".format(psw), port="4010", look_for_keys = False, allow_agent = False)# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	
				remote_conn = remote_conn_pre.invoke_shell()
				output = remote_conn.recv(65535)
				# print(output)
				remote_conn.send("en\n")
				time.sleep(.5)
				output = remote_conn.recv(65535)
				# print(output)
				remote_conn.send("{}\n".format(enable))
				time.sleep(.5)
				output = remote_conn.recv(65535)
				# print (output)
	
				remote_conn.send("terminal length 0\n")
				time.sleep(.5)
				output = remote_conn.recv(65535)
				# print (output)
				
				
				
				remote_conn.send("show run\n")
				time.sleep(.9)
				output = remote_conn.recv(65535)
				# print (type(output))
				output = output.decode("utf-8")
				
				date = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
				ins_dev = "INSERT INTO config (dev_id, date, config) VALUES ('{}','{}','{}')".format(id, date, output)
				self.db.insert(ins_dev)
				# self.write_command_line(output)
				self.write_log("RUNNING CONFIG SAVED TO DATABASE", 'INFO')
				
				
				self.tftp_ser = self.cb_tftp.get()
				print(self.tftp_ser)
				if self.tftp_ser:
					self.device = self.v_dname.cget("text")
					print("----------------------")
					remote_conn.send("copy running-config tftp:\n")
					time.sleep(.5)
					remote_conn.send("{}\n".format(self.tftp_ser))
					time.sleep(.5)
					remote_conn.send("\n")
					time.sleep(.5)
					print("----------------------")
					self.write_log("UPLOADED TO {} TFTP SERVER".format(self.tftp_ser), 'INFO')
				self.update_stats()
			except:
				self.write_log('CONNECTION ERROR!', 'WARNING')


	def showBackup(self):
		self.device = self.conf_cb.get()
		self.date = self.date_cb.get()

		if self.device and self.date:
			self.log.config(state = 'normal')
			self.log.delete('1.0', END)
			self.select_dev = "SELECT id FROM list WHERE name='{}'".format(self.device)
			self.dev_id = self.db.select(self.select_dev)
			print(self.dev_id[0][0])

			self.select_conf = "SELECT id,date,config FROM config WHERE dev_id='{}' and date='{}'".format(self.dev_id[0][0], self.date)
			self.select_conf = self.db.select(self.select_conf)
			self.conf = []
			for raw in self.select_conf:
				self.conf.append(raw[2])
			output = str(self.conf[0])
			self.write_command_line(output)
		else:
			self.write_log('SELECT DEVICE AND DATE','WARNING')
	

	def showDetails(self):
		self.select_dev = "SELECT id, name, ip FROM list WHERE cat not null"
		self.select_dev = self.db.select(self.select_dev)
		
		# dev_name, ip, total backup, last backup, first backup
		table_list = []
		for id, dev in enumerate(self.select_dev):
			l = []
			l.append(id+1)
			l.append(dev[1])
			l.append(dev[2])
			total = "SELECT `dev_id` FROM config WHERE dev_id = {};".format(dev[0])
			total = self.db.select(total)
			l.append(len(total))
			new = "SELECT `date` FROM config WHERE dev_id = {} order by date desc;".format(dev[0])
			new = self.db.select(new)
			if new:
				l.append(new[0][0])
			else:
				l.append(False)
			old = "SELECT `date` FROM config WHERE dev_id = {} order by date;".format(dev[0])
			old = self.db.select(old)
			if old:
				l.append(old[0][0])
			else:
				l.append(False)
			table_list.append(l)
		headers=["#","Name", "IP", "Total Backup", 'Last', 'First']
		self.write_command_line(tabulate(table_list, headers))
		
	
	def check_tftp(self):
		if self.var.get():
			self.cb_tftp.pack(pady = 5)
		else:
			self.cb_tftp.set('')
			self.cb_tftp.pack_forget()
	

	def run_command(self):
		self.command = self.cb_command.get()

		self.commands = self.multi_command.get("1.0","end")

		command_list = self.commands.split('\n')
		commands = list(filter(None, command_list)) # remove emty epement if exists

		self.write_log(commands, 'COMMAND')
		t = Thread(target=self.run_command_thread, args=(commands,))
		t.start()
			
	
	def run_command_thread(self, commands):
		self.command = commands
		if self.command:
			id = self.v_id.cget('text')
			ip = self.v_ip.cget("text")
			user = self.v_uname.cget("text")
			psw = self.v_pass.cget("text")
			enable = self.en_pass.cget("text")
	
			if ip == "-----":
				self.write_log('SELECT DEVICE', 'WARNING')
			else :
				# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
				# try:
				remote_conn_pre = paramiko.SSHClient()
				remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())# remote_conn_pre.connect("192.168.164.5", username = "admin", password = "123456", look_for_keys = False, allow_agent = False)
				remote_conn_pre.connect("{}".format(ip), username = "{}".format(user), password = "{}".format(psw), port=4010, look_for_keys = False, allow_agent = False)# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
				# remote_conn_pre.connect("73.215.176.112", username = "nkobaidze", password = "nikakobaidze1", port=4010, look_for_keys = False, allow_agent = False)# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	
				remote_conn = remote_conn_pre.invoke_shell()
				output = remote_conn.recv(65535)
				print(output)
				remote_conn.send("en\n")
				time.sleep(.5)
				output = remote_conn.recv(65535)
				print(output)
				remote_conn.send("{}\n".format(enable))
				time.sleep(.5)
				output = remote_conn.recv(65535)
				print (output)
	
				remote_conn.send("terminal length 0\n")
				time.sleep(.5)
				output = remote_conn.recv(65535)
				print (output)

				for command in commands:
					remote_conn.send("{}\n".format(command))
					time.sleep(.9)
					output = remote_conn.recv(65535)
					print (type(output))
					output = output.decode("utf-8")
					self.write_log("{}".format(command.upper()), 'COMMAND')
					self.write_command_line(output)
					time.sleep(1)
				# except:
				# 	self.write_log('CONNECTION ERROR', "WARNING")
		else:
			self.write_log('WRITE COMMAND', 'WARNING')	
	
	def deleteBackup(self):
		# self.log.config(state = 'normal')
		# self.log.delete('1.0', END)

		self.device = self.conf_cb.get()
		self.date = self.date_cb.get()

		self.select_dev = "SELECT id FROM list WHERE name='{}'".format(self.device)
		self.dev_id = self.db.select(self.select_dev)
		print(self.dev_id[0][0])

		self.select_conf = "DELETE FROM config WHERE dev_id='{}' and date='{}'".format(self.dev_id[0][0], self.date)
		self.db.insert(self.select_conf)
		self.write_log('BACKUP CONFIG DELETED!', 'INFO')

		self.set_backup_date()
		self.update_stats()
		print(self.conf)


	def get_dev_number(self):
		self.select_dev = "SELECT id, name FROM list WHERE cat not null"
		self.select_dev = self.db.select(self.select_dev)
		self.num_of_dev.configure(text=len(self.select_dev))


	def get_backup_number(self):
		self.select_back = "SELECT id FROM config"
		self.select_back = self.db.select(self.select_back)
		self.num_of_back.configure(text=len(self.select_back))


	def get_without_backup(self):
		self.select_dev = "SELECT id FROM list WHERE cat not null"
		self.all_dev = self.db.select(self.select_dev)
		self.backup_devices = "SELECT dev_id FROM config"
		self.all_backup = self.db.select(self.backup_devices)

		self.count = 0
		for i in self.all_dev:
			if i not in self.all_backup:
				self.count+=1
		self.without_backup.configure(text=self.count)


	def get_old_new(self):
		self.new = "SELECT `date` FROM config group by dev_id order by date desc;"
		self.old = "SELECT `date` FROM config group by dev_id order by date;"

		self.new = self.db.select(self.new)
		self.old = self.db.select(self.old)
		if self.new:
			self.new_lbl.configure(text = str(self.new[0][0]))
		else:
			self.new_lbl.configure(text = "-----")
		if self.old:
			self.old_lbl.configure(text = str(self.old[0][0]))
		else:
			self.old_lbl.configure(text = "-----")


	def get_tree_view(self):
		self.select_cat = "SELECT id, name FROM list WHERE cat is null"
		self.cat = self.db.select(self.select_cat)

		for row in self.cat:
			self.treeview.insert('', '{}'.format(row[0]), '{}'.format(row[0]), text = '{}'.format(row[1]), tags = ('{}'.format(row[0]),))# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

		self.select_dev = "SELECT id, cat, name, ip FROM list WHERE cat not null"
		self.dev = self.db.select(self.select_dev)

		for row in self.dev:
			self.treeview.insert('{}'.format(row[1]), '{}'.format(row[0]), '{}'.format(row[0]), text = '{}'.format(row[2]))
			self.treeview.set(row[0], '#1', row[3])
		# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

		self.treeview.bind("<Button-1>", self.selectNode)
	

	def update_stats(self):
		self.get_backup_number()
		self.get_dev_number()
		self.get_without_backup()
		self.get_old_new()
		self.update_dev_list()
		self.update_fttp_list()
		self.update_command_list()
		self.get_tree_view()
		self.write_log("UPDATE STATISTIC", "INFO")
	

	def run_thread_command(self, ip, user, psw, enable):
			remote_conn_pre = paramiko.SSHClient()
			remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())# remote_conn_pre.connect("192.168.164.5", username = "admin", password = "123456", look_for_keys = False, allow_agent = False)
			remote_conn_pre.connect("{}".format(ip), username = "{}".format(user), password = "{}".format(psw), look_for_keys = False, allow_agent = False)# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
			self.write_log('LOGIN TO DEVICE SUCCESS', 'INFO')
			remote_conn = remote_conn_pre.invoke_shell()
			output = remote_conn.recv(65535)
			print(output)
			remote_conn.send("en\n")
			time.sleep(.5)
			output = remote_conn.recv(65535)
			print(output)
			remote_conn.send("{}\n".format(enable))
			time.sleep(.5)
			output = remote_conn.recv(65535)
			print (output)
			remote_conn.send("conf t\n")
			time.sleep(.5)
			output = remote_conn.recv(65535)
			self.write_log('='*50, 'INFO')
			self.write_log('RESTORE BROCESS BEGINS', 'INFO')
			self.write_log('='*50, 'INFO')
			for command in self.conf[4:]:
				self.write_log('{}'.format(command), 'INFO')
				remote_conn.send("{}\n".format(command))
				time.sleep(.1)
			self.write_log('='*50, 'INFO')
			self.write_log('RESTORE FINISH', 'INFO')
			self.write_log('='*50, 'INFO')
	
	
	def restore_backup(self):
		self.write_log('RESTORE FUNCTION RUN SUCCESS', 'INFO')
		self.device = self.conf_cb.get()
		self.date = self.date_cb.get()
		self.select_dev = "SELECT ip, user, pass, enable FROM list WHERE name = '{}'".format(self.device)
		self.dev = self.db.select(self.select_dev)
		ip = self.dev[0][0]
		user = self.dev[0][1]
		psw = self.dev[0][2]
		enable = self.dev[0][3]
		
		if self.device and self.date:
			self.select_dev = "SELECT id FROM list WHERE name='{}'".format(self.device)
			self.dev_id = self.db.select(self.select_dev)
			self.select_conf = "SELECT id,date,config FROM config WHERE dev_id='{}' and date='{}'".format(self.dev_id[0][0], self.date)
			self.select_conf = self.db.select(self.select_conf)
			self.conf = []
			for raw in self.select_conf:
				self.conf.append(raw[2])
			self.conf = self.conf[0].split('\n')
			self.conf = [x.rstrip() for x in self.conf]
			
			t = Thread(target=self.run_thread_command, args=(ip,user,psw, enable))
			t.start()


	def copy_to_clipboard(self):
		self.device = self.conf_cb.get()
		self.date = self.date_cb.get()
						
		if self.device and self.date:
			self.select_dev = "SELECT id FROM list WHERE name='{}'".format(self.device)
			self.dev_id = self.db.select(self.select_dev)
			self.select_conf = "SELECT id,date,config FROM config WHERE dev_id='{}' and date='{}'".format(self.dev_id[0][0], self.date)
			self.select_conf = self.db.select(self.select_conf)
			self.conf = []
			for raw in self.select_conf:
				self.conf.append(raw[2])
			pyperclip.copy(str(self.conf[0]))
			self.write_log('BACKUP COPYED TO CLIPBOARD', 'INFO')
		else:
			self.write_log('SELECT DEVICE AND DATE', 'WARNING')
	

	def initUI(self, master): #FRAMES# TREE MENU
		treeFrame = Frame(self.master, width = 300, height = 500)
		treeFrame.pack(fill = 'y', side = 'left')

		# LOGO
		logoFrame = Frame(self.master, width = 100, height = 30, background = "#475577")
		logoFrame.pack(fill = 'x', pady = 5, padx = 5)
		l1 = Label(logoFrame, text="Cisco Config Manager", background='#475577', fg="#ffffff").pack(pady = 5, padx=5, side='left')

		date = str(datetime.datetime.now().strftime("%d/%m/%Y"))
		l1 = Label(logoFrame, text="{}".format(date), background='#475577', fg="#ffffff").pack(pady = 5, padx=5,  side='right')

		# CONSOLE LOG
		consoleLog = Frame(self.master)
		self.log = Text(consoleLog, width = 500, bg = "#2B3C50", fg = "#FFFFFF")
		self.log.pack(fill = 'both', expand = 'yes', padx = 5, pady = 5)
		self.scroll_bar = Scrollbar(self.log)
		self.log.config(yscrollcommand = self.scroll_bar.set)
		self.scroll_bar.config(command = self.log.yview)
		self.scroll_bar.pack(side = 'right', fill = 'y')

		# MENU
		master.option_add('*tearOff', False)
		menubar = Menu(master)
		master.config(menu = menubar)
		file = Menu(menubar)
		edit = Menu(menubar)
		help_ = Menu(menubar)
		menubar.add_cascade(menu = file, label = 'File')
		menubar.add_cascade(menu = edit, label = 'Edit')
		menubar.add_cascade(menu = help_, label = 'Help')
		# FILE MENU
		add_cat = file.add_command(label = "New Category", underline = 2, command = self.new_category)
		add_dev = file.add_command(label = "New Device", underline = 2, command = self.new_device)
		file.add_separator()
		add_tftp = file.add_command(label = "New TFTP", underline = 2, command = self.new_tftp)
		add_command = file.add_command(label = "New Command", underline = 2, command = self.new_command)
		file.add_separator()
		add_exit = file.add_command(label = "Exit", command = self.close_program)

		# EDIT MENU
		edit_cat = edit.add_command(label='Category', command = self.edit_category)
		edit_dev = edit.add_command(label='Device', command = self.edit_device)
		edit.add_separator()
		edit_tftp = edit.add_command(label='Command')
		edit_tftp = edit.add_command(label='TFTP')

		# HELP MENU
		help_.add_command(label="About as", command = self.about_as)

		# TREE INIT
		self.treeview = ttk.Treeview(treeFrame)
		self.treeview.pack(padx = 5, pady = 5, side = LEFT, fill = Y, expand=True)
		self.treeview.config(columns = ('#0'))
		self.treeview.config(columns = ('#1'))
		self.treeview.column('#0', width = 130, anchor = 'center')
		self.treeview.column('#1', width = 130, anchor = 'w')
		self.treeview.heading('#0', text = 'Devices')
		self.treeview.heading('#1', text = 'Info')
		# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
		# self.select_cat = "SELECT id, name FROM list WHERE cat is null"
		# self.cat = self.db.select(self.select_cat)
		# 
		# for row in self.cat:
		# 	self.treeview.insert('', '{}'.format(row[0]), '{}'.format(row[0]), text = '{}'.format(row[1]), tags = ('{}'.format(row[0]),))# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
		# 
		# self.select_dev = "SELECT id, cat, name, ip FROM list WHERE cat not null"
		# self.dev = self.db.select(self.select_dev)
		# 
		# for row in self.dev:
		# 	self.treeview.insert('{}'.format(row[1]), '{}'.format(row[0]), '{}'.format(row[0]), text = '{}'.format(row[2]))
		# 	self.treeview.set(row[0], '#1', row[3])
		# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

		self.treeview.bind("<Button-1>", self.selectNode)

		# NOTEBOOK
		self.notebook = ttk.Notebook(self.master)
		self.bf = ttk.Frame(self.notebook)
		self.cf = ttk.Frame(self.notebook)
		self.sf = ttk.Frame(self.notebook)
		self.cronf = ttk.Frame(self.notebook)

		self.notebook.add(self.bf, text = "Backup")
		self.notebook.pack(fill = 'both', padx = 5, pady = 5)
		self.notebook.add(self.cf, text = "Config Manager")
		self.notebook.pack(fill = 'both', padx = 5, pady = 5)
		self.notebook.add(self.sf, text = "Statistic")
		self.notebook.pack(fill = 'both', padx = 5, pady = 5)
		self.notebook.add(self.cronf, text = "Cron Jobs")
		self.notebook.pack(fill = 'both', padx = 5, pady = 5)

		# LABEL FRAME
		self.labelframe = ttk.Frame(self.bf)
		self.labelframe.pack(side = "left", padx = 40, pady = 40, anchor = "n")
		self.l1 = Label(self.labelframe, text = "ID:").pack(anchor = "e")
		self.l1 = Label(self.labelframe, text = "DEVICE:").pack(pady = 5, anchor = "e")
		self.l1 = Label(self.labelframe, text = "IP:").pack(pady = 5, anchor = "e")
		self.l1 = Label(self.labelframe, text = "CATEGORY:").pack(pady = 5, anchor = "e")
		self.l1 = Label(self.labelframe, text = "USER:").pack(pady = 5, anchor = "e")
		self.l1 = Label(self.labelframe, text = "SSH PASS:").pack(pady = 5, anchor = "e")
		self.l1 = Label(self.labelframe, text = "ENABLE PASS:").pack(pady = 5, anchor = "e")

		# VALUE FRAME
		self.valframe = ttk.Frame(self.bf)
		self.valframe.pack(side = "left", padx = 5, pady = 40, anchor = "n")
		self.v_id = Label(self.valframe, text = "-----")
		self.v_id.pack(anchor = "w")
		self.v_dname = Label(self.valframe, text = "-----")
		self.v_dname.pack(pady = 5, anchor = "w")
		self.v_ip = Label(self.valframe, text = "-----")
		self.v_ip.pack(pady = 5, anchor = "w")
		self.v_cat = Label(self.valframe, text = "-----")
		self.v_cat.pack(pady = 5, anchor = "w")
		self.v_uname = Label(self.valframe, text = "-----")
		self.v_uname.pack(pady = 5, anchor = "w")
		self.v_pass = Label(self.valframe, text = "-----")
		self.v_pass.pack(pady = 5, anchor = "w")# canvas.pack(side = 'left')
		self.en_pass = Label(self.valframe, text = "-----")
		self.en_pass.pack(pady = 5, anchor = "w")# canvas.pack(side = 'left')
		
		

		# BACKUP
		#--------------------------------------------------------------------------------
		self.bakframe = ttk.Frame(self.bf)
		self.l1 = Label(self.bakframe, text = "OPERATION").pack(anchor = "w")
		self.bakframe.pack(side = "right", padx = 40, pady = 40, anchor = "n")
		
		self.makeBackup = Button(self.bakframe, width = "16", text = "Make Backup", bg='#5cb85c', command = self.makeConfigBackup)
		self.makeBackup.pack(anchor = 'w', pady = 5)
		self.var = BooleanVar()
		self.tftp = Checkbutton(self.bakframe, variable=self.var, text = "Upload to TFTP",onvalue = 1, offvalue = 0, command=self.check_tftp)
		self.tftp.pack(anchor='w', pady=5)
				
		self.cb_tftp = ttk.Combobox(self.bakframe)
		self.cb_tftp.config(width = "16")
		
		self.showframe = ttk.Frame(self.bf)
		self.showframe.pack(side = "right", padx = 5, pady = 40, anchor = "n")
		self.l1 = Label(self.showframe, text = "COMMAND").pack(anchor = "w", padx=0)
		self.cb_command = ttk.Combobox(self.showframe)
		# self.cb_command.config(width = "100")

		self.multi_command = Text(self.showframe, height = 8, width = 70)
		self.multi_command.pack()


		# self.cb_command['values'] = []
		# self.cb_command.pack(pady = 5, padx=10)

		self.makeBackup = Button(self.showframe, width = "16", text = "Run", command = self.run_command)
		self.makeBackup.pack(side = "right", pady=10, padx=0)
		#-------------------------------------------------------------------------------

		# CONFIG MANAGER TAB
		self.conf_lbl_frame = ttk.Frame(self.cf)
		self.conf_lbl_frame.pack(side = "left", padx = 40, pady = 40, anchor = "n")
		self.l1 = Label(self.conf_lbl_frame, text = "DEVICE:").pack(anchor = "e")
		self.l1 = Label(self.conf_lbl_frame, text = "DATE:").pack(pady = 5, anchor = "e")

		self.conf_widget_frame = ttk.Frame(self.cf)
		self.conf_widget_frame.pack(side = "left", padx = 40, pady = 40, anchor = "n")

		self.conf_cb = ttk.Combobox(self.conf_widget_frame)
		self.conf_cb.config(width = "18")
		self.conf_cb.bind("<<ComboboxSelected>>", self.newselection)
		self.conf_cb.pack()

		self.date_cb = ttk.Combobox(self.conf_widget_frame)
		self.date_cb.config(width = "18")
		self.date_cb.pack(pady = 5, anchor = "w")

		self.showBackup = Button(self.conf_widget_frame, width = "16", text = "Show", command = self.showBackup)
		self.showBackup.pack(anchor = 'w', pady = 5)
		
		self.copyBackup = Button(self.conf_widget_frame, width = "16", text = "Copy", command=self.copy_to_clipboard)
		self.copyBackup.pack(anchor = 'w', pady = 5)

		self.deleteBackup = Button(self.conf_widget_frame, width = "16", text = "Delete", command = self.deleteBackup, fg='red')
		self.deleteBackup.pack(anchor = 'w', pady = 5)
	
		# STATISTIC TAB
		self.stat_lbl_frame = ttk.Frame(self.sf)
		self.stat_lbl_frame.pack(side = "left", padx = 40, pady = 40, anchor = "n")
		self.l1 = Label(self.stat_lbl_frame, text = "DEVICE:").pack(anchor = "e")
		self.l1 = Label(self.stat_lbl_frame, text = "BACKUPS:").pack(pady = 5, anchor = "e")
		self.l1 = Label(self.stat_lbl_frame, text = "WITHOUT BACKUP:").pack(pady = 5, anchor = "e")
		self.l1 = Label(self.stat_lbl_frame, text = "LAST OLD:").pack(pady = 5, anchor = "e")
		self.l1 = Label(self.stat_lbl_frame, text = "LAST NEW:").pack(pady = 5, anchor = "e")


		self.stat_val_frame = ttk.Frame(self.sf)
		self.stat_val_frame.pack(side = "left", padx = 0, pady = 35, anchor = "n")

		self.num_of_dev = Label(self.stat_val_frame, pady = 5, text = "", fg='red')
		self.num_of_dev.pack(anchor='w')

		self.num_of_back = Label(self.stat_val_frame, pady = 5, text = "", fg='red')
		self.num_of_back.pack(anchor='w')

		self.without_backup = Label(self.stat_val_frame, pady=5, text = "", fg='red')
		self.without_backup.pack(anchor='w')

		self.new_lbl = Label(self.stat_val_frame, pady=5, text = "", fg='red')
		self.new_lbl.pack(anchor='w')

		self.old_lbl = Label(self.stat_val_frame, pady=5, text = "", fg='red')
		self.old_lbl.pack(anchor='w')


		#---------------------
		self.bakframe1 = ttk.Frame(self.sf)
		self.l1 = Label(self.bakframe1, text = "OPERATION").pack(anchor = "w")

		self.bakframe1.pack(side = "right", padx = 40, pady = 40, anchor = "n")
		self.showDetail = Button(self.bakframe1, width = "16", bg='#5cb85c', text = "DETEILS", command = self.showDetails)
		self.showDetail.pack(anchor = 'w', pady = 10)

		# ---------------------------------------------------------------------------------------------------------------
		# RESTORE COPY
		self.restore_copy = ttk.Frame(self.cf)
		self.l1 = Label(self.restore_copy, text = "OPERATION").pack(anchor = "w")
		self.restore_copy.pack(side = "right", padx = 40, pady = 40, anchor = "n")
		self.restoreBackup = Button(self.restore_copy, width = "16", text = "Restore Backup", bg='#d9534f', command=self.restore_backup)
		self.restoreBackup.pack(anchor = 'w', pady = 5)
		

		self.update_stats()
		# left1 = Label(self.bf, text = "Inside the LabelFrame")# left1.pack()# left2 = Label(labelframe, text = "Inside the LabelFrame")# left2.pack()# left3 = Label(labelframe, text = "Inside the LabelFrame")# left3.pack()
		# INPUTS# name = ttk.Entry(labelframe, width = "200")# name.pack()
		consoleLog.pack(fill = 'both', expand = 'yes', pady = 5)

def main():
	root = Tk()
	app = MainApp(root)
	root.mainloop()

if __name__ == '__main__':
	main()
