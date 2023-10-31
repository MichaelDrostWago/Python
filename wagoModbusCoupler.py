# Module to handle wago 750 modbus coupler
# Author:        Michael Drost
# Version:       1.0
# PythonVersion: 3.7.3
import json
jsonFile    = open('/home/Development/PythonScripts/Modbus/modbusCoupler/Modules.json')
jsonModules = json.load(jsonFile)

class ModbusRegister:
    """Class for configure requested modbus register"""
    def __init__(self, name, length, address):
        self._name       = name
        self._length     = length
        self._address    = address

    @property
    def name(self):
        """get name of the register"""
        return self._name
    
    @property
    def length(self):
        """get length of the register"""
        return self._length
    
    @property
    def address(self):
        """get address of the register"""
        return self._address


class WagoIoModule:
    """Class for Wago IO-Module
       converts the readings from modbus to an python-class
    """
    # local vars
    _process_data = {}
    _moduleData = {'name' : '',
                   'position' : 0,
                   'type' : '',
                   'input_channel' : 0,
                   'output_channel' : 0,}

    def __init__(self, name, position, type, input_channel_count, output_channel_count):
        self._name                  = name
        self._position              = position
        self._type                  = type
        self._input_channel_count   = input_channel_count
        self._output_channel_count  = output_channel_count
        self._process_data          = {'process_data': {}}

    def display_info(self):
        print("Name:", self._name)
        print("Position:", self._position)
        print("Type:", self._type)
        print("Input Channel Count:", self._input_channel_count)
        print("Output Channel Count:", self._output_channel_count)
        print("Process Data:", self._process_data)

    def _addDigitalInputs(self, start_register, number):
        """adding an digital inputs with modbus-address to the processdata"""
        if self._process_data.get('inputs') is None:
           self._process_data['process_data'].update({'inputs': {}})
        for i in range(0, number): 
            self._process_data['process_data']['inputs'][i] = (start_register)+i

    def _addDigitalOutputs(self,start_register, number):
        """adding an digital outputs (coils) with modbus-address to the processdata"""
        if self._process_data.get('outputs') is None:
           self._process_data['process_data'].update({'coils': {}})
        for i in range(0, number): 
            self._process_data['process_data']['coils'][i] = (start_register)+i
     
    def _addInputRegisters(self,start_register, number):
        """adding an input registers with modbus-address to the processdata  """
        if self._process_data.get('input_register') is None:
           self._process_data['process_data'].update({'input_register': {}})
        for i in range(0, number): 
            self._process_data['process_data']['input_register'][i] = (start_register)+i

    def _addHoldingRegisters(self,start_register, number):
        """adding an holding regsiters with modbus-address to the processdata"""     
        if self._process_data.get('holding_register') is None:
           self._process_data['process_data'].update({'holding_register': {}})
        for i in range(0, number): 
            self._process_data['process_data']['holding_register'][i] = (start_register)+i

    # trigger external write of registers
    def writeRegisters(self, start_din, start_dout, start_in, start_out):  
        """write register addresses to this module"""     
        if len(self._type) > 4:
            if self._input_channel_count > 0:
                self._addDigitalInputs(start_din, self._input_channel_count)         
            if self._output_channel_count > 0: 
                self._addDigitalOutputs(start_dout, self._output_channel_count) 
        else:
            if self._input_channel_count > 0:
                self._addInputRegisters(start_in, self._input_channel_count)           
            if self._output_channel_count > 0:
                self._addHoldingRegisters(start_out, self._output_channel_count) 

    @property
    def get_input_channel_size(self):
        """get the number of input channels for this module"""
        return self._input_channel_count

    @property
    def get_output_channel_size(self):
        """get the number of output channels for this module"""
        return self._output_channel_count
    
    @property
    def process_data(self):
        """get the processdata of this module"""
        return self._process_data
    
    @property
    def module_data(self):
        """get whole module information"""
        self._moduleData['name']          = self._name
        self._moduleData['position']      = self._position
        self._moduleData['type']          = self._type
        self._moduleData['input_channel'] = self._input_channel_count
        self._moduleData['output_channel']= self._output_channel_count
        self._moduleData.update({'process_data': {}})
        self._moduleData['process_data'] = self._process_data
        return self._moduleData

    @property
    def get_type(self):
        """get io-type of module"""
        return self._type
    

def getRegisterConfigJson(ioModules, file_path):
    """
    generate json file for the io-config of specific coupler
    ioModule:  list of words from io coupler
    file_path: path of config.json file for the modbus registers"""
    maskDigital = 0x8000
    maskIn      = 0x0001
    maskOut     = 0x0002
    maskSize    = 0x7F00
    actStartDin = 0
    actStartDout= 0
    actStartIn  = 0
    actStartOut = 0
    modules_list = []

    # evaluate modules and generate list of wagoIomodules
    for index, module in enumerate(ioModules): 
        if module == 0:
            continue
        elif not (module & maskDigital):
            try:
                new_module = WagoIoModule('module'+str(index),                   
                                                          index,                                    
                                                          str(module), 
                                                          jsonModules[str(module)]['sizeIn'],
                                                          jsonModules[str(module)]['sizeOut'])
            except:
                continue
        else:
            dataSize = maskSize & module
            if module & maskIn and module & maskOut:
                new_module = WagoIoModule('module'+str(index), 
                                                          index, 
                                                          str(dataSize>>8)+'-CH-DIO 15xx', 
                                                          dataSize>>8,
                                                          dataSize>>8)
        
            elif module & maskOut:
                new_module = WagoIoModule('module'+str(index), 
                                                          index, 
                                                          str(dataSize>>8)+'-CH-DO x5xx', 
                                                          0,
                                                          dataSize>>8)
                
            else:
                new_module = WagoIoModule('module'+str(index), 
                                                          index, 
                                                          str(dataSize>>8)+'-CH-DI x4xx', 
                                                          dataSize>>8,
                                                          0)
    
        modules_list.append(new_module)

    # write json file 
    with open(file_path, "w") as json_file:
         json_file.write('[')   
    for index in range(0, len(modules_list)):
        modules_list[index].writeRegisters(actStartDin,actStartDout,actStartIn,actStartOut)
        if len(modules_list[index].get_type) > 4:
            actStartDin = actStartDin + modules_list[index].get_input_channel_size  
            actStartDout= actStartDout+ modules_list[index].get_output_channel_size
        else:
            actStartIn  = actStartIn + modules_list[index].get_input_channel_size  
            actStartOut = actStartOut+ modules_list[index].get_output_channel_size 
        
        print(modules_list[index].module_data) 
        with open(file_path, "a") as json_file:
            json.dump(modules_list[index].module_data, json_file)

    with open(file_path, "a") as json_file:
         json_file.write(']') 


# standard wago registers

oModules1 = ModbusRegister("first65Module", 65, 0x2030)   
oModules2 = ModbusRegister("first65Module", 65, 0x2030)   
oModules3 = ModbusRegister("first65Module", 65, 0x2030)   
oWatchdog = ModbusRegister("first65Module", 65, 0x2030)   

