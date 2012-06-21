import ctypes
from struct import  Struct

try: import elementtree.ElementTree as etree
except ImportError:
    try: import cElementTree as etree
    except ImportError:
        try: import lxml.etree as etree
        except ImportError:
            import xml.etree.ElementTree as etree

class LaspyException(Exception):
    """LaspyException: indicates a laspy related error."""
    pass

fmtLen = {"<L":4, "<H":2, "<B":1, "<f":4, "<s":1, "<d":8, "<Q":8}
LEfmt = {ctypes.c_long:"<L", ctypes.c_ushort:"<H", ctypes.c_ubyte:"<B"
        ,ctypes.c_float:"<f", ctypes.c_char:"<s", ctypes.c_double:"<d", ctypes.c_ulonglong:"<Q"}
npFmt = {"<L":"i4", "<H":"u2", "<B":"u1", "<f":"f4", "<s":"s1", "<d":"f8", "<Q":"u8"}
defaults = {"<L":0, "<H":0, "<B": "0", "<f":0.0, "<s":" ", "<d":0.0, "<Q":0}

class Spec():
    '''Holds information about how to read and write a particular field. 
        These are usually created by :obj:`laspy.util.Format` objects.'''
    def __init__(self,name,offs, fmt, num, pack = False,ltl_endian = True, overwritable = True, idx = False):
        '''Build the spec instance.'''
        if ltl_endian:
            self.name = name
            self.offs = offs
            self.Format = fmt
            self.fmt = LEfmt[fmt]
            self.length = fmtLen[self.fmt]
            self.num = num
            self.pack = pack
            self.np_fmt = npFmt[self.fmt]
            if self.num == 1 or type(defaults[self.fmt])== str:
                self.default = defaults[self.fmt]*self.num
            else:
                self.default = [defaults[self.fmt]]*self.num
            self.overwritable = overwritable
            self.idx = idx
        else:
            raise(LaspyException("Big endian files are not currently supported."))
    def etree(self):
        spec = etree.Element("spec")
        name = etree.SubElement(spec, "name")
        name.text = self.name
        fmt = etree.SubElement(spec, "ctypes_format") 
        fmt.text = str(self.Format).split("'")[1] 
        num = etree.SubElement(spec, "number")
        num.text = str(self.num)
        return(spec)
    
    def xml(self):
        return(etree.tostring(self.etree()))

