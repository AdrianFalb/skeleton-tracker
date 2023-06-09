import time
import sys

import cv2
import threading

import camera_process
from udp_server import UdpServer
from camera_read import CamRead

if __name__ == '__main__':

    robot_ip_address = sys.argv[1]
    server_udp_port = sys.argv[2]

    # robot_ip_address = "192.168.1.13"
    # server_udp_port = "23432"

    udp_server = UdpServer(int(server_udp_port))

    # ================================================================================ Threads

    read_thread = CamRead("http://" + str(robot_ip_address) + ":8000/stream.mjpg")
    # read_thread = CamRead(0)

    read_thread.start()
    time.sleep(2)

    while 1:
        image = read_thread.get_frame()

        if image is not None or image != 0:
            cv2.imshow("Camera", cv2.flip(camera_process.process_camera_data(image, udp_server, robot_ip_address), 1))
            if cv2.waitKey(5) & 0xFF == 27:  # Close on ESC
                read_thread.exit_condition = True
                break
