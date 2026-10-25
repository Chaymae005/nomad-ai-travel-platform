import { useState } from 'react'
import AgentChatBox from './AgentChatBox'

function FloatingChat({ outilsActifs, promptDomaine, couleurAccent }) {
  const [ouvert, setOuvert] = useState(false)

  return (
    <>
      {ouvert && (
        <div className="fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
          <div className={`${couleurAccent || 'bg-teal-500'} px-5 py-4 flex items-center justify-between`}>
            <div>
              <p className="text-white font-semibold text-sm">Discutez avec l'assistant</p>
              <p className="text-white/80 text-xs">Posez vos questions sur cette plateforme</p>
            </div>
            <button onClick={() => setOuvert(false)} className="text-white/80 hover:text-white text-lg">✕</button>
          </div>
          <div className="p-4 max-h-[60vh] overflow-y-auto">
            <AgentChatBox
              outilsActifs={outilsActifs}
              promptDomaine={promptDomaine}
              couleurPrincipale={couleurAccent || 'bg-teal-500'}
            />
          </div>
        </div>
      )}

      <button
        onClick={() => setOuvert(!ouvert)}
        className={`fixed bottom-6 right-6 z-50 flex items-center gap-2 px-5 py-3 ${couleurAccent || 'bg-teal-500'} text-white rounded-full shadow-lg hover:opacity-90 transition`}
      >
        <span className="text-sm font-medium">💬 Chat avec un expert</span>
      </button>
    </>
  )
}

export default FloatingChat