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
            // Prettify response: convert markdown-like lists and bold to HTML
            let text = r.response
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') // bold
                .replace(/\* (.+?)(?=\n|$)/g, '<li>$1</li>') // list items
                .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>') // wrap lists
                .replace(/\n{2,}/g, '<br/>') // double newlines to breaks

            const bot = { role: 'assistant', text }
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
                    <div
                        key={i}
                        className={m.role}
                        dangerouslySetInnerHTML={{ __html: m.text }}
                    />
                ))}
            </div>
            <div className="controls">
                <input
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="Ask something or type 'summarize: <text>'"
                    onKeyDown={e => {
                        if (e.key === 'Enter' && !loading) submit()
                    }}
                />
                <button onClick={submit} disabled={loading}>{loading ? '...' : 'Send'}</button>
            </div>
        </div>
    )
}