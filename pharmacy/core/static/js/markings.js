const { createApp } = Vue;

const app = createApp({
    delimiters: ['${', '}'],
    data() {
        return {
            markings: [],
            page: 1,
            hasNextPage: true
        };
    },
    methods: {
        async loadMore() {
            if (!this.hasNextPage) return;

            const res = await axios.get(`/api/markings?page=${this.page}`);
            const data = res.data;

            this.markings.push(...data.markings);
            this.page += 1;
            this.hasNextPage = data.has_next;
        },
        onScroll() {
            const container = this.$refs.scrollContainer;
            const scrollThreshold = 100;

            const atBottom =
                container.scrollTop + container.clientHeight >=
                container.scrollHeight - scrollThreshold;

            if (atBottom) {
                this.loadMore()
            }
        }
    },
    mounted() {
        this.loadMore()
    }
}).mount('#app')
