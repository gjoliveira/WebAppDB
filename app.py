import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask, request, abort


import logging
import db

import matplotlib.pyplot as plt
from io import BytesIO
import base64

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = {}
    stats['v'] = db.execute('SELECT COUNT(*) as v FROM volcano').fetchone()['v']
    stats['e'] = db.execute('SELECT COUNT(*) as e FROM eruption').fetchone()['e']
    stats['ev'] = db.execute('SELECT COUNT(*) as ev FROM events').fetchone()['ev']
    stats['rv'] = db.execute('SELECT COUNT(*) as rv FROM rocks_volcanos').fetchone()['rv']
    stats['r'] = db.execute('SELECT COUNT(*) as r FROM rocks').fetchone()['r']

    logging.info(stats)

    return render_template('index.html', stats=stats)

@APP.route('/volcanos/')
def list_volcanos():
    volcanos = db.execute(
        '''
        SELECT volcano_number, volcano_name, primary_volcano_type, last_eruption_year,
               latitude, longitude, tectonic_settings, country, region, subregion
        FROM VOLCANO
        ORDER BY volcano_name
        '''
    ).fetchall()
    return render_template('volcanos_list.html', volcanos=volcanos)

@APP.route('/volcanos/number/<number>')
def get_volcano_info_number(number):
    volcano_info_number = db.execute(
        '''
        SELECT * FROM VOLCANO
        WHERE volcano_number = :number
        ''',
        {'number': number}
    ).fetchone()

    return render_template('volcano_info_number.html', volcano_info_number=volcano_info_number)

@APP.route('/volcanos/<name>')
def get_volcano_info(name):
    volcano_info = db.execute(
        '''
        SELECT * FROM VOLCANO
        WHERE volcano_name = :name
        ''',
        {'name': name}
    ).fetchone()


    return render_template('volcano_info.html', volcano_info=volcano_info)

@APP.route('/rocks/')
def list_rocks():
    rocks = db.execute(
        '''
        SELECT Rocks,rock_ID
        FROM ROCKS
        ORDER BY rock_ID
        '''
    ).fetchall()
    return render_template('rocks_list.html', rocks=rocks)

@APP.route('/rocks/<volcano_name>')
def rocks_for_volcano(volcano_name):
        # Execute a consulta SQL
        result = db.execute('''
        SELECT r.rocks
        FROM rocks r
        JOIN rocks_volcanos rv ON r.rock_ID = rv.rock_ID
        JOIN volcano v ON v.volcano_number = rv.volcano_number
        WHERE v.volcano_name = :name
        ''', {'name': volcano_name}).fetchall()

        # Extrair os dados para a página HTML
        rocks = [row['rocks'] for row in result]

        return render_template('rocks_for_volcano.html', volcano_name=volcano_name, rocks=rocks)

@APP.route('/volcanos/country/<country>')
def get_volcano_country(country):
        volcano_info = db.execute(
            '''
            SELECT * FROM VOLCANO
            WHERE Country = :country
            ORDER by volcano_name
            ''',
            {'country': country}
        ).fetchall()

        if volcano_info is None:
            logging.warning(f"No volcano information found for country: {country}")
            abort(404)


        return render_template('volcano_by_country.html', volcano_info=volcano_info, country=country)


@APP.route('/eruptions/')
def list_eruption():
        eruption = db.execute(
        '''
        SELECT volcano_number, eruption_number,eruption_category,area_of_activity,vei,
        eruption_start_year,evidence_method_dating,end_year,end_month
        FROM ERUPTION
        ORDER BY eruption_number
        '''
        ).fetchall()
        return render_template('eruption_list.html', eruption=eruption)

@APP.route('/eruptions/<number>')
def get_eruption_info_number(number):
            eruption_info_number = db.execute(
            '''
            SELECT * FROM ERUPTION
            WHERE eruption_number = :number
            ''',
            {'number': number}
            ).fetchone()

            return render_template('eruption_info_number.html', eruption_info_number=eruption_info_number)

