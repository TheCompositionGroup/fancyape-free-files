# Source for 90-day-supply-list.pdf. Edit the text below, then run: python build.py
# Requires: pip install reportlab
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, Flowable, KeepTogether,
                                CondPageBreak, PageBreak)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

W, H = letter
M = 0.6 * inch
BLACK = colors.black
GREY = colors.HexColor("#d9d9d9")
LIGHT = colors.HexColor("#f0f0f0")

def S(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9.5, leading=12.5, textColor=BLACK)
    base.update(kw)
    return ParagraphStyle(name, **base)

kicker = S("kicker", fontName="Helvetica-Bold", fontSize=8.5, leading=11)
title = S("title", fontName="Helvetica-Bold", fontSize=34, leading=36)
subtitle = S("subtitle", fontName="Helvetica-Bold", fontSize=17, leading=21)
tag = S("tag", fontName="Helvetica-Bold", fontSize=11.5, leading=15)
body = S("body")
small = S("small", fontSize=8.5, leading=11)
h2 = S("h2", fontName="Helvetica-Bold", fontSize=13, leading=16, keepWithNext=1, spaceBefore=2)
scope = S("scope", fontName="Helvetica-Oblique", fontSize=8.5, leading=11, keepWithNext=1)
cell = S("cell", fontSize=9, leading=11)
cellb = S("cellb", fontName="Helvetica-Bold", fontSize=9, leading=11)
headc = S("headc", fontName="Helvetica-Bold", fontSize=7.5, leading=9, alignment=TA_CENTER)
headl = S("headl", fontName="Helvetica-Bold", fontSize=7.5, leading=9)
warnh = S("warnh", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=colors.white)
warnb = S("warnb", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.white)
boxh = S("boxh", fontName="Helvetica-Bold", fontSize=10.5, leading=13)
stage_n = S("stage_n", fontName="Helvetica-Bold", fontSize=26, leading=28, alignment=TA_CENTER)
stage_t = S("stage_t", fontName="Helvetica-Bold", fontSize=8.5, leading=11, alignment=TA_CENTER)
stage_s = S("stage_s", fontSize=8.5, leading=11, alignment=TA_CENTER)

class Box(Flowable):
    """Empty checkbox."""
    def __init__(self, size=8):
        super().__init__(); self.s = size
    def wrap(self, aw, ah): return self.s, self.s
    def draw(self):
        self.canv.setLineWidth(0.8); self.canv.rect(0, 0, self.s, self.s)

class Dot(Flowable):
    def __init__(self, r=2.6): super().__init__(); self.r = r
    def wrap(self, aw, ah): return self.r*2, self.r*2
    def draw(self): self.canv.circle(self.r, self.r, self.r, fill=1, stroke=0)

class Buckets(Flowable):
    """Two-bucket toilet diagram."""
    def wrap(self, aw, ah): return 180, 92
    def bucket(self, c, x, label, lined):
        c.setLineWidth(1.4)
        p = c.beginPath()
        p.moveTo(x, 70); p.lineTo(x+64, 70); p.lineTo(x+56, 8); p.lineTo(x+8, 8); p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.setLineWidth(2.2); c.line(x-3, 74, x+67, 74)          # lid / seat
        c.setLineWidth(0.8); c.arc(x+8, 60, x+56, 92, 20, 160)  # handle
        if lined:
            c.setDash(2, 2); c.setLineWidth(0.8)
            c.line(x+6, 68, x+12, 12); c.line(x+58, 68, x+52, 12)
            c.setDash()
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x+32, 36, label)
        c.setFont("Helvetica", 7)
        c.drawCentredString(x+32, 24, "bag liner" if lined else "no liner")
    def draw(self):
        c = self.canv
        self.bucket(c, 6, "PEE", False)
        self.bucket(c, 104, "POO", True)
        c.setFont("Helvetica", 7)
        c.drawCentredString(88, 0, "Lids on · cover each use · wash hands")

