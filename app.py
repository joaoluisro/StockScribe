from flask import Flask, request, render_template_string, jsonify, render_template
import pandas as pd
import traceback
import certifi
import urllib.request
import ssl


app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

# Dictionary of indices, their Wikipedia URLs, and table indices (0-based) to fetch the list of stocks
index_info = {
    "S&P 500": {"url": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", "table_index": 0},
    "Dow Jones": {"url": "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average", "table_index": 2},
    "NASDAQ 100": {"url": "https://en.wikipedia.org/wiki/NASDAQ-100", "table_index": 4},
    "FTSE 100": {"url": "https://en.wikipedia.org/wiki/FTSE_100_Index", "table_index": 4},
    "DAX": {"url": "https://en.wikipedia.org/wiki/DAX", "table_index": 4}
}

def fetch_index_constituents(index_name):
    index_data = index_info.get(index_name)
    if not index_data:
        return None, f"Index '{index_name}' is not supported."

    try:
        url = index_data["url"]
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        # Fetch the raw HTML with urllib and the custom SSL context
        with urllib.request.urlopen(url, context=ssl_context) as response:
            html = response.read()

        tables = pd.read_html(html)  # Fetch all tables
        constituents = tables[index_data["table_index"]]  # Select the table by index

        print(f"Fetching data from URL: {index_data['url']}, Table Index: {index_data['table_index']}")

        if "Ticker" in constituents.columns:
            constituents["Ticker"] = constituents["Ticker"].apply(lambda x: str(x).replace(".", "-") if pd.notnull(x) else x)
        elif "Symbol" in constituents.columns:
            constituents["Symbol"] = constituents["Symbol"].apply(lambda x: str(x).replace(".", "-") if pd.notnull(x) else x)

        if index_name == "FTSE 100":
            constituents["Ticker"] = constituents["Ticker"].apply(lambda x: str(x) + ".L" if pd.notnull(x) else x)

        return constituents, None
    except Exception as e:
        print(f"Error fetching data for {index_name}: {str(e)}")
        return None, f"Error fetching data for {index_name}: {str(e)}"

@app.route('/select-index', methods=['GET'])
def select_index():
    options_html = "".join(f"<option value='{index}'>{index}</option>" for index in index_info.keys())
    content = f"""
    <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
        <div style="text-align: center; padding: 20px; background-color: #1e1e1e; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);">
            <div style="margin-bottom: 16px;">
                <label for="stock-index" class="mdc-typography--headline6" style="display: block; color: white; margin-bottom: 8px;">Select Stock Index</label>
                <select id="stock-index" name="stock-index" class="mdc-select" style="padding: 10px; font-size: 16px; border-radius: 8px; border: 1px solid #bb86fc; background-color: #2a2a2a; color: white; width: 100%; max-width: 250px;">
                    {options_html}
                </select>
            </div>
            <button hx-post="/scrape" hx-target="#output" onclick='this.setAttribute("hx-vals", JSON.stringify({{"index": document.getElementById("stock-index").value}}))'
                class="mdc-button mdc-button--raised" style="background-color: #bb86fc; color: white; padding: 10px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);">
                Submit
            </button>
        </div>
    </div>
    """
    return content

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Retrieve the index from form data instead of JSON
        index_name = request.form.get('index')  # HTMX sends form-encoded data
        
        if not index_name:
            return jsonify({"output": "No index selected."})

        constituents, error = fetch_index_constituents(index_name)
        if error:
            return jsonify({"output": error})

         # Create a Material3-styled table manually using HTML
        table_headers = "".join(f"<th>{col}</th>" for col in constituents.columns)
        table_rows = "".join(
            f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>" for row in constituents.values
        )

        output_html = f"""
        <div style='overflow-y: auto; max-height: 500px;'>
            <table style='width: 100%; border-collapse: collapse;'>
                <thead style='background-color: #bb86fc; color: white;'>
                    <tr>{table_headers}</tr>
                </thead>
                <tbody style='background-color: #2a2a2a; color: white;'>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """

        return output_html

    except Exception as e:
        return jsonify({"output": f"An error occurred: {traceback.format_exc()}"})


if __name__ == '__main__':
    app.run(debug=False)
