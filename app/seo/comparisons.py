"""Localized high-intent comparison pages for portable air conditioners."""

from __future__ import annotations

from app.seo.cities import COUNTRY_LANGUAGES, COUNTRY_NAMES


COMPARISON_SLUG = "12000-btu-portable-air-conditioner"
COMPARISON_COUNTRIES = ("DE", "FR", "IT", "ES", "NL", "BE", "GB")


_LANGUAGE_TEMPLATES = {
    "de": {
        "title": "Mobile Klimaanlage 12000 BTU auf Lager in {country} — KlimaRadar",
        "description": "Vergleich für mobile Klimaanlagen mit 12.000 BTU in {country}: aktuelle Preise, Lagerbestände, Eignung für Räume und Kaufcheckliste.",
        "h1": "Mobile Klimaanlagen mit 12.000 BTU auf Lager in {country}",
        "lead": "12.000 BTU ist eine der beliebtesten Leistungsklassen für Wohnzimmer, größere Schlafzimmer und sonnige Räume. Hier siehst du aktuelle Preise und Verfügbarkeit in {country}.",
        "card_title": "12.000-BTU-Geräte vergleichen",
        "card_body": "Live Preise und Lagerbestände für größere Räume prüfen.",
        "live_title": "Aktuelle 12.000-BTU-Angebote",
        "live_body": "Kühlleistung bringt nur etwas, wenn das Gerät auch lieferbar ist. Diese Liste wird regelmäßig aus aktuellen Händlerdaten aktualisiert.",
        "cta": "Alle 12.000-BTU-Geräte ansehen",
        "sections": [
            {
                "heading": "Für welche Räume 12.000 BTU ausreichen",
                "paragraphs": [
                    "Als Faustregel eignen sich 12.000 BTU für mittelgroße bis große Räume. Bei starker Sonneneinstrahlung, schlechter Dämmung oder sehr hohen Decken solltest du eher zur nächsten Leistungsstufe greifen.",
                    "Achte darauf, dass der Abluftschlauch wirklich nach außen führt. Ein mobiles Klimagerät ohne Außenabluft kann einen Raum nicht mit Kompressorleistung kühlen.",
                ],
                "table_title": "Kühlleistung grob einschätzen",
                "table_headers": ["Raumgröße", "Empfehlung", "Hinweis"],
                "table_rows": [
                    ["bis 20 m²", "7.000–9.000 BTU", "12.000 BTU kann zu stark erscheinen"],
                    ["20–35 m²", "12.000 BTU", "häufig guter Kompromiss"],
                    ["35–45 m²", "12.000–14.000 BTU", "bei Sonne eher 14.000 BTU"],
                    ["über 50 m²", "Split-Gerät prüfen", "ein einzelnes mobiles Gerät stößt an Grenzen"],
                ],
            },
            {
                "heading": "Kaufcheckliste für 12.000-BTU-Geräte",
                "bullets": [
                    "Abluftschlauch und Fensterverschluss mitliefern oder passend kaufen",
                    "Lautstärke im Schlafzimmer beachten",
                    "Energieklasse und Stromverbrauch vergleichen",
                    "Entfeuchtungsleistung für schwüle Tage prüfen",
                    "Gewicht, Rollen und Transport berücksichtigen",
                    "Lieferdatum, Rückgabe und Gewährleistung checken",
                ],
            },
        ],
        "faq_title": "Häufige Fragen zu 12.000-BTU-Klimageräten",
        "faqs": [
            {
                "question": "Für wie viele Quadratmeter reichen 12.000 BTU?",
                "answer": "In typischen Wohnungen sind das etwa 20–35 m². Bei starker Sonne, hohem Fensteranteil oder offenen Grundrissen kann eine höhere Leistung sinnvoll sein.",
            },
            {
                "question": "Braucht ein mobiles 12.000-BTU-Gerät einen Abluftschlauch?",
                "answer": "Ja. Ein Kompressorgerät muss warme Luft nach außen führen. Angebote ohne Schlauch oder mit Wasserkühlung sind meist Verdunstungskühler.",
            },
            {
                "question": "Was kostet ein gutes 12.000-BTU-Gerät in {country}?",
                "answer": "Der Preis hängt von Marke, Lautstärke, Effizienz und Ausstattung ab. Die Live-Liste zeigt aktuelle Händlerpreise statt veralteter Richtwerte.",
            },
            {
                "question": "Wie bekomme ich eine Benachrichtigung bei neuer Ware?",
                "answer": "Erstelle auf der Vergleichsseite eine Lager-Benachrichtigung. KlimaRadar informiert dich, wenn ein passendes 12.000-BTU-Gerät wieder verfügbar ist.",
            },
        ],
    },
    "fr": {
        "title": "Climatiseur mobile 12000 BTU : prix et stock en {country} — KlimaRadar",
        "description": "Comparatif des climatiseurs mobiles 12000 BTU en {country} : prix en direct, disponibilité, surface couverte et points à vérifier avant l'achat.",
        "h1": "Climatiseurs mobiles 12000 BTU disponibles en {country}",
        "lead": "Un climatiseur mobile de 12000 BTU convient à de nombreux salons et grandes chambres. Comparez ici les prix et le stock en direct pour {country}.",
        "card_title": "Comparer les modèles 12000 BTU",
        "card_body": "Prix et disponibilité en direct pour les grandes pièces.",
        "live_title": "Offres 12000 BTU en direct",
        "live_body": "La puissance ne sert à rien si l'appareil est indisponible. Cette liste est rafraîchie à partir des données commerciales courantes.",
        "cta": "Voir les modèles 12000 BTU",
        "sections": [
            {
                "heading": "Quelle surface pour 12000 BTU ?",
                "paragraphs": [
                    "Les modèles 12000 BTU conviennent généralement aux pièces moyennes à grandes. Avec une forte exposition au soleil ou une mauvaise isolation, choisissez plutôt une classe supérieure.",
                    "La tuyau d'évacuation doit impérativement sortir vers l'extérieur. Un appareil sans évacuation d'air chaud ne rafraîchit pas comme un climatiseur à compresseur.",
                ],
                "table_title": "Repères de puissance",
                "table_headers": ["Surface", "Puissance conseillée", "Remarque"],
                "table_rows": [
                    ["jusqu'à 20 m²", "7000–9000 BTU", "12000 BTU n'est pas toujours nécessaire"],
                    ["20–35 m²", "12000 BTU", "souvent le meilleur équilibre"],
                    ["35–45 m²", "12000–14000 BTU", "prévoir 14000 BTU en plein soleil"],
                    ["plus de 50 m²", "envisager un split", "un seul mobile atteint ses limites"],
                ],
            },
            {
                "heading": "Check-list avant l'achat",
                "bullets": [
                    "Vérifier le tuyau d'évacuation et le kit de fenêtre",
                    "Comparer le niveau sonore pour une chambre",
                    "Regarder la classe énergétique et la consommation",
                    "Contrôler la capacité de déshumidification",
                    "Tenir compte du poids et des roulettes",
                    "Vérifier délai de livraison, retour et garantie",
                ],
            },
        ],
        "faq_title": "Questions fréquentes sur les climatiseurs 12000 BTU",
        "faqs": [
            {
                "question": "Quelle surface pour un climatiseur 12000 BTU ?",
                "answer": "Environ 20 à 35 m² dans un logement classique. Une pièce très ensoleillée ou mal isolée peut nécessiter une puissance supérieure.",
            },
            {
                "question": "Faut-il un tuyau d'évacuation pour 12000 BTU ?",
                "answer": "Oui. Un vrai climatiseur mobile à compresseur doit évacuer l'air chaud dehors. Un modèle sans tuyau est généralement un refroidisseur d'air.",
            },
            {
                "question": "Quel prix pour un climatiseur mobile 12000 BTU en {country} ?",
                "answer": "Le prix varie selon la marque, le bruit, l'efficacité et les fonctions. La liste en direct montre les prix marchands actuels.",
            },
            {
                "question": "Comment être alerté en cas de retour de stock ?",
                "answer": "Créez une alerte sur la page de comparaison. KlimaRadar vous prévient dès qu'un modèle 12000 BTU correspondant redevient disponible.",
            },
        ],
    },
    "it": {
        "title": "Climatizzatore portatile 12000 BTU: prezzi e disponibilità in {country} — KlimaRadar",
        "description": "Confronto dei climatizzatori portatili 12000 BTU in {country}: prezzi in tempo reale, disponibilità, metratura consigliata e check-list prima dell'acquisto.",
        "h1": "Climatizzatori portatili 12000 BTU disponibili in {country}",
        "lead": "12000 BTU è una classe adatta a salotti, camere grandi e stanze molto soleggiate. Qui trovi prezzi e disponibilità aggiornati per {country}.",
        "card_title": "Confronta modelli 12000 BTU",
        "card_body": "Prezzi e disponibilità in tempo reale per grandi ambienti.",
        "live_title": "Offerte 12000 BTU in tempo reale",
        "live_body": "La potenza è utile solo se il prodotto è davvero disponibile. Questa lista viene aggiornata dai dati commerciali correnti.",
        "cta": "Vedi i modelli 12000 BTU",
        "sections": [
            {
                "heading": "Quanti metri quadri raffredda 12000 BTU?",
                "paragraphs": [
                    "In condizioni normali, 12000 BTU è adatto a camere e soggiorni di medie-grandissime dimensioni. Con forte sole, vetrate ampie o isolamento scarso conviene salire di classe.",
                    "Il tubo di scarico deve andare all'esterno. Un dispositivo senza scarico dell'aria calda non raffredda come un vero climatizzatore a compressore.",
                ],
                "table_title": "Potenza consigliata",
                "table_headers": ["Superficie", "Potenza consigliata", "Nota"],
                "table_rows": [
                    ["fino a 20 m²", "7000–9000 BTU", "12000 BTU può essere superfluo"],
                    ["20–35 m²", "12000 BTU", "spesso il miglior equilibrio"],
                    ["35–45 m²", "12000–14000 BTU", "con molto sole meglio 14000 BTU"],
                    ["oltre 50 m²", "valutare uno split", "un solo portatile può risultare insufficiente"],
                ],
            },
            {
                "heading": "Check-list prima dell'acquisto",
                "bullets": [
                    "Verificare tubo di scarico e kit finestra",
                    "Controllare il rumore per la camera da letto",
                    "Confrontare classe energetica e consumi",
                    "Valutare la capacità di deumidificazione",
                    "Considerare peso e ruote",
                    "Controllare consegna, reso e garanzia",
                ],
            },
        ],
        "faq_title": "Domande frequenti sui climatizzatori 12000 BTU",
        "faqs": [
            {
                "question": "Quanti m² raffredda un climatizzatore 12000 BTU?",
                "answer": "In genere 20–35 m². In ambienti molto soleggiati o poco isolati può servire una potenza maggiore.",
            },
            {
                "question": "Serve il tubo di scarico per un portatile 12000 BTU?",
                "answer": "Sì. Un vero climatizzatore a compressore deve espellere l'aria calda fuori. I modelli senza tubo sono spesso raffrescatori ad acqua.",
            },
            {
                "question": "Quanto costa un 12000 BTU in {country}?",
                "answer": "Dipende da marca, rumorosità, efficienza e funzioni. L'elenco in tempo reale mostra i prezzi correnti dei rivenditori.",
            },
            {
                "question": "Come ricevo un avviso quando torna disponibile?",
                "answer": "Crea un avviso dalla pagina di confronto. KlimaRadar ti informa quando un modello 12000 BTU adatto torna disponibile.",
            },
        ],
    },
    "es": {
        "title": "Aire acondicionado portátil 12000 BTU: precio y stock en {country} — KlimaRadar",
        "description": "Comparativa de aire acondicionado portátil 12000 BTU en {country}: precios en vivo, disponibilidad, metros cuadrados recomendados y checklist de compra.",
        "h1": "Aire acondicionado portátil 12000 BTU disponible en {country}",
        "lead": "12000 BTU es una de las capacidades más útiles para salones y dormitorios grandes. Compara precios y stock actual en {country}.",
        "card_title": "Comparar modelos de 12000 BTU",
        "card_body": "Precios y disponibilidad en vivo para estancias grandes.",
        "live_title": "Ofertas de 12000 BTU en vivo",
        "live_body": "La potencia solo importa si el equipo está disponible. Esta lista se actualiza con datos comerciales recientes.",
        "cta": "Ver equipos de 12000 BTU",
        "sections": [
            {
                "heading": "¿Cuántos metros cuadra cubre 12000 BTU?",
                "paragraphs": [
                    "En una vivienda normal, 12000 BTU sirve para estancias medianas y grandes. Con mucho sol, grandes ventanales o mal aislamiento conviene elegir más capacidad.",
                    "El tubo de escape debe ir al exterior. Un aparato sin salida de aire caliente no enfría como un aire acondicionado con compresor.",
                ],
                "table_title": "Capacidad recomendada",
                "table_headers": ["Superficie", "Capacidad recomendada", "Nota"],
                "table_rows": [
                    ["hasta 20 m²", "7000–9000 BTU", "12000 BTU puede ser excesivo"],
                    ["20–35 m²", "12000 BTU", "buena opción equilibrada"],
                    ["35–45 m²", "12000–14000 BTU", "con mucho sol, mejor 14000 BTU"],
                    ["más de 50 m²", "valorar un split", "un portátil puede quedarse corto"],
                ],
            },
            {
                "heading": "Checklist antes de comprar",
                "bullets": [
                    "Comprobar tubo de escape y kit de ventana",
                    "Revisar el nivel de ruido para dormitorios",
                    "Comparar etiqueta energética y consumo",
                    "Ver la capacidad de deshumidificación",
                    "Considerar peso y ruedas",
                    "Confirmar entrega, devolución y garantía",
                ],
            },
        ],
        "faq_title": "Preguntas frecuentes sobre aire acondicionado 12000 BTU",
        "faqs": [
            {
                "question": "¿Cuántos metros cuadra enfría 12000 BTU?",
                "answer": "Normalmente entre 20 y 35 m². Si la habitación tiene mucho sol o mal aislamiento, puede necesitar más potencia.",
            },
            {
                "question": "¿Necesita tubo de escape un portátil de 12000 BTU?",
                "answer": "Sí. Un aire acondicionado con compresor debe expulsar el aire caliente fuera. Los modelos sin tubo suelen ser enfriadores evaporativos.",
            },
            {
                "question": "¿Cuánto cuesta un 12000 BTU en {country}?",
                "answer": "Depende de la marca, el ruido, la eficiencia y las funciones. La lista en vivo muestra precios actuales de comercios.",
            },
            {
                "question": "¿Cómo me avisan cuando haya stock?",
                "answer": "Crea una alerta en la página de comparación. KlimaRadar avisa cuando vuelve a estar disponible un modelo adecuado de 12000 BTU.",
            },
        ],
    },
    "nl": {
        "title": "Draagbare airconditioner 12000 BTU: prijs en voorraad in {country} — KlimaRadar",
        "description": "Vergelijk draagbare airconditioners met 12000 BTU in {country}: live prijzen, voorraad, advies voor oppervlakte en een checklist voor het kopen.",
        "h1": "Draagbare airconditioners met 12000 BTU op voorraad in {country}",
        "lead": "12000 BTU is een populaire capaciteit voor woonkamers en grotere slaapkamers. Bekijk hier live prijzen en beschikbaarheid in {country}.",
        "card_title": "12000 BTU-modellen vergelijken",
        "card_body": "Live prijzen en voorraad voor grotere ruimtes.",
        "live_title": "Actuele 12000 BTU-aanbiedingen",
        "live_body": "Koelcapaciteit helpt alleen als het apparaat leverbaar is. Deze lijst wordt bijgewerkt met actuele handelsdata.",
        "cta": "Bekijk alle 12000 BTU-apparaten",
        "sections": [
            {
                "heading": "Voor welke ruimte is 12000 BTU geschikt?",
                "paragraphs": [
                    "In een gewone woning is 12000 BTU bruikbaar voor middelgrote en grote kamers. Bij veel zon, grote ramen of slechte isolatie is een hogere capaciteit verstandiger.",
                    "De afvoerslang moet echt naar buiten lopen. Een apparaat zonder afvoer van warme lucht koelt niet zoals een echte airconditioner met compressor.",
                ],
                "table_title": "Richtlijn voor koelcapaciteit",
                "table_headers": ["Oppervlakte", "Advies", "Let op"],
                "table_rows": [
                    ["tot 20 m²", "7000–9000 BTU", "12000 BTU is soms te veel"],
                    ["20–35 m²", "12000 BTU", "vaak een goede balans"],
                    ["35–45 m²", "12000–14000 BTU", "bij veel zon eerder 14000 BTU"],
                    ["meer dan 50 m²", "split installatie overwegen", "één draagbaar apparaat is beperkt"],
                ],
            },
            {
                "heading": "Checklist voor het kopen",
                "bullets": [
                    "Afvoerslang en raamkit controleren",
                    "Geluidsniveau voor de slaapkamer vergelijken",
                    "Energielabel en verbruik bekijken",
                    "Vochtverwijdering beoordelen",
                    "Gewicht en wielen meenemen",
                    "Levering, retour en garantie checken",
                ],
            },
        ],
        "faq_title": "Veelgestelde vragen over 12000 BTU-airconditioners",
        "faqs": [
            {
                "question": "Voor hoeveel m² is 12000 BTU geschikt?",
                "answer": "Als richtlijn ongeveer 20–35 m². Bij veel zonlicht of slechte isolatie kan een hoger vermogen nodig zijn.",
            },
            {
                "question": "Heeft een draagbare 12000 BTU-airco een afvoerslang nodig?",
                "answer": "Ja. Een echte airconditioner met compressor moet warme lucht naar buiten afvoeren. Modellen zonder slang zijn meestal luchtkoelers met water.",
            },
            {
                "question": "Wat kost een goede 12000 BTU-airco in {country}?",
                "answer": "Dat hangt af van merk, geluid, rendement en functies. De live lijst toont actuele prijzen van winkels.",
            },
            {
                "question": "Hoe krijg ik een melding bij nieuwe voorraad?",
                "answer": "Maak een voorraadmelding op de vergelijkingspagina. KlimaRadar waarschuwt zodra een geschikt 12000 BTU-model weer beschikbaar is.",
            },
        ],
    },
    "en": {
        "title": "12000 BTU Portable Air Conditioner: Prices and Stock in {country} — KlimaRadar",
        "description": "Compare 12000 BTU portable air conditioners in {country}: live prices, current stock, room-size guidance and a practical pre-purchase checklist.",
        "h1": "12000 BTU Portable Air Conditioners in Stock in {country}",
        "lead": "12000 BTU is one of the most useful capacities for living rooms and larger bedrooms. Check live prices and availability in {country}.",
        "card_title": "Compare 12000 BTU units",
        "card_body": "Live prices and stock for larger rooms.",
        "live_title": "Current 12000 BTU offers",
        "live_body": "Cooling capacity only matters when a unit can actually be delivered. This list is refreshed from current retailer data.",
        "cta": "See all 12000 BTU units",
        "sections": [
            {
                "heading": "What room size suits 12000 BTU?",
                "paragraphs": [
                    "In typical homes, 12000 BTU suits medium to large rooms. Strong sunlight, large windows or weak insulation may call for the next capacity class.",
                    "The exhaust hose must vent outside. A unit without hot-air extraction cannot cool like a true compressor air conditioner.",
                ],
                "table_title": "Capacity guide",
                "table_headers": ["Room size", "Recommended capacity", "Note"],
                "table_rows": [
                    ["up to 20 m²", "7000–9000 BTU", "12000 BTU may be excessive"],
                    ["20–35 m²", "12000 BTU", "often the best balance"],
                    ["35–45 m²", "12000–14000 BTU", "choose 14000 BTU in strong sun"],
                    ["over 50 m²", "consider a split system", "one portable unit may struggle"],
                ],
            },
            {
                "heading": "Checklist before buying",
                "bullets": [
                    "Check the exhaust hose and window kit",
                    "Compare noise output for bedrooms",
                    "Review energy label and consumption",
                    "Look at dehumidification capacity",
                    "Consider weight and casters",
                    "Check delivery date, returns and warranty",
                ],
            },
        ],
        "faq_title": "12000 BTU portable AC FAQs",
        "faqs": [
            {
                "question": "How many square metres can 12000 BTU cool?",
                "answer": "Roughly 20–35 m² in a typical home. Very sunny or poorly insulated rooms may need a higher rating.",
            },
            {
                "question": "Does a 12000 BTU portable AC need an exhaust hose?",
                "answer": "Yes. A compressor air conditioner must remove hot air outside. Hoseless models are usually evaporative coolers.",
            },
            {
                "question": "How much does a good 12000 BTU unit cost in {country}?",
                "answer": "Price depends on brand, noise, efficiency and features. The live list shows current retailer prices.",
            },
            {
                "question": "How do I get notified when stock returns?",
                "answer": "Create a stock alert on the comparison page. KlimaRadar emails you when a suitable 12000 BTU model becomes available.",
            },
        ],
    },
}


