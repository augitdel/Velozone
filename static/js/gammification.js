let metingen = []
let transponders = []
let tijden = []

function startMetingen() {
    const socket = io.connect('http://127.0.0.1:5000');
    socket.on('connect', function () {
        console.log("Verbonden met WebSocket!");
    });
    socket.on('fast_lap_data', function (data) {
        VoegMetingToe(data);
    });
    socket.on('disconnect', function () {
        console.log("WebSocket-verbinding verbroken.");
    });
}

function VoegMetingToe(data) {
    let meting = JSON.parse(data);
    console.log(meting);

    meting.forEach(item => {
        transponders.push(item[0]);  // Rijder (transponder) wordt item[0]
        tijden.push(item[1]);  // Tijd wordt item[1]
    });

    console.log("Alle transponders:", transponders);
    console.log("Alle tijden:", tijden);
    toonGrafiek(metingen);
}

// functie om de metingen te tonen
function toonGrafiek(metingen) {
    let grafiek = echarts.init(document.getElementById('grafiek'));
    let option = {
        backgroundColor: '#f5f5f5',
        title: {
            text: 'Snelste tijd per lap'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['Snelste tijd'],
            align: 'left',
        },
        xAxis: {
            type: 'category', // X-as als categorie
            data: transponders, // Lijst met transponder-ID's
            axisLabel: {
                rotate: 45, // Draai labels om ruimte te besparen
                interval: 0 // Toon alle labels
            }
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 50
        },
        series: [
            {
                name: 'Snelste tijd',
                type: 'line', // 'line' kan ook, maar 'bar' is beter voor categorieën
                data: tijden, // Lijst met bijbehorende rondetijden
                itemStyle: {
                    color: '#007bff'
                },
                label: {
                    show: true, // Zorg ervoor dat de labels zichtbaar zijn
                    position: 'top', // Positie van het label boven de datapunten
                    color: '#333', // Kleuren van de labels
                    fontSize: 12, // Grootte van de labels
                }
            }
        ]
    };

    grafiek.setOption(option);
}


window.onload = function () {
    if (document.getElementById('grafiek')) {
        startMetingen();
    } else {
        console.error("Element #grafiek niet gevonden!");
    }
};