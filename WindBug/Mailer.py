import time
import smtplib

class Mailer:
    '''For emailing'''

    def __init__(self, server:str, user:str, fromAddr:str, pw:str)->None:
        self.server = server
        self.user = user
        self.fromAddr = fromAddr
        self.pw = pw

    def sendMail(self, toAddr:str, msg:str)->None:
        '''Send a message

        It's not clear whether we should reconnect to the server every time,
        or keep the link open indefintely (in _init__()). We will do the former.
        '''

        success = False
        while not success:
            try:
                self.smtp_server = smtplib.SMTP_SSL(self.server, 465)
                #print(f'Connected to {self.server}')
                self.smtp_server.login(self.user, self.pw)
                #print(f'Logged in as {self.user}')
                self.smtp_server.sendmail(from_addr=self.fromAddr, to_addrs=toAddr, msg='\n'+msg)
                self.smtp_server.quit()
                success = True
            except OSError as e:
                print(f' {e}. Unable to send email through {self.user}:{self.server}, retrying.')
                time.sleep(60)


