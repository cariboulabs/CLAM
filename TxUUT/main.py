import time
from TxUUT import TxUUT

def shutdown(tx_uut: TxUUT):
    tx_uut.stop_recv_loop = True
    while True:
        if not tx_uut.get_status():
            tx_uut.stop()
            break
        else:
            time.sleep(0.2)


def main():
    tx_uut = TxUUT()
    try:
        while True:
            if not tx_uut.get_status():
                tx_uut.stop()
                break
            else:
                time.sleep(0.2)
    except KeyboardInterrupt:
        shutdown(tx_uut)




if __name__ == "__main__":
    main()