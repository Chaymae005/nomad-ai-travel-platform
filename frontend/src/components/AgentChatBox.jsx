import { useState, useRef, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:8000'

function AgentChatBox() {
  const [ouvert, setOuvert] = useState(false)
  const [visible, setVisible] = useState(false)
  const [question, setQuestion] = useState('')
  const [historique, setHistorique] = useState([])
  const [enChargement, setEnChargement] = useState(false)
  const zoneMessages = useRef(null)

  useEffect(() => {
    if (ouvert) {
      requestAnimationFrame(() => setVisible(true))
    } else {
      setVisible(false)
    }
  }, [ouvert])

  useEffect(() => {
    if (zoneMessages.current) {
      zoneMessages.current.scrollTop = zoneMessages.current.scrollHeight
    }
  }, [historique, enChargement])

  const fermer = () => {
    setVisible(false)
    setTimeout(() => setOuvert(false), 250)
  }

  const gererEnvoi = async () => {
    if (!question.trim() || enChargement) return

    const nouvelleQuestion = question
    setQuestion('')
    setHistorique((h) => [...h, { role: 'user', text: nouvelleQuestion }])
    setEnChargement(true)

    try {
      const reponse = await fetch(`${API_URL}/agent/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: nouvelleQuestion,
          history: historique,
        }),
      })
      const data = await reponse.json()
      setHistorique(data.history)
    } catch (erreur) {
      setHistorique((h) => [...h, { role: 'model', text: "Désolé, je n'arrive pas à répondre pour le moment." }])
    } finally {
      setEnChargement(false)
    }
  }

  if (!ouvert) {
    return (
      <button
        onClick={() => setOuvert(true)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 pl-4 pr-5 py-3 bg-emerald-800 text-white rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.6">
          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <span className="text-sm font-medium">Assistant voyage</span>
      </button>
    )
  }

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 w-[420px] max-w-[92vw] flex flex-col overflow-hidden rounded-2xl shadow-2xl transition-all duration-300 ease-out ${
        visible ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-95'
      }`}
      style={{ height: '620px', maxHeight: '80vh' }}
    >
      {/* Fond dégradé façon aurora, vert foncé, transparent */}
      <div
  className="absolute inset-0 -z-10"
  style={{
    background: `
      radial-gradient(circle at 20% 20%, rgba(16, 87, 66, 0.3), transparent 55%),
      radial-gradient(circle at 80% 15%, rgba(6, 78, 59, 0.25), transparent 50%),
      radial-gradient(circle at 60% 90%, rgba(4, 47, 46, 0.3), transparent 55%),
      linear-gradient(160deg, rgba(6, 40, 34, 0.55), rgba(4, 25, 22, 0.6))
    `,
    backdropFilter: 'blur(24px)',
  }}
/>

      {/* Header */}
      <div className="flex justify-between items-center px-5 py-4 border-b border-white/10">
        <div>
          <p className="font-serif text-white text-base">Assistant </p>
          <p className="text-white/50 text-xs mt-0.5">Posez vos questions sur votre destination</p>
        </div>
        <button onClick={fermer} className="text-white/60 hover:text-white text-lg leading-none transition">
          ✕
        </button>
      </div>

      {/* Messages */}
      <div ref={zoneMessages} className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
        {historique.length === 0 && (
          <p className="text-white/40 text-sm text-center mt-10">
            Demandez-moi la météo, la culture, ou des idées de voyage.
          </p>
        )}

        {historique.map((message, index) => (
          <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                message.role === 'user'
                  ? 'bg-emerald-700/80 text-white rounded-br-sm'
                  : 'bg-white/10 text-white/90 rounded-bl-sm'
              }`}
            >
              {message.text}
            </div>
          </div>
        ))}

        {enChargement && (
          <div className="flex justify-start">
            <div className="bg-white/10 px-4 py-3 rounded-2xl rounded-bl-sm flex gap-1.5">
              <span className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex items-center gap-2 border-t border-white/10 px-4 py-3">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && gererEnvoi()}
          placeholder="Écrivez votre message..."
          disabled={enChargement}
          className="flex-1 outline-none text-white placeholder-white/40 bg-transparent text-sm"
        />
        <button
          onClick={gererEnvoi}
          disabled={enChargement || !question.trim()}
          className="text-white text-sm font-medium hover:opacity-70 transition disabled:opacity-30"
        >
          Envoyer
        </button>
      </div>
    </div>
  )
}

export default AgentChatBox