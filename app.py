from flask import Flask, request, session
import requests
from flask import render_template, jsonify
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)

@app.route("/", methods=["GET", "POST"])
def index():
    info = None
    if request.method == "POST":
        code_postal = request.form.get("code_postal")
        url = "https://api-adresse.data.gouv.fr/search/"
        params = {"q": "Charles de Gaulle", "postcode": code_postal}
        response = requests.get(url, params=params)
        info = response.json()
    return render_template("index.html", data=info)



@app.route("/tp1/ex1")
def home():
    url = "http://worldtimeapi.org/api/timezone/Europe/Paris"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        print(response.text)
        data = response.json()
    except requests.exceptions.RequestException as e:
        app.logger.exception("Erreur API (ex1)")
        return jsonify({"error": "Impossible de contacter WorldTimeAPI", "details": str(e)}), 502

    print("Réponse en texte :")
    print(response.text)
    print("\nRéponse en JSON :")
    print(data)

    heure = data["datetime"].split("T")[1].split(".")[0]
    print("\nHeure actuelle à Paris :", heure)
    return f"Heure actuelle à Paris : {heure}"


@app.route("/tp1/ex2")
def exo2():

    url = "https://api-adresse.data.gouv.fr/search/"

    # Paramètres pour la recherche
    params = {
        "q": "rue de l'université",
        "limit": 3,
        "citycode": "62498"
    }

    # Requête GET avec paramètres
    response = requests.get(url, params=params)

    data = response.json()

    print("Résultat brut :", data)


    for feature in data["features"]:
        properties = feature["properties"]
        print("\nAdresse trouvée :")
        print("  Label :", properties.get("label"))
        print("  Code postal :", properties.get("postcode"))
        print("  Ville :", properties.get("city"))
        print("  Coordonnées :", feature["geometry"]["coordinates"])
    return jsonify(data)


if __name__ == '__main__':
    app.run()