class Drop(Flowable):
    def __init__(self, label): super().__init__(); self.label = label
    def wrap(self, aw, ah): return 46, 52
    def draw(self):
        c = self.canv; c.setLineWidth(1.4)
        p = c.beginPath(); p.moveTo(23, 50)
        p.curveTo(10, 30, 6, 22, 6, 17); p.curveTo(6, 7, 14, 2, 23, 2)
        p.curveTo(32, 2, 40, 7, 40, 17); p.curveTo(40, 22, 36, 30, 23, 50)
        c.drawPath(p, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 9); c.drawCentredString(23, 13, self.label)

def warning(head, text):
    t = Table([[Paragraph(head, warnh)], [Paragraph(text, warnb)]], colWidths=[W-2*M])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), BLACK),
                           ("LEFTPADDING", (0,0), (-1,-1), 10),
                           ("TOPPADDING", (0,0), (-1,0), 7),
                           ("BOTTOMPADDING", (0,-1), (-1,-1), 8),
                           ("BOTTOMPADDING", (0,0), (-1,0), 1)]))
    return t

def card(head, flowables, width=W-2*M):
    rows = [[Paragraph(head, boxh)]] + [[f] for f in flowables]
    t = Table(rows, colWidths=[width])
    t.setStyle(TableStyle([("BOX", (0,0), (-1,-1), 1.6, BLACK),
                           ("LINEBELOW", (0,0), (-1,0), 0.8, BLACK),
                           ("BACKGROUND", (0,0), (-1,0), LIGHT),
                           ("LEFTPADDING", (0,0), (-1,-1), 9),
                           ("RIGHTPADDING", (0,0), (-1,-1), 9),
                           ("TOPPADDING", (0,0), (-1,-1), 3),
                           ("BOTTOMPADDING", (0,0), (-1,-1), 3)]))
    return t

def P(t, st=body): return Paragraph(t, st)

# ---------- master inventory table ----------
COLS = [0.48*inch, 2.79*inch, 1.75*inch, 0.5*inch, 0.5*inch, 1.28*inch]
def inventory(title_txt, scope_txt, rows):
    data = [[Paragraph("3-DAY", headc), Paragraph("ITEM", headl), Paragraph("90-DAY AMOUNT", headl),
             Paragraph("HAVE", headc), Paragraph("NEED", headc), Paragraph("EXPIRES", headl)]]
    for r in rows:
        item, qty = r[0], r[1]
        start = len(r) > 2 and r[2]
        data.append([Dot() if start else "", Paragraph(item, cellb), Paragraph(qty, cell),
                     Box(), Box(), ""])
    t = Table(data, colWidths=COLS, repeatRows=1)
    st = [("FONT", (0,0), (-1,-1), "Helvetica", 9),
          ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
          ("ALIGN", (0,0), (0,-1), "CENTER"),
          ("ALIGN", (3,0), (4,-1), "CENTER"),
          ("LINEBELOW", (0,0), (-1,0), 1.2, BLACK),
          ("LINEBELOW", (0,1), (-1,-1), 0.4, GREY),
          ("LINEBELOW", (5,1), (5,-1), 0.6, BLACK),
          ("TOPPADDING", (0,0), (-1,-1), 1.6),
          ("BOTTOMPADDING", (0,0), (-1,-1), 1.6),
          ("LEFTPADDING", (0,0), (-1,-1), 3)]
    t.setStyle(TableStyle(st))
    blk = [P(title_txt, h2), P(scope_txt, scope), Spacer(1, 2), t]
    return ([KeepTogether(blk)] if len(rows) <= 16 else blk) + [Spacer(1, 8)]

