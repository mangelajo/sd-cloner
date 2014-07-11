#!/usr/bin/env python

#
# NEXCOPY microSD or usb flash disk copier Script
#
#
#  WARNING: please, set ignored_devices with every internal disk you don't want to write
#           to, or it may get erased at any time
#

ignored_devices=['sda']
image = "imagen_rm8_16gb_64MB_rel1.02.img"
#image ="imagen_rm8_4gb_rel1.01.img"

print "using image:" +image
import shlex, subprocess
import time
import wx
import wx.grid as gridlib

# associates device to slot number

device_slot={"sdd":1, "sde":2, "sdb":3, "sdc":4, "sdh":5, "sdi":6,
             "sdf":7, "sdg":8, "sdl":9, "sdm":10,"sdj":11,"sdk":12,
             "sdp":13,"sdq":14,"sdn":15,"sdo":16,"sdt":17,"sdu":18,
             "sdr":19,"sds":20};

# associate slot to grid cell

slot_grid={1:(0,0), 2:(0,1),3:(0,2),4:(0,3),
           5:(1,0), 6:(1,1),7:(1,2),8:(1,3),
           9:(2,0), 10:(2,1),11:(2,2),12:(2,3),
           13:(3,0),14:(3,1),15:(3,2),16:(3,3),
           17:(4,0),18:(4,1),19:(4,2),20:(4,3)}

# our UI to be available from anywhere on the code
ui=None

# running Popen processes dictionary ("sdX" -> Popen process)
running_procs = {}

# command line for image copying
dd_copier = "/bin/dd if="+image+" of=%s bs=1M"

def dmesg():
    """ The dmesg function launches dmesg, gets the contents and return, clearing kernel buffer """
    dmesg_getter="/bin/dmesg -c"
    p = subprocess.Popen(shlex.split(dmesg_getter),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stde,stdo) = p.communicate()
    p.wait()
    return stde


def create_copier(devname):
    """ creates an image copier for a certain device """
    if devname in ignored_devices: return
    cmdline = dd_copier % ("/dev/"+devname)
    p = subprocess.Popen(shlex.split(cmdline),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print cmdline
    if running_procs.has_key(devname):
        print "WARNING, "+devname+" already in list, ??"
    running_procs[devname]=p
    p.poll()

def kill_copier(devname):
    """finishes a copier for a certain device """
    if running_procs.has_key(devname):
        (stde,stdo) = running_procs[devname].communicate()
        print stde,stdo
        running_procs.pop(devname)
        print "FINISHED: ",device_slot[devname]
        ui.finished(device_slot[devname])


def find_inserted(lines):
    """scans dmesg information for new device insertion"""
    for line in lines:
        if line.find("logical blocks")>=0:
            pos = line.find(": [")
            dev = line[pos+3:pos+6]
            print "<",dev,device_slot[dev]
            ui.inserted(device_slot[dev])
            create_copier(dev)


def find_removed(lines):
    """scans dmesg information for removed devices"""
    for line in lines:
        pos = line.find(": detected capacity change from")
        if pos>=0:
            dev = line[pos-3:pos]
            print ">",dev,device_slot[dev]
            kill_copier(dev)
            ui.removed(device_slot[dev])

def find_done():
    """ scans running processes information for finished copies """
    for k in running_procs.keys():
        p = running_procs[k]
        if p.poll()!=None:
            kill_copier(k)

def find_errors(lines):
    """ scans dmesg information for failed copies """
    for line in lines:
        pos = line.find("] Device not ready")
        if pos>=0:
            dev = line[pos-3:pos]
            print "!!!!!!!!!!!!! ERROR ON : "+dev+"  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! SLOT",device_slot[dev]
            ui.error(device_slot[dev])
            return



def update():
    """ must be called periodically to check dmesg output and handle new inserted/removed/failed devices"""
    dmesg_d = dmesg()
    if len(dmesg_d)>0: print dmesg_d
    lines = dmesg_d.split('\n')
    find_inserted(lines)
    find_removed(lines)
    find_errors(lines)
    find_done()


##
## This is our Form
##

class ToasterForm(wx.Frame):

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, parent=None, title="Tostadora")
        panel = wx.Panel(self)

        myGrid = gridlib.Grid(panel)
        myGrid.CreateGrid(5, 4)
        self.grid=myGrid

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(myGrid, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(1000)


    def on_timer(self,event):
        update()

    def inserted(self,slot):
        y,x = slot_grid[slot]
        self.grid.SetCellValue(y,x,str(slot))
        self.grid.SetCellBackgroundColour(y,x,wx.BLUE)
        self.grid.SetCellTextColour(y,x,wx.WHITE)
        self.grid.SetCellAlignment(y, x, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.Update()
        self.grid.Update()
        print "inserted()"

    def finished(self,slot):
        y,x = slot_grid[slot]
        self.grid.SetCellValue(y,x,str(slot))
        self.grid.SetCellBackgroundColour(y,x,wx.GREEN)
        self.grid.SetCellTextColour(y,x,wx.WHITE)
        self.grid.SetCellAlignment(y, x, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.Update()
        self.grid.Update()
        print "inserted()"


    def removed(self,slot):
        y,x = slot_grid[slot]
        self.grid.SetCellValue(y,x,"--")
        self.grid.SetCellBackgroundColour(y,x,wx.WHITE)
        self.grid.SetCellTextColour(y,x,wx.BLACK)
        self.Update()
        self.grid.Update()
        print "removed()"



    def error(self,slot):
        y,x = slot_grid[slot]
        self.grid.SetCellValue(y,x,str(slot))
        self.grid.SetCellBackgroundColour(y,x,wx.RED)
        self.grid.SetCellTextColour(y,x,wx.WHITE)
        self.Update()
        self.grid.Update()
        wx.MessageBox("Ha habido un error con la %d"%slot)

if __name__ == "__main__":
    dmesg() # dmesg is called to clear kernel output buffer and avoid internal disks to be detected
            # or erased ':)
    print "== wxCLONER STARTED =="
    app = wx.PySimpleApp()
    ui=ToasterForm()
    frame = ui.Show()
    app.MainLoop()
