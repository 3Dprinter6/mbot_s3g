"""
A stream parser that decodes an s3g stream
"""

import struct

from errors import *
from constants import *

class s3gStreamDecoder(object):

  def __init__(self):
    pass

  def ReadBytes(self, count):
    """ Read a number of bytes from the current file.

    Throws a EndOfFileError exception if too few bytes were available.
    @return string Bytes from the file.
    """
    data = self.file.read(count)
  
    if len(data) != count:
      raise EndOfFileError
    
    return data 

  def ParseOutParameters(self, cmd):
    """Reads and decodes a certain number of bytes using a specific format string
    from the input s3g file
   
    @param int cmd The command's parameters we are trying to parse out 
    @return list objects unpacked from the input s3g file
    """
    formatString = commandFormats[cmd]
    returnParams = []
    for formatter in formatString:
      if formatter == 's':
        b = self.GetStringBytes()
        formatString = '<'+str(len(b))+formatter
      else:
        b = self.GetBytes(formatter)
        formatString = '<'+formatter
      returnParams.append(self.ParseParameter(formatString, b))
    if cmd == host_action_command_dict['TOOL_ACTION_COMMAND']:
      returnParams.extend(self.ParseOutParameters(returnParams[1]))
    return returnParams

  def ParseParameter(self, formatString, bytes):
    """Given a format string and a set of bytes, unpacks the bytes into the given format

    @param string formatString: A format string of format to be used when unpacking bytes with the struct object
    @param bytes: The bytes to be unpacked
    @return The correctly unpacked string
    """
    returnParam = struct.unpack(formatString, bytes)[0]
    #Remove the null terminator from the decoded string if present
    if 's' in formatString and returnParam[-1] == '\x00':
      returnParam = returnParam[:-1]
    return returnParam

  def GetStringBytes(self):
    """Get all bytes associated with a string
    Assuming the next parameter is a null terminated string, 
    we read bytes until we find that null terminator
    and return the string.  If we read over the 
    packet limit, we raise a StringTooLong error.
    @return The bytes making up a null terminated string
    """
    b = ''
    while True:
      readByte = self.ReadBytes(1)
      b += readByte
      if len(b) > maximum_payload_length:
        raise StringTooLongError
      elif b[-1] == '\x00':
        return b

  def GetBytes(self, formatter):
    """Given a formatter, we read in a certain amount of bytes
    
    @param string formatter: The format string we use to diving the number
    of bytes we read in
    @return string bytes: The correct number of bytes read in
    """
    b = ''
    for i in range(structFormats[formatter]):
      b+= self.ReadBytes(1)
    return b

  def GetNextCommand(self):
    """Assuming the file pointer is at a command, gets the next command number

    @return int The command number
    """
    cmd = self.ReadBytes(1)
    return ord(cmd)

  def ParseNextPayload(self):
    """Gets the next command and returns the parsed commands and associated parameters

    @return list: a list of the cmd and  all information associated with that command
    """
    cmd = self.GetNextCommand()

    parameters = self.ParseOutParameters(cmd)
    return [cmd] + parameters

  def ParseNextPacket(self):
    """
    Assuming the file pointer is at the beginning of a packet, we parse out the information from that packet
    @return parsed packet from the stream
    """
    readHeader = self.ReadBytes(1)
    readHeader = self.ParseParameter('<B', readHeader)

    length = self.ReadBytes(1)
    length = self.ParseParameter('<B', length)

    payload = self.ParseNextPayload()

    crc = self.ReadBytes(1)
    crc = self.ParseParameter('<B', crc)

    return self.PackagePacket(readHeader, length, payload, crc)

  def PackagePacket(self, *args):
    """Packages all args into a single list

    @param args: Arguments to be packaged
    @return package: A single non-nested list comprised of all arguments
    """
    package = []
    for arg in args:
      try:
        package.extend(arg)
      except TypeError:
        package.append(arg)
    return package

  def ReadStream(self):
    """Reads from an s3g stream until it cant read anymore
    @return packets: A list of packets, where each index of 
      the list is comprised of one packet
    """
    packets = []
    try:
      while True:
        packets.append(self.ParseNextPacket())
    # TODO: We aren't catching partial packets at the end of files here.
    except EndOfFileError:
      return packets