# ---------- page decoration ----------
def decorate(c, doc):
    c.saveState()
    if doc.page > 1:
        c.setLineWidth(1.2); c.line(M, H-0.45*inch, W-M, H-0.45*inch)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(M, H-0.4*inch, "READY WHEN NEEDED  ·  BUILD YOUR 90-DAY HOME RESERVE")
    c.setLineWidth(0.6); c.line(M, 0.55*inch, W-M, 0.55*inch)
    c.setFont("Helvetica", 7.5)
    c.drawString(M, 0.4*inch, "fancyape.com  ·  THE IDEA IS THE ART. THE HELP IS THE POINT.  ·  Version 1.2  ·  November 2026  ·  Free to share  ·  CC BY 4.0")
    c.drawRightString(W-M, 0.4*inch, "Page %d" % doc.page)
    c.restoreState()

doc = BaseDocTemplate(os.path.join(os.path.dirname(os.path.abspath(__file__)), "90-day-supply-list.pdf"), pagesize=letter,
                      leftMargin=M, rightMargin=M, topMargin=0.65*inch, bottomMargin=0.7*inch,
                      title="Ready When Needed: Build Your 90-Day Home Reserve",
                      author="fancyape.com", subject="Version 1.2, November 2026")
frame = Frame(M, 0.7*inch, W-2*M, H-1.35*inch, id="f", leftPadding=0, rightPadding=0,
              topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=decorate)])

s = []
# ---------- PAGE 1 ----------
s += [
      P("READY WHEN NEEDED", title), Spacer(1, 2),
      P("Build Your 90-Day Home Reserve", subtitle), Spacer(1, 8),
      P("Use what you already own. Buy what you actually eat. Build gradually.", tag),
      Spacer(1, 3), P("Start with 3 days. Build toward 90.", body), Spacer(1, 10)]

stages = [("3", "1 · START", "3 gal water / person"),
          ("14", "2 · PREPARE", "14 gal water / person"),
          ("30", "3 · BUILD", "30 gal water / person"),
          ("90", "4 · EXTEND", "90 gal water / person")]
cw = (W-2*M)/4
st_tbl = Table([[P(n, stage_n) for n, _, _ in stages],
                [P("DAYS", stage_t)]*4,
                [P(t, stage_t) for _, t, _ in stages],
                [P(w, stage_s) for _, _, w in stages]], colWidths=[cw]*4)
st_tbl.setStyle(TableStyle([("BOX", (0,0), (-1,-1), 1.6, BLACK),
                                                        ("LINEAFTER", (0,0), (2,-1), 1, BLACK),
                            ("BACKGROUND", (0,0), (0,-1), LIGHT),
                            ("TOPPADDING", (0,0), (-1,0), 8),
                            ("BOTTOMPADDING", (0,-1), (-1,-1), 8),
                            ("TOPPADDING", (0,1), (-1,-1), 0)]))
s += [st_tbl, Spacer(1, 10)]

how = [P("<b>Per person</b> items: multiply by the number of people in your home.", body),
       P("<b>Per household</b> items: one set covers the home.", body),
       P("The lists show <b>90-day amounts</b>. For a smaller goal, scale down: 14 days = about 1/6, 30 days = about 1/3.", body),
       P("Start with the <b>3-day</b> items: marked with a dot (•) in the 3-DAY column and listed in the Stage 1 box below. They count toward your 90-day totals. They are not extra.", body),
       P("Mark each line: <b>Have</b>  ·  <b>Need</b>  ·  <b>Expires</b>.", body)]
s += [card("HOW TO USE THIS LIST", how), Spacer(1, 10)]

s += [warning("LEAVE NOW AND CALL 911", "Gas smell  ·  Downed power lines  ·  Unsafe building"), Spacer(1, 6),
      warning("CARBON MONOXIDE KILLS",
              "Never run a generator, grill, camp stove, or heater indoors, in a garage, or near windows."),
      Spacer(1, 10)]

