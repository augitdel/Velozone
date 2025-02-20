let metingen;

function startMetingen() {
    metingen = []; // metingen bijhouden
    // websocket openen om nieuwe metingen te ontvangen in JSON formaat en dan te verwerken
}

function startMetingenTest() {
    metingen = [];
    setInterval(() => {
        let tijd = new Date();
        let waarde = 30.4 + Math.random() * 0.1;
        metingen.push([tijd, waarde]);
        console.log([tijd, waarde])
        toonGrafiek(metingen);
    }, 10);
}

// functie om de metingen te tonen
function toonGrafiek(metingen) {
    let grafiek = echarts.init(document.getElementById('grafiek'));
    let option = {
        backgroundColor: '#f5f5f5',
        title: {
            text: 'Snelheid renner'
        },
        tooltip: {},
        legend: {
            data: [''],
            align: 'left',
        },
        xAxis: {
            type: 'time',
            axisLabel: {
                formatter: '{HH}-{mm}'
            }
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 50
        },
        series: [
            {
                name: 'snelheid',
                type: 'line',
                data: metingen // metingen instellen
            }
        ]
    };
    grafiek.setOption(option);
}

window.onload = function () {
    if (document.getElementById('grafiek')) {
        startMetingenTest();
    } else {
        console.error("Element #grafiek niet gevonden!");
    }
};