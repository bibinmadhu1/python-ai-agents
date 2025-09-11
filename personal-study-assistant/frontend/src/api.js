import axios from 'axios'


const apiOld = axios.create({ baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' })
const api = axios.create({ baseURL:  'https://super-duper-trout-x5p4pqr4g7g7hpg7p-8000.app.github.dev' })


export async function sendPrompt(prompt, mode = 'chat') {
    const res = await api.post('/api/chat', { prompt, mode }, {
        headers: {
            'Content-Type': 'application/json'
        }
    })
    return res.data
}