stage1 = [P("Food that needs no heat and no water. These items count toward your 90-day totals. They are not extra.", small)]
s1rows = [("Water", "3 gallons"), ("Canned meat or fish (pop-top)", "3 cans"),
          ("Peanut butter or other nut butter", "1 jar"), ("Crackers", "1 box"),
          ("Canned fruit or fruit cups", "3"), ("Granola or protein bars", "6"),
          ("Shelf-stable milk or juice boxes", "3"), ("Trail mix or nuts", "1 bag"),
          ("Manual can opener", "1 per household")]
half = [s1rows[:5], s1rows[5:]]
sub = []
for col in half:
    tt = Table([[Box(), P("<b>%s</b>" % a, cell), P(b, cell)] for a, b in col],
               colWidths=[0.2*inch, 2.0*inch, 1.0*inch])
    tt.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                            ("TOPPADDING", (0,0), (-1,-1), 1.5), ("BOTTOMPADDING", (0,0), (-1,-1), 1.5),
                            ("LEFTPADDING", (0,0), (-1,-1), 0)]))
    sub.append(tt)
two = Table([sub], colWidths=[(W-2*M-18)/2]*2)
two.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0)]))
s += [card("STAGE 1  ·  FIRST 3 DAYS  ·  NO COOKING  (per person)", stage1 + [two]), PageBreak()]

# ---------- WATER ----------

s += inventory("WATER", "Per person: 1 gallon per day for drinking and basic hygiene. Add more for heat, illness, nursing, cooking, and pets.", [
    ("Water, per person", "90 gallons (1 gal/day)", True),
])
s += inventory("WATER GEAR", "Per household", [
    ("Food-grade containers: 5–7 gal jugs and/or 55-gal barrels", "Enough to hold your total"),
    ("Siphon pump (for barrels)", "1"),
    ("Gravity water filter", "1"),
    ("Water treatment tablets", "2 packs", True),
    ("Unscented regular bleach, dated", "1–2 bottles"),
    ("Dropper", "1"),
    ("Coffee filters or clean cloth (pre-filter cloudy water)", "1 pack"),
])
weight = card("KNOW THE WEIGHT", [P("Water weighs about 8.3 lb per gallon. 90 days for one person is about <b>750 lb</b>. "
                                     "Store it on a ground floor or slab, never on a balcony or upper floor.", body)])
backup = card("BACKUP WATER SOURCES", [
    P("You don't have to store all 90 days, but know your backups:", body),
    P("<b>Safe to drink:</b> water in your water heater tank and pipes, and ice cubes made before the emergency, only if you shut the main water valve before contamination gets in. Turn off the heater power or gas before draining it.", body),
    P("<b>Treat before drinking:</b> rainwater, streams, and lakes. Do not use them if they may contain fuel, chemicals, or floodwater.", body),
    P("<b>Verified public water distribution points:</b> follow local announcements.", body),
    P("<b>Pools and spas:</b> for cleaning and flushing only. Never drink this water.", body)])
s += [KeepTogether([weight, Spacer(1, 8), backup]), Spacer(1, 10)]

drops = Table([[Drop("8"), P("<b>Clear water:</b><br/>8 drops per gallon", body),
                Drop("16"), P("<b>Cloudy, colored, or very cold water:</b><br/>16 drops per gallon", body)]],
              colWidths=[0.75*inch, 2.4*inch, 0.75*inch, 2.9*inch])
drops.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 0)]))
treat = card("TREATING WATER  (CDC)", [
    P("<b>Boiling is best</b> when you can do it safely outdoors: bring water to a rolling boil for "
      "<b>1 minute</b> (3 minutes above 6,500 ft). Let it cool.", body),
    P("<b>If you can't boil, use bleach:</b>", body),
    P("1. Use regular, unscented bleach (5–9%). Check the label.", body),
    P("2. If cloudy, let it settle, then filter through a cloth or coffee filter.", body),
    P("3. Add bleach:", body),
    drops,
    P("4. Stir and wait <b>30 minutes</b>. It should smell slightly of chlorine. If not, repeat the dose and wait 15 more minutes.", body),
    P("5. Replace bleach yearly. It weakens over time.", body),
    Spacer(1, 2),
    P("<b>Boiling and bleach do NOT remove fuel or chemicals.</b> If water may contain them, use stored water only.", body)])
