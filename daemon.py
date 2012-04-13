import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import servicemanager
import os
import socket
import random
import pickle

DEFAULT_PORT=9876
DEFAULT_TIMEOUT=2000
DEFAULT_BUFSIZE=8192

class IDACommentDaemon(win32serviceutil.ServiceFramework):
    _svc_name_ = "IDACommentDaemon"
    _svc_display_name_ = "IDA Comment Daemon"
    _svc_description_='IDA Comment Daemon'
    _svc_deps_ = ["EventLog"]
    func_dict = {}

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        s = socket.socket()
        s.connect((socket.gethostname(),DEFAULT_PORT))
        s.send("SHUTDOWN")
        s.close()

    def SvcDoRun(self):
        # wait for beeing stopped...
        #win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        #win32event.WaitForSingleObject(self.hWaitStop, self.timeout)

        servicemanager.LogInfoMsg(self._svc_display_name_+" Binding...")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("",DEFAULT_PORT))

        while 1:
            servicemanager.LogInfoMsg(self._svc_display_name_+" Listening...")
            server_socket.listen(5)

            client_socket, address = server_socket.accept()
            data = client_socket.recv(DEFAULT_BUFSIZE)
            servicemanager.LogInfoMsg(self._svc_display_name_+" Got: "+str(data))

            if str(data) == "SHUTDOWN":
                client_socket.close()
                return
            
            elif str(data) == "REPORT":
                client_socket.send("PROCEED")
                report_data = ''
                while 1:
                    tmp_data = client_socket.recv(DEFAULT_BUFSIZE)
                    if tmp_data == "DONE":
                            break
                    report_data += tmp_data

                client_socket.close()
                func_names = pickle.loads(report_data)
                self.func_dict.update(func_names)
                servicemanager.LogInfoMsg(self._svc_display_name_+" DB size: "+str(len(self.func_dict)))
                servicemanager.LogInfoMsg(self._svc_display_name_+" Contents: "+str(self.func_dict))

            elif str(data) == "QUERY":
                client_socket.send("PROCEED")
                query_data = client_socket.recv(DEFAULT_BUFSIZE)
                client_socket.close()



if __name__=='__main__':
        #win32api.SetConsoleCtrlHandler(ctrlHandler, True)
        win32serviceutil.HandleCommandLine(IDACommentDaemon)







