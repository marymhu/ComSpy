ComSpy has been created to spy and forward data between two COM ports.
com0com may be needed depending on how ComSpy is used.
  
# From external board to software
        (to computer)
Board ----------------> | COM X | ->  ComSpy -> | COM Y || COM Z | -> Sofware
                                                   |_________|
                                                   com0com loop
                                                   
# From external board to external board                                                   
If Physical connection on two sides, no com0com needed

# From software to software
com0com is needed on both sides: 2 virtual COM ports pairs must be configured.

ComSpy is currently designed to log only HL transmission which always begin with 0x01 0xFF 0x02 (to be improved) - but all bytes are forwarded.