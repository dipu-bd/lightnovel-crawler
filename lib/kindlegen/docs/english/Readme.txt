Creating Kindle ebooks - Basic users (Windows and Mac only):
---------------------------------------------------------------------------
- Download the Kindle Previewer from http://www.amazon.com/kindleformat/kindlepreviewer
- Once the download is finished, install the Kindle Previewer
- If you need further instruction on how to install Kindle Previewer, please refer http://kindlepreviewer.s3.amazonaws.com/UserGuide.pdf
- Once the install is complete, launch Kindle Previewer 
- Click on "Open book" link in Kindle Previewer
- Select the EPUB/HTML/OPF to convert to Kindle ebook
- Follow the instructions to convert the book and preview
- The converted ebook with extension ".mobi" can be obtained from the folder Compiled-filename from the same folder as the source HTML/EPUB.

Creating Kindle ebooks - Advanced users:
-------------------------------------------
Advanced users can use the command line tool to convert EPUB/HTML to Kindle ebooks. This interface is available in Windows, Mac and Linux platform. This tool can be used for automated bulk conversions.

KindleGen for Windows (XP, Vista, 7, 8):
1. Download the KindleGen zip file from www.amazon.com/kindleformat/kindlegen to the desktop.
2. Right-click the zip file, select Extract All, and enter the folder name as c:\KindleGen.
3. Open a command prompt by selecting Start menu > All Programs > Accessories > Command Prompt. 
4. Type c:\KindleGen\kindlegen. Instructions on how to run KindleGen are displayed.
5. Conversion Example: To convert a file called book.html, go to the directory where the book is located, such as cd desktop, and type c:\KindleGen\kindlegen book.html. If the conversion was successful, a new file called book.mobi displays on the desktop.
6. Please note: it is recommended to follow these steps to run KindleGen. Double-clicking the KindleGen icon does not launch this program. Run the above commands without quotes.  If you drag and drop a file on the kindlegen executable it will convert the file for you, but you will not be able to capture the output logging, so this is also not recommended. 

KindleGen for Linux 2.6 i386 :
1. Download the KindleGen tar.gz from www.amazon.com/kindleformat/kindlegen to a folder such as Kindlegen in home directory (~/KindleGen).
2. Extract the contents of the file to '~/KindleGen'. Open the terminal, move to folder containing the downloaded file using command "cd ~/KindleGen" and then use command "tar xvfz kindlegen_linux_2.6_i386_v2.tar.gz" to extract the contents.
3. Open the Terminal application and type ~/KindleGen/kindlegen. Instructions on how to run KindleGen are displayed.
4. Conversion Example: To convert a file called book.html, go to the directory where the book is located, such as cd desktop, and type ~/KindleGen/kindlegen book.html. If the conversion was successful, a new file called book.mobi displays on the desktop.
5. Please note: It is recommended to follow these steps to run KindleGen. Double-clicking the KindleGen icon does not launch this program. Run the above commands without quotes

KindleGen for Mac OS 10.5 and above i386:
1. Download KindleGen.zip from www.amazon.com/kindleformat/kindlegen. By default, the file is downloaded in the Downloads folder
2. Unzip the file. In Safari, the zip file is automatically unzipped after download. If this setting is disabled or if another browser was used, double-click the downloaded file to unzip it.
3. Click the spotlight icon in the top right corner and type Terminal. Click the application to open it.
4. To view the instructions on how to run KindleGen, locate the kindlegen program in the Finder window. Click and drag it to Terminal window where the cursor is. The cursor writes in the path and moves to the end of the line. Press Enter to view the instructions. 
5. Alternative to step 4, view the instructions by typing the command cd ~/Downloads/KindleGen_Mac_i386_v2 in Terminal and then typing the command kindlegen.
6. Conversion Example: To convert a file called book.html, copy book.html to the desktop. In the Finder window, locate the kindlegen program. Click and drag it to the Terminal window, and drop it where the cursor is. The cursor inserts the path automatically and moves to the end of that line. In the Finder window, locate the document. Click and drag it to the Terminal window, and drop it where the cursor is. The cursor writes in the path and moves to the end of the line. Press Enter. If the conversion was successful, a new file called book.mobi displays on the desktop.
7. Alternative to step6: Copy book.html to the desktop and convert the file by typing the command cd ~/Downloads/KindleGen_Mac_i386_v2 in Terminal and then typing the command kindlegen ~/Desktop/book.html. If the conversion was successful, a new file called book.mobi displays on the desktop.
8. Please note: It is recommended to follow these steps to run KindleGen. Double-clicking the KindleGen icon does not launch this program. Run the above commands without quotes


