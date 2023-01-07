#!/usr/bin/env python3
import curses
from curses.textpad import Textbox, rectangle
import subprocess
from math import floor
from os import getuid
class ScanOptions():
    ip_address = ''
    mode = 0 # 0- Ping Scan, 1- Quick Scan, 2- Quick + OS Discovery, 3 - Full Scan

class Host():
    ip_address = ''
    mac_address = ''
    os = 'Unknown'
    ports = []

def init_application():
    scr = curses.initscr()
    curses.init_pair(2,curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3,curses.COLOR_WHITE, curses.COLOR_RED)
    scr.keypad(True)
    curses.curs_set(0)
    curses.noecho()
    return scr

def terminate_application():
    curses.endwin()

def error_dialog(title,message):
    msglen = len(message)
    win = curses.newwin(5,msglen+4,floor(curses.LINES / 2),floor(curses.COLS / 2 - msglen/ 2 -2))
    win.border(curses.ACS_VLINE,curses.ACS_VLINE,curses.ACS_HLINE,curses.ACS_HLINE,curses.ACS_ULCORNER,curses.ACS_URCORNER,curses.ACS_LLCORNER,curses.ACS_LRCORNER)
    win.bkgd(' ',curses.color_pair(3))
    win.timeout(10)
    win.addstr(0,2,f'[{title}]')
    win.addstr(2,2,message)
    while(True):
        keypressed = win.getch()
        if keypressed in [10, 13, curses.KEY_ENTER, curses.ascii.BEL, curses.KEY_EXIT] :
            break
    del(win)

def scan_dialog(scan_options):
    scan_window = curses.newwin(13,30,floor(curses.LINES / 2 -6),floor(curses.COLS / 2 -15))
    scan_window.bkgd(' ',curses.color_pair(2))
    scan_window.border(curses.ACS_VLINE,curses.ACS_VLINE,curses.ACS_HLINE,curses.ACS_HLINE,curses.ACS_ULCORNER,curses.ACS_URCORNER,curses.ACS_LLCORNER,curses.ACS_LRCORNER)
    scan_window.addstr(0,1,"[ Scan Options ]")
    scan_window.timeout(10)
    scan_window.addstr(1,2,f"IP Address/Range")
    scan_window.addstr(2,2,f"[{scan_options.ip_address}",curses.A_BOLD)
    scan_window.addch(2,22,']')
    rectangle(scan_window,4,1,9,20)
    scan_window.addstr(4,2,'[ Scan options ]',curses.A_BOLD)
    scan_window.addstr(5,2,'[ ] (P)ing Scan',0)
    scan_window.addch(5,3,'X',curses.A_BOLD)
    scan_window.addstr(6,2,'[ ] (Q)uick Scan',0)
    scan_window.addstr(7,2,'[ ] (O)S Scan',0)
    scan_window.addstr(8,2,'[ ] (F)ull Scan',0)
    scan_window.addstr(11,2,"[ (S)can ]    [ (C)ancel ]")
    keypressed = 0
    while(True):
        if keypressed == ord('p'):
            scan_options.mode = 0
            scan_window.addch(5,3,'X',curses.A_BOLD)
            scan_window.addch(6,3,' ',curses.A_BOLD)
            scan_window.addch(7,3,' ',curses.A_BOLD)
            scan_window.addch(8,3,' ',curses.A_BOLD)
            scan_window.refresh()
        elif keypressed == ord('q'):
            scan_options.mode = 1
            scan_window.addch(6,3,'X',curses.A_BOLD)
            scan_window.addch(5,3,' ',curses.A_BOLD)
            scan_window.addch(7,3,' ',curses.A_BOLD)
            scan_window.addch(8,3,' ',curses.A_BOLD)
            scan_window.refresh()
        elif keypressed == ord('o'):
            scan_options.mode = 2
            scan_window.addch(7,3,'X',curses.A_BOLD)
            scan_window.addch(6,3,' ',curses.A_BOLD)
            scan_window.addch(5,3,' ',curses.A_BOLD)
            scan_window.addch(8,3,' ',curses.A_BOLD)
            scan_window.refresh()
        elif keypressed == ord('f'):
            scan_options.mode = 3
            scan_window.addch(8,3,'X',curses.A_BOLD)
            scan_window.addch(6,3,' ',curses.A_BOLD)
            scan_window.addch(7,3,' ',curses.A_BOLD)
            scan_window.addch(5,3,' ',curses.A_BOLD)
            scan_window.refresh()
        elif keypressed == curses.KEY_DOWN:
            if scan_options.mode < 2:
                scan_options.mode +=1
            if scan_options.mode == 0:
                scan_window.addch(5,3,'X',curses.A_BOLD)
                scan_window.addch(6,3,' ',curses.A_BOLD)
                scan_window.addch(7,3,' ',curses.A_BOLD)
                scan_window.addch(8,3,' ',curses.A_BOLD)    
            elif scan_options.mode == 1:
                scan_window.addch(6,3,'X',curses.A_BOLD)
                scan_window.addch(5,3,' ',curses.A_BOLD)
                scan_window.addch(7,3,' ',curses.A_BOLD)
                scan_window.addch(8,3,' ',curses.A_BOLD)
            elif scan_options.mode == 2:
                scan_window.addch(7,3,'X',curses.A_BOLD)
                scan_window.addch(6,3,' ',curses.A_BOLD)
                scan_window.addch(5,3,' ',curses.A_BOLD)
                scan_window.addch(8,3,' ',curses.A_BOLD)
            elif scan_options.mode == 3:
                scan_window.addch(8,3,'X',curses.A_BOLD)
                scan_window.addch(6,3,' ',curses.A_BOLD)
                scan_window.addch(7,3,' ',curses.A_BOLD)
                scan_window.addch(5,3,' ',curses.A_BOLD)
            scan_window.refresh()
        elif keypressed == curses.KEY_UP:
            if scan_options.mode > 0:
                scan_options.mode -=1
            if scan_options.mode == 0:
                scan_window.addch(5,3,'X',curses.A_BOLD)
                scan_window.addch(6,3,' ',curses.A_BOLD)
                scan_window.addch(7,3,' ',curses.A_BOLD)
                scan_window.addch(8,3,' ',curses.A_BOLD)    
            elif scan_options.mode == 1:
                scan_window.addch(6,3,'X',curses.A_BOLD)
                scan_window.addch(5,3,' ',curses.A_BOLD)
                scan_window.addch(7,3,' ',curses.A_BOLD)
                scan_window.addch(8,3,' ',curses.A_BOLD)
            elif scan_options.mode == 2:
                scan_window.addch(7,3,'X',curses.A_BOLD)
                scan_window.addch(6,3,' ',curses.A_BOLD)
                scan_window.addch(5,3,' ',curses.A_BOLD)
                scan_window.addch(8,3,' ',curses.A_BOLD)
            elif scan_options.mode == 3:
                scan_window.addch(8,3,'X',curses.A_BOLD)
                scan_window.addch(6,3,' ',curses.A_BOLD)
                scan_window.addch(7,3,' ',curses.A_BOLD)
                scan_window.addch(5,3,' ',curses.A_BOLD)
            scan_window.refresh()

        elif ((keypressed >= 48) and (keypressed <= 57)) or (keypressed == ord('-')) or (keypressed == ord('.')):
            if len(scan_options.ip_address) < 20:
                scan_options.ip_address = scan_options.ip_address + chr(keypressed)
            scan_window.addstr(1,2,f"IP Address/Range")
            scan_window.addstr(2,2,f"[{scan_options.ip_address}",curses.A_BOLD)
            scan_window.addch(2,22,']')
            scan_window.refresh()
        elif (keypressed == curses.KEY_BACKSPACE) or (keypressed == 127) or (keypressed == ord("\b")):
            scan_options.ip_address = scan_options.ip_address[:-1]
            scan_window.addstr(1,2,f"IP Address/Range")
            scan_window.addstr(2,2,"                    ",curses.A_BOLD)
            scan_window.addstr(2,2,f"[{scan_options.ip_address}",curses.A_BOLD)
            scan_window.addch(2,22,']')
            scan_window.refresh()
        elif (keypressed == ord('s')):
            del(scan_window)
            return True
        elif (keypressed == ord('c')):
            del(scan_window)
            return False
        keypressed = scan_window.getch()

