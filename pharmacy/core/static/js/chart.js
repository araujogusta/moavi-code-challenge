const { createApp } = Vue

const app = createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            chart: null,
            debounceTimer: null,
        }
    },
    methods: {
        createChart(data) {
            const ctx = document.querySelector('#chart')

            const chartAlreadyExists = Chart.getChart(ctx);
            if (chartAlreadyExists) {
                chartAlreadyExists.destroy();
            }

            this.chart = new Chart(ctx, {
                data: {
                    datasets: [{
                        label: 'Nº Colaboradores',
                        data,
                        type: 'bar',
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            })
        },
        async fetchChartData(date) {
            const { data } = await axios.get('/api/chart-data?date=' + date)
            const { employee_interval_count } = data
            return employee_interval_count
        },
        async inputNewDate(event) {
            clearTimeout(this.debounceTimer)
            const date = event.target.value
            debounceTimer = setTimeout(async () => {
                const chartData = await this.fetchChartData(date)
                this.createChart(chartData)
            }, 1000)
        },
    },
    async mounted() {
        const currentDate = new Date().toISOString().split('T')[0]
        const chartData = await this.fetchChartData(currentDate)
        this.createChart(chartData)
    }
}).mount('#app')