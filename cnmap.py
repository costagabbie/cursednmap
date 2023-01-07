#!/usr/bin/env python3
import curses
from curses.textpad import Textbox, rectangle
import subprocess
from math import floor
from os import getuid,path

ScanModes = [{'Ping Scan','-sn'},{'TCP SYN Scan','-sS'},{'TCP Syn+OS Discovery','-sS -O -T4'},{'UDP Scan','-sU'}]

class ScanOptions():
    ip_address = ''
    mode = 0

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

def error_dialog(title,message):
    msglen = len(message)
    win = init_dialog(4,msglen+4,floor(curses.LINES / 2),floor(curses.COLS / 2 - msglen/ 2 -2),3,title)
    win.addstr(2,2,message)
    win.redrawwin()
    win.refresh()
    while(True):
        keypressed = win.getch()
        if keypressed in [10, 13, curses.KEY_ENTER, curses.ascii.BEL, curses.KEY_EXIT] :
            break
    del(win)

def input_dialog(title, message, default_text, max_length):
    msglen = len(message)
    if (msglen >= max_length) or (max_length >= curses.COLS -4):
        win = init_dialog(5,msglen+4,floor(curses.LINES / 2),floor(curses.COLS / 2 - msglen/ 2 -2),1,title)
    else:
        win = init_dialog(5,max_length+4,floor(curses.LINES / 2),floor(curses.COLS / 2 - max_length/ 2 -2),title)
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
            return result
        elif(keypressed >=32) and (keypressed <=126) :
            result += chr(keypressed)
            win.addstr(3,2,result)
            win.refresh()

def choice_dialog(title, message,choices =[]):
    msglen = len(message)
    win = init_dialog(13,msglen+4,floor(curses.LINES / 2),floor(curses.COLS / 2 - msglen/ 2 -2),title)
    win.addstr(2,2,message)
    rectangle(win,4,2,6,msglen-4)
    win.addstr(5,2,str(choices[0])[0:msglen-6],curses.color_pair(2))
    win.addch(5,msglen-5,curses.ACS_DARROW)
    itemindex = 0
    while(True):
        keypressed = win.getch()
        if (keypressed == curses.KEY_ENTER) or (keypressed in [10,13]):
            return itemindex
        elif keypressed == curses.KEY_DOWN:
            if itemindex < len(choices):
                itemindex += 1
            win.addstr(5,2,str(choices[itemindex])[0:msglen-6],curses.color_pair(2))
            win.refresh()
        elif keypressed == curses.KEY_UP:
            if itemindex > 0:
                itemindex -= 1
            win.addstr(5,2,str(choices[itemindex])[0:msglen-6],curses.color_pair(2))
            win.refresh()

def perform_scan(nmap, mode, target):
    scanning_window = init_dialog(4,30,floor(curses.LINES / 2 -2),floor(curses.COLS / 2 -15),3,'Scanning')
    scanning_window.addstr(1,3,"/!\\ Scan in progress /!\\",curses.A_BLINK)
    scanning_window.addstr(2,7,"Please wait...")
    scanning_window.refresh()
    result_list = []
    try: 
        nmap_output = subprocess.check_output([nmap,str(ScanModes[mode]),target])
    except subprocess.CalledProcessError as E:
        del(scanning_window)
        error_dialog('Error',f'nmap exited with return code {E.returncode}.')
        exit()
        
def main(arg):
    stdscr = init_application()
    stdscr.border(curses.ACS_VLINE,curses.ACS_VLINE,curses.ACS_HLINE,curses.ACS_HLINE,curses.ACS_ULCORNER,curses.ACS_URCORNER,curses.ACS_LLCORNER,curses.ACS_LRCORNER)
    stdscr.addstr(0,1,"[ Cursed nmap ]")
    for i in range(curses.COLS-2):
        stdscr.addch(1,1+i,' ',curses.color_pair(2))
        stdscr.addch(2,1+i,curses.ACS_HLINE)
    stdscr.addstr(1,2,'[(N)ew Scan | (S)ave Output | (Q)uit]',curses.color_pair(2))
    stdscr.timeout(10)
    stdscr.refresh()
    try:
        nmap_binary = str(subprocess.check_output(['whereis','nmap'])).split()[1]
    except:
        error_dialog('Critical Error','nmap binary not found, please install nmap and try again.')
        exit()
    current_uid = getuid()
    if current_uid != 0:
        error_dialog('Error','You must be root or use sudo to use this program.')
        stdscr.redrawwin()
        stdscr.refresh()
    scan_opt = ScanOptions()
    
        
    stdscr.refresh()
    while(True):
        keypressed = stdscr.getch()
        if keypressed == ord('n'):
            error_dialog('Not implemented','The new scan dialog is not implemented yet :(')
        if keypressed == ord('s'):
            input_dialog('Save Scan','Select where you want to save the output file',path.expanduser('~'),260)
        if keypressed == ord('q'):
            terminate_application()
            break
    
if __name__== '__main__':
    curses.wrapper(main)