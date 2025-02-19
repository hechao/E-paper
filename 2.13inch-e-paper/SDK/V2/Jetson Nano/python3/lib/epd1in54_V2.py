# *****************************************************************************
# * | File        :	  epd1in54_V2.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1
# * | Date        :   2019-06-20
# # | Info        :   python3 demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and//or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import epdconfig

# Display resolution
EPD_WIDTH       = 200
EPD_HEIGHT      = 200

class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200) 
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(10)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(200)   

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        print("e-Paper busy")
        while(epdconfig.digital_read(self.busy_pin) == 1):
            epdconfig.delay_ms(100)
        print("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xF7)
        self.send_command(0x20) # MASTER_ACTIVATION
        
        self.ReadBusy()
    
    def TurnOnDisplayPart(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xFF)
        self.send_command(0x20) # MASTER_ACTIVATION
        
        self.ReadBusy()

    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
            
        # EPD hardware init start
        self.reset()
        
        self.ReadBusy()
        self.send_command(0x12) # SWRESET
        self.ReadBusy()
        
        self.send_command(0x01) # DRIVER_OUTPUT_CONTROL
        self.send_data(0xC7) # (EPD_HEIGHT - 1) & 0xFF
        self.send_data(0x00) # ((EPD_HEIGHT - 1) >> 8) & 0xFF
        self.send_data(0x01) # GD = 0 SM = 0 TB = 0
        
        self.send_command(0x11) # data entry mode
        self.send_data(0x01)
        
        self.send_command(0x44) # set Ram-X address start//end position
        self.send_data(0x00)
        self.send_data(0x18) # 0x0C-->(18+1)*8=200
        
        self.send_command(0x45) # set Ram-Y address start//end position
        self.send_data(0xC7) # 0xC7-->(199+1)=200
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C) # BorderWavefrom
        self.send_data(0x01)

        self.send_command(0x18)
        self.send_data(0x80)

        self.send_command(0x22) # #Load Temperature and waveform setting.
        self.send_data(0XB1)
        self.send_command(0x20)

        self.send_command(0x4E) # set RAM x address count to 0;
        self.send_data(0x00)
        self.send_command(0x4F) # set RAM y address count to 0X199;
        self.send_data(0xC7)
        self.send_data(0x00)
        
        self.ReadBusy()
        
    def Clear(self, color):
        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, self.width // 8):
                self.send_data(color)
        self.TurnOnDisplay()
        
    def getbuffer(self, image):
        buf = [0xFF] * ((self.width//8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        if(imwidth == self.width and imheight == self.height):
            print("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[(x + y * self.width) // 8] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            print("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[(newx + newy*self.width) // 8] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, image):
        if (image == None):
            return
            
        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, self.width // 8):
                self.send_data(image[i + j * (self.width // 8)])   
        self.TurnOnDisplay()
        
    def displayPartBaseImage(self, image):
        if (image == None):
            return
            
        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, self.width // 8):
                self.send_data(image[i + j * (self.width // 8)])
        
        self.send_command(0x26)
        for j in range(0, self.height):
            for i in range(0, self.width // 8):
                self.send_data(image[i + j * (self.width // 8)])
                
        self.TurnOnDisplayPart()
        
    def displayPart(self, image):
        if (image == None):
            return
            
        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, self.width // 8):
                self.send_data(image[i + j * (self.width // 8)])
                
        self.TurnOnDisplayPart()
        
    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP_MODE
        self.send_data(0x01)
        
        epdconfig.module_exit()

### END OF FILE ###

