创建 Kindle 电子书 - 初级用户（只适用于 Windows 和 Mac）：
---------------------------------------------------------------------------
- 从 http://www.amazon.com/kindleformat/kindlepreviewer 下载 Kindle 预览器
- 下载完成后，请安装 Kindle 预览器
- 如果您需要安装 Kindle 预览器的更多指导建议，请参考 http://kindlepreviewer.s3.amazonaws.com/UserGuide.pdf
- 安装完成后，请打开 Kindle 预览器
- 单击 Kindle 预览器上的“Open book”（打开书）链接
- 选择 EPUB/HTML/OPF 以转换 Kindle 电子书
- 遵循指导以转换电子书并进行预览
- 转换成功的电子书扩展名为“.mobi”，位于与源 HTML/EPUB 相同的文件夹中带有 Compiled- 文件名的文件夹之下。

创建 Kindle 电子书 - 高级用户：
-------------------------------------------
高级用户可以使用命令行工具将 EPUB/HTML 转换为 Kindle 电子书。 您可以在 Windows、Mac 和 Linux 平台上使用此界面。此工具可用于自动批量转换。

适用于 Windows (XP, Vista, 7, 8) 的 KindleGen：
1. 从 www.amazon.com/kindleformat/kindlegen 下载 KindleGen zip 压缩文件至桌面。
2. 右击此压缩文件，选择“Extract All”（解压全部），并输入文件夹名称 c:\KindleGen。
3. 通过选择 Start menu（开始菜单）> All Programs（所有程序）> Accessories（附件）> Command Prompt（命令提示符），打开一个命令提示符。 
4. 输入 c:\KindleGen\kindlegen。 系统将显示如何运行 KindleGen 的指导。
5. 转换示例：要转换一个名为 book.html 的文件，请进入书所在的目录文件，例如 cd desktop，然后输入 c:\KindleGen\kindlegen book.html。 如果转换成功，一个名为 book.mobi 的新文件将显示在桌面。
6. 请注意：我们建议您遵循这些步骤运行 KindleGen。 双击 KindleGen 图标不能打开此程序。运行上述命令时不带引号。  如果您将某个文件拖至 kindlegen 可执行文件，该工具将为您转换文件，但是您无法获得输出日志，因此，我们不推荐此操作。

适用于 Linux 2.6 i386 的 KindleGen：
1. 从 www.amazon.com/kindleformat/kindlegen 下载 KindleGen tar.gz 至一个文件夹，例如主目录中的 Kindlegen (~/KindleGen)。
2. 解压文件的内容至 '~/KindleGen'。打开终端，使用命令“cd ~/KindleGen”移至包含下载文件的文件夹，然后使用命令“tar xvfz kindlegen_linux_2.6_i386_v2.tar.gz”解压内容。
3. 打开终端应用程序，并输入 ~/KindleGen/kindlegen。 系统将显示如何运行 KindleGen 的指导。
4. 转换示例：要转换一个名为 book.html 的文件，请进入书所在的目录文件，例如 cd desktop，然后输入 ~/KindleGen/kindlegen book.html。如果转换成功，一个名为 book.mobi 的新文件将显示在桌面。
5. 请注意：我们建议您遵循这些步骤运行 KindleGen。 双击 KindleGen 图标不能开启此程序。运行上述命令时不带引号

适用于 Mac OS 10.5 和 i386 以上版本的 KindleGen：
1. 从 www.amazon.com/kindleformat/kindlegen 下载 KindleGen.zip。在默认情况下，此文件下载到“Downloads”（下载）文件夹
2. 解压此文件。 如果您使用 Safari 浏览器，zip 文件在下载后自动解压。如果您禁用此设置或使用其他浏览器，双击下载的文件即可解压。
3. 单击右上角的聚焦图标，然后输入 Terminal（终端）。 单击应用程序打开它。
4. 要查看如何运行 KindleGen 的指导，在 Finder（查找）窗口中定位 kindlegen 程序。单击并将其拖至鼠标所在的 Terminal（终端）窗口。使用鼠标写入路径，并将鼠标移至行的末尾。按 Enter（输入）查看指导。
5. 与步骤 4 产生同样结果的另一种方法是，通过在终端输入命令 cd ~/Downloads/KindleGen_Mac_i386_v2，然后输入命令 kindlegen，以查看指导。
6. 转换示例：要转换名为 book.html 的文件，将 book.html 复制到桌面。在 Finder（查找）窗口中，找到 kindlegen 程序。单击并将文件拖至 Terminal（终端）窗口，然后将其放在鼠标的位置。使用鼠标自动插入路径，并将鼠标移至行的末尾。在 Finder（查找）窗口中，找到该文件。单击并将文件拖至 Terminal（终端）窗口，然后将其放在鼠标的位置。使用鼠标写入路径，并将鼠标移至行的末尾。按 Enter（输入）。如果转换成功，一个名为 book.mobi 的新文件将显示在桌面。
7. 与步骤 6 产生同样结果的另一种方法是：将 book.html 复制到桌面，通过在终端输入命令 cd ~/Downloads/KindleGen_Mac_i386_v2，然后输入命令 kindlegen ~/Desktop/book.html 来转换文件。如果转换成功，一个名为 book.mobi 的新文件将显示在桌面。
8. 请注意：我们建议您遵循这些步骤运行 KindleGen。 双击 KindleGen 图标不能开启此程序。运行上述命令时不带引号


