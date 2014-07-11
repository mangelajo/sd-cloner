#!/usr/bin/env python
import shlex, subprocess
import time

device_slot={"sdd":1, "sde":2, "sdb":3, "sdc":4, "sdh":5, "sdi":6,
             "sdf":7, "sdg":8, "sdl":9, "sdm":10,"sdj":11,"sdk":12,
             "sdp":13,"sdq":14,"sdn":15,"sdo":16,"sdt":17,"sdu":18,
             "sdr":19,"sds":20};

dmesg_getter="/bin/dmesg -c"

ignored_devices=['sda']

running_procs = {}

image = "imagen_rm8_16gb_64MB_rel1.02.img"

dd_copier = "/bin/dd if="+image+" of=%s bs=1M"

def dmesg():
    p = subprocess.Popen(shlex.split(dmesg_getter),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stde,stdo) = p.communicate()
    p.wait()
    return stde


def create_copier(devname):
    if devname in ignored_devices: return
    cmdline = dd_copier % ("/dev/"+devname)
    p = subprocess.Popen(shlex.split(cmdline),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print cmdline
    if running_procs.has_key(devname):
        print "WARNING, "+devname+" already in list, ??"
    running_procs[devname]=p
    p.poll()

def kill_copier(devname):
    if running_procs.has_key(devname):
        (stde,stdo) = running_procs[devname].communicate()
        print stde,stdo
        running_procs.pop(devname)
        print "FINISHED: ",device_slot[devname]


def find_inserted(lines):
    for line in lines:
        if line.find("logical blocks")>=0:
            pos = line.find(": [")
            dev = line[pos+3:pos+6]
            print "<",dev,device_slot[dev]
            create_copier(dev)

def find_removed(lines):
    for line in lines:
        pos = line.find(": detected capacity change from")
        if pos>=0:
            dev = line[pos-3:pos]
            print ">",dev,device_slot[dev]
            kill_copier(dev)

def find_done():
    for k in running_procs.keys():
        p = running_procs[k]
        if p.poll()!=None:
            kill_copier(k)

def find_errors(lines):
    for line in lines:
        pos = line.find("] Device not ready")
        if pos>=0:
            dev = line[pos-3:pos]
            print "!!!!!!!!!!!!! ERROR ON : "+dev+"  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! SLOT",device_slot[dev]
            return
dmesg()

print "== CLONER STARTED =="

while True:
    dmesg_d = dmesg()
    if len(dmesg_d)>0: print dmesg_d
    lines = dmesg_d.split('\n')
    find_inserted(lines)
    find_removed(lines)
    find_errors(lines)
    find_done()
    time.sleep(1)
