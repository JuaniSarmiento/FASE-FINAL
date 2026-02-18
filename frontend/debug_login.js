import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1/auth';

async function testLogin() {
    const email = 'test_1771268025928@example.com';
    const password = 'password123';

    try {
        console.log('Testing Login...');
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

testLogin();
