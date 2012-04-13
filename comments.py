import idaapi
import idautils
import sys
import socket
import pickle

DEFAULT_PORT=9876
DEFAULT_BUFSIZE=8192

hotkey_str = "Alt-s"
hotkey_str2 = "Alt-g"
default_operand = 0

def report(func_dict):
    s = socket.socket()
    s.connect((socket.gethostname(),DEFAULT_PORT))
    s.send("REPORT")
    data = s.recv(DEFAULT_BUFSIZE)
    if str(data) == "PROCEED":
        dumped = pickle.dumps(func_dict)
        s.sendall(dumped)
        s.send("DONE")
    s.close()
    print "Reported"

def report_all():
    print "Scanning..."
    all_func_ea = idautils.Functions()
    func_list = {}
    #func_names = []
    for ida_func_ea in all_func_ea:
        func_name = GetFunctionName(ida_func_ea)
        comm = GetFunctionCmt(ida_func_ea, True)
        print comm
        if comm:
                func_list[func_name] = comm
                #func_names.append(func_name)
    if len(func_list) >0:
        report(func_list)
    print "Done"

report_all()



class comment_idb_hook_t(idaapi.IDB_Hooks):
    def __init__(self):
        idaapi.IDB_Hooks.__init__(self)

    def cmt_changed(self, ea, repeatable):
        print "cmt_changed"
        #print str(ea)
        #print str(arg1)
        func_name = GetFunctionName(ea)
        comm = GetFunctionCmt(ea, repeatable)
        print func_name
        print comm
        tmp_dict = {func_name:comm}
        report(tmp_dict)
        return 0
#
#     def assemble(self, ea, cs, ip, use32, line):
#         line = line.strip()
#         if line == "xor eax, eax":
#             return "\x33\xC0"
#         elif line == "nop":
#             # Decode current instruction to figure out its size
#             cmd = idautils.DecodeInstruction(ea)
#             if cmd:
#                 # NOP all the instruction bytes
#                 return "\x90" * cmd.size
#         return None

#---------------------------------------------------------------------
# Remove an existing hook on second run
try:
    print "IDB hook checking for hook..."
    idbhook
    print "IDB hook unhooking...."
    idbhook.unhook()
    del idbhook
except:
    print "IDB hook was not installed"

try:
    idbhook = comment_idb_hook_t()
    idbhook.hook()
    print "IDB hook installed"
except:
    print "Failed installing hook"


# class CommentUIHook(idaapi.UI_Hooks):
#     def __init__(self):
#         idaapi.UI_Hooks.__init__(self)
#         self.cmdname = "<no command>"
# 
#     def get_ea_hint(self, ea):
#         """
#         The UI wants to display a simple hint for an address in the navigation band
#         @param ea: The address
#         @return: String with the hint or None
#         """
#         print("get_ea_hint(%x)" % ea)
#  
# 
# # Remove an existing hook on second run
# try:
#     ui_hook_stat = "un"
#     print("UI hook: checking for hook...")
#     uihook
#     print("UI hook: unhooking....")
#     uihook.unhook()
#     del uihook
# except:
#     print("UI hook: not installed, installing now....")
#     ui_hook_stat = ""
#     uihook = CommentUIHook()
#     uihook.hook()
# 
# print("UI hook %sinstalled. Run the script again to %sinstall" % (ui_hook_stat, ui_hook_stat))




#---------------------------------------------------------------------
class CommentViewer(simplecustviewer_t):
    def Create(self, sn=None):
        # Form the title
        title = "Comment Viewer"
        # Create the customviewer
        if not simplecustviewer_t.Create(self, title):
            return False
        self.menu_set_comment = self.AddPopupMenu("Set Comment")
        self.menu_remove_comment = self.AddPopupMenu("Remove Comment")

        self.AddLine("")
        return True

    def OnClick(self, shift):
        """
        Cursor position changed.
        @return: Nothing
        """
        #print "OnClick" 

    def SetComment(self,comm):
        self.EditLine(self,0,comm)

    def OnPopupMenu(self, menu_id):
        if menu_id == self.menu_set_comment:
	    sEA = ScreenEA()
	    SetFunctionCmt(sEA,"Test Comment",0)
        elif menu_id == self.menu_world:
            sEA = ScreenEA()
            g.SetComment(GetFunctionCmt(sEA,0))
        else:
            # Unhandled
            return False
        return True




g = CommentViewer()
g.Create()
g.Show()


def on_click():
    sEA = ScreenEA()
    g.SetComment(GetFunctionCmt(sEA,0))
    #lnum = GetLineNumber(sEA)
    #if lnum in comment_dict:
    #        print comment_dict(lnum)        


def on_hotkey():
    sEA = ScreenEA()
    #operand = GetOpnd(sEA,default_operand)
    #operand_val = GetOperandValue(sEA,default_operand)
    #print "Operand: "+str(operand)
    #if operand_val:
    #    print "Value: "+str(operand_val)
    #lnum = GetLineNumber(sEA)
    #comment = sys.stdin.readlines()
    #comment_dict[lnum] = comment
    #MakeComm(sEA,"Test Comment")
    SetFunctionCmt(sEA,"Test Comment",0)
    ##graph()


def go_callback(*args):
    go()
    return 1


# IDA binds hotkeys to IDC functions so a trampoline IDC function must be created
idaapi.CompileLine('static flopy_key() { RunPythonStatement("on_hotkey()"); }')
add_idc_hotkey(hotkey_str, 'flopy_key')
idaapi.CompileLine('static flopy_click() { RunPythonStatement("on_click()"); }')
add_idc_hotkey(hotkey_str2, 'flopy_click')


# Add menu item
try:
    if ctx:
        idaapi.del_menu_item(ctx)
except:
    pass

ctx = idaapi.add_menu_item("Search/", "Go", "", 0, go_callback, tuple("hello world"))
if ctx is None:
    print "Failed to add menu!"
    del ctx
else:
    print "Menu added successfully!"

