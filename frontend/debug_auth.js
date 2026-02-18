import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1/auth';

async function testAuth() {
    console.log('Testing Registration...');
    const email = `test_${Date.now()}@example.com`;
    const password = 'password123';

    try {
        // 1. Register
        const regRes = await axios.post(`${API_URL}/register`, {
            email,
            password,
            username: 'testuser',
            full_name: 'Test User'
        });
        console.log('Register Response Status:', regRes.status);
        console.log('Register Response Data:', JSON.stringify(regRes.data, null, 2));

        // 2. Login
        console.log('\nTesting Login...');
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        // Axios with FormData might need headers handling or just simpler post
        // For node, we might need 'form-data' package, but let's try URLSearchParams which is standard
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        const loginRes = await axios.post(`${API_URL}/token`, params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        console.log('Login Response Status:', loginRes.status);
        console.log('Login Response Data:', JSON.stringify(loginRes.data, null, 2));

    } catch (error) {
        console.error('Error:', error.response ? error.response.data : error.message);
    }
}

testAuth();
