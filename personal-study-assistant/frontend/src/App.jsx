import React from 'react'
import Chat from './components/Chat'


export default function App() {
    return (
        <div className="app-root">
            <header>
                <h1>Personal Study Assistant</h1>
            </header>
            <main>
                <Chat />
            </main>
        </div>
    )
}