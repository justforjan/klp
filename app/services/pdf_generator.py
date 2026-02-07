from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors


def generate_favorites_pdf(events_data: dict, exhibitions_data: dict = None) -> BytesIO:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=12,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
        spaceBefore=12,
    )

    event_title_style = ParagraphStyle(
        'EventTitle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=4,
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=3,
    )

    story = []

    story.append(Paragraph("Meine Favoriten", title_style))
    story.append(Paragraph(f"Kulturelle Landpartie", normal_style))
    story.append(Paragraph(f"Exportiert am: {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}", normal_style))
    story.append(Spacer(1, 15))

    has_content = False

    if exhibitions_data and len(exhibitions_data) > 0:
        has_content = True
        story.append(Paragraph("Favorisierte Ausstellungen", heading_style))
        story.append(Spacer(1, 6))

        for location_data in exhibitions_data.values():
            location = location_data['location']
            exhibitions = location_data['exhibitions']

            story.append(Paragraph(f"<b>{location['name']}</b>", event_title_style))
            if location.get('subtitle'):
                story.append(Paragraph(location['subtitle'], normal_style))
            story.append(Spacer(1, 4))

            for exhibition in exhibitions:
                story.append(Paragraph(f"• <b>{exhibition['name']}</b>", normal_style))
                story.append(Paragraph(f"  von {exhibition['artist']}", normal_style))
                if exhibition.get('description'):
                    story.append(Paragraph(f"  <i>{exhibition['description']}</i>", normal_style))
                story.append(Spacer(1, 6))

            story.append(Spacer(1, 12))

    if events_data and len(events_data) > 0:
        has_content = True
        if exhibitions_data and len(exhibitions_data) > 0:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Favorisierte Termine", heading_style))
            story.append(Spacer(1, 6))

        sorted_dates = sorted(events_data.keys())
        for date_str in sorted_dates:
            date_obj = datetime.fromisoformat(date_str + 'T00:00:00')
            formatted_date = date_obj.strftime('%A, %d. %B %Y')

            story.append(Paragraph(formatted_date, heading_style))
            story.append(Spacer(1, 6))

            day_events = events_data[date_str]

            for item in day_events:
                occurrence = item['occurrence']
                event = item['event']
                location = item['location']

                start_time = datetime.fromisoformat(occurrence['start_datetime']).strftime('%H:%M')

                event_name = event['name']
                if occurrence.get('is_cancelled'):
                    event_name = f"[ABGESAGT] {event_name}"

                story.append(Paragraph(f"<b>{start_time} Uhr - {event_name}</b>", event_title_style))

                if event.get('description'):
                    story.append(Paragraph(event['description'], normal_style))

                location_info = []
                location_info.append(f"<b>Ort:</b> {location['name']}")

                if location.get('subtitle'):
                    location_info.append(location['subtitle'])

                if location.get('address'):
                    location_info.append(f"<b>Adresse:</b> {location['address']}")

                if location.get('phone'):
                    location_info.append(f"<b>Telefon:</b> {location['phone']}")

                if location.get('email'):
                    location_info.append(f"<b>E-Mail:</b> {location['email']}")

                for info in location_info:
                    story.append(Paragraph(info, normal_style))

                payment_info = []
                if event['payment_type'] == 'free':
                    payment_info.append("Eintritt frei")
                elif event['payment_type'] == 'hat_collection':
                    payment_info.append("Hutkasse")
                elif event['payment_type'] == 'fixed_price' and event.get('entry_price'):
                    payment_info.append(f"{event['entry_price']} €")
                elif event['payment_type'] == 'hat_plus_materials':
                    text = "Hutkasse"
                    if event.get('material_cost'):
                        text += f" + {event['material_cost']} € Material"
                    payment_info.append(text)

                if event.get('booking_required'):
                    payment_info.append("Anmeldung erforderlich")

                if payment_info:
                    story.append(Paragraph(f"<b>Eintritt:</b> {' | '.join(payment_info)}", normal_style))

                if event.get('organizer'):
                    story.append(Paragraph(f"<b>Veranstalter:</b> {event['organizer']}", normal_style))

                story.append(Spacer(1, 12))

            story.append(Spacer(1, 6))

    if not has_content:
        story.append(Paragraph("Keine Favoriten vorhanden.", normal_style))

    doc.build(story)

    buffer.seek(0)
    return buffer
