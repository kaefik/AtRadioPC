from flask import Flask, render_template, request

app = Flask(__name__)

# Список радиостанций
radio_stations = [
    {"name": "Китап радиосы", "url": "http://radio.tatmedia.com:8800/kitapfm"},
    {"name": "Саф радиосы", "url": "https://c7.radioboss.fm:18335/stream"},
    {"name": "Күнел Радиосы", "url": "http://live.kunelradio.ru:8000/128.mp3"},
    {"name": "Курай ФМ", "url": "http://av.bimradio.ru:8066/kurai_mp3"},
    {"name": "Юлдаш (башкирское радио)", "url": "https://radio.mediacdn.ru/uldash.mp3"},
    {"name": "Радио Матур", "url": "http://radio.matur-tv.ru/radio/radio-mp3-128k"},
    {"name": "Ватан сердасы (крым татар)", "url": "http://91.214.128.125:64000/vatan"},
    {"name": "Ашҡаҙар радиоһы (Башҡортостан)", "url": "http://radio.mediacdn.ru/ashkadar.mp3"},
    {"name": "Дулкын радиосы", "url": "http://radio.tatmedia.com:8800/Saba"},
    {"name": "РадиоТМК (Казахстан)", "url": "http://a4.radioheart.ru:8036/RH13170"},
    {"name": "Татарская поп музыка", "url": "http://pub0101.101.ru:8000/stream/pro/aac/64/246"},
    {"name": "ТатРадиоЦентр", "url": "https://listen4.myradio24.com/trc"},
    {"name": "Белем радиосы", "url": "https://radiobelem.ru/belem128"},
    {"name": "Тәртип FM (93.1) Казань", "url": "https://radio.tatmedia.com:8443/tartipfm"},
    {"name": "Татар радиосы", "url": "https://tatarradio.hostingradio.ru/tatarradio320.mp3"},
    {"name": "Болгар радиосы", "url": "https://live.bolgarradio.com/b_aac_hifi.m3u8"},
    {"name": "Татарстан Авазы", "url": "https://listen6.myradio24.com/gtrk"},
    {"name": "Роксана радиосы", "url": "https://listen1.myradio24.com/2761"},
    {"name": "Татарская Народная Музыка", "url": "https://pub0302.101.ru:8000/stream/pro/aac/64/262"},
    {"name": "Әтнә театры интернет-радиосы", "url": "https://c2.radioboss.fm:18571/stream"},
    {"name": "ТАТАРСТАН МӘДӘНИЯТЕ", "url": "https://c20.radioboss.fm:8560/stream"},
    {"name": "Ногайское радио", "url": "http://radio05.ru:8000/nogayskoe_radio_128"},
    {"name": "Таван радио (Чувашское)", "url": "http://icecast.ntrk21.ru:8000/tavan"},
    {"name": "Жулдыз FM", "url": "http://91.201.214.229:8000/zhulduz"}
]



@app.route("/")
def index():
    return render_template("index.html", stations=radio_stations)


@app.route("/play", methods=["POST"])
def play():
    """Страница для воспроизведения выбранной радиостанции."""
    station_url = request.form.get("station_url")
    station_name = request.form.get("station_name")
    return render_template("play.html", station_name=station_name, station_url=station_url)

if __name__ == "__main__":
    app.run(debug=True)