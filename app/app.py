import argparse
import multiprocessing
import time
import sys
from threading import Thread

import nltk
import webview
from dash import Dash, html, page_container
from dash.dcc import Location
from dash_bootstrap_components import NavbarSimple, NavItem, NavLink, themes
from utils import database as db

PAGE_TITLE_BASE = "FysioPraxis"
PAGE_TITLE_SEPERATOR = " - "

app = Dash(
    __name__,
    title=PAGE_TITLE_BASE,
    use_pages=True,
    external_stylesheets=[themes.BOOTSTRAP],
    # Remove errors due callbacks depending on unrendered DOM elements.
    suppress_callback_exceptions=True,
)

app.layout = html.Div([
    Location(id='url', refresh=True),
    NavbarSimple(
        children=[
            NavItem(NavLink("Grafieken", href="/grafieken")),
            NavItem(NavLink("Pagina Resultaten", href="/pagina_resultaten")),
            NavItem(NavLink("PDF's", href="/pdf_beheren")),
            NavItem(NavLink("Woorden", href="/woorden_beheren")),
            NavItem(NavLink("Help", href="/help")),
        ],
        brand=html.Span([
            html.Img(
                src='/assets/book-svgrepo-com(3).svg',
                height="50px",
                style={'marginRight': '10px'}
            ),
            "FysioPraxis Analyse Platform"
        ]),
        brand_href="/",
        color="primary",
        dark=True,
    ),
    page_container,
])


def register_callbacks():
    from pages.magazine import register_magazine_callbacks
    register_magazine_callbacks(app)
    from pages.dashboard import register_dashboard_callbacks
    register_dashboard_callbacks(app)
    from pages.page_results import register_page_result_callbacks
    register_page_result_callbacks(app)
    from pages.words.main import register_words_callbacks
    register_words_callbacks(app)
    from pages.faq.help import register_help_callbacks
    register_help_callbacks(app)


if __name__ == '__main__':
    if hasattr(sys, 'frozen'):
        multiprocessing.freeze_support()

    register_callbacks()
    nltk.download('stopwords')

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode with no webview'
    )
    args = parser.parse_args()

    db.init_db(args.debug)

    if args.debug:
        print("Debug mode enabled, webview is disabled.")
        app.run(debug=True)
    else:
        # Thread to launch the server
        t = Thread(
            target=app.run,
            daemon=True  # Automatically close when exiting the app
        )

        # Initiate the server
        t.start()

        # 3 seconds pause to make sure the server is up
        time.sleep(3)

        # Webview start (for automatically starting the app in a separate view)
        try:
            webview.create_window(
                'FysioPraxis Analyse App',
                'http://127.0.0.1:8050',
                width=1920,
                height=1080,
                maximized=True,
                confirm_close=True,
                zoomable=True,
                min_size=(640, 720)
            )
        except Exception as e:
            print(f"Error opening webview: {e}")

        webview.start()
