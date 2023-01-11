#!/usr/bin/env python3
import curses
from curses.textpad import Textbox, rectangle
from math import floor
from os import getuid,path
import nmap
import subprocess

VERSION_STRING = '0.0.1.1'
ScanModes = [
            {'name':'Ping Scan','param':'-sn','root':False},
            {'name':'TCP Connect','param':'-sT','root':False},
            {'name':'TCP SYN Ping','param':'-PS','root':True},
            {'name':'TCP ACK','param':'-PA','root':True},
            {'name':'UDP Ping','param':'-PU','root':True},
            {'name':'ARP Ping','param':'-PR','root':False},
            {'name':'TCP SYN','param':'-sS','root':True},
            {'name':'TCP NULL','param':'-sN','root':True},
            {'name':'TCP FIN','param':'-sF','root':True},
            {'name':'TCP XMAS','param':'-sX','root':True},
            {'name':'TCP SYN+OS','param':'-sS -O -T4','root':True},
            {'name':'UDP Scan','param':'-sU','root':True}
            
            ]

current_uid = getuid()

class ScanOptions():
    ip_address = ''
    mode = 0

# Helper function that we call when we are initializing curses
def init_application():
    scr = curses.initscr()
    if (curses.COLS < 60) or (curses.LINES < 15):
        scr.addstr(1,1,'You need at least a 60x15 terminal.')
        scr.addstr(2,1,'Press any key to quit.')
        scr.refresh()
        scr.timeout(10)
        while True :
            if scr.getch() > -1:
                exit()
    curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2,curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3,curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(4,curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5,curses.COLOR_BLUE, curses.COLOR_WHITE)
    scr.keypad(True)
    curses.curs_set(0)
    curses.noecho()
    return scr

# Helper function that we call to initialize new dialog windows
def init_dialog(height:int, width:int, pos_y:int, pos_x:int,color_pair:int,title:str):
    try:
        dialog= curses.newwin(height,width,pos_y,pos_x)
        dialog.border(curses.ACS_VLINE,curses.ACS_VLINE,curses.ACS_HLINE,curses.ACS_HLINE,curses.ACS_ULCORNER,curses.ACS_URCORNER,curses.ACS_LLCORNER,curses.ACS_LRCORNER)
        dialog.bkgd(' ',curses.color_pair(color_pair))
        dialog.timeout(10)
        dialog.addstr(0,2,f'[{title}]')
        return dialog
    except:
        return None

#--------------- Beginning of Reusable dialogs section ---------------
def error_dialog(title:str,message:str):
    msglen = len(message)
    win = init_dialog(4,msglen+4,floor(curses.LINES / 2),floor(curses.COLS / 2 - msglen/ 2 -2),3,title)
    win.addstr(1,2,message,curses.color_pair(4))
    win.addstr(2,2,'Press ENTER to continue')
    win.redrawwin()
    win.refresh()
    while(True):
        keypressed = win.getch()
        if keypressed in [10, 13, curses.KEY_ENTER, curses.ascii.BEL, curses.KEY_EXIT] :
            break
    del(win)

def input_dialog(title:str, message:str, default_text:str, max_length:int):
    msglen = len(message)
    if (msglen >= max_length) or (max_length >= curses.COLS -4):
        win = init_dialog(5,msglen+4,floor(curses.LINES / 2),floor(curses.COLS / 2 - msglen/ 2 -2),2,title)
    else:
        win = init_dialog(5,max_length+4,floor(curses.LINES / 2),floor(curses.COLS / 2 - max_length/ 2 -2),2,title)
    win.addstr(2,2,message)
    result = default_text
    win.addstr(3,2,result)
    win.refresh()
    while(True):
        keypressed = win.getch()
        if (keypressed == curses.KEY_BACKSPACE) or (keypressed == 127) or (keypressed == ord("\b")):
            if (msglen >= max_length) or (max_length >= curses.COLS -4):
                for i in range(msglen -4 ):
                    win.addch(3,2+i,' ')
            else:
                for i in range(max_length):
                    win.addch(3,2+i,' ')
            result = result[:-1]
            win.addstr(3,2,result)
            win.refresh()
        elif (keypressed == curses.KEY_ENTER) or (keypressed in [10,13]):
            del(win)
            return result
        elif(keypressed >=32) and (keypressed <=126) :
            result += chr(keypressed)
            win.addstr(3,2,result)
            win.refresh()

