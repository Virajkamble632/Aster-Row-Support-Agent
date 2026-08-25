import { createRoot } from 'react-dom/client'
import { useState } from 'react'
import { RotateCcw, Send, ShieldCheck, Sparkles, Truck, Package } from 'lucide-react'
import './styles.css'

const starters = [
  { icon: RotateCcw, label: 'Returns & refunds', prompt: 'What is the return policy?' },
  { icon: Truck, label: 'Shipping windows', prompt: 'How long does shipping to Canada take?' },
  { icon: Package, label: 'Track an order', prompt: 'Can you check order ORD-1007?' },
]

const initialMessage = {
  role: 'assistant',
  content: 'Hello, I\'m the Aster & Row support assistant. Ask me about returns, shipping, products, or an order. I\'ll keep the answer grounded in our current policies.',
}

function App() {
  const [messages, setMessages] = useState([initialMessage])
  const [draft, setDraft] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async (text = draft) => {
    const message = text.trim()
    if (!message || loading) return
    setDraft('')
    setMessages((current) => [...current, { role: 'user', content: message }])
    setLoading(true)
    try {
      const result = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      })
      const data = await result.json()
      setMessages((current) => [...current, { role: 'assistant', content: data.response || data.error }])
    } catch {
      setMessages((current) => [...current, { role: 'assistant', content: 'I can\'t reach the support service right now. Please make sure the API is running on port 8000.' }])
    } finally {
      setLoading(false)
    }
  }

  const reset = async () => {
    await fetch('/api/reset', { method: 'POST' }).catch(() => {})
    setMessages([initialMessage])
    setDraft('')
  }

  return (
    <div className="app-shell">
      <main className="chat-card">
        <header className="simple-header"><div className="brand-mark">A<span>&</span>R</div><div><strong>ASTER & ROW</strong><small>Customer support</small></div><button className="reset-button" title="Reset conversation" onClick={reset}><RotateCcw size={16} /> New chat</button></header>
        <section className="chat-content">
          <div className="intro"><p className="eyebrow">SUPPORT ASSISTANT</p><h1>How can we help?</h1><p>Ask about returns, shipping, products, or an order.</p><div className="privacy"><ShieldCheck size={14} /> Answers use current customer-facing policies</div></div>
          <div className="messages" aria-live="polite">{messages.map((message, index) => <Message key={`${message.role}-${index}`} message={message} />)}{loading && <div className="message-row assistant"><div className="avatar"><Sparkles size={16} /></div><div className="typing"><span /><span /><span /></div></div>}</div>
          <div className="composer-area"><div className="suggestion-row">{starters.map(({ icon: Icon, label, prompt }) => <button key={label} className="suggestion" onClick={() => sendMessage(prompt)}><Icon size={15} /> {label}</button>)}</div><form className="composer" onSubmit={(event) => { event.preventDefault(); sendMessage() }}><input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Type your question..." aria-label="Your question" /><button className="send-button" type="submit" disabled={!draft.trim() || loading} title="Send message"><Send size={18} /></button></form></div>
        </section>
      </main>
    </div>
  )
}

function Message({ message }) {
  const isUser = message.role === 'user'
  return <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>{!isUser && <div className="avatar"><Sparkles size={16} /></div>}<div className={`bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}><p>{message.content}</p>{!isUser && message.content.includes('[Source:') && <div className="source-label"><ShieldCheck size={13} /> Verified policy source</div>}</div></div>
}

const rootContainer = document.getElementById('root')
const root = globalThis.__asterRowRoot ?? createRoot(rootContainer)
globalThis.__asterRowRoot = root
root.render(<App />)

export default App
