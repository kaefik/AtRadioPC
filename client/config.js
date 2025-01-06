const config = {
    development: {
        API_URL: 'http://localhost:5000/api'
    },
    production: {
        API_URL: '/api'
    }
};

export default config[window.ENV];