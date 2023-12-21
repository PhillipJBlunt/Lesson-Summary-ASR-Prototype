from fpdf import FPDF
import matplotlib.pyplot as plt
from PIL import Image

class CustomPDF(FPDF):        
    def header(self):
        # Logo
        self.image('temp\\logo.png', 10, 10, 190)
        # Line break
        self.ln(15)
 
    def footer(self):
        # Offset from bottom
        self.set_y(-10)
        self.set_font('times', 'I', 10)
        # Add a page number
        page = 'Page ' + str(self.page_no()) + ' of {nb}'
        self.cell(0, 10, page, 0, 0, align='C')
        
def PlotPie(keywords, slice_mentions, gname):
    plt.pie(slice_mentions, labels=keywords, startangle=90)
    #plt.pie(slice_mentions, labels=keywords, startangle=90)
    plt.savefig(fname = gname, quality = 100, dpi = 300)# bbox_inches = 'tight')
    #crop to fix pyplot white space
    g = Image.open(gname)
    c_g = g.crop((0,160,1800,1040))
    c_g.save(gname)

def CreatePDF(output_path, lesson_details, keywords, mentions, other, associations, transcript, font = "times", orientation='P', unit = 'mm', page_format = 'A4'):
    #document header and footer
    pdf = CustomPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font(font, 'BU', size=14)
    pdf.ln(2)
    
    #lesson heading
    pdf.cell(0, 5, lesson_details[0], align='C', ln = 1)
    #other lesson details
    pdf.set_font(font, "", size=10)
    for i in range(1,len(lesson_details)):
        pdf.cell(0, 5, lesson_details[i], align='C', ln = 1)
    
    #pie chart header
    pdf.ln(2)
    pdf.set_font(font, 'BU', size=14)
    pdf.cell(0,5,"Keywords mentioned in this lesson:", ln=1)
    
    #pie chart plot and details
    gname = "temp\\graph.jpg"
    PlotPie(keywords, mentions, gname)
    pdf.image(gname, w = 180, h = 100)
    pdf.set_font(font, 'i', size=10)
    pdf.cell(0, 5, "Pie chart plot for the frequencies of identified keywords (in sequence of mention, counter clockwise)", align = 'C', ln=1)
    pdf.ln(4)
    pdf.multi_cell(0, 5, txt = other, align='C')
    pdf.ln(4)
    
    #write the section associations header
    pdf.set_font(font, 'BU', size=14)
    pdf.cell(0,5,"Course content covered in this lesson:", ln=1)
    pdf.ln(4)
    
    #write the associated sections
    pdf.set_font(font, '', size = 12)
    for section in associations:
        pdf.multi_cell(0, 5, section, align = "J")
    
    #transcript header
    pdf.ln(4)
    pdf.set_font(font, 'BU', size=14)
    pdf.cell(0,5,"Lesson Transcript", ln=1)
    
    #print the transcript
    pdf.ln(4)
    pdf.set_font(font, '', size = 10)
    pdf.multi_cell(0, 5, txt = transcript, align='J')
    
    #output the document
    pdf.output(output_path)