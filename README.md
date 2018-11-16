<img src="es_gui/resources/logo/Quest_Logo_RGB.png" alt="QuESt logo" width=300px margin="auto" />

# QuESt: Optimizing Energy Storage
Current release version: 1.0

## Table of contents
- [Introduction](#intro)
- [Getting started](#getting-started)
- [Frequently Asked Questions](#faq)
    - [QuESt Data Manager](#faq-data-manager)
    - [QuESt Valuation](#faq-valuation)

### What is it?
<a id="intro"></a>
QuESt is an open source, Python-based application suite for energy storage simulation and analysis developed by the Energy Storage Systems program at Sandia National Laboratories, Albuquerque, NM. It is designed to give users access to models and analysis for energy storage used and developed by Sandia National Laboratories. It's designed to be transparent and easy to use without having to have knowledge of the mathematics behind the models or knowing how to develop code in Python. At the same time, because it is open source, users may modify it to suit their needs should they desire to. We will continue developing QuESt and its applications to enable more functionality.

#### QuESt Data Manager
An application for acquiring data from regional transmission operator (RTO), independent system operator (ISO), or other electricity market operating entities. Data selected for download is acquired in a format and structure compatible with other QuESt applications.

*Note: An internet connection is required to download data.*

*Note: Certain data sources require registering an account to obtain access.*

<img src="es_gui/resources/gifs/01_datamanager.gif" alt="Download ISO/RTO data" width=600px margin="auto" />

#### QuESt Valuation

An application for energy storage valuation, an analysis where the maximum revenue of a hypothetical energy storage device is estimated using historical market data. This is done by determining the sequence of state of charge management actions that optimize revenue generation, assuming perfect foresight of the historical data.

<img src="es_gui/resources/gifs/02_wizard.gif" alt="Wizard setup" width=600px margin="auto" />

<img src="es_gui/resources/gifs/03_reportcharts.gif" alt="Wizard report charts" width=600px margin="auto" />

<img src="es_gui/resources/gifs/04_batch.gif" alt="Batch runs" width=600px margin="auto" />

### Who should use it?
The software is designed to be used by anyone with an interest in performing analysis of energy storage or its applications without having to create their own models or write their own code. It’s designed to be easy to use out of the box but also modifiable by the savvy user if they so choose. The software is intended to be used as a platform for running simulations, obtaining results, and using the information to inform planning decisions. 

## Getting started
<a id="getting-started"></a>

### Requirements
* Python 3.6+
* Kivy 1.10.1+ and its dependencies
* Solver compatible with Pyomo

### Installation
You will want to obtain the codebase for QuESt. You can do that by downloading a release version in a compressed archive from the "releases" tab on the GitHub repository page. Alternatively, you can clone this repository or download a compressed archive of it by clicking the "Clone or download" button on this page. We recommend keeping the QuESt files in a location where you have read/write permission. Once you have the codebase, follow the appropriate set of instructions for your operating system.

#### Windows
1. Install Python, preferably via scientific distribution such as [Anaconda](https://www.anaconda.com/download/). Use the 64 or 32-Bit Graphical installer as appropriate.
2. Install Kivy. Check [here](https://kivy.org/docs/installation/installation-windows.html) for the latest instructions. 
3. Navigate to the root directory of the codebase. Then run the setup
 ``python setup.py develop`` This will check dependencies for QuESt and install them as needed.
4. Install a solver for Pyomo to use. See other sections for instructions on this.
  
#### OSX
1. Install Python, preferably via scientific distribution such as [Anaconda](https://www.anaconda.com/download/). Use the 64 or 32-Bit Graphical installer as appropriate.
2. Install Kivy. Check [here](https://kivy.org/doc/stable/installation/installation-osx.html#using-homebrew-with-pip) for the latest instructions. (Refer to "Using Homebrew with pip" OR "Using MacPorts with pip")
3. Navigate to the root directory of the codebase. Then run the setup
 ``python setup.py develop`` This will check dependencies for QuESt and install them as needed.
4. Install a solver for Pyomo to use. See other sections for instructions on this.

#### Solvers for Pyomo
At least one solver compatible with Pyomo is required to solve optimization problems. For QuESt Valuation, a solver capable of solving linear programs is required. Here are a few of the many choices for solvers:

##### Installing GLPK (for Windows)
1. Download and extract the executables for Windows linked [here](http://winglpk.sourceforge.net/).
2. The .dll and glpsol.exe files are in the `w32` and `w64` subdirectories for 32-Bit and 64-Bit Windows, respectively. These files need to be in the search path for Windows. The easiest way to do this is to move those files to the `C:\windows\system32` directory.
3. Try running the command ``glpsol`` in the command prompt (Windows) or terminal (OSX). If you receive a message other than something like "command not found," it means the solver is successfully installed.

##### Installing GLPK (for OSX)
You will need to either build GLPK from source or install it using the [homebrew](https://brew.sh/) package manager. This [blog post](http://arnab-deka.com/posts/2010/02/installing-glpk-on-a-mac/) may be useful.

##### Installing IPOPT (for Windows)
1. Download and extract the pre-compiled binaries linked [here](https://www.coin-or.org/download/binary/Ipopt/). Select the latest version appropriate for your system and OS.
2. Add the directory with the `ipopt.exe` executable file to your path system environment variable. For example, if you extracted the archive to `C:\ipopt`, then `C:\ipopt\bin` must be added to your path.
3. Try running the command ``ipopt`` in the command prompt (Windows) or terminal (OSX). If you receive a message other than something like "command not found," it means the solver is successfully installed.
Regardless of which solver(s) you install, remember to specify which of them to use in Settings within QuESt.

### Running QuESt
From the Anaconda Prompt or Command Prompt, run:
```
python main.py
```

Alternatively, run ```main.py``` in a Python IDE of your choice.

**NOTE: The current working directory must be where ``main.py`` is located (the root of the repository).**

## Frequently Asked Questions
<a id="faq"></a>

### General

> The appearance of GUI elements in QuESt do not appear correct/The window does not display properly/The window is too big for my display/I cannot click or interact with the UI properly.

QuESt is designed to be displayed at minimum resolution of 1600x900.

There are a number of possible reasons for display issues, but the most likely reason is due to operating system scaling. For example, Windows 10 has a feature that scales the appearance of display elements, usually to assist with higher resolution displays. For example, if scaling is set to 125% in Windows, this will scale the QuESt window to be too big for the display (on a 1920x1080 resolution display).

Scaling may also have the effect of confusing Kivy of where a UI element is and where it is displayed; e.g., you may be clicking where a button appears to be, but the scaling causes Kivy to not "detect" that you are pressing the button.

So far, this issue has been observed on a variety of laptops of both Windows and OSX varieties. Our suggestion is to disable OS level scaling or to connect to an external display and try to launch QuESt on it.

> How do I update QuESt?

If you cloned the GitHub repository, you can execute a `git pull` command in the terminal/cmd while in the root of the QuESt directory. If you haven't modified any source code, there should be no conflicts.

If you downloaded an archive of the master branch or a release version archive, you can download the latest release version as if it were a fresh install. You can drag and drop your old data directory so that you do not hae to download all the data again if you would like.

### QuESt Data Manager
<a id="faq-data-manager"></a>

> I am connecting to the internet through a proxy, such as on a corporate network. How should I configure my connection settings?

Typically, devices have their connection settings configured for the network they will primarily residing on. For example, proxy settings may already be configured in system environment variables and whatnot. We recommend that your proxy settings be configured at the operating system level and that you do not additionally specify using a proxy in QuESt settings. In our experience, additionally specifying the same proxy settings in QuESt "does no harm," but your mileage may vary.

> I am trying to download data and am receiving many messages about connection errors, timeouts, etc. What should I do?

We found these issues to be very network dependent and hard to diagnose or mitigate against. The best practice would be to limit the amount of data that you request at a time. Additionally, QuESt Data Manager is configured to skip data that is already downloaded so you can just issue the same request to patch up any data that may have failed to download.

> I downloaded data but other QuESt applications are telling me that I haven't downloaded any.

QuESt expects data to be in a certain directory structure as structured by QuESt Data Manager. Changing directory names, filenames, modifying files, etc. will produce unexpected results. We recommend not performing any modifications to downloaded data files except for perhaps deleting them.

> How do I obtain PJM Data Miner 2 API access?

Refer to the instructions in QuESt Data Manager or see the API guide [here](http://www.pjm.com/markets-and-operations/etools/data-miner-2.aspx).

> How do I obtain an ISO-NE ISO Express account?

Refer to the instructions in QuESt Data Manager or simply register an account at ISO-NE's [website](https://www.iso-ne.com/). Make sure to sign up for Data Feeds access.

> Why can't I download [data for which no option in QuESt Data Manager exists]?

RTO/ISO/etc. provide a lot more varieties of data than what is shown in QuESt Data Manager. We are focused on acquiring data necessary for other QuESt applications to function. Additionally, acquiring data is not the fastest process. In order to improve the user experience, we decided to limit the amount of data that one can request at a time. For that reason, we have limited the number of pricing nodes for which data can be requested directly. (For example, PJM has over 11,000 pricing nodes.) We can consider lifting some of these limitations if requested.

> I downloaded data for a previous month before the month was over. Now I can't complete the month's data set because it skips over it. What should I do?

QuESt Data Manager skips downloads if a file with the anticipated filename already exists. If you delete the specific file(s) in the `/data/` directory, it should try to download the data.

> Why does it take so long to download data?

* Some download requests are requesting large amounts of data.
* Some ISO/RTO websites or APIs have connection issues. We incorporate mechanisms for automatically retrying a limited amount of times.
* CAISO's API limits API requests to every five seconds.

### QuESt Valuation
<a id="faq-valuation"></a>

> I am getting import errors when trying to run QuESt.

The current working directory must be where ``main.py`` is located.

> Why are only [x] options available for market areas/historical data/revenue streams/etc.?

These options are based on the data that you have downloaded through QuESt Data Manager. Download more varieties if you wish to use them!

> I'm getting solver errors/QuESt is crashing when building optimization models. How can I fix that?

Our experience indicates that most crashes are due to data issues. For example, data for a month is missing unexpectedly, disallowing the model building process from completing. We make every effort to limit these incidents from happening, but it is difficult to perfectly predict the data that we need to design around. We will try to handle these exceptions as best we can as we learn more about the common situations.

> An electricity market area I want to do analysis on isn't available. When will it be available?

The development team is working on modeling and doing analysis for the remaining market areas. When we have vetted the results and viability of data acquisition and processing, we will work on implementing them into QuESt. Please look forward to it!

#### Wizard

> I selected [x] year for my historical dataset and only [y] months had results after the optimization. Why is that?

Due to (rolling) data availability, data for certain periods may be absent. For example, ERCOT's 2010 data only starts at December or data sets for the current year will obviously be incomplete. There's also the possibility that the data failed to download.

> Why can I only adjust [x] parameters for my energy storage device?

To streamline the user experience in the Wizard, we decided to reduce the range of options available. Please try the "Single Run" and "Batch Runs" interfaces for fuller flexibility.

> The pro forma report's appearance doesn't seem quite right/there is a bunch of cryptic commands underneath the "Optimization formulation" section.

For best results when viewing the report, you must be connected to the internet and enable JavaScript. We use content delivery services for resources such as fonts (Google Fonts) and use JavaScript to render the equations under the "Optimization formulation" section (MathJax).

#### Batch Runs

> What is a parameter sweep?

A parameter sweep will adjust the specified parameter from the min value to the max value in the given number of steps. It will do this for each month of data selected on the "data" interface. A simulation will be performed for the all of the combinations. This is a useful way for performing sensitivity analysis.
