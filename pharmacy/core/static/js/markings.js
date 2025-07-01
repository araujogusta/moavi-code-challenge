const { createApp } = Vue

const app = createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            markings: [],
            isLoading: true,
        }
    },
    async mounted() {
        const { data } = await axios.get('/api/markings')
        const { markings } = data
        this.markings = markings
        this.isLoading = false
    }
}).mount('#app')