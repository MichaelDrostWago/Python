# Script for Reading Modbus Coupler Config And Cyclic Data
# Write Config to JSON
# Author:        Michael Drost
# Version:       1.0
# PythonVersion: 3.7.3


from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder,BinaryPayloadDecoder
from pymodbus.constants import Endian
import wagoModbusCoupler as wagoModbusCoupler
import json

# PARAMETER 
serverIP    = "192.168.2.139"
outputFile  = '/home/Development/PythonScripts/Modbus/modbusCoupler/coupler_config.json'



# PROGRAM
client = ModbusTcpClient(serverIP)
client.connect()


def checkByteOrder():
    """check byte order of Wago Modbus device"""
    #Check Byte Order LE/BE
    Constantregister = 0x2002
    ByteOrder = 0x1234
    result = client.read_input_registers(Constantregister)

    if result.registers[0] == ByteOrder:
        print("Byte Order is Intel Format and Correct!")
    else:
        print("Motorola Format!! not Correct")
def writeDecoderToList(decoder, num_values):
    """write date from modbus registers to list of ioModules"""
    ioModules = []

    for i in range(1, num_values + 1):
        word = decoder.decode_16bit_uint() 
        ioModules.append(word)
    return ioModules


# MAIN
if __name__ == "__main__":
    checkByteOrder()
    try:
        result = client.read_input_registers(wagoModbusCoupler.oModules1.address, wagoModbusCoupler.oModules1.length)

        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Little)

        wagoModbusCoupler.getRegisterConfigJson(writeDecoderToList(decoder, wagoModbusCoupler.oModules1.length), outputFile)

    except KeyboardInterrupt:
        pass

    client.close()