s += [KeepTogether([treat]), Spacer(1, 12)]

# ---------- FOOD ----------
s += [P("FOOD", S("hf", fontName="Helvetica-Bold", fontSize=15, leading=18, keepWithNext=1)),
      P("Per person, 90 days. Target: about 2,000 calories a day for adults, less for young children. "
        "Quantities are planning estimates, not a verified 90-day meal plan. Check calories, serving sizes, "
        "and dietary needs for your household. Choose foods you already eat. Swap freely within each group.", small),
      Spacer(1, 6)]
def foodgroup(name, rows):
    return inventory(name, "Per person", rows)
s += foodgroup("Protein", [
    ("Canned meat or fish (chicken, tuna, salmon, ham)", "45 cans", True),
    ("Canned beans or chili", "45 cans"),
    ("Dry beans and lentils", "10 lb"),
    ("Peanut butter or other nut butter", "4 jars", True)])
s += foodgroup("Staples", [
    ("White rice", "20 lb"), ("Dry pasta", "10 lb"), ("Oatmeal", "5 lb"),
    ("Instant potatoes", "3 packs"), ("Ramen or quick noodles", "18 packs"),
    ("Crackers", "4 boxes", True), ("Breakfast cereal", "4 boxes")])
s += foodgroup("Fruit, vegetables & ready meals", [
    ("Canned vegetables", "60 cans"), ("Canned tomatoes or sauce", "18 cans or jars"),
    ("Canned fruit or fruit cups", "36", True), ("Dried fruit", "2 lb"),
    ("Canned soups, stews, and pasta meals", "45 cans")])
s += foodgroup("Milk, fats, sugar & extras", [
    ("Powdered milk", "4–6 gal yield"),
    ("Evaporated or shelf-stable milk", "18 cans or cartons", True),
    ("Cooking oil", "1 gallon"), ("Sugar or honey", "5 lb"),
    ("Nuts or trail mix", "4 lb", True), ("Granola bars", "4 boxes", True),
    ("Coffee, tea, cocoa, drink mix", "As your household uses them"),
    ("Electrolyte packets", "1 box"),
    ("Comfort foods (candy, cookies, chocolate)", "A few bags")])
s += inventory("Pantry basics", "Per household (flour is per person)", [
    ("Flour", "10 lb per person"),
    ("Instant yeast, baking powder, baking soda", "1 each"),
    ("Salt, seasonings, bouillon", "Assorted")])
s += [P("<b>Bread basics:</b> flour + water + salt. Add yeast for risen bread, baking powder for quick bread. "
        "Remember: rice, beans, and pasta need clean water and cooking fuel.", small), Spacer(1, 12)]

# ---------- COOKING ----------
s += inventory("COOKING", "Per household", [
    ("Outdoor camp stove", "1"),
    ("20-lb propane tanks with stove adapter hose", "See fuel estimate"),
    ("Lighters", "2"), ("Matches", "2 boxes")])
math = Table([[P("<b>Tank hours</b>", body), P("=  430,000  ÷  your burner's BTU per hour", body)],
              [P("<b>Tanks needed</b>", body), P("=  hours of cooking per day  ×  90  ÷  tank hours", body)]],
             colWidths=[1.3*inch, 5.3*inch])
