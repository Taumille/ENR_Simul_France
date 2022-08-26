import os
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


os.system('python productionHydro.py')
recu=1
recu=recu.to_bytes(1,'little')
message=0

def reception():
    message=0
    message = socket.recv()
    return message

while True:
    message=0
    try:
        if __name__ == '__main__':
            # Start foo as a process
            p = multiprocessing.Process(target=reception, name="Foo", args=())
            p.start()
            print("Tentative")

            # Wait 10 seconds for foo
            time.sleep(1)

            # Terminate foo
            p.terminate()

            # Cleanup
            p.join()
        socket.send(recu)
        print("Recu")
    except:
        pass
    if int(message)!=0:
        print("le message recu est : "+str(message))