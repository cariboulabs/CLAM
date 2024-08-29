import os, sys, time
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)
from ControlPC import ControlPC
from tools import print_dict


def shutdown(control_pc: ControlPC):
    if control_pc.unit_status["RxMeas"].operable or control_pc.unit_status["TxUUT"].operable:
        control_pc.broadcast_systems(txt="Close")
    else:
        control_pc.inner_off()
    while True:
        if control_pc.get_status() is False:
            control_pc.close()
            print("\nExiting the CLAM, Goodbye!")
            break
        else:
            time.sleep(0.2)


def run(control_pc: ControlPC):
    freq, power, wave_type = 0, 0, ""
    options = {
        '0': "Exit",
        '1': "Check system status",
        '2': "Change motors angles on TxUUT",
        '3': "Transmit using TxUUT",
        '4': "Stop Transmitting TxUUT",
        '5': "Transmit continuously using both units",
        '6': "Change frequency on RxMeas",
        '7': "Sampling on RxMeas and get RSSI and IQ"
    }
    try:
        while True:
            if control_pc.get_status() is False:
                break
            else:
                print("\nCLAM Menu:")
                print_dict(options)

                choice = input("\nPlease select an option: ")
                # Process the user input
                if choice in options.keys():
                    if choice == '0':
                        shutdown(control_pc)
                    else:
                        if choice == '1':
                            control_pc.broadcast_systems(txt="Ready?")

                        elif choice == '2':
                                if control_pc.unit_status["TxUUT"].operable:
                                    azimuth = float(input("Enter azimuth angle: "))
                                    pitch = float(input("Enter pitch angle: "))
                                    control_pc.move_motors(azimuth, pitch)
                                else:
                                    print("TxUUT is not active")

                        elif choice == '3':
                            if control_pc.unit_status["TxUUT"].operable:
                                freq = float(input("Enter frequency: "))
                                power = float(input("Enter power: "))
                                wave_type = input("Enter wave type: ")
                                control_pc.transmit(freq, power, wave_type, True)
                            else:
                                print("TxUUT is not active")
                                    
                        elif choice == '4':
                            if control_pc.unit_status["TxUUT"].operable:
                                control_pc.transmit(control_pc.curr_freq, control_pc.data["power"], control_pc.data["wave_type"], onoff=False)
                            else:
                                print("TxUUT is not active")
                                
                        elif choice == '5':
                            if control_pc.unit_status["TxUUT"].operable and control_pc.unit_status["RxMeas"].operable:
                                control_pc.continuous_tx_rx()
                            else:
                                print("Problem:\n")
                                print_dict(control_pc.unit_status)

                        elif choice == '6':
                            if control_pc.unit_status["RxMeas"].operable:
                                freq = float(input("Enter frequency: "))
                                control_pc.set_freq(freq=freq)
                            else:
                                print("RxMeas is not active")

                        elif choice == '7':
                            if control_pc.unit_status["RxMeas"].operable:
                                control_pc.sample(True)
                            else:
                                print("RxMeas is not active")
                          
                else:
                    print("\nInvalid option, please try again.") 
                time.sleep(0.4)
    except KeyboardInterrupt:
        shutdown(control_pc)


if __name__ == "__main__":
    controller = ControlPC()
    controller.start()
    run(controller)