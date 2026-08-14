"""Localized country buying-guide content for portable air conditioners."""

from __future__ import annotations

from app.seo.cities import COUNTRY_LANGUAGES, COUNTRY_NAMES


GUIDE_SLUG = "portable-air-conditioner"

_GUIDE_COUNTRY_CONFIG = {
    "DE": {"retailers": "Amazon Germany and other large German electronics retailers"},
    "FR": {"retailers": "Amazon France and major French electronics retailers"},
    "IT": {"retailers": "Amazon Italy and other national retailers"},
    "ES": {"retailers": "Amazon Spain and other national retailers"},
    "NL": {"retailers": "Amazon Netherlands and other national retailers"},
    "BE": {"retailers": "Amazon Belgium and other national retailers"},
    "GB": {"retailers": "Amazon United Kingdom and other national retailers"},
}

_GUIDE_LANGUAGE_TEMPLATES = {
    "de": {
        "title": "Mobile Klimaanlage 2026: BTU, Preise & Geräte auf Lager — KlimaRadar",
        "description": "Kaufberatung für mobile Klimaanlagen in {country}: passende BTU-Leistung, realistische Preise, Lieferzeit und aktuelle Lagerbestände vergleichen.",
        "h1": "Mobile Klimaanlage 2026: Kaufberatung für {country}",
        "lead": "Hitzeperioden verkaufen mobile Klimageräte in {country} oft innerhalb weniger Stunden aus. Diese Kaufberatung erklärt, welche Leistung zu Ihrem Raum passt, welche Preise realistisch sind und wie Sie verfügbare Geräte schneller finden.",
        "badge": "Kaufberatung 2026",
        "read_guide": "Kaufberatung lesen →",
        "card_title": "Kaufberatung: mobile Klimaanlagen in {country}",
        "card_body": "BTU-Leistung, Preisrahmen, Lieferzeit und Kauf-Checklist nachlesen.",
        "cities_title": "Mobile Klimaanlagen in diesen Städten suchen",
        "other_guides_title": "Weitere europäische Kaufberatungen",
        "live_title": "Aktuelle Lagerbestände und Preise prüfen",
        "live_body": "KlimaRadar vergleicht Verfügbarkeit und Preise, damit Sie kaufen können, bevor Geräte ausverkauft sind.",
        "cta": "Aktuelle Geräte in {country} ansehen",
        "sections": [
            {
                "heading": "Warum Verfügbarkeit in {country} schnell wechselt",
                "paragraphs": [
                    "Mobile Klimaanlagen sind besonders dann gefragt, wenn mehrtägige Hitzewellen Wohnungen ohne Festklimaanlage stark aufheizen. Händler erhöhen dann nicht immer sofort die Bestände, deshalb können beliebte 9.000- und 12.000-BTU-Modelle kurzfristig ausverkauft sein.",
                    "KlimaRadar verfolgt Angebote von {retailers}. Die Lager- und Preisdaten ändern sich laufend; verwenden Sie daher die Produktauflistung für den aktuellen Stand und diese Seite für die Kaufentscheidung.",
                ],
            },
            {
                "heading": "Wie viele BTU passen zu Ihrem Raum?",
                "paragraphs": [
                    "Die nötige Kühlleistung hängt von Raumgröße, Deckenhöhe, Sonneneinstrahlung, Dämmung und elektrischen Geräten ab. Bei sehr sonnigen Dachwohnungen wählen Sie eher die nächsthöhere Stufe.",
                ],
                "table_title": "Orientierungswerte für mobile Klimageräte",
                "table_headers": ["Raumgröße", "Empfohlene Leistung", "Typische Nutzung"],
                "table_rows": [
                    ["bis 20 m²", "7.000 BTU / 2,0 kW", "Schlafzimmer, kleines Büro"],
                    ["25–35 m²", "9.000 BTU / 2,6 kW", "Wohnzimmer, geteilte Räume"],
                    ["35–50 m²", "12.000 BTU / 3,5 kW", "große Räume, offene Bereiche"],
                    ["über 50 m²", "14.000 BTU oder mehr", "Räume mit hoher Wärmelast"],
                ],
            },
            {
                "heading": "Preise und Lieferzeiten realistisch einschätzen",
                "paragraphs": [
                    "Einfache 7.000-BTU-Geräte beginnen meist im unteren Preisbereich, leisere Geräte mit 12.000 BTU, Invertertechnik und besserer Energieeffizienz liegen deutlich höher. Zubehör, Wanddurchführung oder längere Abluftschläuche können zusätzliche Kosten verursachen.",
                    "Vergleichen Sie nicht nur den Verkaufspreis, sondern auch Versandkosten, Rückgaberecht und Ersatzteilverfügbarkeit. Ein günstiges Gerät ohne passendes Fenster-Set kann die eigentliche Einsparung schnell aufbrauchen.",
                ],
            },
            {
                "heading": "Checkliste vor dem Kauf",
                "bullets": [
                    "Fenster- oder Türausschnitt für den Abluftschlauch messen",
                    "Abluft nach außen führen — nicht in einen geschlossenen Raum",
                    "Lautstärke im Schlafzimmer mit dem Datenblatt prüfen",
                    "Energieklasse, Stromverbrauch und Abschalttimer vergleichen",
                    "Gewicht und Rollen berücksichtigen, wenn Sie das Gerät zwischen Räumen bewegen",
                    "Liefertermin, Rücksendebedingungen und Garantie prüfen",
                ],
            },
        ],
        "faq_title": "Häufige Fragen zu mobilen Klimaanlagen",
        "faqs": [
            {
                "question": "Wie viel BTU brauche ich für mein Zimmer?",
                "answer": "Als Orientierung: 7.000 BTU für kleine Räume bis etwa 20 m², 9.000 BTU für 25–35 m² und mindestens 12.000 BTU für 35–50 m². Bei starker Sonneneinstrahlung oder schlechter Dämmung eher höher rechnen.",
            },
            {
                "question": "Was kostet eine mobile Klimaanlage in {country}?",
                "answer": "Die Preisspanne hängt von Leistung, Geräuschentwicklung und Effizienz ab. Kleine Geräte liegen im unteren Bereich, leise 12.000- oder 14.000-BTU-Modelle deutlich höher. Die aktuelle Spanne sehen Sie in der Live-Preisliste.",
            },
            {
                "question": "Warum sind mobile Klimaanlagen plötzlich ausverkauft?",
                "answer": "Nachfrage steigt bei Hitzewellen sehr schnell, während Bestände und Lieferkapazitäten begrenzt sind. Beliebte Leistungsstufen können deshalb täglich oder stündlich wechseln.",
            },
            {
                "question": "Kann ein mobiles Klimagerät einen ganzen Raum kühlen?",
                "answer": "Ja, wenn die BTU-Leistung zur Raumgröße passt und die warme Abluft effektiv nach außen geleitet wird. Bei sehr großen oder offenen Wohnflächen ist oft ein leistungsstärkeres Gerät oder eine feste Split-Anlage sinnvoller.",
            },
            {
                "question": "Wie werde ich bei neuer Verfügbarkeit benachrichtigt?",
                "answer": "Erstellen Sie auf der Suchseite für {country} einen Lager-Alarm. KlimaRadar benachrichtigt Sie, sobald ein passendes Gerät wieder verfügbar ist.",
            },
        ],
    },
    "fr": {
        "title": "Climatiseur mobile 2026 : puissance, prix et stock — KlimaRadar",
        "description": "Guide d'achat des climatiseurs mobiles en {country} : puissance BTU, prix réalistes, délais de livraison et disponibilités actuelles.",
        "h1": "Climatiseur mobile 2026 : guide d'achat pour {country}",
        "lead": "En période de canicule, les climatiseurs mobiles peuvent partir en quelques heures. Ce guide explique quelle puissance choisir pour votre pièce, quels prix sont réalistes et comment repérer les modèles disponibles.",
        "badge": "Guide d'achat 2026",
        "read_guide": "Lire le guide →",
        "card_title": "Guide d'achat : climatiseurs mobiles en {country}",
        "card_body": "Puissance BTU, budget, délai de livraison et checklist avant achat.",
        "cities_title": "Rechercher dans ces villes",
        "other_guides_title": "Autres guides européens",
        "live_title": "Vérifier stock et prix en direct",
        "live_body": "KlimaRadar compare disponibilité et prix pour acheter avant la rupture de stock.",
        "cta": "Voir les appareils disponibles en {country}",
        "sections": [
            {
                "heading": "Pourquoi la disponibilité change vite en {country}",
                "paragraphs": [
                    "Les climatiseurs mobiles sont surtout demandés pendant les vagues de chaleur prolongées. Les modèles de 9 000 et 12 000 BTU deviennent alors rapidement indisponibles car les stocks ne suivent pas toujours la demande soudaine.",
                    "KlimaRadar suit des offres de {retailers}. Cette page vous aide à choisir ; la liste en direct montre les prix et stocks actuels.",
                ],
            },
            {
                "heading": "Quelle puissance BTU choisir ?",
                "paragraphs": [
                    "La puissance dépend de la surface, de la hauteur sous plafond, de l'ensoleillement, de l'isolation et des appareils présents. Dans une pièce très ensoleillée ou sous toit, choisissez la puissance supérieure.",
                ],
                "table_title": "Repères de puissance pour un climatiseur mobile",
                "table_headers": ["Surface", "Puissance conseillée", "Usage typique"],
                "table_rows": [
                    ["jusqu'à 20 m²", "7 000 BTU / 2,0 kW", "chambre, petit bureau"],
                    ["25 à 35 m²", "9 000 BTU / 2,6 kW", "salon, pièce partagée"],
                    ["35 à 50 m²", "12 000 BTU / 3,5 kW", "grande pièce, espace ouvert"],
                    ["plus de 50 m²", "14 000 BTU ou plus", "forte charge thermique"],
                ],
            },
            {
                "heading": "Prix et délais de livraison",
                "paragraphs": [
                    "Les modèles d'entrée de gamme de 7 000 BTU sont les moins chers. Les appareils plus silencieux de 12 000 BTU, avec inverter et meilleure efficacité énergétique, coûtent nettement plus.",
                    "Comparez aussi les frais de port, le droit de rétractation, la disponibilité des pièces et le kit de fenêtre. Un prix bas peut devenir moins intéressant si l'évacuation de l'air chaud demande des accessoires supplémentaires.",
                ],
            },
            {
                "heading": "Checklist avant l'achat",
                "bullets": [
                    "Mesurer l'ouverture disponible pour la gaine d'évacuation",
                    "Évacuer l'air chaud vers l'extérieur, jamais dans une pièce fermée",
                    "Vérifier le niveau sonore pour une chambre",
                    "Comparer classe énergétique, consommation et minuterie",
                    "Tenir compte du poids et des roulettes",
                    "Contrôler délai, retour et garantie",
                ],
            },
        ],
        "faq_title": "Questions fréquentes sur les climatiseurs mobiles",
        "faqs": [
            {
                "question": "Combien de BTU pour ma pièce ?",
                "answer": "Environ 7 000 BTU jusqu'à 20 m², 9 000 BTU pour 25 à 35 m² et au moins 12 000 BTU pour 35 à 50 m². Ajoutez une marge en cas de fort ensoleillement ou d'isolation limitée.",
            },
            {
                "question": "Quel est le prix d'un climatiseur mobile en {country} ?",
                "answer": "Le budget dépend surtout de la puissance, du bruit et de l'efficacité. Consultez la liste en direct pour la fourchette actuelle plutôt qu'un prix figé.",
            },
            {
                "question": "Pourquoi les climatiseurs mobiles sont-ils en rupture ?",
                "answer": "La demande augmente très vite pendant les canicules alors que les stocks et les capacités de livraison restent limités. La disponibilité peut donc changer plusieurs fois par jour.",
            },
            {
                "question": "Un climatiseur mobile peut-il refroidir toute une pièce ?",
                "answer": "Oui, si la puissance correspond à la surface et si l'air chaud est bien évacué vers l'extérieur. Pour un très grand espace ouvert, un modèle plus puissant ou une solution fixe est souvent préférable.",
            },
            {
                "question": "Comment être alerté d'un retour en stock ?",
                "answer": "Créez une alerte sur la page de recherche pour {country}. KlimaRadar vous prévient dès qu'un modèle correspondant redevient disponible.",
            },
        ],
    },
    "it": {
        "title": "Climatizzatore portatile 2026: BTU, prezzi e disponibilità — KlimaRadar",
        "description": "Guida all'acquisto dei climatizzatori portatili in {country}: BTU giusti, prezzi realistici, consegna e modelli disponibili adesso.",
        "h1": "Climatizzatore portatile 2026: guida all'acquisto in {country}",
        "lead": "Durante le ondate di calore i modelli più richiesti possono esaurirsi in poche ore. Questa guida spiega come scegliere la potenza, quanto spendere e come trovare i dispositivi disponibili.",
        "badge": "Guida 2026",
        "read_guide": "Leggi la guida →",
        "card_title": "Guida: climatizzatori portatili in {country}",
        "card_body": "Potenza BTU, prezzi, consegna e checklist prima dell'acquisto.",
        "cities_title": "Cerca in queste città",
        "other_guides_title": "Altre guide europee",
        "live_title": "Controlla scorte e prezzi in tempo reale",
        "live_body": "KlimaRadar confronta disponibilità e prezzi per acquistare prima dell'esaurimento.",
        "cta": "Vedi i dispositivi disponibili in {country}",
        "sections": [
            {
                "heading": "Perché la disponibilità cambia rapidamente in {country}",
                "paragraphs": [
                    "La domanda cresce soprattutto quando il calore dura diversi giorni. I modelli da 9.000 e 12.000 BTU sono spesso i primi a scomparire perché uniscono prezzo e prestazioni adatti a molte stanze.",
                    "KlimaRadar controlla offerte di {retailers}. Usa questa guida per scegliere e la lista in tempo reale per vedere prezzi e stock attuali.",
                ],
            },
            {
                "heading": "Quanti BTU servono per la tua stanza?",
                "paragraphs": [
                    "La potenza dipende da metratura, esposizione al sole, isolamento, altezza del soffitto e apparecchi accesi. In mansarde molto soleggiate conviene salire di categoria.",
                ],
                "table_title": "Potenze indicative per climatizzatori portatili",
                "table_headers": ["Superficie", "Potenza consigliata", "Uso tipico"],
                "table_rows": [
                    ["fino a 20 m²", "7.000 BTU / 2,0 kW", "camera da letto, piccolo studio"],
                    ["25–35 m²", "9.000 BTU / 2,6 kW", "soggiorno, stanze condivise"],
                    ["35–50 m²", "12.000 BTU / 3,5 kW", "grandi stanze, spazi aperti"],
                    ["oltre 50 m²", "14.000 BTU o più", "carico termico elevato"],
                ],
            },
            {
                "heading": "Prezzi e tempi di consegna",
                "paragraphs": [
                    "I modelli base da 7.000 BTU costano meno. I dispositivi più silenziosi da 12.000 BTU, con inverter e maggiore efficienza, hanno prezzi più alti.",
                    "Considera anche spese di spedizione, reso, garanzia e kit per finestra. Un prezzo basso può non essere conveniente se servono accessori aggiuntivi.",
                ],
            },
            {
                "heading": "Cosa verificare prima dell'acquisto",
                "bullets": [
                    "Misura l'apertura per il tubo dell'aria calda",
                    "Manda l'aria calda fuori, non in un'altra stanza chiusa",
                    "Controlla il rumore se usarai il device in camera",
                    "Confronta classe energetica, consumo e timer",
                    "Valuta peso e rotelle se sposti spesso il dispositivo",
                    "Verifica consegna, reso e garanzia",
                ],
            },
        ],
        "faq_title": "Domande frequenti sui climatizzatori portatili",
        "faqs": [
            {
                "question": "Quanti BTU servono per la mia camera?",
                "answer": "Come indicazione: 7.000 BTU fino a 20 m², 9.000 BTU per 25–35 m² e almeno 12.000 BTU per 35–50 m². Con molto sole o isolamento scarso scegli una potenza superiore.",
            },
            {
                "question": "Quanto costa un climatizzatore portatile in {country}?",
                "answer": "Il prezzo dipende da potenza, rumorosità ed efficienza. La lista in tempo reale mostra la gamma attuale invece di un prezzo fisso.",
            },
            {
                "question": "Perché i modelli sono spesso esauriti?",
                "answer": "Durante il caldo intenso la domanda sale più velocemente delle scorte e delle consegne, quindi la disponibilità può cambiare ogni giorno.",
            },
            {
                "question": "Un climatizzatore portatile raffredda tutta la stanza?",
                "answer": "Sì, se i BTU sono adeguati alla superficie e l'aria calda viene espulsa all'esterno. Per ambienti molto grandi o aperti può servire una soluzione più potente o fissa.",
            },
            {
                "question": "Come ricevo un avviso quando torna disponibile?",
                "answer": "Crea un avviso nella pagina di ricerca per {country}. KlimaRadar ti segnala appena un modello adatto è di nuovo disponibile.",
            },
        ],
    },
    "es": {
        "title": "Aire acondicionado portátil 2026: BTU, precios y stock — KlimaRadar",
        "description": "Guía de compra de aire acondicionado portátil en {country}: potencia BTU, precios realistas, entrega y modelos disponibles ahora.",
        "h1": "Aire acondicionado portátil 2026: guía de compra en {country}",
        "lead": "En olas de calor, los modelos más buscados pueden agotarse en pocas horas. Esta guía explica qué potencia elegir, cuánto pagar y cómo encontrar unidades disponibles.",
        "badge": "Guía 2026",
        "read_guide": "Leer la guía →",
        "card_title": "Guía: aire acondicionado portátil en {country}",
        "card_body": "Potencia BTU, presupuesto, entrega y checklist antes de comprar.",
        "cities_title": "Buscar en estas ciudades",
        "other_guides_title": "Más guías europeas",
        "live_title": "Comprobar stock y precios en directo",
        "live_body": "KlimaRadar compara disponibilidad y precios para que compres antes del agotamiento.",
        "cta": "Ver unidades disponibles en {country}",
        "sections": [
            {
                "heading": "Por qué el stock cambia rápido en {country}",
                "paragraphs": [
                    "La demanda aumenta cuando el calor se prolonga varios días. Los modelos de 9.000 y 12.000 BTU suelen agotarse antes porque encajan con muchas habitaciones y presupuestos.",
                    "KlimaRadar sigue ofertas de {retailers}. Usa esta guía para decidir y la lista en directo para consultar precio y disponibilidad actual.",
                ],
            },
            {
                "heading": "¿Cuántos BTU necesito?",
                "paragraphs": [
                    "La potencia depende de metros cuadrados, sol, aislamiento, altura y aparatos que generen calor. En buhardillas muy soleadas conviene subir de potencia.",
                ],
                "table_title": "Potencias orientativas",
                "table_headers": ["Superficie", "Potencia recomendada", "Uso habitual"],
                "table_rows": [
                    ["hasta 20 m²", "7.000 BTU / 2,0 kW", "dormitorio, oficina pequeña"],
                    ["25–35 m²", "9.000 BTU / 2,6 kW", "salón, habitaciones compartidas"],
                    ["35–50 m²", "12.000 BTU / 3,5 kW", "habitaciones grandes, espacios abiertos"],
                    ["más de 50 m²", "14.000 BTU o más", "carga térmica alta"],
                ],
            },
            {
                "heading": "Precios y plazos de entrega",
                "paragraphs": [
                    "Los equipos básicos de 7.000 BTU son los más económicos. Los modelos más silenciosos de 12.000 BTU, con inverter y mejor eficiencia, cuestan bastante más.",
                    "Compara también envío, devolución, garantía y kit de ventana. Un precio bajo puede perder valor si necesitas accesorios adicionales.",
                ],
            },
            {
                "heading": "Checklist antes de comprar",
                "bullets": [
                    "Mide la apertura para el tubo de aire caliente",
                    "Evacúa el aire caliente al exterior",
                    "Revisa el ruido si lo usarás en un dormitorio",
                    "Compara eficiencia, consumo y temporizador",
                    "Ten en cuenta peso y ruedas",
                    "Verifica entrega, devolución y garantía",
                ],
            },
        ],
        "faq_title": "Preguntas frecuentes sobre aire acondicionado portátil",
        "faqs": [
            {
                "question": "¿Cuántos BTU necesito para mi habitación?",
                "answer": "Orientación: 7.000 BTU hasta 20 m², 9.000 BTU para 25–35 m² y al menos 12.000 BTU para 35–50 m². Con mucho sol o mal aislamiento elige más potencia.",
            },
            {
                "question": "¿Cuánto cuesta un aire acondicionado portátil en {country}?",
                "answer": "El precio depende de potencia, ruido y eficiencia. Consulta la lista en directo para ver la horquilla actual.",
            },
            {
                "question": "¿Por qué se agotan tan rápido?",
                "answer": "En una ola de calor la demanda crece más rápido que el stock y la capacidad de reparto, por eso la disponibilidad cambia a diario.",
            },
            {
                "question": "¿Enfría toda la habitación?",
                "answer": "Sí, si la potencia es suficiente y el aire caliente se expulsa al exterior. En espacios muy grandes o abiertos suele ser mejor un equipo más potente o una instalación fija.",
            },
            {
                "question": "¿Cómo recibo un aviso cuando haya stock?",
                "answer": "Crea una alerta en la página de búsqueda de {country}. KlimaRadar te avisará cuando haya una unidad adecuada disponible.",
            },
        ],
    },
    "nl": {
        "title": "Draagbare airconditioner 2026: BTU, prijzen en voorraad — KlimaRadar",
        "description": "Aankoopgids voor draagbare airconditioners in {country}: juiste BTU, realistische prijzen, levertijd en beschikbare modellen.",
        "h1": "Draagbare airconditioner 2026: aankoopgids voor {country}",
        "lead": "Tijdens hittegolven kunnen populaire modellen binnen enkele uren uitverkocht zijn. Deze gids helpt je de juiste capaciteit, een realistisch budget en beschikbare units te kiezen.",
        "badge": "Aankoopgids 2026",
        "read_guide": "Lees de gids →",
        "card_title": "Aankoopgids: draagbare airconditioners in {country}",
        "card_body": "BTU-capaciteit, prijsklasse, levertijd en aankoopchecklist.",
        "cities_title": "Zoeken in deze steden",
        "other_guides_title": "Meer Europese gidsen",
        "live_title": "Bekijk live voorraad en prijzen",
        "live_body": "KlimaRadar vergelijkt beschikbaarheid en prijzen, zodat je kunt kopen vóór de voorraad op is.",
        "cta": "Bekijk beschikbare units in {country}",
        "sections": [
            {
                "heading": "Waarom beschikbaarheid in {country} snel wisselt",
                "paragraphs": [
                    "Vraag piekt zodra hitte meerdere dagen aanhoudt. Modellen van 9.000 en 12.000 BTU zijn vaak als eerste uitverkocht omdat ze geschikt zijn voor veel kamers.",
                    "KlimaRadar volgt aanbiedingen van {retailers}. Gebruik deze gids om te kiezen en de live lijst voor actuele prijzen en voorraad.",
                ],
            },
            {
                "heading": "Hoeveel BTU heb ik nodig?",
                "paragraphs": [
                    "De benodigde capaciteit hangt af van oppervlakte, zon, isolatie, plafondhoogte en warmtebronnen. Kies in een zonnige zolderkamer de hogere klasse.",
                ],
                "table_title": "Richtlijnen voor koelcapaciteit",
                "table_headers": ["Oppervlakte", "Aanbevolen capaciteit", "Gebruik"],
                "table_rows": [
                    ["tot 20 m²", "7.000 BTU / 2,0 kW", "slaapkamer, kleine werkkamer"],
                    ["25–35 m²", "9.000 BTU / 2,6 kW", "woonkamer, gedeelde ruimtes"],
                    ["35–50 m²", "12.000 BTU / 3,5 kW", "grote kamers, open ruimtes"],
                    ["meer dan 50 m²", "14.000 BTU of meer", "hoge warmtelast"],
                ],
            },
            {
                "heading": "Prijzen en levertijd inschatten",
                "paragraphs": [
                    "Basismodellen van 7.000 BTU zijn het voordeligst. Stillere 12.000-BTU-units met inverter en betere efficiëntie zijn duidelijk duurder.",
                    "Vergelijk ook verzending, retour, garantie en raamkit. Een lage prijs is minder interessant als je extra accessoires nodig hebt.",
                ],
            },
            {
                "heading": "Checklist voor het kopen",
                "bullets": [
                    "Meet de opening voor de afvoerslang",
                    "Voer warme lucht naar buiten af",
                    "Controleer geluidsniveau voor een slaapkamer",
                    "Vergelijk energielabel, verbruik en timer",
                    "Let op gewicht en wieltjes",
                    "Bekijk levering, retour en garantie",
                ],
            },
        ],
        "faq_title": "Veelgestelde vragen over draagbare airconditioners",
        "faqs": [
            {
                "question": "Hoeveel BTU heb ik nodig voor mijn kamer?",
                "answer": "Richtlijn: 7.000 BTU tot 20 m², 9.000 BTU voor 25–35 m² en minstens 12.000 BTU voor 35–50 m². Bij veel zon of slechte isolatie kies je beter hoger.",
            },
            {
                "question": "Wat kost een draagbare airconditioner in {country}?",
                "answer": "De prijs hangt af van capaciteit, geluid en efficiëntie. De live lijst toont de actuele prijsrange.",
            },
            {
                "question": "Waarom zijn modellen snel uitverkocht?",
                "answer": "Tijdens hittegolven stijgt de vraag sneller dan voorraad en levercapaciteit, waardoor beschikbaarheid per dag kan veranderen.",
            },
            {
                "question": "Koelt een draagbare airconditioner een hele kamer?",
                "answer": "Ja, als de capaciteit past bij de oppervlakte en warme lucht buiten wordt afgevoerd. Voor hele grote of open ruimtes is een krachtiger of vast systeem vaak beter.",
            },
            {
                "question": "Hoe krijg ik een melding bij nieuwe voorraad?",
                "answer": "Maak een melding aan op de zoekpagina voor {country}. KlimaRadar waarschuwt zodra een geschikte unit weer beschikbaar is.",
            },
        ],
    },
    "en": {
        "title": "Portable Air Conditioner 2026: BTU, Prices and Stock — KlimaRadar",
        "description": "Portable air conditioner buying guide for {country}: BTU sizing, realistic prices, delivery times and models currently in stock.",
        "h1": "Portable Air Conditioner 2026: Buying Guide for {country}",
        "lead": "During heat waves, popular portable air conditioners can sell out within hours. This guide explains how to choose the right BTU size, set a realistic budget and find available units faster.",
        "badge": "2026 buying guide",
        "read_guide": "Read guide →",
        "card_title": "Buying guide: portable air conditioners in {country}",
        "card_body": "BTU sizing, price expectations, delivery and a pre-purchase checklist.",
        "cities_title": "Search in these cities",
        "other_guides_title": "More European AC guides",
        "live_title": "Check live stock and prices",
        "live_body": "KlimaRadar compares availability and prices so you can buy before stock disappears.",
        "cta": "See available units in {country}",
        "sections": [
            {
                "heading": "Why availability changes quickly in {country}",
                "paragraphs": [
                    "Demand rises when hot weather lasts several days. Models around 9,000 and 12,000 BTU often disappear first because they suit many room sizes and budgets.",
                    "KlimaRadar tracks offers from {retailers}. Use this guide to decide what to buy and the live listing for the current stock and price.",
                ],
            },
            {
                "heading": "How many BTU do you need?",
                "paragraphs": [
                    "Cooling capacity depends on room size, ceiling height, sunlight, insulation and heat-producing appliances. For a sunny top-floor room, move up one capacity class.",
                ],
                "table_title": "Portable AC capacity guide",
                "table_headers": ["Room size", "Recommended capacity", "Typical use"],
                "table_rows": [
                    ["up to 20 m²", "7,000 BTU / 2.0 kW", "bedroom, small office"],
                    ["25–35 m²", "9,000 BTU / 2.6 kW", "living room, shared rooms"],
                    ["35–50 m²", "12,000 BTU / 3.5 kW", "large rooms, open areas"],
                    ["over 50 m²", "14,000 BTU or more", "high heat load"],
                ],
            },
            {
                "heading": "Prices and delivery expectations",
                "paragraphs": [
                    "Basic 7,000 BTU models are usually cheapest. Quieter 12,000 BTU units with inverter technology and better efficiency cost considerably more.",
                    "Compare delivery fees, returns, warranty support and window kits. A low headline price can lose value if you need extra accessories.",
                ],
            },
            {
                "heading": "Checklist before buying",
                "bullets": [
                    "Measure the window or door opening for the exhaust hose",
                    "Vent hot air outside, never into another closed room",
                    "Check noise output for bedrooms",
                    "Compare energy label, consumption and timer",
                    "Consider weight and casters",
                    "Review delivery date, returns and warranty",
                ],
            },
        ],
        "faq_title": "Portable air conditioner FAQs",
        "faqs": [
            {
                "question": "How many BTU do I need for my room?",
                "answer": "As a guide: 7,000 BTU for rooms up to 20 m², 9,000 BTU for 25–35 m² and at least 12,000 BTU for 35–50 m². Choose a higher rating for strong sunlight or weak insulation.",
            },
            {
                "question": "How much does a portable air conditioner cost in {country}?",
                "answer": "Price depends on capacity, noise and efficiency. The live listing shows the current range rather than an outdated fixed price.",
            },
            {
                "question": "Why are portable air conditioners out of stock?",
                "answer": "During heat waves demand grows faster than stock and delivery capacity, so availability can change several times a day.",
            },
            {
                "question": "Can a portable AC cool an entire room?",
                "answer": "Yes, if the capacity matches the room size and hot air is vented outside. For very large or open spaces, a more powerful or fixed system is often better.",
            },
            {
                "question": "How do I get notified when stock returns?",
                "answer": "Create an alert on the {country} search page. KlimaRadar emails you as soon as a matching unit becomes available.",
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


def guide_path(country: str) -> str:
    return f"/guides/{country.lower()}/{GUIDE_SLUG}"


def get_country_guide(country: str) -> dict | None:
    """Return formatted localized buying-guide content for a market."""
    code = country.upper()
    config = _GUIDE_COUNTRY_CONFIG.get(code)
    if config is None:
        return None
    language = COUNTRY_LANGUAGES.get(code, "en")[:2]
    template = _GUIDE_LANGUAGE_TEMPLATES.get(language, _GUIDE_LANGUAGE_TEMPLATES["en"])
    country_name = COUNTRY_NAMES.get(code, {}).get(language, code)
    return _format_value(
        template,
        country=country_name,
        retailers=config["retailers"],
    ) | {
        "country": code,
        "country_name": country_name,
        "language": language,
        "html_lang": COUNTRY_LANGUAGES.get(code, "en"),
        "path": guide_path(code),
    }


def list_country_guides(exclude: str | None = None) -> list[dict]:
    """Return compact guide metadata for internal links and the sitemap."""
    guides = []
    for code in _GUIDE_COUNTRY_CONFIG:
        if exclude and code == exclude.upper():
            continue
        guide = get_country_guide(code)
        if guide:
            guides.append(
                {
                    "country": code,
                    "country_name": guide["country_name"],
                    "title": guide["title"],
                    "h1": guide["h1"],
                    "path": guide["path"],
                }
            )
    return guides


def build_article_jsonld(base_url: str, guide: dict) -> dict:
    """Build Article structured data for a country guide."""
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": guide["h1"],
        "description": guide["description"],
        "inLanguage": guide["html_lang"],
        "mainEntityOfPage": f"{base_url}{guide['path']}",
        "datePublished": "2026-08-14",
        "dateModified": "2026-08-14",
        "author": {"@type": "Organization", "name": "KlimaRadar"},
        "publisher": {"@type": "Organization", "name": "KlimaRadar"},
    }
