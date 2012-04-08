import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import servicemanager
import os
import socket

DEFAULT_PORT=9876
DEFAULT_TIMEOUT=2000

class IDACommentDaemon(win32serviceutil.ServiceFramework):
    _svc_name_ = "IDACommentDaemon"
    _svc_display_name_ = "IDA Comment Daemon"
    _svc_description_='IDA Comment Daemon'
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
        self.timeout=DEFAULT_TIMEOUT
        servicemanager.LogInfoMsg(_svc_display_name_+" started")

        #server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #server_socket.bind(("", DEFAULT_PORT))

        while 1:
            # Wait for service stop signal, if I timeout, loop again
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                servicemanager.LogInfoMsg(_svc_display_name_+" stopped")
                break

            # server_socket.listen(5)
#             print "Waiting for client on port"
# 
#             while 1:
#                 client_socket, address = server_socket.accept()
#                 print "I got a connection from ", address
#                 data = client_socket.recv(BUFSIZE)



def ctrlHandler(ctrlType):
        return True

if __name__=='__main__':
        win32api.SetConsoleCtrlHandler(ctrlHandler, True)
        win32serviceutil.HandleCommandLine(IDACommentDaemon)







