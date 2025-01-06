const config = {
    development: {
        API_URL: 'http://localhost:5000/api'
    },
    production: {
        API_URL: '/api'
    }
};

// In browser environment, we'll default to production since we're serving via nginx
const ENV = 'production';
export default config[ENV];