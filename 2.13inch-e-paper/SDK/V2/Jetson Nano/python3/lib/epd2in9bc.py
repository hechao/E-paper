# *****************************************************************************
# * | File        :	  epd2in9bc.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0
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
EPD_WIDTH       = 128
EPD_HEIGHT      = 296

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
        while(epdconfig.digital_read(self.busy_pin) == 0):      #  0: idle, 1: busy
            epdconfig.delay_ms(200)                
        print("e-Paper busy release")
        
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        
        self.send_command(0x06) # boost
        self.send_data (0x17)
        self.send_data (0x17)
        self.send_data (0x17)
        self.send_command(0x04) # POWER_ON
        self.ReadBusy()
        self.send_command(0X00) # PANEL_SETTING
        self.send_data(0x8F)
        self.send_command(0X50) # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0x77)
        self.send_command(0x61) # TCON_RESOLUTION
        self.send_data (0x80)
        self.send_data (0x01)
        self.send_data (0x28)
        # self.send_command(VCM_DC_SETTING_REGISTER)
        # self.send_data (0x0A)
        
        return 0

    def getbuffer(self, image):
        # print "bufsiz = ",(self.width//8) * self.height
        buf = [0xFF] * ((self.width//8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # print "imwidth = %d, imheight = %d",imwidth,imheight
        if(imwidth == self.width and imheight == self.height):
            print("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[(x + y * self.width) // 8] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            print("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[(newx + newy*self.width) // 8] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, blackimage, ryimage): # ryimage: red or yellow image
        if (blackimage != None):
            self.send_command(0X10)
            for i in range(0, self.width * self.height // 8):
                self.send_data(blackimage[i])        
        if (ryimage != None):
            self.send_command(0X13)
            for i in range(0, self.width * self.height // 8):
                self.send_data(ryimage[i])

        self.send_command(0x12)
        self.ReadBusy()
        
    def Clear(self):
        self.send_command(0X10)
        for i in range(0, self.width * self.height // 8):
            self.send_data(0xff)
        self.send_command(0X13)
        for i in range(0, self.width * self.height // 8):
            self.send_data(0xff)

        self.send_command(0x12)
        self.ReadBusy()
        
    def sleep(self):
        self.send_command(0X02) # power off
        self.ReadBusy()
        self.send_command(0X07) # deep sleep
        self.send_data(0xA5)
        
        epdconfig.module_exit()
### END OF FILE ###