### Note: ctypes formats may behave differently across platforms. 
### Those specified here follow the bytesize convention given in the
### LAS specification. 
class Format():
    '''A Format instance consists of a set of 
    :obj:`laspy.util.Spec` objects, as well as some calculated attributes 
    and summary methods. For example, Format builds the *pt_fmt_long* 
    attribute, which provides a :obj:`struct` compatable format string to 
    pack and unpack an entire formatted object (:obj:`laspy.util.Point` in particular) in its entireity. Format additionally
    supports the :obj:`laspy.util.Format.xml` and :obj:`laspy.util.Format.etree`
    methods for interrogating the members of a format. This can be useful in finding out
    what dimensions are available from a given point format, among other things.''' 
    def __init__(self, fmt, overwritable = False):
        '''Build the :obj:`laspy.util.Format` instance. '''
        fmt = str(fmt)
        self.fmt = fmt
        self._etree = etree.Element("Format")
        self.specs = []
        self.rec_len = 0
        self.pt_fmt_long = "<"
        if not (fmt in ("0", "1", "2", "3", "4", "5", "VLR", "h1.0", "h1.1", "h1.2", "h1.3")):
            raise LaspyException("Invalid format: " + str(fmt))
        ## Point Fields
        if fmt in ("0", "1", "2", "3", "4", "5"):
            self.format_type = "point format = " + fmt
            self.add("X", ctypes.c_long, 1)
            self.add("Y", ctypes.c_long, 1)
            self.add("Z", ctypes.c_long, 1)
            self.add("intensity",  ctypes.c_ushort, 1)
            self.add("flag_byte", ctypes.c_ubyte, 1)
            self.add("raw_classification", ctypes.c_ubyte, 1)
            self.add("scan_angle_rank", ctypes.c_ubyte, 1)
            self.add("user_data",  ctypes.c_ubyte, 1)
            self.add("pt_src_id",  ctypes.c_ushort, 1)
        if fmt in ("1", "3", "4", "5"):
            self.add("gps_time", ctypes.c_double, 1)
        if fmt in ("3", "5"):
            self.add("red", ctypes.c_ushort, 1)
            self.add("green", ctypes.c_ushort, 1)
            self.add("blue" , ctypes.c_ushort,1)
        elif fmt == "2":
            self.add("red", ctypes.c_ushort, 1)
            self.add("green", ctypes.c_ushort, 1)
            self.add("blue" , ctypes.c_ushort,1)
        if fmt == "4":
            self.add("wave_packet_descp_idx", ctypes.c_ubyte, 1)
            self.add("byte_offset_to_wavefm_data", ctypes.c_ulonglong,1)
            self.add("wavefm_pkt_size",ctypes.c_long, 1)
            self.add("return_pt_wavefm_loc",  ctypes.c_float, 1)
            self.add("x_t", ctypes.c_float, 1)
            self.add("y_t", ctypes.c_float, 1)           
            self.add("z_t", ctypes.c_float, 1)
        elif fmt == "5":
            self.add("wave_packet_descp_idx", ctypes.c_ubyte, 1)
            self.add("byte_offset_to_wavefm_data", ctypes.c_ulonglong,1)
            self.add("wavefm_pkt_size", ctypes.c_long, 1)
            self.add("return_pt_wavefm_loc", ctypes.c_float, 1)
            self.add("x_t", ctypes.c_float, 1)
            self.add("y_t", ctypes.c_float, 1)          
            self.add("z_t", ctypes.c_float, 1)
        ## VLR Fields
        if fmt == "VLR":
            self.format_type = "VLR"
            self.add("reserved", ctypes.c_ushort, 1)
            self.add("user_id", ctypes.c_char, 16)
            self.add("record_id", ctypes.c_ushort, 1)
            self.add("rec_len_after_header", ctypes.c_ushort, 1)
            self.add("description", ctypes.c_char, 32, pack = True)
        
        ## Header Fields
        if fmt[0] == "h": 
            self.format_type = "header version = " + fmt[1:]
            self.add("file_sig",ctypes.c_char, 4, pack = True, overwritable=overwritable)
            self.add("file_src", ctypes.c_ushort, 1)
            self.add("global_encoding",ctypes.c_ushort, 1)
            self.add("proj_id_1",ctypes.c_long, 1)
            self.add("proj_id_2", ctypes.c_ushort, 1)
            self.add("proj_id_3", ctypes.c_ushort, 1)
            self.add("proj_id_4", ctypes.c_ubyte, 8)
            self.add("version_major", ctypes.c_ubyte, 1, overwritable=overwritable)
            self.add("version_minor", ctypes.c_ubyte, 1, overwritable=overwritable)
            self.add("sys_id", ctypes.c_char, 32, pack=True)
            self.add("gen_soft",  ctypes.c_char, 32, pack = True)
            self.add("created_day", ctypes.c_ushort, 1)
            self.add("created_year", ctypes.c_ushort,1)
            self.add("header_size", ctypes.c_ushort, 1, overwritable=overwritable)
            self.add("offset_to_point_data", ctypes.c_long, 1)
            self.add("num_variable_len_recs",  ctypes.c_long, 1)
            self.add("pt_dat_format_id",  ctypes.c_ubyte, 1, overwritable=overwritable)
            self.add("pt_dat_rec_len",  ctypes.c_ushort, 1)
            self.add("num_pt_recs", ctypes.c_long, 1)         
            if fmt == "h1.3":
                self.add("num_pts_by_return",  ctypes.c_long, 7)
                self.add("x_scale", ctypes.c_double, 1)
                self.add("y_scale", ctypes.c_double, 1)
                self.add("z_scale", ctypes.c_double, 1)
                self.add("x_offset", ctypes.c_double, 1)
                self.add("y_offset", ctypes.c_double, 1)
                self.add("z_offset", ctypes.c_double, 1) 
                self.add("x_max", ctypes.c_double, 1)
                self.add("x_min", ctypes.c_double, 1)
                self.add("y_max",ctypes.c_double, 1)
                self.add("y_min",ctypes.c_double, 1)
                self.add("z_max", ctypes.c_double, 1)
                self.add("z_min", ctypes.c_double, 1)
            elif fmt in ("h1.0", "h1.1", "h1.2"):
                self.add("num_pts_by_return", ctypes.c_long, 5)
                self.add("x_scale", ctypes.c_double, 1)
                self.add("y_scale", ctypes.c_double, 1)
                self.add("z_scale", ctypes.c_double, 1)
                self.add("x_offset", ctypes.c_double, 1)
                self.add("y_offset", ctypes.c_double, 1)
                self.add("z_offset", ctypes.c_double, 1) 
                self.add("x_max", ctypes.c_double, 1)
                self.add("x_min", ctypes.c_double, 1)
                self.add("y_max", ctypes.c_double, 1)
                self.add("y_min", ctypes.c_double, 1)
                self.add("z_max", ctypes.c_double, 1)
                self.add("z_min", ctypes.c_double, 1)

        self.lookup = {}
        for spec in self.specs:
            self.lookup[spec.name] = spec
        self.packer = Struct(self.pt_fmt_long)
        
    def add(self, name, fmt, num, pack = False, overwritable = True):
        if len(self.specs) == 0:
            offs = 0
        else:
            last = self.specs[-1]
            offs = last.offs + last.num*fmtLen[last.fmt]
        self.rec_len += num*fmtLen[LEfmt[fmt]]
        self.specs.append(Spec(name, offs, fmt, num, pack, overwritable =  overwritable, idx = len(self.specs)))
        self.pt_fmt_long += LEfmt[fmt][1]
        self._etree.append(self.specs[-1].etree()) 
    def xml(self):
        '''Return an XML Formatted string, describing all of the :obj:`laspy.util.Spec` objects belonging to the Format.'''
        return(etree.tostring(self._etree)) 
    def etree(self):
        '''Return an XML etree object, describing all of the :obj:`laspy.util.Spec` objects belonging to the Format.'''
        return(self._etree)

    def __getitem__(self, index):
        '''Provide slicing functionality: return specs[index]'''
        try:
            index.stop
        except AttributeError:
            return self.specs[index]
        if index.step:
            step = index.step
        else:
            step = 1
        return(self.specs[index.start:index.stop:step])
    
    def __iter__(self):
        '''Provide iterating functionality for spec in specs'''
        for item in self.specs:
            yield item

