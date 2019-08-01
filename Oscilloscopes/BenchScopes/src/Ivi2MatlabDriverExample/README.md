# Convert IVI to MATLAB Driver and Read Waveform (TBS1kB-EDU)
Original Attribution: Will D

The purpose of this example is to demonstrate how to get a MATLAB driver for an instrument not listed in the MathWorks repository [here](https://www.mathworks.com/programs/products/instrument/instrument-drivers-search.html) but with a driver available via the IVI Foundation repository [here](http://www.ivifoundation.org/registered_drivers/driver_registry.aspx), such as [this driver](http://www.ivifoundation.org/registered_drivers/driver_registry.aspx) which I am using with a TBS1202B-EDU.

This example will lead you through installing the NI driver, recognizing where that installation is and confirming its existence, then using the ".c" driver to make a MATLAB ".mdd" driver.

First, download and install the NI Driver. [This](http://sine.ni.com/apps/utf8/niid_web_display.download_page?p_id_guid=E3B19B3E94FE659CE034080020E74861) is the relevant driver for my TBS1202B-EDU. You do not need to install the LabVIEW specific components, but you do need to install the LabWindows component, since that will create the necessary ".c" driver file.

----

After installation, check that the appropriate driver files are in C:\Program Files (x86)\IVI\Drivers\. Mine are in C:\Program Files (x86)\IVI\Drivers\tktds1k2k and the directory looks like the attached image.
![example directory structure](https://forum.tek.com/download/file.php?id=24621)

----

Once you have verified that, you can start up Matlab. [This link](https://www.mathworks.com/help/instrument/makemid.html) describes how to convert the ".c" driver to a MATLAB ".mdd" driver via the "makemid" function. When you have created the MATLAB driver, you can begin making use of it in the Instrument Toolbox or MATLAB Command Line. The attached .m file is an example of creating the driver and using the driver functions to plot a waveform in Command Line.

[Sample \*.m file](./TBS1kB_IVI_driver_convert_and_read.m)


