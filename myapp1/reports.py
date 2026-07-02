"""
reports.py  -  SnackCart PDF Report Generator
Matches real Order model fields:
  customer (FK User), seller (FK User), product (FK Product),
  food_price, platform_fee, delivery_charge, total_amount,
  payment_mode (online/cod), payment_status, order_status,
  seller_earning, commission_percent, razorpay_order_id, created_at
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable,
)
from reportlab.pdfgen import canvas as rl_canvas

C_ORANGE  = colors.HexColor('#FF6B35')
C_ORANGE2 = colors.HexColor('#FF8C5A')
C_DARK    = colors.HexColor('#1C1C2E')
C_MGRAY   = colors.HexColor('#888888')
C_WHITE   = colors.white
TH_BG     = colors.HexColor('#FF6B35')
TR_ALT    = colors.HexColor('#FFF3EC')
TR_TOTAL  = colors.HexColor('#FFE4D0')


class BrandedCanvas(rl_canvas.Canvas):
    def __init__(self, *args, report_title='Report', **kwargs):
        super().__init__(*args, **kwargs)
        self.report_title = report_title
        self._pages = []

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._pages)
        for state in self._pages:
            self.__dict__.update(state)
            self._draw_chrome(total)
            super().showPage()
        super().save()

    def _draw_chrome(self, total_pages):
        self.saveState()
        w, h = A4
        # Header band
        self.setFillColor(C_ORANGE)
        self.rect(0, h - 22*mm, w, 22*mm, fill=1, stroke=0)
        # Diagonal accent
        self.setFillColor(C_ORANGE2)
        path = self.beginPath()
        path.moveTo(w - 65*mm, h)
        path.lineTo(w, h)
        path.lineTo(w, h - 22*mm)
        path.lineTo(w - 85*mm, h - 22*mm)
        path.close()
        self.drawPath(path, fill=1, stroke=0)
        # Logo
        self.setFillColor(C_WHITE)
        self.setFont('Helvetica-Bold', 17)
        self.drawString(12*mm, h - 10*mm, 'SnackCart')
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#FFCDB2'))
        self.drawString(12*mm, h - 16.5*mm, 'Home Food Marketplace Platform')
        # Report title right-aligned
        self.setFillColor(C_WHITE)
        self.setFont('Helvetica-Bold', 13)
        self.drawRightString(w - 12*mm, h - 9.5*mm, self.report_title)
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#FFCDB2'))
        self.drawRightString(w - 12*mm, h - 16.5*mm,
            'Generated: ' + datetime.now().strftime('%d %b %Y  %I:%M %p'))
        # Separator
        self.setStrokeColor(C_ORANGE)
        self.setLineWidth(0.5)
        self.line(0, h - 23*mm, w, h - 23*mm)
        # Footer
        self.setFillColor(C_DARK)
        self.rect(0, 0, w, 11*mm, fill=1, stroke=0)
        self.setFillColor(colors.HexColor('#AAAAAA'))
        self.setFont('Helvetica', 7)
        self.drawString(12*mm, 4*mm, 'SnackCart  |  Confidential  |  www.snackcart.com')
        self.setFillColor(C_WHITE)
        self.setFont('Helvetica-Bold', 7)
        self.drawRightString(w - 12*mm, 4*mm, f'Page {self._pageNumber} of {total_pages}')
        self.restoreState()


def _styles():
    base = getSampleStyleSheet()
    def add(name, **kw):
        base.add(ParagraphStyle(name=name, **kw))
    add('R_Title',   fontSize=22, fontName='Helvetica-Bold', textColor=C_DARK, alignment=TA_CENTER, spaceAfter=2)
    add('R_Sub',     fontSize=9,  fontName='Helvetica',      textColor=C_MGRAY, alignment=TA_CENTER, spaceAfter=14)
    add('R_Section', fontSize=12, fontName='Helvetica-Bold', textColor=C_ORANGE, spaceBefore=12, spaceAfter=5)
    add('R_TH',      fontSize=8,  fontName='Helvetica-Bold', textColor=C_WHITE, alignment=TA_CENTER)
    add('R_TD',      fontSize=7.5,fontName='Helvetica',      textColor=C_DARK,  alignment=TA_LEFT)
    add('R_CardVal', fontSize=20, fontName='Helvetica-Bold', textColor=C_DARK,  alignment=TA_CENTER)
    add('R_CardLbl', fontSize=7.5,fontName='Helvetica',      textColor=C_MGRAY, alignment=TA_CENTER)
    add('R_Note',    fontSize=7,  fontName='Helvetica-Oblique', textColor=C_MGRAY)
    return base


def _card_row(cards):
    s = _styles()
    n = len(cards)
    cell_w = 170 * mm / n
    cells = []
    for label, value, bg in cards:
        inner = Table(
            [[Paragraph(str(value), s['R_CardVal'])],
             [Paragraph(label, s['R_CardLbl'])]],
            colWidths=[cell_w - 6*mm],
        )
        inner.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), colors.HexColor(bg)),
            ('TOPPADDING',    (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING',   (0, 0), (-1, -1), 4),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
        ]))
        cells.append(inner)
    row = Table([cells], colWidths=[cell_w] * n)
    row.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    return row


def _data_table(headers, rows, col_widths, highlight_last=False):
    s = _styles()
    data = [[Paragraph(h, s['R_TH']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c) if c is not None else '-', s['R_TD']) for c in row])
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ('BACKGROUND',    (0, 0), (-1, 0),  TH_BG),
        ('LINEBELOW',     (0, 0), (-1, 0),  1.5, C_ORANGE),
        ('TOPPADDING',    (0, 0), (-1, 0),  7),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  7),
        ('ALIGN',         (0, 0), (-1, 0),  'CENTER'),
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 7.5),
        ('TOPPADDING',    (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID',          (0, 0), (-1, -1), 0.35, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [C_WHITE, TR_ALT]),
    ]
    if highlight_last and len(data) > 1:
        cmds += [
            ('BACKGROUND', (0, -1), (-1, -1), TR_TOTAL),
            ('FONTNAME',   (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]
    tbl.setStyle(TableStyle(cmds))
    return tbl


def _f(val):
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


# ═════════════════════════════════════════════════════════════════════════════
# ORDER REPORT
# ═════════════════════════════════════════════════════════════════════════════
def generate_order_report_pdf(orders, date_range='All Time'):
    orders = list(orders)
    s = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        topMargin=28*mm, bottomMargin=18*mm,
        leftMargin=15*mm, rightMargin=15*mm)
    story = []

    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('Order Report', s['R_Title']))
    story.append(Paragraph(f'Period: {date_range}  |  Total Orders: {len(orders)}', s['R_Sub']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=C_ORANGE, spaceAfter=8))

    total      = len(orders)
    revenue    = sum(_f(o.total_amount) for o in orders)
    delivered  = sum(1 for o in orders if o.order_status in ('Delivered', 'Completed'))
    cancelled  = sum(1 for o in orders if o.order_status == 'Cancelled')
    pending    = sum(1 for o in orders if o.order_status == 'Pending')
    paid_cnt   = sum(1 for o in orders if o.payment_status == 'Paid')
    cod_cnt    = sum(1 for o in orders if o.payment_mode == 'cod')
    online_cnt = sum(1 for o in orders if o.payment_mode == 'online')
    cod_rev    = sum(_f(o.total_amount) for o in orders if o.payment_mode == 'cod')
    online_rev = sum(_f(o.total_amount) for o in orders if o.payment_mode == 'online')

    story.append(Paragraph('Summary', s['R_Section']))
    story.append(_card_row([
        ('Total Orders',  str(total),           '#EBF5FB'),
        ('Total Revenue', f'Rs.{revenue:,.0f}', '#EAFAF1'),
        ('Delivered',     str(delivered),       '#E9F7EF'),
        ('Cancelled',     str(cancelled),       '#FDEDEC'),
    ]))
    story.append(Spacer(1, 4*mm))
    story.append(_card_row([
        ('Pending',       str(pending),         '#FEF9E7'),
        ('Paid Orders',   str(paid_cnt),        '#EAFAF1'),
        ('COD Orders',    str(cod_cnt),         '#F5EEF8'),
        ('Online Orders', str(online_cnt),      '#FFF3E8'),
    ]))
    story.append(Spacer(1, 8*mm))

    # Status breakdown
    story.append(Paragraph('Order Status Breakdown', s['R_Section']))
    statuses = ['Pending','Accepted','Preparing','Ready for Pickup',
                'Out for Delivery','Delivered','Completed','Cancelled']
    s_rows = []
    for st in statuses:
        cnt = sum(1 for o in orders if o.order_status == st)
        rev = sum(_f(o.total_amount) for o in orders if o.order_status == st)
        pct = f'{cnt/total*100:.1f}%' if total else '0%'
        s_rows.append([st, str(cnt), f'Rs.{rev:,.2f}', pct])
    s_rows.append(['TOTAL', str(total), f'Rs.{revenue:,.2f}', '100%'])
    story.append(_data_table(
        ['Status', 'Count', 'Revenue', '% Share'], s_rows,
        col_widths=[72*mm, 28*mm, 44*mm, 26*mm], highlight_last=True))
    story.append(Spacer(1, 8*mm))

    # Payment mode breakdown
    story.append(Paragraph('Payment Mode Breakdown', s['R_Section']))
    p_rows = [
        ['Cash on Delivery (COD)', str(cod_cnt),    f'Rs.{cod_rev:,.2f}',    f'{cod_cnt/total*100:.1f}%'    if total else '0%'],
        ['Online - Razorpay',      str(online_cnt), f'Rs.{online_rev:,.2f}', f'{online_cnt/total*100:.1f}%' if total else '0%'],
        ['TOTAL',                  str(total),      f'Rs.{revenue:,.2f}',    '100%'],
    ]
    story.append(_data_table(
        ['Mode', 'Orders', 'Amount', '% Share'], p_rows,
        col_widths=[72*mm, 28*mm, 44*mm, 26*mm], highlight_last=True))
    story.append(Spacer(1, 10*mm))

    # Detail table
    story.append(Paragraph('Order Details', s['R_Section']))
    story.append(Paragraph('Complete list of all orders in this report.', s['R_Note']))
    story.append(Spacer(1, 3*mm))
    d_hdrs = ['#', 'ID', 'Customer', 'Seller', 'Product', 'Qty',
              'Amount', 'Mode', 'Pay Status', 'Order Status', 'Date']
    d_rows = []
    for i, o in enumerate(orders, 1):
        d_rows.append([
            str(i),
            f'#{o.id}',
            (o.customer.name[:14] if o.customer else '-'),
            (o.seller.name[:14]   if o.seller   else '-'),
            (o.product.product_name[:16] if o.product else '-'),
            str(o.quantity),
            f'Rs.{_f(o.total_amount):,.0f}',
            ('Online' if o.payment_mode == 'online' else 'COD'),
            str(o.payment_status or '-'),
            str(o.order_status   or '-'),
            (o.created_at.strftime('%d/%m/%y') if o.created_at else '-'),
        ])
    story.append(_data_table(d_hdrs, d_rows,
        col_widths=[7*mm,11*mm,19*mm,19*mm,22*mm,
                    7*mm,17*mm,13*mm,16*mm,22*mm,17*mm]))

    doc.build(story,
        canvasmaker=lambda *a, **kw: BrandedCanvas(*a, report_title='Order Report', **kw))
    buf.seek(0)
    return buf


# ═════════════════════════════════════════════════════════════════════════════
# PAYMENT REPORT
# ═════════════════════════════════════════════════════════════════════════════
def generate_payment_report_pdf(orders, date_range='All Time'):
    orders = list(orders)
    s = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        topMargin=28*mm, bottomMargin=18*mm,
        leftMargin=15*mm, rightMargin=15*mm)
    story = []

    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('Payment Report', s['R_Title']))
    story.append(Paragraph(f'Period: {date_range}  |  Transactions: {len(orders)}', s['R_Sub']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=C_ORANGE, spaceAfter=8))

    paid_o    = [o for o in orders if o.payment_status == 'Paid']
    pending_o = [o for o in orders if o.payment_status == 'Pending']
    failed_o  = [o for o in orders if o.payment_status == 'Failed']
    refund_o  = [o for o in orders if o.payment_status == 'Refunded']

    collected   = sum(_f(o.total_amount)      for o in paid_o)
    food_total  = sum(_f(o.food_price)         for o in paid_o)
    plat_total  = sum(_f(o.platform_fee)       for o in paid_o)
    dlv_total   = sum(_f(o.delivery_charge)    for o in paid_o)
    earn_total  = sum(_f(o.seller_earning)     for o in paid_o)
    comm_total  = sum(_f(o.food_price) * _f(o.commission_percent) / 100 for o in paid_o)
    refund_amt  = sum(_f(o.total_amount)       for o in refund_o)
    total_all   = sum(_f(o.total_amount)       for o in orders)
    avg_val     = collected / len(paid_o) if paid_o else 0
    online_cnt  = sum(1 for o in orders if o.payment_mode == 'online')
    cod_cnt     = sum(1 for o in orders if o.payment_mode == 'cod')

    story.append(Paragraph('Financial Overview', s['R_Section']))
    story.append(_card_row([
        ('Total Collected', f'Rs.{collected:,.0f}',  '#EAFAF1'),
        ('Platform Fees',   f'Rs.{plat_total:,.0f}', '#EBF5FB'),
        ('Delivery Revenue',f'Rs.{dlv_total:,.0f}',  '#FEF9E7'),
        ('Commission Earned',f'Rs.{comm_total:,.0f}','#F5EEF8'),
    ]))
    story.append(Spacer(1, 4*mm))
    story.append(_card_row([
        ('Paid Orders',    str(len(paid_o)),    '#EAFAF1'),
        ('Pending',        str(len(pending_o)), '#FEF9E7'),
        ('Refunded',       str(len(refund_o)),  '#FDEDEC'),
        ('Avg Order Value',f'Rs.{avg_val:,.0f}','#EBF5FB'),
    ]))
    story.append(Spacer(1, 8*mm))

    # Revenue breakdown
    story.append(Paragraph('Revenue Breakdown  (Paid Orders Only)', s['R_Section']))
    n = len(paid_o) if paid_o else 1
    rev_rows = [
        ['Food Price (Gross)',           f'Rs.{food_total:,.2f}', f'Rs.{food_total/n:,.2f}',  f'{food_total/collected*100:.1f}%'  if collected else '0%'],
        ['Platform Fee (Rs.10/order)',   f'Rs.{plat_total:,.2f}', f'Rs.{plat_total/n:,.2f}',  f'{plat_total/collected*100:.1f}%'  if collected else '0%'],
        ['Delivery Charge (Rs.40/order)',f'Rs.{dlv_total:,.2f}',  f'Rs.{dlv_total/n:,.2f}',   f'{dlv_total/collected*100:.1f}%'   if collected else '0%'],
        ['Seller Earnings (paid out)',   f'Rs.{earn_total:,.2f}', f'Rs.{earn_total/n:,.2f}',  '-'],
        ['Commission (10%)',             f'Rs.{comm_total:,.2f}', f'Rs.{comm_total/n:,.2f}',  '-'],
        ['TOTAL COLLECTED',              f'Rs.{collected:,.2f}',  f'Rs.{avg_val:,.2f}',        '100%'],
    ]
    story.append(_data_table(
        ['Component', 'Total', 'Per Order (Avg)', '% of Revenue'],
        rev_rows, col_widths=[72*mm, 36*mm, 36*mm, 30*mm], highlight_last=True))
    story.append(Spacer(1, 8*mm))

    # Payment status summary
    story.append(Paragraph('Payment Status Summary', s['R_Section']))
    nn = len(orders)
    ps_rows = [
        ['Paid',     str(len(paid_o)),    f'Rs.{collected:,.2f}',                                    f'{len(paid_o)/nn*100:.1f}%'    if nn else '0%'],
        ['Pending',  str(len(pending_o)), f'Rs.{sum(_f(o.total_amount) for o in pending_o):,.2f}',   f'{len(pending_o)/nn*100:.1f}%' if nn else '0%'],
        ['Failed',   str(len(failed_o)),  f'Rs.{sum(_f(o.total_amount) for o in failed_o):,.2f}',    f'{len(failed_o)/nn*100:.1f}%'  if nn else '0%'],
        ['Refunded', str(len(refund_o)),  f'Rs.{refund_amt:,.2f}',                                   f'{len(refund_o)/nn*100:.1f}%'  if nn else '0%'],
        ['TOTAL',    str(nn),             f'Rs.{total_all:,.2f}',                                    '100%'],
    ]
    story.append(_data_table(
        ['Status', 'Count', 'Amount', '% Share'],
        ps_rows, col_widths=[48*mm, 32*mm, 58*mm, 32*mm], highlight_last=True))
    story.append(Spacer(1, 10*mm))

    # Transaction detail
    story.append(Paragraph('Transaction Details', s['R_Section']))
    story.append(Paragraph('Full transaction log for the selected period.', s['R_Note']))
    story.append(Spacer(1, 3*mm))
    t_hdrs = ['#', 'Order ID', 'Customer', 'Total', 'Food', 'Platform',
              'Delivery', 'Mode', 'Pay Status', 'Razorpay ID', 'Date']
    t_rows = []
    for i, o in enumerate(orders, 1):
        rzp = (str(o.razorpay_order_id)[:16] if o.razorpay_order_id else '-')
        t_rows.append([
            str(i),
            f'#{o.id}',
            (o.customer.name[:14] if o.customer else '-'),
            f'Rs.{_f(o.total_amount):,.0f}',
            f'Rs.{_f(o.food_price):,.0f}',
            f'Rs.{_f(o.platform_fee):,.0f}',
            f'Rs.{_f(o.delivery_charge):,.0f}',
            ('Online' if o.payment_mode == 'online' else 'COD'),
            str(o.payment_status or '-'),
            rzp,
            (o.created_at.strftime('%d/%m/%y') if o.created_at else '-'),
        ])
    story.append(_data_table(t_hdrs, t_rows,
        col_widths=[7*mm,13*mm,20*mm,15*mm,14*mm,
                    15*mm,14*mm,13*mm,16*mm,24*mm,13*mm]))

    doc.build(story,
        canvasmaker=lambda *a, **kw: BrandedCanvas(*a, report_title='Payment Report', **kw))
    buf.seek(0)
    return buf
