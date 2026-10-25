import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

const iconParDefaut = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

function AjusterCarte({ points }) {
  const map = useMap()

  useEffect(() => {
    const conteneur = map.getContainer()

    const recalculer = () => {
      map.invalidateSize()
      if (points.length === 1) {
        map.setView([points[0].latitude, points[0].longitude], 4)
      } else if (points.length > 1) {
        const bounds = L.latLngBounds(points.map((p) => [p.latitude, p.longitude]))
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 5 })
      }
    }

    recalculer()
    const observateur = new ResizeObserver(recalculer)
    observateur.observe(conteneur)

    return () => observateur.disconnect()
  }, [points, map])

  return null
}

function CarteFavoris({ points }) {
  if (!points || points.length === 0) {
    return <p className="text-sm text-gray-400 p-6">Ajoutez des favoris pour les voir apparaître sur la carte.</p>
  }

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer
        center={[points[0].latitude, points[0].longitude]}
        zoom={2}
        minZoom={2}
        maxZoom={10}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
        worldCopyJump={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        <AjusterCarte points={points} />
        {points.map((p) => (
          <Marker key={`${p.nom}-${p.latitude}-${p.longitude}`} position={[p.latitude, p.longitude]} icon={iconParDefaut}>
            <Popup>{p.nom}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}

export default CarteFavoris