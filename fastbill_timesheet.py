import datetime
import requests
import sys
from os import environ
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


class FastBillAPIController:
    def __init__(self, api_username, api_key, api_url='https://my.fastbill.com/api/1.0/api.php'):
        self.api_username = api_username
        self.api_key = api_key
        self.api_url = api_url

    def _post(self, payload, offset=0, results=None):
        all_results = results if results else []
        payload['OFFSET'] = offset
        payload['LIMIT'] = 100
        r = requests.post(url=self.api_url, auth=(self.api_username, self.api_key), json=payload)
        this_result = r.json()
        this_response = next(
            iter(this_result['RESPONSE'].values()))  # result has only one response in dict, get the first / only one
        all_results.extend(this_response)
        if len(this_response) >= payload['LIMIT']:
            self._post(payload, offset + payload['LIMIT'], results=all_results)
        return all_results

    def _get_service(self, service, year_month=None, customer_id=None, project_id=None):
        payload = {'SERVICE': service,
                   'Filter': {}
                   }
        year, month = map(int, year_month.split("-"))
        start_date = datetime.date(year, month, 1)
        end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)

        print(f'{start_date.isoformat()=}')
        print(f'{end_date.isoformat()=}')

        payload['Filter']['START_DATE'] = start_date.isoformat()
        payload['Filter']['END_DATE'] = end_date.isoformat()

        if customer_id:
            payload['Filter']['CUSTOMER_ID'] = customer_id
        if project_id:
            payload['Filter']['PROJECT_ID'] = project_id

        return self._post(payload=payload)

    def get_times_per_month(self, year_month, customer_id=None, project_id=None):
        return self._get_service(service='time.get',
                                 year_month=year_month,
                                 customer_id=customer_id,
                                 project_id=project_id)


def get_last_month():
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    return last_month.strftime("%Y-%m")


def create_pdf(filename, data, title, username=environ.get('USERNAME', '')):

    month_sum_minutes = sum(int(row['BILLABLE_MINUTES']) for row in data)
    month_sum_hours = str(datetime.timedelta(minutes=month_sum_minutes))[:-3]
    month_sum_hours_decimal = round(month_sum_minutes/60, 2)

    header = [
        ['Datum', 'Beginn', 'Ende', 'Dauer', 'Tätigkeitsbeschreibung'],
        [],
    ]

    data_list = []
    for row in data:
        data_list.append([
            row['DATE'][:10],
            row['START_TIME'][11:-3],
            row['END_TIME'][11:-3],
            row['BILLABLE_MINUTES'],
            row['COMMENT'],
        ])

    final_data = header + sorted(data_list)

    doc = SimpleDocTemplate(f"{filename}.pdf",
                            pagesize=A4,
                            rightMargin=30,
                            leftMargin=30,
                            topMargin=30,
                            bottomMargin=18)
    doc.pagesize = portrait(A4)
    elements = []

    style = TableStyle([('ALIGN', (1, 1), (-2, -2), 'RIGHT'),
                        ('TEXTCOLOR', (1, 1), (-2, -2), colors.red),
                        ('VALIGN', (0, 0), (0, -1), 'TOP'),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
                        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
                        ('TEXTCOLOR', (0, -1), (-1, -1), colors.green),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                        ])

    # Configure style and word wrap
    s = getSampleStyleSheet()
    s = s["BodyText"]
    s.wordWrap = 'CJK'
    data2 = [[Paragraph(cell, s) for cell in row] for row in final_data]
    t = Table(data2, colWidths=[70, 45, 45, 45, 350])
    t.setStyle(style)

    # Send the data and build the file
    title_text = f"Leistungsnachweis: {title} - {username}"
    title_style = getSampleStyleSheet()["Heading1"]
    title_paragraph = Paragraph(title_text, title_style)
    elements.append(title_paragraph)
    elements.append(Spacer(1, 12))

    elements.append(t)

    style_sheet = getSampleStyleSheet()
    elements.append(Spacer(1, 12))

    sum_minutes = Paragraph(f'Summe Minuten: {month_sum_minutes}', style_sheet['BodyText'])
    sum_hours = Paragraph(f'Summe Stunden (real): {month_sum_hours}', style_sheet['BodyText'])
    sum_hours_dec = Paragraph(f'Summe Stunden (dec): {month_sum_hours_decimal}', style_sheet['BodyText'])

    elements.extend([sum_minutes, Spacer(1, 6), sum_hours, Spacer(1, 6), sum_hours_dec, Spacer(1, 12)])

    date_line = Paragraph('Datum: ' + '_' * 35 , style_sheet['BodyText'])
    signature_line = Paragraph('Unterschrift: ' + '_' * 35, style_sheet['BodyText'])

    elements.extend([date_line, Spacer(1, 6), signature_line])

    doc.build(elements)


def main():
    fbc = FastBillAPIController(api_username=environ.get('API_USER'), api_key=environ.get('API_KEY'))

    project_id = sys.argv[1]

    if len(sys.argv) > 2:
        year_month = sys.argv[2]
    else:
        year_month = get_last_month()

    data = fbc.get_times_per_month(year_month=year_month, project_id=project_id)
    create_pdf(filename=f'Leistungsnachweis_Projekt_{project_id}_{year_month}_{environ.get("USERNAME","")}',
               data=data,
               title=year_month
               )


if __name__ == '__main__':
    main()
