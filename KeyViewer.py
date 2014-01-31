from Tkinter import *
from kinetic import Client
import tkMessageBox
#Using Threading with connect to decrease lockups.
import threading
import time
import sys

#The Kinetic drive should accept all keys up to 4 KiB in size.
#Kinetic sorts in lexographical order, so the last possible key is probably chr(255)*4*KiB
KiB = 2**10
KEY_MAX = chr(255)*4*KiB
KEY_MAX_SIZE = 4*KiB

#The Kinetic drive should also accept all values up to 1 MiB in size.
MiB = 2**20
VALUE_MAX_SIZE = 1*MiB

class PutWindow(Toplevel):
	ButtonWidth = 20
	def __init__(self, parent):
		Toplevel.__init__(self, parent)
		self.title("Put...")
		self.parent = parent
		self.grab_set()
		self.focus_set()
		self.DriveClient = self.parent.DriveClient
		if not self.DriveClient and self.DriveClient.isConnected:
			sys.stderr.write("Shouldn't be here...client should be open!")
			self.destroy()
		self.parent = parent

		Label(self, text="Key:").grid(row=0, column=0, sticky=E)
		self.KeyVariable = StringVar(root)
		self.KeyEntry = Entry(self, textvariable=self.KeyVariable)
		self.KeyEntry.grid(row=1, column=0, columnspan=2, sticky=E+W)

		Label(self, text="Value:").grid(row=2, column=0, sticky=E)
		self.ValueText = ScrollText(self)
		self.ValueText.grid(row=3, column=0, columnspan=2, sticky=E+W)

		self.PutButton = Button(self, text="Put", command=self.Put, width=self.ButtonWidth)
		self.PutButton.grid(row=4,column=0)

		self.CancelButton = Button(self, text="Cancel", command=self.destroy, width=self.ButtonWidth)
		self.CancelButton.grid(row=4, column=1)

	def Put(self):
		#Wrapping key and value with str, since Tkinter likes returning stuff as unicde, whereas the client needs ASCII.
		key = str(self.KeyVariable.get())
		value = str(self.ValueText.GetText().get(1.0, END))
		if key and value:
			self.DriveClient.put(key, value)
			self.destroy()


class ListBoxScroll(Frame):
	def __init__(self, parent, entries={}):
		Frame.__init__(self, parent)
		self.parent = parent
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)
		
		self.vscrollbar = Scrollbar(self, orient=VERTICAL)
		self.vscrollbar.grid(row=0, column = 1, sticky=N+S)
		
		self.lbox = Listbox(self, yscrollcommand=self.vscrollbar.set)
		self.vscrollbar.config(command=self.lbox.yview)
		for item in entries:
			self.lbox.insert(END, item)
		self.lbox.grid(row=0, column=0, sticky=N+S+E+W)
	
	def GetListbox(self):
		return self.lbox

class ScrollText(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, parent)
		self.parent = parent
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)
		
		self.vscrollbar = Scrollbar(self, orient=VERTICAL)
		self.vscrollbar.grid(row=0, column = 1, sticky=N+S)
		
		self.tbox = Text(self, *args, **kwargs)
		self.tbox.config(yscrollcommand=self.vscrollbar.set)
		self.vscrollbar.config(command=self.tbox.yview)
		self.tbox.grid(row=0, column=0, sticky=N+S+E+W)
	
	def GetText(self):
		return self.tbox
		
