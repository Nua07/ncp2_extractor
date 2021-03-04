import os
import struct

psa = b"\x50\x53\x61\x10\x64\x00\x00\x00"
endpsa = b"\x00\x00\x50\x45"

class ncp2():
    def __init__(self):
        self.pos = 0
        self.data = b""
    
    def open(self, filename):
        f = open(filename, "rb")
        self.pos = 0
        self.data = f.read()
        
    def _read_uint_le(self):
        value = struct.unpack("<I", self.data[self.pos:self.pos+4])[0]
        self.pos += 4
        return value
    
    def _read_header(self):
        value = self.data[self.pos:self.pos+32]
        self.pos += 32
        return value
    
    def _check_start_section(self):
        if self.data[self.pos:self.pos+8] == psa:
            self.pos += 8
            return True
        return False
    
    def _check_end_section(self):
        if self.data[self.pos:self.pos+4] == endpsa:
            self.pos += 4
            return True
        return False
    
    def _read_section(self):
        sectionName = self.data[self.pos:self.pos+4]
        self.pos += 4
        
        sectionLength = self._read_uint_le()
        
        sectionData = self.data[self.pos:self.pos+sectionLength]
        self.pos += sectionLength
        
        if not self._check_end_section():
            raise Exception("Invalid Format")
        
        return sectionName, sectionLength, sectionData
    
    def _parse_file_table(self, data):
        file_table = []
        
        ppos = 0
        
        while(ppos < len(data)):
            name = data[ppos:ppos+44]
            ppos += 44
            
            
            start = struct.unpack("<I", data[ppos:ppos+4])[0]
            ppos += 8
            
            
            length = struct.unpack("<I", data[ppos:ppos+4])[0]
            ppos += 12
            
            file_table.append({"name": name.decode().replace("\x00", ""), "start":start, "length": length})
            
        return file_table
    
    def _extract_file_table(self, data, ft):
        for file in ft:
            print(file)
            ff = open(file["name"], "wb")
            
            ff.write(data[file["start"]:file["start"]+file["length"]])
            ff.close()
            
    def extract(self):
        header = self._read_header()
        if header[0:4] != b"NPQF":
            raise Exception("Invalid Header")
        
        while(self.pos < len(self.data)):
            if(self._check_start_section()):
                sectionName, sectionLength, sectionData = self._read_section()
                
                if sectionName == b"INFO":
                    print(sectionData)
                    
                if sectionName == b"FTBL":
                    ft = self._parse_file_table(sectionData)
                
                if sectionName == b"DATA":
                    self._extract_file_table(sectionData, ft)

n = ncp2()
n.open("Alphabet_note.ncp2")
n.extract()
