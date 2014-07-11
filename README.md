sd cloner
=========

  Is a tool to take an SD image, and a bunch of sd card
readers/writers, those are mapped in a grid, and different
colors are used to show the status of the process with
a certain sd card writer.

  When you insert a card, it starts writing to the card,
when it finishes it goes green and you can switch that
card for a new one.

  You may want to disable your operating system automounter.

  At this moment everything is pretty hard coded, so, 
if you plan to make use of it, read the code carefully, and
change anything you need. 

Notes
-----

   I'm not very proud of this code, as I wrote it long
ago, but, I'm uploading it to share it, and for archival
purposes.

   SD card insertion detection is done via dmesg interface
that means that different kernel versions could affect
the operation (for example if the kernel messages change).
There are better ways to do this.

   Writing to the SD cards is done using the operating
system DD tool, one process per card.

   
  This tool must be executed with root privileges, otherwise
it would blindly fail to detect new cards.