class Point():
    '''A data structure for reading and storing point data. The lastest version 
    of laspy's api does not use the Point class' reading capabilities, and it is important
    to not that reading and writing points does not require a list of point instances. 
    See :obj:`laspy.file.points` for more details'''
    def __init__(self, reader, bytestr = False, unpacked_list = False, nice = False):
        '''Build a point instance, either by being given a reader which can provide data or by a list of unpacked attributes.'''
        self.reader = reader 
        self.packer = self.reader.point_format.packer
        if bytestr != False:
            self.unpacked = self.packer.unpack(bytestr) 
        elif unpacked_list != False:
            self.unpacked = unpacked_list
        else:
            raise LaspyException("No byte string or attribute list supplied for point.")
        if nice:
            self.make_nice()
    def make_nice(self):
        '''Turn a point instance with the bare essentials (an unpacked list of data)
        into a fully populated point. Add all the named attributes it possesses, including binary fields.
        '''
        i = 0
        for dim in self.reader.point_format.specs: 
                self.__dict__[dim.name] = self.unpacked[i]
                i += 1

        bstr = self.reader.binary_str(self.flag_byte)
        self.return_num = self.reader.packed_str(bstr[0:3])
        self.num_returns = self.reader.packed_str(bstr[3:6])
        self.scan_dir_flag = self.reader.packed_str(bstr[6])
        self.edge_flight_line = self.reader.packed_str(bstr[7])

        bstr = self.reader.binary_str(self.raw_classification)
        self.classification = self.reader.packed_str(bstr[0:5])
        self.synthetic = self.reader.packed_str(bstr[5])
        self.key_point = self.reader.packed_str(bstr[6])
        self.withheld = self.reader.packed_str(bstr[7])       


    def pack(self):
        '''Return a binary string representing the point data. Slower than 
        :obj:`numpy.array.tostring`, which is used by :obj:`laspy.base.DataProvider`.'''
        return(self.packer.pack(*self.unpacked))
        
    


