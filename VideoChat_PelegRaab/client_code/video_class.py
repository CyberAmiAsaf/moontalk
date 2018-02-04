__author__ = 'Peleg Raab'

import cv2
import time
import numpy
import datetime
from win32api import GetSystemMetrics
import thread


class Video:
    def __init__(self, sock, dst_username):
        #Video vars
        self.sock = sock
        self.frame = None
        self.capture = None
        self.window_height = GetSystemMetrics(1)
        self.window_width = GetSystemMetrics(0)
        self.dst_username = dst_username
        self.to_close = False

    def get_self_img(self):
        self.capture = cv2.VideoCapture(0)
        while not self.to_close:
            try:
                ret, self.frame = self.capture.read()
                frame = cv2.resize(self.frame, (self.window_width/2, self.window_height*3/4))
                frame = cv2.flip(frame, 1)
                cv2.imshow("You", frame)
                cv2.moveWindow("You", 0, self.window_height/4)
                cv2.resizeWindow("You", self.window_width/2, self.window_height*3/4)
            except:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # When everything done, release the capture
                self.capture.release()
                cv2.destroyAllWindows()
                self.sock.close()
                self.to_close = True
            try:
                self.send_video()
            except:
                self.to_close = True
        self.capture.release()
        cv2.destroyAllWindows()
        self.sock.close()
        thread.exit()

    def send_video(self):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', self.frame, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()
        self.sock.send(str(len(stringData)).ljust(16))
        self.sock.send(stringData)
        time.sleep(0.1)

    def receive_all(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def receive_data(self):
        data = 1
        while data != '' and not self.to_close:
            try:
                length = self.receive_all(self.sock, 16)
                stringData = self.receive_all(self.sock, int(length))
                data = numpy.fromstring(stringData, dtype='uint8')
                decimg = cv2.imdecode(data, 1)
                frame = cv2.resize(decimg, (self.window_width/2, self.window_height*3/4))
                cv2.imshow(self.dst_username, frame)
                cv2.moveWindow(self.dst_username, self.window_width/2, self.window_height/4)
                cv2.resizeWindow(self.dst_username, self.window_width/2, self.window_height*3/4)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    # self.capture.release()
                    cv2.destroyAllWindows()
                    break
            except:
                self.to_close = True
        cv2.destroyAllWindows()
        self.sock.close()
        thread.exit()

    def close_vid(self):
        self.to_close = True