def perform_scan(options,nmap):
    scanning_window = curses.newwin(4,30,floor(curses.LINES / 2 -2),floor(curses.COLS / 2 -15))
    scanning_window.bkgd(' ',curses.color_pair(3))
    scanning_window.border(curses.ACS_VLINE,curses.ACS_VLINE,curses.ACS_HLINE,curses.ACS_HLINE,curses.ACS_ULCORNER,curses.ACS_URCORNER,curses.ACS_LLCORNER,curses.ACS_LRCORNER)
    scanning_window.addstr(1,3,"/!\\ Scan in progress /!\\",curses.A_BLINK)
    scanning_window.addstr(2,7,"Please wait...")
    scanning_window.refresh()
    result_list = []
    try: 
        if options.mode == 0:
            nmap_output = subprocess.check_output([nmap,'-sn',options.ip_address])
        elif options.mode == 1:
            nmap_output = subprocess.check_output([nmap,'-sS',options.ip_address],shell=True)
        elif options.mode == 2:
            nmap_output = subprocess.check_output([nmap,'-sS','-O','-T4',options.ip_address])
        elif options.mode == 3:
            nmap_output = subprocess.check_output([nmap,'-sSAL',options.ip_address])
        del(scanning_window)
        for line in nmap_output.split('\n'):
            if line.find('Nmap scan report for') != -1:
                host = line[20:len(line)-1]
            elif line.find('/') != -1:
                port = line
                


    except subprocess.CalledProcessError as E:
        del(scanning_window)

        error_dialog('Error',f'nmap exited with return code {E.returncode}.')
        exit()
        
def main(arg):

    stdscr = init_application()
    stdscr.border(curses.ACS_VLINE,curses.ACS_VLINE,curses.ACS_HLINE,curses.ACS_HLINE,curses.ACS_ULCORNER,curses.ACS_URCORNER,curses.ACS_LLCORNER,curses.ACS_LRCORNER)
    stdscr.addstr(0,1,"[ Cursed nmap ]")
    stdscr.timeout(10)
    stdscr.refresh()
    try:
        nmap_binary = str(subprocess.check_output(['whereis','nmap'])).split()[1]
    except:
        error_dialog('Critical Error','nmap binary not found, please install nmap and try again.')
        exit()

    if getuid != 0:
        error_dialog('Error','You must be root or use sudo to use this program.')
        stdscr.redrawwin()
        stdscr.refresh()
    scan_opt = ScanOptions()
    if scan_dialog(scan_opt):
        stdscr.redrawwin()
        stdscr.refresh()
        output = perform_scan(scan_opt,nmap_binary)
        stdscr.redrawwin()
        stdscr.refresh()
    stdscr.addstr(1,curses.LINES-1,'Scan finished, press q to quit')
    keypressed = 0
    while(True):
        if keypressed == ord('q'):
            terminate_application()
            break
    
if __name__== '__main__':
    curses.wrapper(main)