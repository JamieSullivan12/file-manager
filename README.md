# IB File Manager Documentation

This document covers the installation and usage of the IB File Manager application for Windows and Mac OS.


# Items

An **item** refers to a 'past paper' data entry. The mechanics of adding/editing/removing items may be explored in detail under the **Main page** heading.

The purpose of an **item** is to allow the user to keep a record of documents pertaining to study (most commonly past papers). Each **item** is defined by a set of metadata (below), and has functionality for the user to attach PDF documents pertaining to that particular **item**. Attached PDF documents automatically copied into a system file heirarchy structure controlled by the program.

Attributes of an **item**:
 - Name (string)
 - Year (int)
 - Session (string)
 - Timezone (int)
 - Paper (int)
 - Subject (string)
 - Level (string)
 - Notes (string)
 - Printed (bool)
 - Completed (bool)
 - Partial (bool)
 - Mark (int)
 - Maximum (int)
 - Original (file)
 - Marksheme (file)
 - Scanned (file)
 - Completed date (date)
 - Grade boundaries 1 through 7 (int)

Inputted data will be used in the following situations:
 - Display in the heirarchy on the main page
 - Filter on the main page
 - Store PDF documents in the system file heirarchy

***WARNING:*** if a violation to the described data types above occurs, then any attempt to save changes to the item will fail, and the incorrect data entries wiped. 

### How an item interacts with the system file heirarchy

An **item** can have any number of PDF documents attached to it. Different types of documents include:

 - Original (the original PDF of the past paper / document)
 - Markscheme (the marscheme to the original PDF)
 - Scanned (the user may choose to scan their response to each paper, and store it in the program for organisational purposes)

As to avoid duplicate file directories and names, a set of subfolders based on item metadata will be created inside a folder, "Papers". Then, any PDF files attributed to an item will be stored in a file/folder heirarchy structure based on the following metadata fields:

 - session
 - year
 - timezone
 - paper
 - subject
 - level

Examples of the relative path of subfolders based on item metadata:
    
|Year|Subject  |Level|Paper |Relative path |
|--|--| -- | -- | -- |
|2022  |Maths |HL |1 |/Maths/HL/2022/{file name} |
|2022  |Maths  |HL |2 |/Maths/HL/2022/{file name} |
|2021  |Maths  |HL |1 |/Maths/HL/2021/{file name} |
|2020  |Maths  |HL |1 |/Maths/HL/2020/{file name} |
|2022  |Physics  |SL |1 |/Physics/SL/2022/{file name} |
|2021  |Physics  |SL |1 |/Physics/SL/2021/{file name} |
|2020  |Physics  |SL |1 |/Physics/SL/2020/{file name} |


The {file name} will be as follows (note that the {type} refers to Original/Markscheme/Scanned)

    {type}-{session}-{year}-{timezone}-{paper}-{subject}-{level}.pdf


This structure will mirror that of the metadata inserted by the user in the program, even if they are changed (i.e. attached PDFs will move location). Thus, it is recommended to store the app in cloud storage, such that all PDF files may be accessed on a mobile device.



# Main page
The following are a list of static and interactive elements available on the main page.

 - List tree view [element]
 - Load new [button]
 - Bulk load [button]
 - Delete selected items [button]
 - Plot selected items [button]
 - Filter selectors [text input]

 

### [Main page] List tree view

The **tree view** shows the user all items stored in the database (unfiltered by default). 

When no items in the database exist, the treeview will appear blank.

#### Available interactions

 - Single click: highlight an individual item in the treeview by clicking on it
 - Multi click: using CTRL or SHIFT to highlight multiple items in the treeview. This functionality is required when deleting or plotting items
 - Double click: to open an item (in order to edit/enter data). See **Edit an item** for more information



### [Main page] Load new

The **load new** button lets the user add a new item to the database. See **Adding an item** for more information.

### [Main page] Bulk load

The **bulk load** button lets the user add many new items to a database through an automatic directory scanning process. See **Bulk add** for more information.

### [Main page] Delete selected items

The **delete selected items** button will delete all items selected in the treeview heirarchy. View *available interactions* under the **[Main page] List tree view** heading for how to select items.

***NOTE:*** deleting all selected items will not only remove them from the database, but will also wipe any associated PDF files with those items from the hard drive. See ** How an item interacts with the system file heirarchy** for more information.

### [Main page] Plot selected items

The **plot selected items** button will open a browser window with a plot of all the selected items. The x-axis will always be the completion date of the selected items. The y-axis (depending on whether the *grades* or *percentages* button is pressed) will show the following data:

 - [grades]: the grade achieved on the item (based on grade boundaries)
 - [percentages]: the raw percentage achieved on the item