def _format_value(value, **values):
    if isinstance(value, str):
        return value.format(**values)
    if isinstance(value, list):
        return [_format_value(item, **values) for item in value]
    if isinstance(value, dict):
        return {key: _format_value(item, **values) for key, item in value.items()}
    return value


def comparison_path(country: str) -> str:
    return f"/compare/{country.lower()}/{COMPARISON_SLUG}"


def get_btu_comparison(country: str) -> dict | None:
    """Return a localized 12000 BTU comparison configuration."""
    code = country.upper()
    if code not in COMPARISON_COUNTRIES:
        return None
    language = COUNTRY_LANGUAGES.get(code, "en")[:2]
    template = _LANGUAGE_TEMPLATES.get(language, _LANGUAGE_TEMPLATES["en"])
    country_name = COUNTRY_NAMES.get(code, {}).get(
        language, COUNTRY_NAMES.get(code, {}).get("en", code)
    )
    return _format_value(template, country=country_name) | {
        "country": code,
        "country_name": country_name,
        "language": language,
        "html_lang": COUNTRY_LANGUAGES.get(code, "en"),
        "path": comparison_path(code),
    }


def list_btu_comparisons(exclude: str | None = None) -> list[dict]:
    """Return compact comparison metadata for internal links and sitemaps."""
    comparisons = []
    for code in COMPARISON_COUNTRIES:
        if exclude and code == exclude.upper():
            continue
        comparison = get_btu_comparison(code)
        if comparison:
            comparisons.append(
                {
                    "country": code,
                    "country_name": comparison["country_name"],
                    "title": comparison["title"],
                    "h1": comparison["h1"],
                    "card_title": comparison["card_title"],
                    "card_body": comparison["card_body"],
                    "path": comparison["path"],
                }
            )
    return comparisons


def build_comparison_article_jsonld(base_url: str, comparison: dict) -> dict:
    """Build Article structured data for a comparison page."""
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": comparison["h1"],
        "description": comparison["description"],
        "inLanguage": comparison["html_lang"],
        "mainEntityOfPage": f"{base_url}{comparison['path']}",
        "datePublished": "2026-08-15",
        "dateModified": "2026-08-15",
        "author": {"@type": "Organization", "name": "KlimaRadar"},
        "publisher": {"@type": "Organization", "name": "KlimaRadar"},
    }
