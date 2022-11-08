import os
import struct

psa = b"\x00\x00\x00\x00\x50\x53\x61\x10"
endpsa = b"\x00\x00\x50\x45\x50\x53\x61\x10"
info = b"\x64\x00\x00\x00\x49\x4E\x46\x4F"
ftbl = b'd\x00\x00\x00FTBL'
data = b'd\x00\x00\x00DATA'
endfile =b'\x00\x00PE'

class ncp2():
    def __init__(self):
        self.pos = 0
        self.data = b""

    def open(self, filename):
        f = open(filename, "rb")
        self.pos = 0
        self.data = f.read()

    def _read_uint_le(self):
        value = struct.unpack("<I", self.data[self.pos:self.pos + 4])[0]
        self.pos += 4
        return value

    def _read_header(self):
        value = self.data[self.pos:self.pos + 32]
        self.pos += 32
        return value

    def _check_start_section(self):
        print('_check_start_section')
        curdata = self.data[self.pos:self.pos + 8]
        print(curdata)
        if curdata == psa:
            self.pos += 8
            return True
        elif curdata == ftbl:
            return True
        elif curdata == data:
            return True
        return False

    def _check_end_section(self):
        print('_check_end_section')
        curdata = self.data[self.pos:self.pos + 8]
        print(curdata)
        if curdata == endpsa:
            self.pos += 8
            return True
        elif curdata == endfile:
            return True
        return False

    @property
    def _read_section(self):
        print('_read_section')
        sectionName = self.data[self.pos:self.pos + 8]
        self.pos += 8
        print(sectionName)

        sectionLength = self._read_uint_le()
        print(sectionLength)

        sectionData = self.data[self.pos:self.pos + sectionLength]
        self.pos += sectionLength
        #print(sectionData)

        if not self._check_end_section():
            raise Exception("Invalid Format")

        return sectionName, sectionLength, sectionData

    def _parse_file_table(self, data):
        file_table = []

        ppos = 0

        while (ppos < len(data)):
            name = data[ppos:ppos + 44]
            ppos += 44

            start = struct.unpack("<I", data[ppos:ppos + 4])[0]
            ppos += 8

            length = struct.unpack("<I", data[ppos:ppos + 4])[0]
            ppos += 12

            file_table.append(dict(name=name.decode(encoding='cp949').replace("\x00", ""), start=start, length=length))

        return file_table

    def _extract_file_table(self, data, ft):
        for file in ft:
            print(file)
            ff = open(file["name"], "wb")

            ff.write(data[file["start"]:file["start"] + file["length"]])
            ff.close()

    def extract(self):
        header = self._read_header()
        if header[0:8] != b"RIFFNPQF":
            raise Exception("Invalid Header")

        while (self.pos < len(self.data)):
            if (self._check_start_section()):
                sectionName, sectionLength, sectionData = self._read_section

                if sectionName == info:
                    print('INFO')
                    print(sectionData)

                if sectionName == ftbl:
                    print('FTBL')
                    ft = self._parse_file_table(sectionData)

                if sectionName == data:
                    print("DATA")
                    self._extract_file_table(sectionData, ft)


n = ncp2()
n.open("Yundubi_BB_1.ncp2")
n.extract()
