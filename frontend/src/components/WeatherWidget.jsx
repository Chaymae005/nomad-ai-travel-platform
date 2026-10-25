import { useState, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:8000'

function WeatherWidget({ ville, couleurAccent }) {
  const [meteo, setMeteo] = useState(null)
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    if (!ville) {
      setChargement(false)
      return
    }
    fetch(API_URL + '/platform/meteo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ville: ville }),
    })
      .then(function (r) { return r.json() })
      .then(function (data) { setMeteo(data) })
      .finally(function () { setChargement(false) })
  }, [ville])

  if (chargement) return null
  if (!meteo || meteo.error) return null

  const actuel = meteo.current || {}
  const journalier = meteo.daily_forecast || {}
  const maxAujourdhui = journalier.temperature_2m_max ? journalier.temperature_2m_max[0] : null
  const minAujourdhui = journalier.temperature_2m_min ? journalier.temperature_2m_min[0] : null

  return (
    <div className="bg-white rounded-2xl shadow-sm p-5 w-full max-w-xs">
      <p className="text-sm font-medium text-gray-500 mb-1">{meteo.city}</p>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-4xl font-semibold text-gray-800">
            {Math.round(actuel.temperature)}°
          </p>
          {(maxAujourdhui != null && minAujourdhui != null) && (
            <p className="text-xs text-gray-400 mt-1">
              {Math.round(maxAujourdhui)}° / {Math.round(minAujourdhui)}°
            </p>
          )}
        </div>
        <div className={"text-3xl " + couleurAccent}>☀️</div>
      </div>
    </div>
  )
}

export default WeatherWidget