axios.defaults.xsrfCookieName = "csrftoken"
axios.defaults.xsrfHeaderName = "X-CSRFToken"

const { createApp } = Vue

const app = createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            markingsImports: [],
        }
    },
    methods: {
        async uploadNewFile(event) {
            const files = event.target.files
            const formData = new FormData()
            formData.append('file', files[0])

            const { data } = await axios.post('/api/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
            const { markings_import } = data

            this.markingsImports.unshift(markings_import)
            this.$refs.uploadFilesInput.value = null
        },
        openFileInput() {
            this.$refs.uploadFilesInput.click()
        },
        formatDateTimeString(dateTimeString) {
            return new Date(dateTimeString).toLocaleString('pt-BR')
        }
    },
    async mounted() {
        const { data } = await axios.get('/api/markings-imports')
        const { markings_imports } = data
        this.markingsImports = markings_imports
    }
}).mount('#app')