def choice_dialog(title:str, message:str,choices =[]):
    msglen = len(message)
    itemindex = 0 #this will hold the selected choice
    win = init_dialog(8,msglen+4,floor(curses.LINES / 2),floor(curses.COLS / 2 - msglen/ 2 -2),2,title) # Make the window centered
    win.keypad(True) #we are using up and arrow keys so we need the keypad to be True
    # render the widgets with the defaults
    win.addstr(2,2,message)
    rectangle(win,4,1,6,msglen)
    win.addstr(5,2,str(choices[0])[0:msglen-2],curses.color_pair(2))
    win.addch(5,msglen-1,curses.ACS_DARROW) 
    while(True):
        keypressed = win.getch()
        if (keypressed == curses.KEY_ENTER) or (keypressed in [10,13]):
            return itemindex
        elif keypressed == curses.KEY_DOWN:
            if itemindex < len(choices)-1: #check if we are not on the last item of the choice list
                itemindex += 1
            # Render the new choice on the widget
            for i in range(msglen-2):
                win.addch(5,2+i,' ',curses.color_pair(2))
            win.addstr(5,2,str(choices[itemindex])[0:msglen-6],curses.color_pair(2))
            win.addch(5,msglen-1,curses.ACS_DARROW)
            win.refresh()
        elif keypressed == curses.KEY_UP:
            if itemindex > 0: #check if we are not on the first item of the choice list
                itemindex -= 1
            # Render the new choice on the widget
            for i in range(msglen-2):
                win.addch(5,2+i,' ',curses.color_pair(2))
            win.addstr(5,2,str(choices[itemindex])[0:msglen-6],curses.color_pair(2))
            win.addch(5,msglen-1,curses.ACS_DARROW)
            win.refresh()

#--------------- End of Reusable dialogs section ---------------

# New Scan window function
def newscan_win(options:ScanOptions):
    win = init_dialog(6,40,floor(curses.LINES / 2),floor(curses.COLS / 2 - 20),1,'New Scan')
    win.keypad(True)
    scan_modes = []
    focus = 0
    for item in ScanModes: #extracting just the names and putting on a list for the choice dialog 
        if item['root'] and current_uid != 0:
            continue
        scan_modes.append(item['name'])
    # Rendering the window
    win.addstr(1,2,'Target IPs:')
    win.addstr('None                ',curses.color_pair(4))
    win.addstr(2,2,' Scan Mode:')
    win.addstr(2,13,'                    ',curses.color_pair(4))
    win.addstr(2,13,scan_modes[options.mode],curses.color_pair(4))
    win.addstr(3,2,'[ Start Scanning ]',curses.color_pair(2))
    win.addstr(4,2,'[ Cancel ]',curses.color_pair(2))
    win.addch(1,1,'>',2)
    while True:
        keypressed = win.getch()
        if keypressed == curses.KEY_UP:
            if focus > 0: #if the focused "widget" is not the first one, we focus on the prior "widget"
                focus -= 1
                for i in range(4): #we update the cursor
                    if i == focus:
                        win.addch(1+i,1,'>',2)
                    else:
                        win.addch(1+i,1,' ')
                win.refresh()
            else:
                curses.beep() # beep if the up arrow key is pressed but we are on the first item
        elif keypressed == curses.KEY_DOWN:
            if focus < 3: #if the focused "widget" is not the last one, we focus on the next
                focus += 1
                for i in range(4): #we update the cursor
                    if i == focus:
                        win.addch(1+i,1,'>',2)
                    else:
                        win.addch(1+i,1,' ')
                win.refresh()
            else:
                curses.beep() # beep if the focused "widget" is the last one and the down key was pressed
        elif (keypressed == curses.KEY_ENTER) or (keypressed in [10,13]):
            if focus == 0: #IP Address field is focused
                options.ip_address = input_dialog('Target IPs','Insert the target IP or IP range.',options.ip_address,20)
                win.addstr(1,13,'                    ',curses.color_pair(4)) #fill with blank spaces
                if options.ip_address == '': #if the ip address is blank we print None
                    win.addstr(1,13,'None                ',curses.color_pair(4))
                else: #otherwise we print the target ip address   
                    win.addstr(1,13,options.ip_address,curses.color_pair(4)) #
                win.redrawwin()
                win.refresh()
            elif focus == 1:#Scan Mode field is focused
                options.mode = choice_dialog('Scan Mode','Select the scan mode',scan_modes)
                win.addstr(2,13,'                   ',curses.color_pair(4))
                win.addstr(2,13,scan_modes[options.mode],curses.color_pair(4))
                win.redrawwin()
                win.refresh()
            elif focus == 2:#Confirm "button" is focused
                del(win)
                return True
            elif focus == 3:#Cancel "button" is focused
                del(win)
                return False
        elif keypressed == curses.KEY_CANCEL:
            return False

