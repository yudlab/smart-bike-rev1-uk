from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.graphics.shapes import Drawing, Circle, Line, Rect, String
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/Yudlab-Smart-Bike-Proposal.pdf'
navy=HexColor('#102232'); teal=HexColor('#128d83'); muted=HexColor('#476377'); amber=HexColor('#e5a225')
s=getSampleStyleSheet()
for name,size,leading,color in [('TitleBike',30,35,navy),('BodyBike',10,14,navy),('SectionBike',22,27,navy),('Kicker',9,12,teal),('CellBike',8,11,navy),('SmallBike',8,11,muted)]:
 s.add(ParagraphStyle(name=name,fontName='Helvetica-Bold' if name in ('TitleBike','SectionBike') else 'Helvetica',fontSize=size,leading=leading,textColor=color,spaceAfter=12 if name!='CellBike' else 0))
def p(t,style='BodyBike'):return Paragraph(escape(t),s[style])
def drawing():
 d=Drawing(490,260)
 for x in [115,370]:
  d.add(Circle(x,85,60,strokeColor=muted,strokeWidth=3,fillColor=None))
  d.add(Line(x-60,85,x+60,85,strokeColor=HexColor('#cad7df')))
  d.add(Line(x,25,x,145,strokeColor=HexColor('#cad7df')))
 for a,b in [((115,85),(185,170)),((185,170),(245,85)),((245,85),(115,85)),((185,170),(325,170)),((325,170),(245,85)),((325,170),(370,85)),((325,170),(315,205))]:d.add(Line(*a,*b,strokeColor=teal,strokeWidth=5))
 d.add(Line(166,183,203,183,strokeColor=navy,strokeWidth=5));d.add(Line(315,205,345,205,strokeColor=navy,strokeWidth=5))
 for x,y,w,h,c in [(222,126,65,34,navy),(299,211,33,24,navy),(333,177,17,13,amber),(158,164,14,9,HexColor('#d94d60')),(344,109,7,15,muted)]:d.add(Rect(x,y,w,h,fillColor=c,strokeColor=None))
 d.add(String(305,218,'24',fontSize=13,fillColor=white))
 for x in [159,175,334,350]:d.add(Circle(x,150,4,fillColor=amber,strokeColor=None))
 for x,y,t in [(214,112,'Pico + ESP'),(275,246,'2-inch SPI display'),(357,128,'Reed'),(8,227,'Trackball remote')]:d.add(String(x,y,t,fontSize=10,fillColor=navy))
 d.add(Rect(22,137,48,78,rx=8,ry=8,fillColor=navy,strokeColor=None));d.add(Rect(30,180,32,24,fillColor=teal,strokeColor=None));d.add(Circle(46,159,9,fillColor=white,strokeColor=None))
 return d

def architecture():
 d=Drawing(490,250)
 for x,y,title,sub in [(0,165,'LOCAL INPUTS','Reed / brakes / buttons'),(175,165,'PICO','Speed / lamps / SPI TFT'),(350,165,'BIKE ESP32-S3','GPS / records / web'),(175,30,'LOAD DRIVERS','Fused external power'),(350,30,'REMOTE ESP','Trackball / screen / radio')]:
  d.add(Rect(x,y,140,65,rx=7,ry=7,fillColor=navy,strokeColor=None));d.add(String(x+10,y+40,title,fontSize=10,fillColor=white));d.add(String(x+10,y+18,sub,fontSize=8,fillColor=HexColor('#a9d7db')))
 for x1,y1,x2,y2 in [(140,197,175,197),(315,197,350,197),(245,165,245,95),(420,165,420,95)]:d.add(Line(x1,y1,x2,y2,strokeColor=teal,strokeWidth=2))
 d.add(String(322,211,'UART',fontSize=7,fillColor=muted));d.add(String(430,124,'Radio',fontSize=8,fillColor=muted));d.add(String(0,5,'Functional allocation only. Not a verified circuit or pinout.',fontSize=9,fillColor=muted))
 return d

def footer(c,doc):
 c.setStrokeColor(HexColor('#d5e2e7'));c.line(42,40,553,40);c.setFont('Helvetica',8);c.setFillColor(muted);c.drawString(42,26,'YUDLAB / SMART BIKE REV 1  |  ENGINEERING PROPOSAL  |  10 NOV 2026');c.drawRightString(553,26,str(doc.page))
story=[p('YUDLAB / REV 1.0','Kicker'),p('One bike. One connected system.','TitleBike'),p('Breadboard-first proposal, firmware draft and animated diagnostic dashboard.'),Image(str(ROOT/'docs/concept.png'),width=510,height=287),Spacer(1,20),p('Pico for the ride. ESP for the records.','SectionBike'),p('Local sensing and lighting, connected trip data, and a handheld trackball remote. Built around your photographed parts, with unknown ratings left explicit.'),p('DESIGN STATUS','Kicker'),p('Runnable software simulation and input-only Pico demo. Hardware drivers, wireless security, GPS logging and parking mechanics still require integration and bench verification.'),p('Cover: AI-generated concept, not your actual bicycle or an electrical drawing. Following diagrams are vector artwork.','SmallBike'),PageBreak()]
story += [p('PHYSICAL & LOGICAL LAYOUT','Kicker'),p('Equipment around the bike','SectionBike'),drawing(),p('Handlebar: TFT and buttons. Frame: Pico, ESP and protected power. Fork: reused reed sensor. Front/rear: lamps. Remote: second ESP, trackball and its own display.'),architecture(),p('Lock output is unimplemented. Use independent mechanical parking interlocks before considering actuator integration.','SmallBike'),PageBreak()]
sections=(ROOT/'docs/design.md').read_text().split('\n## ')[1:]
for idx,section in enumerate(sections):
 lines=section.splitlines();story.extend([p('DESIGN DETAIL / '+str(idx+1).zfill(2),'Kicker'),p(lines[0],'SectionBike')])
 for block in '\n'.join(lines[1:]).strip().split('\n\n'):
  if block.startswith('|'):
   rows=[[p(c.strip(),'CellBike') for c in line.strip('|').split('|')] for line in block.splitlines() if not line.startswith('|---')]
   table=Table(rows,colWidths=[155,95,260],repeatRows=1)
   table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#d8eee9')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.4,HexColor('#d5e2e7'))]));story.extend([table,Spacer(1,12)])
  elif block.startswith('- '):story.extend(p(line,'SmallBike') for line in block.splitlines())
  else:
   # Preserve numbered build stages and source list entries as separate paragraphs.
   if any(line.startswith('- ') for line in block.splitlines()):
    story.extend(p(line,'SmallBike') for line in block.splitlines())
   elif block[:1].isdigit():
    import re
    story.extend(p(item.replace('\n',' ')) for item in re.split(r'\n(?=\d+\. )',block))
   else:story.append(p(block.replace('\n',' ')))
 if idx<len(sections)-1:story.append(PageBreak())
SimpleDocTemplate(str(OUT),pagesize=(595,842),rightMargin=42,leftMargin=42,topMargin=48,bottomMargin=55,title='Yudlab Smart Bike rev1 - Combined System Proposal',author='Yudlab').build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