math.setStyle(TableStyle([("BOX", (0,0), (-1,-1), 0.8, BLACK), ("INNERGRID", (0,0), (-1,-1), 0.4, GREY),
                          ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
fuel = card("ESTIMATE YOUR FUEL", [
    P("1. Find your stove's fuel use on its label or manual (BTU per hour, per burner).", body),
    P("2. A full 20-lb propane tank holds about 430,000 BTU.", body),
    math,
    P("Use only a hose and regulator rated for your stove and a 20-lb tank.", body),
    P("<b>Cook outdoors only.</b> Store tanks outside, upright, and out of direct sun.", body)])
s += [KeepTogether([fuel]), Spacer(1, 12)]

# ---------- TOILET ----------
s += inventory("TOILET BACKUP", "Per household of 2–4; double for more", [
    ("5-gallon buckets with lids", "2"),
    ("Toilet seat that fits a bucket", "1"),
    ("Heavy contractor bags", "50 for 2 people, 100 for 4"),
    ("Cat litter, sawdust, or shredded paper", "25 lb"),
    ("Handwashing station: water jug with spout, soap, towels", "1")])
steps = [P("1. Label one bucket PEE and one bucket POO.", body),
         P("2. Line the POO bucket with a heavy bag.", body),
         P("3. After each use, cover with a scoop of litter or sawdust. Keep lids on.", body),
         P("4. When a bag is 1/3 full, tie it, double-bag it, and store it in a covered bin away from water and living spaces.", body),
         P("5. Wash hands every time.", body),
         P("6. Follow local instructions for disposal.", body)]
inner = Table([[Buckets(), steps]], colWidths=[2.7*inch, W-2*M-2.7*inch-18])
inner.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 0)]))
s += [KeepTogether([card("TWO-BUCKET SETUP", [inner])]), Spacer(1, 12)]

# ---------- HYGIENE / CLEANING ----------
s += inventory("HYGIENE", "Per person", [
    ("Toilet paper", "36–48 rolls"), ("Bar soap", "6 bars"), ("Shampoo", "2 bottles"),
    ("Toothpaste", "3 tubes"), ("Spare toothbrushes", "2"), ("Deodorant", "2"),
    ("Feminine products", "90 days, if needed"), ("Baby wipes", "4 packs"),
    ("Diapers and formula", "90 days, if infants")])
s += inventory("CLEANING", "Per household", [
    ("Hand soap", "4 refills"), ("Hand sanitizer", "2 bottles", True), ("Dish soap", "3 bottles"),
    ("Laundry detergent", "90–120 loads"), ("Paper towels", "12 rolls"),
    ("Disinfecting wipes", "4 tubs"), ("Trash bags", "2 boxes"), ("Zip bags", "2 boxes"),
    ("Foil and plastic wrap", "2 rolls each"), ("Rubber gloves", "2 pairs"), ("Scrub brushes", "2")])

# ---------- LIGHT ----------
s += inventory("LIGHT, POWER & COMMS", "Per household. Use LED lights, not candles. Candles start fires.", [
    ("Flashlights", "3", True), ("LED lanterns", "2"), ("Headlamp", "1 per person"),
    ("AA and AAA batteries", "48 each", True), ("C/D batteries", "As needed"),
    ("NOAA weather radio (hand-crank or battery)", "1", True),
    ("USB power banks", "2", True), ("Spare charging cables", "Spares"),
    ("Solar charger", "Optional")])

# ---------- MEDICAL ----------
s += inventory("MEDICAL & SAFETY  ·  PER PERSON", "Per person", [
    ("Prescriptions", "Ask your pharmacist or doctor about an emergency supply", True),
    ("Spare glasses or contacts and solution", "1 set", True),
    ("Written list of medicines, doses, allergies, and doctors", "1", True),
    ("Power plan for medical devices (CPAP, oxygen, hearing aids)", "Check device watts; plan battery capacity or ask your supplier", True)])
