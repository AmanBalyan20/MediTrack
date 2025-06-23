const request = require('supertest'); 
const express = require('express'); 
const routes = require('./routes/route'); 
const axios = require('axios');


jest.mock('axios');

const app = express(); 
app.use(express.json()); 
app.use('/api', routes); 

describe('/signin endpoint tests', () => {
    it('should return 200 and token on successful sign-in', async () => {
        // Mock response for successful sign-in
        const mockResponse = {
            status: 200,
            data: { token: 'mock-token' },
        };

        // Mock axios.post
        axios.post.mockResolvedValue(mockResponse);

        const response = await request(app)
            .post('/api/signin')
            .send({ email: 'test@example.com', password: 'password123' });

        expect(response.status).toBe(200);
        expect(response.body).toEqual({
            message: 'Sign-in successful',
            token: 'mock-token',
        });
    });

    it('should return the same status and error as the external API on failure', async () => {
        // Mock response for failed sign-in
        const mockErrorResponse = {
            response: {
                status: 401,
                data: { error: 'Invalid credentials' },
            },
        };

        // Mock axios.post to throw an error
        axios.post.mockRejectedValue(mockErrorResponse);

        const response = await request(app)
            .post('/api/signin')
            .send({ email: 'test@example.com', password: 'wrongpassword' });

        expect(response.status).toBe(401);
        expect(response.body).toEqual({ error: 'Invalid credentials' });
    });

    it('should handle server errors gracefully', async () => {
        // Mock server error response
        const mockErrorResponse = new Error('Server error');
        axios.post.mockRejectedValue(mockErrorResponse);

        const response = await request(app)
            .post('/api/signin')
            .send({ email: 'test@example.com', password: 'password123' });

        expect(response.status).toBe(500);
        expect(response.body).toEqual({ error: 'Sign-in failed' });
    });
});
