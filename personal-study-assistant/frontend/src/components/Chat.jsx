import React, { useState } from 'react'
import { sendPrompt } from '../api'


export default function Chat() {
    const [input, setInput] = useState('')
    const [messages, setMessages] = useState([])
    const [loading, setLoading] = useState(false)


    async function submit() {
        if (!input) return
        const userMsg = { role: 'user', text: input }
        setMessages(m => [...m, userMsg])
        setLoading(true)
        try {
            const r = await sendPrompt(input, 'chat')
            const bot = { role: 'assistant', text: r.response }
            setMessages(m => [...m, bot])
        } catch (err) {
            setMessages(m => [...m, { role: 'assistant', text: 'Error: ' + (err.message || err) }])
        } finally {
            setLoading(false)
            setInput('')
        }
    }


    return (
        <div className="chat">
            <div className="messages">
                {messages.map((m, i) => (
                    <div key={i} className={m.role}>{m.text}</div>
                ))}
            </div>
            <div className="controls">
                <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask something or type 'summarize: <text>'" />
                <button onClick={submit} disabled={loading}>{loading ? '...' : 'Send'}</button>
            </div>
        </div>
    )
}