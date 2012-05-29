"""
/******************************************************************************
 * $Id$
 *
 * Project:  libLAS - http://liblas.org - A BSD library for LAS format data.
 * Purpose:  Python LASHeader implementation

 * Author:   Howard Butler, hobu.inc@gmail.com
 *
 ******************************************************************************
 * Copyright (c) 2009, Howard Butler
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following
 * conditions are met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in
 *       the documentation and/or other materials provided
 *       with the distribution.
 *     * Neither the name of the Martin Isenburg or Iowa Department
 *       of Natural Resources nor the names of its contributors may be
 *       used to endorse or promote products derived from this software
 *       without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
 * OF SUCH DAMAGE.
 ****************************************************************************/
 """
import datetime

def leap_year(year):
    if (year % 400) == 0:
        return True
    elif (year % 100) == 0:
        return True
    elif (year % 4) == 0:
        return False
    return False

## NOTE: set_attr methods are currently not implemented. These methods need
## to update the file using reader/mmap. 
class LaspyHeaderException(Exception):
    pass

class Header(object):
    def __init__(self,reader, copy=False):
        self.Format = reader.header_format        
        self.reader = reader
        for dim in self.Format.dimensions:
            self.__dict__[dim.name] = self.read_words(dim.offs, dim.fmt,dim.num, dim.length, dim.compress)
    
    def read_words(self, offs, fmt,num, length, compress):
        self.reader.seek(offs,rel=False)
        out = self.reader._ReadWords(fmt, num, length)
        if compress:
            return("".join(out))
        return(out)
        
    def get_filesignature(self):
        """Returns the file signature for the file. It should always be
        LASF"""
        return self.FileSig
    doc = """The file signature for the file.  It should always be 'LASF'

    From the specification_:
        The file signature must contain the four characters "LASF", and it is
        required by the LAS specification. These four characters can be
        checked by user software as a quick look initial determination of file
        type.
    """
    file_signature = property(get_filesignature, None, None, doc)

    def get_filesourceid(self):
        return self.FileSrc

    def set_filesourceid(self, value):
        return 
    doc = """File Source ID for the file.

    From the specification_:
        This field should be set to a value between 1 and 65,535, inclusive. A
        value of zero (0) is interpreted to mean that an ID has not been
        assigned. In this case, processing software is free to assign any
        valid number. Note that this scheme allows a LIDAR project to contain
        up to 65,535 unique sources. A source can be considered an original
        flight line or it can be the result of merge and/or extract
        operations.
    """
    filesource_id = property(get_filesourceid, set_filesourceid, None, doc)
    file_source_id = filesource_id

    def get_global_encoding(self):
        return self.GlobalEncoding

    def set_global_encoding(self, value):
        return
    doc = """Global encoding for the file.

    From the specification_:

        This is a bit field used to indicate certain global properties about
        the file. In LAS 1.2 (the version in which this field was introduced),
        only the low bit is defined (this is the bit, that if set, would have
        the unsigned integer yield a value of 1). This bit field is defined
        as:

        .. csv-table:: Global Encoding - Bit Field Encoding
            :header: "Bits", "Field Name", "Description"
            :widths: 10, 20, 60

            0, "GPS Time Type", "The meaning of GPS Time in the Point Records
            0 (not set) -> GPS time in the point record fields is GPS Week
            Time (the same as previous versions of LAS) 1 (set) -> GPS Time is
            standard GPS Time (satellite GPS Time) minus 1 x 10^9 (Adjusted
            Standard GPS Time). The offset moves the time back to near zero to
            improve floating point resolution."
            1, "Waveform Data Packets Internal", "If this bit is set, the
            waveform data packets are located within this file (note that this
            bit is mutually exclusive with bit 2)"
            2, "Waveform Data Packets External", "If this bit is set, the
            waveform data packets are located external to this file in an
            auxiliary file with the same base name as this file and the
            extension \".wdp\". (note that this bit is mutually exclusive with
            bit 1)"
            3, "Return numbers have been synthetically generated", "If set,
            the point return numbers in the Point Data Records have been
            synthetically generated. This could be the case, for example, when
            a composite file is created by combining a First Return File and a
            Last Return File. In this case, first return data will be labeled
            \"1 of 2\" and second return data will be labeled \"2 of 2\""
            4:15, "Reserved", "Must be set to zero"

    """
    global_encoding = property(get_global_encoding,
                               set_global_encoding,
                               None,
                               doc)
    encoding = global_encoding

    def get_projectid(self):
        """Returns the ProjectID/GUID for the file.  \
        libLAS does not currently support setting this value from Python"""
        return(str(self.ProjID1) + str(self.ProjID2) + str(self.ProjID3) + str(self.ProjID4))
    doc = """ProjectID for the file.  \
        libLAS does not currently support setting this value from Python, as
        it is the same as :obj:`liblas.header.Header.guid`. Use that to
        manipulate the ProjectID for the file.

        From the specification_:
            The four fields that comprise a complete Globally Unique Identifier
            (GUID) are now reserved for use as a Project Identifier (Project
            ID). The field remains optional. The time of assignment of the
            Project ID is at the discretion of processing software. The
            Project ID should be the same for all files that are associated
            with a unique project. By assigning a Project ID and using a File
            Source ID (defined above) every file within a project and every
            point within a file can be uniquely identified, globally.

        """
    project_id = property(get_projectid, None, None, doc)

    def get_guid(self):
        """Returns the GUID for the file as a :class:`liblas.guid.GUID`
        instance"""
        return self.get_projectid() 

    def set_guid(self, value):
        """Sets the GUID for the file. It must be a :class:`liblas.guid.GUID`
        instance"""
        return
    doc = """The GUID/:obj:`liblas.header.Header.project_id` for the file."""
    guid = property(get_guid, set_guid, None, doc)

    def get_majorversion(self):
        """Returns the major version for the file. Expect this value to always
        be 1"""
        return self.VersionMajor

    def set_majorversion(self, value):
        """Sets the major version for the file. Only the value 1 is accepted
        at this time"""
        return
    doc = """Major version number for the file.  For all practical purposes, \
    this is always '1'"""
    major_version = property(get_majorversion, set_majorversion, None, doc)
    version_major = major_version
    major = major_version

    def get_minorversion(self):
        """Returns the minor version of the file. Expect this value to always
        be 0, 1, or 2"""
        return self.VersionMinor

    def set_minorversion(self, value):
        """Sets the minor version of the file. The value should be 0 for 1.0
        LAS files, 1 for 1.1 LAS files ..."""
        return 
    doc = """Minor version for the file. [0, 1, 2] are currently supported."""
    minor_version = property(get_minorversion, set_minorversion, None, doc)
    version_minor = minor_version
    minor = minor_version

    def set_version(self, value):
        major, minor = value.split('.')
        self.major_version = int(major)
        self.minor_version = int(minor)

    def get_version(self):
        major = self.major_version
        minor = self.minor_version
        return '%d.%d' % (major, minor)
    doc = """The version as a dotted string for the file (ie, '1.0', '1.1',
    etc)"""
    version = property(get_version, set_version, None, doc)

    def get_systemid(self):
        """Returns the system identifier specified in the file"""
        return self.SysId

    def set_systemid(self, value):
        """Sets the system identifier. The value is truncated to 31
        characters"""
        return
    doc = """The system identifier. The value is truncated to 31 characters and
            defaults to 'libLAS'

        :arg value: a string that will automatically be truncated to 31 \
        characters
        :type value: string

        From the specification_:

            .. csv-table:: System Identifier
                :header: "Generating Agent", "System ID"
                :widths: 40, 60

                "Hardware system", "String identifying hardware (e.g. \"ALTM
                1210\" or \"ALS50\""
                "Merge of one or more files","MERGE"
                "Modification of a single file","MODIFICATION"
                "Extraction from one or more files", "EXTRACTION"
                "Reprojection, rescaling, warping, etc.","TRANSFORMATION"
                "Some other operation","\"OTHER\" or a string up to 32
                characters identifying the operation"

        >>> h.system_id
        ''
        >>> h.system_id = 'MODIFICATION'
        >>> h.system_id
        'MODIFICATION'
    """
    system_id = property(get_systemid, set_systemid, None, doc)

    def get_softwareid(self):
        """Returns the software identifier specified in the file"""
        return self.GenSoft

    def set_softwareid(self, value):
        """Sets the software identifier.
        """
        return 
    doc = """The software identifier. The value is truncated to 31 characters
    and defaults to 'libLAS 1.LASVERSION' (ie, libLAS 1.6 for the 1.6
    release)

        :arg value: a string that will automatically be truncated to 31 \
        characters
        :type value: string

        From the specification_:
            This information is ASCII data describing the generating software
            itself. This field provides a mechanism for specifying which
            generating software package and version was used during LAS file
            creation (e.g. "TerraScan V-10.8", "REALM V-4.2" and etc.). If the
            character data is less than 32 characters, the remaining data must
            be null.

        >>> h.software_id
        'libLAS 1.0'
        >>> h.software_id = 'hobu'
        >>> h.software_id
        'hobu'
        >>> h.software_id = 'hobu'*9
        >>> h.software_id
        'hobuhobuhobuhobuhobuhobuhobuhob'
        """
    software_id = property(get_softwareid, set_softwareid, None, doc)

    def get_date(self):
        """Return the header's date as a datetime.datetime. If no date is set
        in the header, None is returned.

        Note that dates in LAS headers are not transitive because the header
        only stores the year and the day number.
        """
        day = self.CreatedDay
        year = self.CreatedYear
        if year == 0 and day == 0:
            return None
        if not leap_year(year):
            return datetime.datetime(year, 1, 1) + datetime.timedelta(day)
        else:
            return datetime.datetime(year, 1, 1) + datetime.timedelta(day - 1)

    def set_date(self, value=datetime.datetime.now()):
        """Set the header's date from a datetime.datetime instance.
        """
        delta = value - datetime.datetime(value.year, 1, 1)
        if not leap_year(value.year):
            pass
            #core.las.LASHeader_SetCreationDOY(self.handle, delta.days)
        else:
            pass
            #core.las.LASHeader_SetCreationDOY(self.handle, delta.days + 1)
        #core.las.LASHeader_SetCreationYear(self.handle, value.year)
        return

    doc = """The header's date from a :class:`datetime.datetime` instance.

        :arg value: :class:`datetime.datetime` instance or none to use the \
        current time


        >>> t = datetime.datetime(2008,3,19)
        >>> hdr.date = t
        >>> hdr.date
        datetime.datetime(2008, 3, 19, 0, 0)

        .. note::
            LAS files do not support storing full datetimes in their headers,
            only the year and the day number. The conversion is handled for
            you if you use :class:`datetime.datetime` instances, however.
        """
    date = property(get_date, set_date, None, doc)

    def get_headersize(self):
        """Return the size of the header block of the LAS file in bytes.

        Should not be needed in Python land
        """
        return self.HeaderSize 
    doc = """The number of bytes that the header contains. For libLAS, this is
    always 227, and it is not configurable."""
    header_size = property(get_headersize, None, None, doc)
    header_length = header_size

    def get_dataoffset(self):
        """Returns the location in bytes of where the data block of the LAS
        file starts"""
        return self.OffsetToPointData

    def set_dataoffset(self, value):
        """Sets the data offset

        Any space between this value and the end of the VLRs will be written
        with 0's
        """
        return
    doc = """The number of bytes of offset between the end of the header and
    the start of the point data in the file. Set this to a large value if you
    plan to include many :obj:`liblas.vlr.VLR`'s to the file.

    .. note::
        libLAS will manage this value for you as you add or remove VLRs or
        :class:`liblas.srs.SRS` instances to the header. Make sure to adjust
        your header information before opening a new file to write, as that is
        when the header's VLRs are written to the file, and they cannot be
        adjusted after that.
    """
    data_offset = property(get_dataoffset, set_dataoffset, None, doc)

    def get_padding(self):
        """Returns number of bytes between the end of the VLRs and the 
           beginning of the point data."""
        return self.Reader.get_padding() 

    def set_padding(self, value):
        """Sets the header's padding.

        """
        return
    doc = """The number of bytes between the end of the VLRs and the 
    beginning of the point data.
    """
    padding = property(get_padding, set_padding, None, doc)

    def get_recordscount(self):
        return Reader.get_recordscount()
    doc = """Returns the number of user-defined header records in the header.
    libLAS will manage this value you for you as you add new
    :class:`liblas.srs.SRS` or :class:`liblas.vlr.VLR` instances to the
    header.
    """
    records_count = property(get_recordscount, None, None, doc)
    num_vlrs = records_count

    def get_dataformatid(self):
        """The point format value as an integer
        """
        return self.PtDatFormatId 

    def set_dataformatid(self, value):
        if value not in range(6):
            raise LaspyHeaderException("Format ID must be 3, 2, 1, or 0")
        return 
    doc = """The point format as an integer. See the specification_ for more
    detail.

        It can be 5, 4, 3, 2, 1, or 0.

        .. note::
            Use :obj:`liblas.schema.Schema` and set the
            :obj:`liblas.header.Header.schema` object instead of using the
            dataformat_id directly. Otherwise, you will have to account for
            the :obj:`liblas.header.Header.data_record_length`.
        """
    dataformat_id = property(get_dataformatid, set_dataformatid, None, doc)
    data_format_id = dataformat_id

    def get_datarecordlength(self):
        lenDict = {0:20,1:28,2:26,3:34,4:57,5:63}
        return lenDict[self.PtDatFormatID] 

    doc = """The length in bytes of the point format. Use
    :class:`liblas.schema.Schema` and \ the :obj:`liblas.header.Header.schema`
    instead of manipulating this directly"""
    data_record_length = property(get_datarecordlength,
                                  None,
                                  None,
                                  doc)

    ## SCHEMA NOT IMPLEMENTED
    def get_schema(self):
        return
        
    def set_schema(self, value):
        return 
    doc = """The :class:`liblas.schmea.Schema` for this file

    Use the schema to set whether or not color or time should be stored
    on the points:

    >>> h = liblas.header.Header()
    >>> f = liblas.schema.Schema()
    >>> f.time = True
    >>> f.color = True
    >>> h.schema = f
    >>> h.schema.color
    True
    >>> h.schema.time
    True
    >>> h.schema.size
    34
    >>> h.data_record_length
    34

    The following example demonstrates how to make a point schema that does
    not store color or time, but also provides 22 extra bytes to store
    :obj:`liblas.point.Point.data`

    >>> h = liblas.header.Header()
    >>> h.schema
    <liblas.schema.Schema object at 0x100779f90>
    >>> h.schema.time
    False
    >>> h.schema.color
    False
    >>> h.schema.size
    20
    >>> f = h.schema
    >>> f.size = 42
    >>> f.size
    42
    >>> f.color
    False
    >>> f.time
    False
    >>> h.schema = f
    >>> h.schema.size
    42
    """
    schema = property(get_schema, set_schema, None, doc)

    ## COMPRESSION NOT IMPLEMENTED
    def get_compressed(self):
        #return bool(core.las.LASHeader_Compressed(self.handle))
        return

    def set_compressed(self, value):
        #return core.las.LASHeader_SetCompressed(self.handle, value)
        return
    doc = """Controls compression for this file.

    If True, the file is compressed with lasZIP compression and will
    be written with lasZIP compression.  If False, the file is not
    compressed.
    """

    compressed = property(get_compressed, set_compressed, None, doc)

    def get_pointrecordscount(self):
        """Returns the expected number of point records in the file.

        .. note::
            This value can be grossly out of sync with the actual number of
            points in the file, because some some softwares are not careful to
            keep it up-to-date. If libLAS detects a case where it is not
            properly written, an exception will be thrown.
        """
        return self.Reader.get_pointrecordscount()

    def set_pointrecordscount(self, value):
        """Sets the number of point records expected in the file.

        .. note::
            Don't use this unless you have a damn good reason to. As you write
            points to a file, libLAS is going to keep this up-to-date for you
            and write it back into the header of the file once the file is
            closed after writing data.
        """
        return
    set_count = set_pointrecordscount
    get_count = get_pointrecordscount
    point_records_count = property(get_pointrecordscount,
                                   set_pointrecordscount)
    count = point_records_count 

    __len__ = get_pointrecordscount

    def get_pointrecordsbyreturncount(self):
        """Gets the histogram of point records by return number for returns
        0...8

        >>> h.point_return_count
        [0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L]

        """
        return self.NumPtsByReturn   

    def set_pointrecordsbyreturncount(self, value):
        """Sets the histogram of point records by return number from a list of
        returns 0..8

        >>> l = [1341235L, 3412341222L, 0L, 0L, 4321L, 0L, 0L, 0L]
        >>> h.point_return_count = l
        >>> h.point_return_count
        [1341235L, 3412341222L, 0L, 0L, 4321L, 0L, 0L, 0L]

        """
        return  
      
    
    doc = """The histogram of point records by return number for returns 0...8

        .. note::
            libLAS does not manage these values automatically for you. You
            must cumulate and generate the histogram manually if you wish to
            keep these data up-to-date with what actually exists in the file.

        >>> hdr.point_return_count
        [0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L]
        >>> l = [1341235L, 3412341222L, 0L, 0L, 4321L, 0L, 0L, 0L]
        >>> hdr.point_return_count = l
        >>> hdr.point_return_count
        [1341235L, 3412341222L, 0L, 0L, 4321L, 0L, 0L, 0L]


    """
    point_return_count = property(get_pointrecordsbyreturncount,
                                  set_pointrecordsbyreturncount,
                                  None,
                                  doc)
    return_count = point_return_count

    def get_scale(self):
        """Gets the scale factors in [x, y, z] for the point data.

        .. note::
            libLAS uses this header value when reading/writing raw point data
            to the file. If you change it in the middle of writing data,
            expect the unexpected.

        >>> h.scale
        [0.01, 0.01, 0.01]
        """
        return [self.XScale, self.YScale, self.ZScale]

    def set_scale(self, value):
        """Sets the scale factors in [x, y, z] for the point data.

        >>> h.scale = [0.5, 0.5, 0.001]
        >>> h.scale
        [0.5, 0.5, 0.001]
        """
        return
    doc = """The scale factors in [x, y, z] for the point data.  libLAS uses \
        the scale factors plus the :obj:`liblas.header.Header.offset` values
        to store the point coordinates as integers in the file.

        From the specification_:
            The scale factor fields contain a double floating point value that
            is used to scale the corresponding X, Y, and Z long values within
            the point records. The corresponding X, Y, and Z scale factor must
            be multiplied by the X, Y, or Z point record value to get the
            actual X, Y, or Z coordinate. For example, if the X, Y, and Z
            coordinates are intended to have two decimal point values, then
            each scale factor will contain the number 0.01

        Coordinates are calculated using the following formula(s):
            * x = (x_int * x_scale) + x_offset
            * y = (y_int * y_scale) + y_offset
            * z = (z_int * z_scale) + z_offset

        .. note::
            libLAS uses this header value when reading/writing raw point data
            to the file. If you change it in the middle of writing data,
            expect the unexpected.


        >>> hdr.scale
        [0.01, 0.01, 0.01]
        >>> hdr.scale = [0.5, 0.5, 0.001]
        >>> hdr.scale
        [0.5, 0.5, 0.001]
    """
    scale = property(get_scale, set_scale, None, doc)

    def get_offset(self):
        """Gets the offset factors in [x, y, z] for the point data.
        """
        return [self.XOffset, self.YOffset, self.ZOffset]

    def set_offset(self, value):
        """Sets the offset factors in [x, y, z] for the point data.
        """
        return
    doc = """The offset factors in [x, y, z] for the point data.

        From the specification_:
            The offset fields should be used to set the overall offset for the
            point records. In general these numbers will be zero, but for
            certain cases the resolution of the point data may not be large
            enough for a given projection system. However, it should always be
            assumed that these numbers are used. So to scale a given X from
            the point record, take the point record X multiplied by the X
            scale factor, and then add the X offset.

        Coordinates are calculated using the following formula(s):
            * x = (x_int * x_scale) + x_offset
            * y = (y_int * y_scale) + y_offset
            * z = (z_int * z_scale) + z_offset

        .. note::
            libLAS uses this header value when reading/writing raw point data
            to the file. If you change it in the middle of writing data,
            expect the unexpected.

        >>> hdr.offset
        [0.0, 0.0, 0.0]
        >>> hdr.offset = [32, 32, 256]
        >>> hdr.offset
        [32.0, 32.0, 256.0]

    """
    offset = property(get_offset, set_offset, None, doc)

    def get_min(self):
        """Gets the minimum values of [x, y, z] for the data.
        """
        return [self.XMin, self.YMin, self.ZMin]

    def set_min(self, value):
        """Sets the minimum values of [x, y, z] for the data.

        """
        return

    doc = """The minimum values of [x, y, z] for the data in the file.

        .. note::
            libLAS does not manage these values automatically for you. You
            must cumulate and generate the histogram manually if you wish to
            keep these data up-to-date with what actually exists in the file.

        >>> hdr.min
        [0.0, 0.0, 0.0]
        >>> hdr.min = [33452344.2333, 523442.344, -90.993]
        >>> hdr.min
        [33452344.2333, 523442.34399999998, -90.992999999999995]

    """
    min = property(get_min, set_min, None, doc)

    def get_max(self):
        return([self.XMax, self.YMax, self.ZMax])
    def set_max(self, value):
        """Sets the maximum values of [x, y, z] for the data.
        """
        return

    doc = """The maximum values of [x, y, z] for the data in the file.

        .. note::
            libLAS does not manage these values automatically for you. You
            must cumulate and generate the histogram manually if you wish to
            keep these data up-to-date with what actually exists in the file.

        >>> hdr.max
        [0.0, 0.0, 0.0]
        >>> hdr.max = [33452344.2333, 523442.344, -90.993]
        >>> hdr.max
        [33452344.2333, 523442.34399999998, -90.992999999999995]
    """
    max = property(get_max, set_max, None, doc)


    ### VLR MANIPULATION NOT IMPLEMENTED
    def add_vlr(self, value):
        return

    def get_vlr(self, value):
        return
   
    def delete_vlr(self, value):
        return  

    def get_vlrs(self):
        return

    def set_vlrs(self, value):
        return

    doc = """Get/set the :class:`liblas.vlr.VLR`'s for the header as a list

    .. note::
        Existing VLRs are left untouched, and if you are wishing to overwrite
        existing data, you must first delete them from the header using
        :obj:`liblas.header.header.delete_vlr`
    """
    vlrs = property(get_vlrs, set_vlrs, None, doc)

    def get_srs(self):
        return   

    def set_srs(self, value):
        return

    srs = property(get_srs, set_srs)

    def get_xml(self):
        return 
        
    xml = property(get_xml, None, None, None)