def perform_scan(nm:nmap,mode:int, target:str):
    #Rendering the window
    try:
        scanning_window = init_dialog(4,30,floor(curses.LINES / 2 -2),floor(curses.COLS / 2 -15),3,'Scanning')
        scanning_window.addstr(1,3,"/!\\ Scan in progress /!\\",curses.A_BLINK)
        scanning_window.addstr(2,7,"Please wait...")
        scanning_window.refresh()
        nm.scan(target,arguments=ScanModes[mode]['param'],sudo=current_uid==0)
        del(scanning_window)
        return True
    except:
        error_dialog('Error scanning',f'cmdline:{nm.command_line()}')
        del(scanning_window)
        return False

def custom_scan(nm:nmap,arguments:str, target:str):
    try:
        scanning_window = init_dialog(4,34,floor(curses.LINES / 2 -2),floor(curses.COLS / 2 -17),3,'Scanning')
        scanning_window.addstr(1,2,"/!\\ Custom scan in progress",curses.A_BLINK)
        scanning_window.addstr(2,7,"Please wait...")
        scanning_window.refresh()
        nm.scan(target,arguments=arguments,sudo=current_uid==0)
        del(scanning_window)
        return True
    except:
        error_dialog('Error scanning',f'cmdline:{nm.command_line()}')
        del(scanning_window)
        return False

def mainwindow_clear(stdscr:curses.window,focused_list:int):
    stdscr.border(curses.ACS_VLINE,curses.ACS_VLINE,curses.ACS_HLINE,curses.ACS_HLINE,curses.ACS_ULCORNER,curses.ACS_URCORNER,curses.ACS_LLCORNER,curses.ACS_LRCORNER)
    stdscr.addstr(0,1,"[ Cursed nmap ]")
    #Rendering the toolbar 
    for i in range(curses.COLS-2):
        stdscr.addch(1,1+i,' ',curses.color_pair(2))
        stdscr.addch(2,1+i,curses.ACS_HLINE)
    stdscr.addstr(1,2,'[New Scan | Custom Scan | Save Output | Quit]',curses.color_pair(2))
    stdscr.addch(1,3,'N',curses.color_pair(5))
    stdscr.addch(1,14,'C',curses.color_pair(5))
    stdscr.addch(1,28,'S',curses.color_pair(5))
    stdscr.addch(1,42,'Q',curses.color_pair(5))
    #Rendering the Host List Rectangle
    rectangle(stdscr,3,1,curses.LINES-3,25)
    if focused_list == 0:
        stdscr.addstr(3,2,'[Host List]',curses.color_pair(2))    
    else:
        stdscr.addstr(3,2,'[Host List]',curses.color_pair(0))
    #Rendering the Host Details Rectangle
    rectangle(stdscr,3,26,10,curses.COLS-3)
    stdscr.addstr(3,27,'[Host Detail]')
    stdscr.addstr(4,27,'Operating System:')
    for i in range(curses.COLS - 47):
        stdscr.addstr(4,44+i,' ')
    stdscr.addstr(5,27,'IP Address:')
    for i in range(curses.COLS - 42):
        stdscr.addstr(5,38+i,' ')
    stdscr.addstr(6,27,'Hostname:')
    for i in range(curses.COLS - 39):
        stdscr.addstr(6,36+i,' ')
    stdscr.addstr(7,27,'MAC Addr:')
    for i in range(curses.COLS - 44):
        stdscr.addstr(7,39+i,' ')
    stdscr.addstr(8,27,'Vendor:')
    for i in range(curses.COLS - 40):
        stdscr.addstr(8,34+i,' ')
    stdscr.addstr(9,27,'Uptime:')
    for i in range(curses.COLS - 40):
        stdscr.addstr(9,34+i,' ')
    #Render Port detail
    rectangle(stdscr,11,26,curses.LINES-3,curses.COLS-3)
    if focused_list == 1:
        stdscr.addstr(11,27,'[Port Detail]',curses.color_pair(2))
    else:
        stdscr.addstr(11,27,'[Port Detail]',curses.color_pair(0))
    for i in range(curses.COLS-31):
        for j in range(curses.LINES-15):
            stdscr.addch(12+j,28+i,' ')
    #Render the status bar
    for i in range(curses.COLS-2):
        stdscr.addch(curses.LINES-2,1+i,' ',curses.color_pair(2))
    stdscr.addstr(curses.LINES-2,1,f'Cursed nmap version:{VERSION_STRING}',curses.color_pair(2))

