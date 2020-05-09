from network import LoRa
from machine import I2C
import machine
import socket,pycom,ubinascii,struct,time

pycom.heartbeat(False)

# Initialise LoRa in LORAWAN mode, Please pick the region that matches where you are using the device:
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.IN865,device_class=LoRa.CLASS_A)

i2c = I2C(0, I2C.MASTER)
lora.nvram_restore()

if not lora.has_joined():
    dev_addr = struct.unpack(">l", ubinascii.unhexlify('26011F4F'))[0]
    nwk_swkey = ubinascii.unhexlify('4F9D9FF41CBD9C04D5C4E34C36254003')
    app_swkey = ubinascii.unhexlify('65F3876AEB66DB36EE3463AD51C8395F')

    lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey)) # Reties every 15 sec until join accepted

    while not lora.has_joined():
        pycom.rgbled(0xff0000)
        time.sleep(2.5)

pycom.rgbled(0x00ff00)


lora_socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# (waits for the data to be sent and for the 2 receive windows to expire)
lora_socket.setblocking(True)
data = i2c.readfrom_mem(0x5c, 0x00, 5)

lora_socket.send(data)
lora_socket.setblocking(False)

# get any data received (if any...)
# data = lora_socket.recv(64)

lora_socket.close()
pycom.heartbeat(True)
time.sleep(10) #Delay to help if you want to updat the scripts as this is not possible if the controller gets into deepsleep
# lte = LTE()
# lte.deinit(detach=True, reset = False)
lora.nvram_save()
machine.deepsleep(900000)