let order_ctx = $('#orderChart')[0].getContext('2d');
let income_ctx = $('#incomeChart')[0].getContext('2d');
const month = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь'
};
let statistics = $('#statistics').val().split('. ');
let orders = statistics[0].split(', ');
let income = statistics[1].split(', ');
let labels = statistics[2].split(', ');
let period = statistics[3];

function stats_Chart(ctx, data, label) {
    let chartPeriod = [];
    if (period === 'month') {
        labels.forEach(now_month => {
            chartPeriod.push(month[now_month]);
        });
    } else if (period === 'year') {
        labels.forEach(now_year => {
            console.log(now_year)
            chartPeriod.push(now_year);
        });
    } else {
        labels.forEach(now_day => {
            chartPeriod.push(now_day.slice(-5));
        })
    }
    console.log(chartPeriod)

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartPeriod,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

stats_Chart(order_ctx, orders, 'Количество заказов')
stats_Chart(income_ctx, income, 'Доход')
