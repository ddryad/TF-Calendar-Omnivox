import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
 
MOIS = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
}
 
def parse_classe(raw: dict) -> dict:
    """ 
    Input:
        {
            "titre": "Projet - Développement d'une application Web",
            "date": "Jeudi 16 avril 2026",
            "heure": "8:00 à 11:00",
            "local": "S-013",
            "categorie": "COURS THÉORIE 420-412-MV gr. 00002"
        }
 
    Output:
        {
            "nom": "Projet - Développement d'une application Web",
            "description": "COURS THÉORIE 420-412-MV gr. 00002 — Local: S-013",
            "dateDepart": "2026-04-16T08:00:00",
            "dureeHeures": 3.0
        }
    """
    _, jour, mois_str, annee = raw["date"].split()
    mois = MOIS[mois_str.lower()]
 
    debut_str, _, fin_str = raw["heure"].split()
    h_debut, m_debut = map(int, debut_str.split(":"))
    h_fin, m_fin = map(int, fin_str.split(":"))
 
    date_depart = datetime(int(annee), mois, int(jour), h_debut, m_debut)
    duree_minutes = (h_fin * 60 + m_fin) - (h_debut * 60 + m_debut)
 
    return {
        "nom": raw["titre"],
        "description": f"{raw['categorie']} — Local: {raw['local']}",
        "dateDepart": date_depart.isoformat(), 
        "dureeHeures": duree_minutes / 60,     
    }

BASE_URL = "https://collegemv.omnivox.ca"
LOGIN_PAGE = f"{BASE_URL}/Login/Account/Login?ReturnUrl=%2fintr%2f"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-CA,fr;q=0.9,en;q=0.8",
}


def login(student_number: str, password: str):
    session = requests.Session()
    session.max_redirects = 20

    r = session.get(LOGIN_PAGE, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    payload = {}
    for inp in soup.find_all("input"):
        name = inp.get("name")
        if name:
            payload[name] = inp.get("value", "")

    payload["NoDA"] = student_number
    payload["PasswordEtu"] = password

    form = soup.find("form")
    post_url = urljoin(BASE_URL, form["action"]) if form and form.get("action") else LOGIN_PAGE

    resp = session.post(post_url, data=payload, headers=HEADERS, allow_redirects=False)
    while resp.is_redirect:
        location = resp.headers.get("Location", "")
        resp = session.get(urljoin(BASE_URL, location), headers=HEADERS, allow_redirects=False)

    if "modal-data" not in resp.text:
        raise ValueError("Login failed — check your credentials.")

    return session


def get_classes(session: requests.Session) -> list[dict]:
    resp = session.get(f"{BASE_URL}/intr/", headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")

    classes = []
    for ev in soup.find_all("div", class_="modal-data"):
        nom_cat = ev.get("data-nom-categorie", "")
        if "COURS" not in nom_cat.upper():
            continue

        classes.append({
            "titre":     BeautifulSoup(ev.get("data-titre", ""), "html.parser").get_text().strip(),
            "date":      ev.get("data-date", ""),
            "heure":     ev.get("data-heure", ""),
            "local":     BeautifulSoup(ev.get("data-local", ""), "html.parser").get_text().strip(),
            "categorie": BeautifulSoup(nom_cat, "html.parser").get_text(separator=" ").strip(),
        })

    return sorted(classes, key=lambda x: x["date"])