def mainwindow_update_hostlist(scr:curses.window,scan_result:nmap.PortScanner,item_index,hostpad:curses.window,portpad:curses.window):
    host_index = 0
    for host in scan_result.all_hosts():
        if host_index == item_index: #If we are printing the selected host
            #scr.addstr(4+host_index,2,host,curses.color_pair(3)) #Make it highlighted
            hostpad.addstr(host_index,0,host,curses.color_pair(3))
            #Print the host details
            if 'osmatch' in scan_result[host]:
                try:
                    scr.addstr(4,45,f"{scan_result[host]['osmatch'][0]['name']}(")
                except:
                    scr.addstr(4,45,"Unknown")
                
            else:
                scr.addstr(4,45,'Not identified')
            if 'vendor' in scan_result[host]:
                try:
                    scr.addstr(7,36,list(scan_result[host]['vendor'])[0])
                    scr.addstr(8,34,list(scan_result[host]['vendor'])[1])
                except:
                    scr.addstr(8,34,"Unknown")
            if 'uptime' in scan_result[host]:
                try:
                    scr.addstr(9,34,f"{scan_result[host]['uptime']['seconds']}s (boot:{scan_result[host]['uptime']['lastboot']})")
                except:
                    scr.addstr(9,34,'Unknown')
            scr.addstr(5,39,host)
            if len(scan_result[host].hostname()) >0:
                scr.addstr(6,39,scan_result[host].hostname())
            else:
                scr.addstr(6,39,'Not resolved')
            mainwindow_update_portlist(scr,scan_result,item_index,portpad)
        else:
            #scr.addstr(4+host_index,2,host,curses.color_pair(0)) #Print it normally
            hostpad.addstr(host_index,0,host,curses.color_pair(0)) 
        host_index+=1

def mainwindow_update_portlist(scr:curses.window,scan_result:nmap.PortScanner,item_index:int,portpad:curses.window):
    port_index = 0
    for proto in scan_result[scan_result.all_hosts()[item_index]].all_protocols():
        lport = list(scan_result[scan_result.all_hosts()[item_index]][proto])
        lport.sort()
        for port in lport:
            portpad.addstr(port_index,0,f"{proto}/{port} state:{scan_result[scan_result.all_hosts()[item_index]][proto][port]['state']}")
            port_index +=1