class KeyViewer(Frame):
	#The width of all the buttons in the GUI.
	ButtonWidth = 20
	ColumnsMax = 6
	def __init__(self, parent, r=0, c=0):
		#Frame Initialization steps
		Frame.__init__(self, parent)
		self.grid(row=r, column=c)
		self.parent=parent


		#Set Maximum drive connection time here...
		#Time to connect successfull or return something at all (in seconds).
		self.ConnectTime = 20.0
		
		#Class Variables Initialization
		self.DriveClient = None
		self.DriveAdminClient = None

		#Input Section
		#!!!!!!!!!!!!!!!!!!!!
		#ROW 0 GUI Objects. !
		#!!!!!!!!!!!!!!!!!!!!

		#Use a frame to allow the inputs to expand.
		self.RowZeroInputFrame = Frame(self)
		self.RowZeroInputFrame.grid(row=0, column=1, columnspan=self.ColumnsMax-1, sticky=E+W)

		self.ConnectButton = Button(self, text="Connect", command=self.Connect, width = self.ButtonWidth)
		self.ConnectButton.grid(row=0, column=0, sticky=E+W)
		self.DriveAddress = StringVar(root)
		self.DriveAddress.set('localhost')
		Label(self.RowZeroInputFrame, text="Drive Address:").pack(side=LEFT)
		self.IPEntry = Entry(self.RowZeroInputFrame, textvariable=self.DriveAddress)
		self.IPEntry.pack(side=LEFT, fill=X, expand=1)
		self.DrivePort = IntVar(root)
		self.DrivePort.set(8123)
		Label(self.RowZeroInputFrame, text="Drive Port:").pack(side=LEFT)
		self.PortEntry = Entry(self.RowZeroInputFrame, textvariable=self.DrivePort)
		self.PortEntry.pack(side=LEFT, fill=X, expand=1)

		#!!!!!!!!!!!!!!!!!!!!
		#ROW 1 GUI Objects. !
		#!!!!!!!!!!!!!!!!!!!!

		self.DisconnectButton = Button(self, text="Disconnect", command=self.Disconnect, width = self.ButtonWidth)
		self.DisconnectButton.grid(row=1, column=0, sticky = E+W)

		self.RefreshButton = Button(self, text="Refresh", command=self.Refresh, width=self.ButtonWidth)
		self.RefreshButton.grid(row=1, column=1, sticky=E+W)

		self.CopyKeyButton = Button(self, text="Copy Key", command=self.CopyKey, width=self.ButtonWidth)
		self.CopyKeyButton.grid(row=1, column=2, sticky =E+W)

		self.CopyValueButton = Button(self, text="Copy Value", command=self.CopyValue, width=self.ButtonWidth)
		self.CopyValueButton.grid(row=1, column=3, sticky = E+W)

		self.PutButton = Button(self, text="Put...", command=self.PutPair, width=self.ButtonWidth)
		self.PutButton.grid(row=1, column=4, sticky = E+W)

		self.StatusFrame = Frame(self)
		self.StatusFrame.grid(row=1, column=self.ColumnsMax-1, sticky=E+W)
		Label(self.StatusFrame, text="Status:").grid(row=0, column = 0)
		self.StatusVar = StringVar(root)
		self.StatusVar.set("Disconnected")
		self.StatusLabel = Label(self.StatusFrame, textvariable=self.StatusVar)
		self.StatusLabel.grid(row=0, column=1)
		
		#!!!!!!!!!!!!!!!!!!!!
		#ROW 2 GUI Objects. !
		#!!!!!!!!!!!!!!!!!!!!

		self.DeleteButton = Button(self, text="Delete", command=self.DeleteKey, width=self.ButtonWidth)
		self.DeleteButton.grid(row=2, column=0, sticky=E+W)

		self.GetLogsButton = Button(self, text="Get Logs...", width=self.ButtonWidth)
		self.GetLogsButton.grid(row=2, column=1, sticky=E+W)

		self.UpdateFirmwareButton = Button(self, text="Update Firmware", width=self.ButtonWidth)
		self.UpdateFirmwareButton.grid(row=2, column=2, sticky=E+W)

		self.EraseDriveButton = Button(self, text="Erase Drive", width=self.ButtonWidth)
		self.EraseDriveButton.grid(row=2, column = 3, sticky=E+W)

		self.AboutButton = Button(self, text="About...", command=self.About, width=self.ButtonWidth)
		self.AboutButton.grid(row=2, column =4, sticky=E+W)

		self.RepresentationButton = Button(self, text="Representation...", width=self.ButtonWidth)
		self.RepresentationButton.grid(row=2, column=self.ColumnsMax-1, sticky=E+W)

		#!!!!!!!!!!!!!!!!!!!!
		#ROW 3+4 GUI Objects. !
		#!!!!!!!!!!!!!!!!!!!!
		#Key list
		Label(self, text="Keys on Drive:").grid(row=3, column = 0)
		self.KeyList = ListBoxScroll(self)
		self.KeyList.GetListbox().config(width=80)
		self.KeyList.grid(row=4, column=0, columnspan=self.ColumnsMax, sticky=E+W)

		#!!!!!!!!!!!!!!!!!!!!
		#ROW 4+5 GUI Objects. !
		#!!!!!!!!!!!!!!!!!!!!
		#Values
		Label(self, text="Stored Value:").grid(row=5, column = 0)
		self.ValueTextBox = ScrollText(self, width=64)
		self.ValueTextBox.grid(row=6, column = 0, columnspan=self.ColumnsMax, sticky=E+W)
		#Bind the value box to display the key on selecting a key.
		self.KeyList.GetListbox().bind("<<ListboxSelect>>", self.GetAndDisplayValue)
	
	def __del__(self):
		self.Disconnect()
	
	def GetAndDisplayValue(self, *args):
		kbox = self.KeyList.GetListbox()
		key = kbox.get(kbox.curselection())
		if self.DriveClient:
			ReturnValue = self.DriveClient.get(key)
			self.ValueTextBox.GetText().delete("1.0", END)
			if ReturnValue:
				self.ValueTextBox.GetText().insert("1.0", ReturnValue.value)
			
		
	def Connect(self):
		if self.DriveAddress.get():
			#Load up the kinetic client.
			self.DriveClient = Client(self.DriveAddress.get(), self.DrivePort.get())
			#Attempt to connect.
			try:
				self.DriveClient.connect()
				#If this connects, isConnected will return a socket, otherwise it will return None
				if self.DriveClient.isConnected:
					self.StatusVar.set("Connected")
					self.Refresh()
				else:
					tkMessageBox.showerror(title="Unable to Reach Drive!", message="Drive is currently accessible.\nCheck settings and try again!")
					self.Disconnect()
			#Need to fix this exception cause to ONLY handle the socket error.
			except:
				tkMessageBox.showerror(title="Unable to Reach Drive!", message="Drive is currently accessible.\nCheck settings and try again!")
				self.Disconnect()
		
	def Disconnect(self):
		#If a Drive Client is open...
		if self.DriveClient:
			#Close the drive client,, return that the drive is disconnected, and set our Client pointer to None.
			self.DriveClient.close()
		self.KeyList.GetListbox().delete(0, END)
		self.ValueTextBox.GetText().delete("1.0", END)
		self.StatusVar.set("Disconnected")
		self.DriveClient = None



	def ValueBoxCallback(self, *args):
		pass
		

	def Refresh(self):
		if self.DriveClient and self.DriveClient.isConnected:
			self.KeyList.GetListbox()
			self.KeyList.GetListbox().delete(0, END)
			self.KeyList.GetListbox().insert(0, *self.DriveClient.getKeyRange('', KEY_MAX))
			self.ValueTextBox.GetText().delete("1.0", END)
		else:
			self.NotConnectedError()


	def CopyKey(self):
		if self.DriveClient and self.DriveClient.isConnected:
			CurrentKey = self.KeyList.GetListbox().get(self.KeyList.GetListbox().curselection())
			if CurrentKey:
				self.parent.clipboard_clear()
				self.parent.clipboard_append(CurrentKey)
		else:
			self.NotConnectedError()

	def CopyValue(self):
		"""
			Copy everything in the value box onto the clipboard.
		"""
		if self.DriveClient and self.DriveClient.isConnected:
			CurrentKey = self.KeyList.GetListbox().get(self.KeyList.GetListbox().curselection())
			if CurrentKey:
				self.parent.clipboard_clear()
				self.parent.clipboard_append(self.ValueTextBox.GetText().get(1.0, END))
		else:
			self.NotConnectedError()

	def DeleteKey(self):
		if self.DriveClient and self.DriveClient.isConnected:
			CurrentKey = self.KeyList.GetListbox().get(self.KeyList.GetListbox().curselection())
			if CurrentKey:
				self.DriveClient.delete(CurrentKey)
				self.Refresh()
		else:
			self.NotConnectedError()

	def PutPair(self):
		if self.DriveClient and self.DriveClient.isConnected:
			self.PWindow = PutWindow(self)
			self.wait_window(self.PWindow)
			self.Refresh()
		else:
			self.NotConnectedError()

	def About(self):
		aboutMessage = "Written by Robert P. Cope (2013)\nBuilt on Seagate Kinetic Technology\nProtected by LGPL, all rights reserved."
		tkMessageBox.showinfo("About...", aboutMessage)

	def NotConnectedError(self):
		errorMessage = "Not currently connected to any device!"
		tkMessageBox.showerror("Not Connected!", errorMessage)

if __name__ == "__main__":
	root = Tk()
	root.title("Kinetic Viewer")
	root.resizable(width=FALSE, height=FALSE)
	KeyViewer(root)
	root.mainloop()