***NOTE:*** only completed items will be shown in the grade/percentage plot.


### [Main page] Filter selectors

Each item has a range of attributes. The meaning to these attributes can be found under the heading **What is an 'item'?***:

 - Name
 - Year
 - Session
 - Timezone
 - Paper
 - Subject
 - Level
 - Notes
 - **Printed (bool)**
 - **Completed (bool)**
 - **Partial (bool)**
 - **Original document valid (bool)**
 - **Markscheme document valid (bool)**
 - **Scanned document valid (bool)**

***NOTE:*** the filters (above) in bold are boolean selectors (TRUE/FALSE). The user may interact with them through a dropdown menu. The remaining filters may be interacted with through a textbox input. The user must be wary of spelling and datatype when entering a filter in these boxes, as an incorrrect entry may hinder search results.

***NOTE:*** more than one filter may be used at any given time. The program will show an intersection of all selected filters in the search results.



# Edit an item

The user may edit an item when it is 'double clicked' on the treeview in the main page.

The edit page gives the user the ability to insert/edit metadata fields described under the **Item** heading of this document. The user must note the datatypes of each metadata element, as an invalid datatype will prevent the changes from saving.

### Save changes

The user can save changes by clicking the **Confirm** button at the bottom of the page. This will save all changes to the database and refresh the page. The user may ensure all changes have been saved by reviewing the metadata elements which should not show the new values.


### Working with files

The usage of files and how they are stored in relation to the system file heirarchy are described under **How an item interacts with the system file heirarchy**. On the item edit page, the user may attribute a file to the item using the **Add original**, **Add markscheme** or **Add scanned** buttons (the three different types are described prior). 

The textbox next to the **Add original**, **Add markscheme** or **Add scanned** buttons allows the user to enter a unique extension for the file name (i.e. giving more granular detail than the provided original/markscheme/scanned differentiation). The file name extension is critical if more than one original/markscheme/scanned document exists for one item, as it will prevent duplicate file names in the directory.

##### Adding a file

To add a file to an item, click on the **Add Original**, **Add Markscheme** or **Add Scanned** buttons. Select a PDF to associate, and press **Open**. This file will then be moved into the mirrored file heirarchy and shown on the page after it is refreshed automatically. The file is now referred to as a *path*. 

##### Functions once a path has been generated

 - View the path (relative to the location of the executable)
 - View the validity of the path (TRUE if the file can be found in the path, FALSE if otherwise)
 - (button) Change Path: change the associated PDF file
 - (text entry) Unique Extension: add a string to the end of the file name, to ensure no duplicates exist if more than one PDF file is associated to the Original, Marksheme or Scanned file types. This process is completed automatically, but can also be done manually.
 - (button) Delete Path: remove the associated PDF from the item and delete the file from the system file heirarchy
 - (button) View: preview the PDF with the inbuilt PDF viewer
 - (button) Open: view the PDF in the default system browser

##### Deleting a path
when an item or file path is deleted, all associated PDF files  and folders will also be removed. 


### Marks and grade boundaries

When an item is created, it is possible to enter a mark using the **Mark** (float) and **Maximum** (float) entry fields. An automatic percentage (Mark/Maximum) is then calculated upon saving the item.

**Grade boundaries:** each item may also have associated grade boundaries. A number may be entered for each boundary (indicating the inclusive minimum mark required to achieve that grade).

# Bulk load

The user may create a large number of items at once using Bulk load to all the folders in a particular directory. The process will search for prompts in the folder and file names in order to populate the metadata for each item found. 

It is recommended that each PDF file name contains:

    Paper|paper_# (defines the paper number)
    TZ# (defines the timezone of the paper)
    HL/SL/HLSL/SLHL (defines the level of the paper) 
 If the file is a markscheme, it must have 'markscheme' in the name.

It is recommended that the folder in which the PDF files are stored contains:

    jan/feb/mar/apr/may/jun/jul/aug/sep/oct/nov/dec (defines the session)
    #### (four digits defining the year of the paper)

If any of the data above is NOT found, then the metadata will be less granular, increasing the chance of bad data (i.e. items may not have data pertaining to their level, meaning duplicate items may exist for HL and SL files).

#### Exclusions
When completing a bulk load, a set of exclusions will be shown in a text box. An exclusion is a word which, when found in the path of a file, will prevent that file from creating an item. 

For example, having the word 'spanish' as an exclusion will prevent any spanish PDFs from being read as an item. Each exclusion must be separated by a comma (,). By default, these are the exclusions:

    spanish, french, german, discrete, statistics, sets, calculus
    