s += inventory("MEDICAL & SAFETY  ·  HOUSEHOLD", "Per household", [
    ("First-aid kit", "1", True), ("Bandages, gauze, tape", "Assorted"),
    ("Antiseptic wipes", "2 boxes"), ("Adult pain reliever", "1–2 bottles"),
    ("Child fever medicine", "1, if children"), ("Rehydration solution", "2 packs"),
    ("Thermometer", "1"), ("Cooler and ice packs for medicines that need cold", "1"),
    ("N95 masks", "1 box"), ("Work gloves", "1 pair per adult"),
    ("Insect repellent", "2 bottles"), ("Sunscreen", "2 bottles"),
    ("Fire extinguisher", "1", True), ("Carbon monoxide alarm with battery", "1", True),
    ("Smoke alarm batteries", "Spares")])

# ---------- GO BAG ----------
gb = [("Water you can carry", "On foot: as much as you can manage, plus a filter or tablets. By vehicle: 1 gal per person per day for 3 days."),
      ("No-cook food", "3 days"), ("Medicines, glasses, and medical list", ""),
      ("Copies of IDs, insurance, and important documents", ""), ("Cash in small bills", ""),
      ("Phone, charger, and power bank", ""), ("Flashlight and spare batteries", ""),
      ("Change of clothes and sturdy shoes", ""), ("Written contact list and a family meeting spot", "")]
gbt = Table([[Box(), P("<b>%s</b>" % a, cell), P(b, cell)] for a, b in gb],
            colWidths=[0.22*inch, 2.9*inch, W-2*M-0.22*inch-2.9*inch-18])
gbt.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 0),
                         ("LINEBELOW", (0,0), (-1,-2), 0.4, GREY),
                         ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5)]))
s += [KeepTogether([card("GO BAG  ·  PER PERSON  ·  IF YOU MUST LEAVE", [gbt, Spacer(1, 2),
      P("Everything else on this list stays home.", small)])]), Spacer(1, 12)]

# ---------- OTHER ----------
s += inventory("OTHER", "Per household", [
    ("Tarp", "1"), ("Duct tape", "2 rolls"), ("Tool kit", "1"),
    ("Cash in small bills", "Set aside", True),
    ("Copies of important documents, waterproof bag", "1 packet", True),
    ("Games, books, coloring supplies", "Assorted"),
    ("Pet food, water, and medicine", "90 days, if pets")])

storage = card("STORAGE", [
    P("Store food and water indoors, cool, dry, and off the floor. Garages get too hot.", body),
    P("Write the purchase date on everything.", body),
    P("Use the oldest items first and replace them as you go.", body),
    P("Check allergies, dietary needs, and expiration dates for your household.", body)])
src_rows = [[P("<b>TOPIC</b>", headl), P("<b>SOURCE</b>", headl), P("<b>WEB ADDRESS</b>", headl)],
            [P("Water treatment", cell), P("CDC", cell), P("cdc.gov/water-emergency", cell)],
            [P("Carbon monoxide", cell), P("CDC", cell), P("cdc.gov/carbon-monoxide", cell)],
            [P("Emergency disinfection", cell), P("EPA", cell), P("epa.gov/ground-water-and-drinking-water/<br/>emergency-disinfection-drinking-water", cell)],
            [P("Supply guidance", cell), P("FEMA / Ready.gov", cell), P("ready.gov/kit", cell)],
            [P("Two-bucket toilet", cell), P("Oregon State University Extension", cell), P("extension.oregonstate.edu/catalog/pub/em9334", cell)]]
srct = Table(src_rows, colWidths=[1.6*inch, 2.0*inch, W-2*M-3.6*inch])
srct.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                          ("LINEBELOW", (0,0), (-1,0), 1.2, BLACK),
                          ("LINEBELOW", (0,1), (-1,-1), 0.4, GREY),
                          ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5),
                          ("LEFTPADDING", (0,0), (-1,-1), 3)]))
sources = [Spacer(1, 12), P("SOURCES", h2), Spacer(1, 3), srct]
s += [KeepTogether([storage] + sources)]

doc.build(s)
print("ok")
