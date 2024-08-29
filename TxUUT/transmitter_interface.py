from abc import ABC, abstractmethod


class Transmitter(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass


    @abstractmethod
    def transmit(self, freq, power, wave_type, on_off):
        pass