@APP.route('/eruption/<country>')
def eruptions_by_country(country):
    page = request.args.get('page', default=1, type=int)
    items_per_page = 20
    eruptions = db.execute(
        '''
        SELECT volcano_name, eruption_start_year, end_year, vei, area_of_activity, event_type
        FROM VOLCANO v
        JOIN ERUPTION e ON e.volcano_number = v.volcano_number
        JOIN EVENTS ev ON ev.eruption_number = e.eruption_number
        WHERE v.country = :country
        ORDER BY eruption_start_year
        ''',
        {'country': country}
    ).fetchall()

    #to make the pagination:

    total_items = len(eruptions)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    paginated_eruptions = eruptions[start_index:end_index]

    return render_template('eruption_event.html', country=country, eruptions=paginated_eruptions, page=page, total_pages=total_pages, total_items = total_items)

@APP.route('/eruption')
@APP.route('/eruption/')
def eruptions_between_years():
    start_year = request.args.get('start_year')
    end_year = request.args.get('end_year')

    try:
        start_year, end_year = int(start_year), int(end_year)
    except (ValueError, TypeError):
        return "Invalid input. Please provide valid numeric start and end years."

    eruptions = db.execute(
    '''
    SELECT volcano_name, eruption_start_year, primary_volcano_type, country, region
    FROM eruption e
    JOIN volcano v ON e.volcano_number = v.volcano_number
    WHERE e.eruption_start_year BETWEEN :start_year AND :end_year
    order by eruption_start_year asc, country
    ''',
    {'start_year': start_year, 'end_year': end_year}
    ).fetchall()

    return render_template('eruption.html', start_year=start_year, end_year=end_year, eruptions=eruptions)


@APP.route('/events/')
def list_events():
        events = db.execute(
        '''
        SELECT eruption_number,event_number,event_type,event_date_year,event_date_month,
        event_date_day
        FROM EVENTS
        ORDER BY eruption_number
        '''
        ).fetchall()
        return render_template('events_list.html', events=events)

@APP.route('/events/<number>')
def get_events_info_number(number):
            events_info_number = db.execute(
            '''
            SELECT * FROM EVENTS
            WHERE event_number = :number
            ''',
            {'number': number}
            ).fetchone()

            return render_template('events_info_number.html', events_info_number=events_info_number)

@APP.route('/eruption/vei/<vei>')
def eruptions_vei(vei):
    page = request.args.get('page', default=1, type=int)
    items_per_page = 20
    eruptions_vei = db.execute(
        '''
        SELECT vei,volcano_name, eruption_start_year, end_year, area_of_activity, event_type
        FROM ERUPTION e
        JOIN VOLCANO v ON e.volcano_number = v.volcano_number
        JOIN EVENTS ev ON ev.eruption_number = e.eruption_number
        WHERE e.vei = :vei
        ORDER BY v.volcano_name
        ''',
        {'vei': vei}
    ).fetchall()

    #to make the pagination:

    total_items = len(eruptions_vei)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    paginated_eruptions = eruptions_vei[start_index:end_index]

    return render_template('eruptions_vei.html', vei=vei, eruptions_vei=paginated_eruptions, page=page, total_pages=total_pages, total_items = total_items)

@APP.route('/volcanos/graph')
def volcano_graph():
        chart_data = db.execute('''
        SELECT volcano_name, count(*) as eruption_count
        FROM eruption
        JOIN volcano ON eruption.volcano_number = volcano.volcano_number
        GROUP BY volcano.volcano_number
        ORDER BY eruption_count DESC
        LIMIT 20
        ''').fetchall()

        return render_template('volcano_graph.html', chart_data=chart_data)

@APP.route('/volcanos/chart')
def volcano_chart():
            result = db.execute('''
            SELECT count(*) as num_volcanos, country
            FROM volcano
            GROUP BY country
            ORDER BY num_volcanos DESC
            LIMIT 10
            ''').fetchall()

            # Extrair dados para o gráfico
            countries = [row['country'] for row in result]
            num_volcanos = [row['num_volcanos'] for row in result]


            plt.figure(figsize=(10, 6))
            plt.pie(num_volcanos, labels=countries, autopct='%1.1f%%', startangle=140)
            plt.title('Top 10 Countries with the Most Volcanos \n\n')
            plt.axis('equal')

            # Converter o gráfico em uma imagem para ser incorporada na página
            image_stream = BytesIO()
            plt.savefig(image_stream, format='png')
            image_stream.seek(0)
            img_str = base64.b64encode(image_stream.read()).decode('utf-8')

            plt.close()

            return render_template('volcano_chart.html', chart_image=img_str)
