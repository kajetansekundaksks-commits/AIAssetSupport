def build_html_email(brief_text):

    html = f"""
    <html>
    <body style="
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        padding: 20px;
    ">

        <div style="
            max-width: 900px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
        ">

            <h1 style="color: #1f2937;">
                Daily Investor Brief
            </h1>

            <pre style="
                white-space: pre-wrap;
                font-family: Arial, sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: #111827;
            ">{brief_text}</pre>

        </div>

    </body>
    </html>
    """

    return html