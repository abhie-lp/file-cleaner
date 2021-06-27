# File cleaner
Remove files from directory which are n days old.<br>
Works on both Linux and Windows.<br>
Using `gio trash` in Linux to send files to Trash and 
`Recycle.exe` by [MaDdog CmdUtils](http://www.maddogsw.com/cmdutils/) in Windows to send files to Recycle Bin

```
python cleaner.py   # To start cleaning of files for directories specified. Runs once every day.
python cleaner.py --cmd     # Start the cmd application to add, view or delete directories
python cleaner.py --gui     # Start the gui application to add, view or delete directories
```
