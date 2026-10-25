function StatBlock({ titre, sousTitre, couleurAccent, onClick }) {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 cursor-pointer hover:shadow-md transition"
    >
      <p className={`text-xs font-medium uppercase tracking-wide mb-2 ${couleurAccent}`}>
        {sousTitre}
      </p>
      <h4 className="text-lg font-semibold text-gray-800">{titre}</h4>
    </div>
  )
}

export default StatBlock