def main(arg):
    scan_opt = ScanOptions()
    scanned_hosts = 0
    selected_host = -1
    nm = nmap.PortScanner()   
    stdscr = init_application()
    hostlist_pad = curses.newpad(1,24)
    hostlist_page = 0
    portlist_pad = curses.newpad(curses.LINES * 10,curses.COLS-31)
    portlist_page = 0
    focused_list = 0
    stdscr.timeout(10)
    #Rendering border
    mainwindow_clear(stdscr,focused_list)
    #Check if nmap i,focused_lists installed 
    try:
        subprocess.check_output(['whereis','nmap'])
    except:
        error_dialog('Critical Error','nmap binary not found, please install nmap and try again.')
        exit()
    #Check if we are root, and warn if we are not
    if current_uid != 0:
        error_dialog('Warning','Not running as root, this will limit your scan options!')
        stdscr.refresh()
    stdscr.refresh()
    while(True):
        keypressed = stdscr.getch()
        if keypressed == ord('n'):
            if newscan_win(scan_opt):
                if not perform_scan(nm,scan_opt.mode,scan_opt.ip_address):
                    continue
                scanned_hosts = len(nm.all_hosts())
                selected_host = 0
                if scanned_hosts > 0:
                    hostlist_pad = curses.newpad(scanned_hosts,24)
                    mainwindow_clear(stdscr,focused_list)
                    mainwindow_update_hostlist(stdscr,nm,selected_host,hostlist_pad,portlist_pad)
                    stdscr.addstr(curses.LINES-2,1,f'Cursed nmap version:{VERSION_STRING} | Host count: {len(nm.all_hosts())}',curses.color_pair(2))
                    stdscr.refresh()
                    hostlist_pad.refresh(0,0,4,2,curses.LINES-3,23)
                    portlist_pad.refresh(0,0,12,28,curses.LINES-4,curses.COLS-4)
                else:
                    error_dialog('Warning','No hosts found!')
            else:
                stdscr.refresh()
        elif keypressed == ord('c'):
            hosts = input_dialog('Custom Scan','Insert the target ip address/range','',30)
            arguments = input_dialog('Custom Scan','Insert the nmap command parameters(e.g: -sS -A -T4','',200)
            if not custom_scan(nm,arguments,hosts):
                continue
            scanned_hosts = len(nm.all_hosts())
            selected_host = 0
            if scanned_hosts > 0:
                mainwindow_clear(stdscr,focused_list)
                mainwindow_update_hostlist(stdscr,nm,0)
                stdscr.addstr(curses.LINES-2,2,f'Cursed nmap version:{VERSION_STRING} | Host count: {nm.all_hosts().count()}',curses.color_pair(2))
                stdscr.refresh()
                hostlist_pad.refresh(0,0,4,2,curses.LINES-3,23)
                portlist_pad.refresh(0,0,12,28,curses.LINES-4,curses.COLS-4)
        elif keypressed == ord('s'):
            try:
                filename = input_dialog('Save Scan','Select where you want to save the output file',path.expanduser('~'),260)
                with open(filename,'w') as filp:
                    filp.write(nm.csv())
                stdscr.refresh()
                if selected_host <= curses.LINES - 7:
                    hostlist_pad.refresh(0,0,4,2,curses.LINES-3,23)
                else:
                    hostlist_pad.refresh(selected_host,0,4,2,curses.LINES-3,23)
                portlist_pad.refresh(0,0,12,28,curses.LINES-4,curses.COLS-4)
            except:
                error_dialog('Error','Error saving the file.')
                stdscr.refresh()
                if selected_host <= curses.LINES - 7:
                    hostlist_pad.refresh(0,0,4,2,curses.LINES-3,23)
                else:
                    hostlist_pad.refresh(selected_host,0,4,2,curses.LINES-3,23)
                portlist_pad.refresh(0,0,12,28,curses.LINES-4,curses.COLS-4)

        elif keypressed == ord('q'):
            curses.endwin()
            break
        elif keypressed == curses.KEY_UP:
            if scanned_hosts == 0:
                continue
            if focused_list == 0:
                if selected_host > 0:
                    selected_host -= 1
                    mainwindow_clear(stdscr,focused_list)
                    mainwindow_update_hostlist(stdscr,nm,selected_host,hostlist_pad,portlist_pad)
                    stdscr.refresh()
            if selected_host <= curses.LINES - 7:
                hostlist_pad.refresh(0,0,4,2,curses.LINES-3,23)
            else:
                hostlist_pad.refresh(selected_host,0,4,2,curses.LINES-3,23)
            portlist_pad.refresh(0,0,12,28,curses.LINES-4,curses.COLS-4)

        elif keypressed == curses.KEY_DOWN:
            if scanned_hosts == 0:
                continue
            
            if focused_list == 0:
                if selected_host < len(nm.all_hosts())-1:
                    selected_host+=1
                    mainwindow_clear(stdscr,focused_list)
                    mainwindow_update_hostlist(stdscr,nm,selected_host,hostlist_pad,portlist_pad)
                    stdscr.refresh()
            if selected_host <= curses.LINES - 7:
                hostlist_pad.refresh(0,0,4,2,curses.LINES-3,23)
            else:
                hostlist_pad.refresh(selected_host,0,4,2,curses.LINES-3,23)
            portlist_pad.refresh(0,0,12,28,curses.LINES-4,curses.COLS-4)

        elif keypressed == curses.KEY_LEFT: #tab key
            if focused_list == 1:
                focused_list =0
                mainwindow_clear(stdscr,focused_list)
            if scanned_hosts > 0:
                mainwindow_update_hostlist(stdscr,nm,selected_host,hostlist_pad,portlist_pad)
            stdscr.refresh()
            if selected_host <= curses.LINES - 7:
                hostlist_pad.refresh(0,0,4,2,curses.LINES-3,23)
            else:
                hostlist_pad.refresh(selected_host,0,4,2,curses.LINES-3,23)
            portlist_pad.refresh(0,0,12,28,curses.LINES-4,curses.COLS-4)

        elif keypressed == curses.KEY_RIGHT: #tab key
            if focused_list == 0:
                focused_list =1
                mainwindow_clear(stdscr,focused_list)
            if scanned_hosts > 0:
                mainwindow_update_hostlist(stdscr,nm,selected_host,hostlist_pad,portlist_pad)
            stdscr.refresh()
            if selected_host <= curses.LINES - 7:
                hostlist_pad.refresh(0,0,4,2,curses.LINES-3,23)
            else:
                hostlist_pad.refresh(selected_host,0,4,2,curses.LINES-3,23)
            portlist_pad.refresh(0,0,12,28,curses.LINES-4,curses.COLS-4)
    
if __name__== '__main__':
    curses.wrapper(main)