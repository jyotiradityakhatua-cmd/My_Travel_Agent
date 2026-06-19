// import React, { useState, useEffect, useRef } from 'react'

// // Icon and color configuration for map markers
// const TYPE_EMOJI: Record<string, string> = { 
//   hotel: "🏨", 
//   attraction: "🏛️", 
//   restaurant: "🍽️", 
//   transport: "✈️", 
//   airport: "✈️", 
//   other: "📍" 
// }

// const TYPE_COLOR: Record<string, string> = { 
//   hotel: "#1d4ed8", 
//   attraction: "#059669", 
//   restaurant: "#d97706", 
//   transport: "#7c3aed", 
//   airport: "#7c3aed", 
//   other: "#64748b" 
// }

// // Interfaces
// interface Message {
//   id: string
//   role: 'user' | 'assistant' | 'system'
//   text: string
//   isStreaming?: boolean
// }

// interface ChatSession {
//   chat_id: string
//   title: string
//   created_at: string
// }

// interface Place {
//   _id: number
//   name: string
//   type: string
//   day: number | null
//   status: 'found' | 'pending' | 'missing'
//   lat?: number
//   lng?: number
//   address?: string
// }

// interface User {
//   user_id: string
//   username: string
// }

// // ── UTILITY FUNCTIONS ──
// function cleanForDisplay(raw: string) {
//   return raw
//     .replace(/\n*<!--LOCATIONS_JSON:[\s\S]*?-->/g, "")
//     .replace(/\n*<!--CHAT_ID:[^>]+-->/g, "")
//     .trimEnd()
// }

// function tryExtractLocationsJSON(raw: string) {
//   const m = raw.match(/<!--LOCATIONS_JSON:(\[[\s\S]*?\])-->/)
//   if (!m) return null
//   try {
//     return JSON.parse(m[1])
//   } catch (e) {
//     return null
//   }
// }

// function guessType(name: string) {
//   const n = name.toLowerCase()
//   if (/hotel|resort|inn|villa|lodge|suites|oyo|hyatt|marriott|hilton|taj|leela|radisson|novotel|oberoi|lemon tree|itc |sheraton|westin|four seasons|ritz|intercontinental/.test(n)) return "hotel"
//   if (/airport|airbase|aerodrome/.test(n)) return "airport"
//   if (/station|terminal|port|bus stand/.test(n)) return "transport"
//   if (/restaurant|cafe|café|diner|bistro|bar |pub |eatery|dhaba|food/.test(n)) return "restaurant"
//   if (/beach|fort|temple|museum|palace|market|falls|lake|park|garden|monument|gate|cave|ruins|viewpoint|mahal|gurdwara|church|mosque/.test(n)) return "attraction"
//   return "other"
// }

// function looksLikePlace(t: string) {
//   if (!t || t.length < 3 || t.length > 80) return false
//   if (/^\d+$/.test(t)) return false
//   if (/[₹$€£]/.test(t.slice(0, 4))) return false
//   if (/per night|per day|rating|stars?|\d+\s*night|checkout|check-in/i.test(t)) return false
//   if (/^(Budget|Mid|Luxury|Deluxe|Standard|Premium|Morning|Afternoon|Evening|Night|Total|Price|Note|Day|Here)$/i.test(t.split(" ")[0])) return false
//   return true
// }

// function guessDestination(userText: string) {
//   const m = userText.match(/(?:to|in|at|visiting?|for|going to)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)/)
//   return m ? m[1] : ""
// }

// function extractPlacesFromMarkdown(md: string, destHint: string) {
//   const results: Array<{ name: string; type: string; day: number | null; geocodeQuery: string }> = []
//   const seen = new Set<string>()

//   function add(name: string, type?: string, day?: number | null) {
//     name = name.trim().replace(/[.,;:]+$/, "").trim()
//     if (name.length < 3 || name.length > 80) return
//     const key = name.toLowerCase()
//     if (seen.has(key)) return
//     const SKIP = /^(morning|afternoon|evening|night|total|note|day|here|check|stay|book|enjoy|experience|budget|luxury|premium|standard|mid-range|deluxe|return|depart|price|cost|rate|the|and|or|for|with|from|to|via)/i
//     if (SKIP.test(name)) return
//     if (/^\d/.test(name)) return
//     seen.add(key)

//     const geocodeQuery = destHint && !name.toLowerCase().includes(destHint.toLowerCase())
//       ? `${name}, ${destHint}`
//       : name

//     results.push({ name, type: type || guessType(name), day: day || null, geocodeQuery })
//   }

//   // PASS 1: Scan line by line to capture Day context
//   let currentDay: number | null = null
//   const lines = md.split("\n")

//   for (const line of lines) {
//     const dayMatch = line.match(/\bDay\s+(\d+)\b/i)
//     if (dayMatch) currentDay = parseInt(dayMatch[1])

//     const boldRe = /\*\*([A-Z][A-Za-z0-9&'.()\-,\/ ]{2,55}?)\*\*/g
//     let m
//     while ((m = boldRe.exec(line)) !== null) {
//       const t = m[1].trim()
//       if (looksLikePlace(t)) add(t, guessType(t), currentDay)
//     }

//     const hotelRe = /\b(Hotel|Resort|Hyatt|Marriott|Hilton|Taj|Leela|Radisson|Novotel|OYO|Lemon Tree|ITC|Oberoi|Trident|Vivanta|Ginger|Park|The (?:Leela|Taj|Park|Westin|Ritz))\s+([A-Z][A-Za-z0-9&'.()\-,\/ ]{1,45})/g
//     while ((m = hotelRe.exec(line)) !== null) {
//       const full = (m[1] + " " + m[2]).trim().replace(/[.,;]+$/, "")
//       if (looksLikePlace(full)) add(full, "hotel", currentDay)
//     }

//     const placeRe = /\b([A-Z][A-Za-z ]{2,35}(?:Beach|Fort|Temple|Market|Palace|Museum|Park|Lake|Falls|Gate|Garden|Monument|Cafe|Airport|Station|Mahal|Gurdwara|Church|Mosque|Cave|Viewpoint|Hill|Peak|Island|Village))\b/g
//     while ((m = placeRe.exec(line)) !== null) {
//       if (looksLikePlace(m[1])) add(m[1].trim(), guessType(m[1]), currentDay)
//     }

//     const airportRe = /\b([A-Z][A-Za-z ]{3,40}(?:International\s+)?Airport)\b/g
//     while ((m = airportRe.exec(line)) !== null) {
//       add(m[1].trim(), "airport", null)
//     }
//   }

//   // PASS 2: emoji-tagged hotels
//   const emojiRe = /[🏨🏩]\s*([A-Z][A-Za-z0-9&'.()\- ]{3,55}?)(?:\s*[⭐★|]|\s*\d|\n|$)/g
//   let m
//   while ((m = emojiRe.exec(md)) !== null) {
//     const t = m[1].trim()
//     if (looksLikePlace(t)) add(t, "hotel", null)
//   }

//   return results.slice(0, 18)
// }

// async function geocodeOne(query: string) {
//   try {
//     const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1&addressdetails=0`
//     const r = await fetch(url, {
//       headers: {
//         "Accept-Language": "en",
//         "User-Agent": "AI-Travel-Agent/1.0 (travel planner)"
//       }
//     })
//     const d = await r.json()
//     if (d && d[0]) {
//       return { lat: parseFloat(d[0].lat), lng: parseFloat(d[0].lon), address: d[0].display_name }
//     }
//   } catch (e) {}
//   return null
// }

// function tripTitleFromText(text: string) {
//   const m = text.match(/✈️\s*([A-Za-z ]+)\s*→\s*([A-Za-z ]+)/) || text.match(/from\s+([A-Za-z ]+)\s+to\s+([A-Za-z ]+)/i)
//   if (m) return `${m[1].trim()}-to-${m[2].trim()}`.replace(/\s+/g, "-")
//   return "trip-plan"
// }

// function detectResultSections(text: string) {
//   const t = text
//   const hasFlights =
//     /🛫|🛬/.test(t) ||
//     /\b(?:departure|return|outbound|inbound)\s+flights?\b/i.test(t) ||
//     /your\s+flights?\b/i.test(t) ||
//     /flight\s+(?:no|number|#|details)/i.test(t) ||
//     /\b(?:indigo|air\s*india|spicejet|go\s*first|akasa|vistara|emirates|etihad|lufthansa|british\s*airways|singapore\s*airlines?)\b/i.test(t)

//   const hasHotels =
//     /🏨/.test(t) ||
//     /\bhotel[s]?\b/i.test(t) ||
//     /\bresort[s]?\b/i.test(t) ||
//     /per\s*night/i.test(t) ||
//     /₹[\d,]+\s*\/\s*(?:night|nite)/i.test(t) ||
//     /💚|🌟|👑/.test(t) ||
//     /top\s*pick/i.test(t) ||
//     /\bcheck.?in\b|\bcheck.?out\b/i.test(t)

//   const hasItinerary =
//     /day.by.day/i.test(t) ||
//     /\bday\s*[1-9]\b/i.test(t) ||
//     /##\s*(?:day|morning|afternoon|evening)/i.test(t) ||
//     /###\s*(?:day|morning|afternoon|evening)/i.test(t) ||
//     /\*\*(?:day\s*[1-9]|morning|afternoon|evening)\b/i.test(t) ||
//     /itinerary/i.test(t) ||
//     /travel\s+tips?/i.test(t) ||
//     /what\s+to\s+pack/i.test(t) ||
//     /weather\s*&\s*what/i.test(t) ||
//     /estimated\s+(?:cost|budget|expense)/i.test(t) ||
//     /total\s+estimated/i.test(t) ||
//     /\bsightseeing\b/i.test(t) ||
//     /\bday\s+\d+.*\bday\s+\d+/is.test(t)

//   return { hasFlights, hasHotels, hasItinerary }
// }

// function isExportableResult(text: string) {
//   const t = text.trim()
//   if (t.length < 80) return false
//   const { hasFlights, hasHotels, hasItinerary } = detectResultSections(t)
//   return hasFlights || hasHotels || hasItinerary
// }

// function resultTypeLabel(text: string) {
//   const { hasFlights, hasHotels, hasItinerary } = detectResultSections(text)
//   const p = []
//   if (hasItinerary) p.push("Itinerary")
//   if (hasFlights) p.push("Flights")
//   if (hasHotels) p.push("Hotels")
//   return p.length ? p.join(" + ") : "Result"
// }

// function downloadBlob(content: string, filename: string, mime: string) {
//   const blob = new Blob([content], { type: mime })
//   const url = URL.createObjectURL(blob)
//   const a = document.createElement("a")
//   a.href = url
//   a.download = filename
//   document.body.appendChild(a)
//   a.click()
//   document.body.removeChild(a)
//   URL.revokeObjectURL(url)
// }

// const exportAsMarkdown = (text: string) => {
//   downloadBlob(text, `${tripTitleFromText(text)}.md`, "text/markdown")
// }

// const exportAsText = (text: string) => {
//   const plain = text
//     .replace(/^#{1,6}\s*/gm, "")
//     .replace(/\*\*(.*?)\*\*/g, "$1")
//     .replace(/\*(.*?)\*/g, "$1")
//     .replace(/`/g, "")
//     .replace(/^\s*[-—]{3,}\s*$/gm, "")
//   downloadBlob(plain, `${tripTitleFromText(text)}.txt`, "text/plain")
// }

// const exportAsPDF = (text: string) => {
//   const jspdf = (window as any).jspdf
//   if (!jspdf) {
//     alert("jsPDF library is not loaded. Please ensure index.html includes the script.")
//     return
//   }
//   const { jsPDF } = jspdf.umd ? jspdf.umd : jspdf
//   const doc = new jsPDF({ unit: "pt", format: "a4" })
//   const pw = doc.internal.pageSize.getWidth()
//   const margin = 40
//   const mw = pw - margin * 2
//   let y = 50

//   doc.setFont("helvetica", "bold")
//   doc.setFontSize(16)
//   doc.setTextColor(29, 78, 216)
//   doc.text("AI Travel Agent — Trip Plan", margin, y)
//   y += 26

//   doc.setDrawColor(220, 226, 235)
//   doc.line(margin, y, pw - margin, y)
//   y += 18

//   for (let raw of text.split("\n")) {
//     let line = raw.trim()
//     if (!line) {
//       y += 6
//       continue
//     }
//     let isH1 = false, isH2 = false, isH3 = false, isBullet = false
//     if (/^#\s+/.test(line)) {
//       line = line.replace(/^#\s+/, "")
//       isH1 = true
//     } else if (/^##\s+/.test(line)) {
//       line = line.replace(/^##\s+/, "")
//       isH2 = true
//     } else if (/^###\s+/.test(line)) {
//       line = line.replace(/^###\s+/, "")
//       isH3 = true
//     } else if (/^[-•]\s+/.test(line)) {
//       line = line.replace(/^[-•]\s+/, "")
//       isBullet = true
//     }
//     line = line.replace(/\*\*(.*?)\*\*/g, "$1").replace(/\*(.*?)\*/g, "$1").replace(/`/g, "")
//     if (/^[-|]+$/.test(line)) continue
//     line = line.replace(/^\|/, "").replace(/\|$/, "").replace(/\|/g, " · ")

//     if (isH1) {
//       doc.setFont("helvetica", "bold")
//       doc.setFontSize(15)
//       doc.setTextColor(29, 78, 216)
//       y += 8
//     } else if (isH2) {
//       doc.setFont("helvetica", "bold")
//       doc.setFontSize(13)
//       doc.setTextColor(30, 64, 175)
//       y += 6
//     } else if (isH3) {
//       doc.setFont("helvetica", "bold")
//       doc.setFontSize(12)
//       doc.setTextColor(30, 41, 59)
//       y += 4
//     } else {
//       doc.setFont("helvetica", "normal")
//       doc.setFontSize(10.5)
//       doc.setTextColor(30, 41, 59)
//     }

//     const wrapped = doc.splitTextToSize((isBullet ? "•  " : "") + line, mw)
//     for (const wl of wrapped) {
//       if (y > doc.internal.pageSize.getHeight() - 50) {
//         doc.addPage()
//         y = 50
//       }
//       doc.text(wl, margin, y)
//       y += isH1 ? 20 : isH2 ? 18 : isH3 ? 16 : 15
//     }
//     if (isH1 || isH2) y += 2
//   }
//   doc.save(`${tripTitleFromText(text)}.pdf`)
// }

// // ── REACT COMPONENT ──
// export default function App() {
//   // Session States
//   const [user, setUser] = useState<User | null>(null)
//   const [chats, setChats] = useState<ChatSession[]>([])
//   const [activeChatId, setActiveChatId] = useState<string | null>(null)
//   const [messages, setMessages] = useState<Message[]>([])

//   // Auth Inputs
//   const [usernameInput, setUsernameInput] = useState('')
//   const [passwordInput, setPasswordInput] = useState('')
//   const [authStatusMsg, setAuthStatusMsg] = useState('')

//   // Chat Input
//   const [inputValue, setInputValue] = useState('')
//   const [isSending, setIsSending] = useState(false)

//   // Map States
//   const [mapReady, setMapReady] = useState(false)
//   const [placeListData, setPlaceListData] = useState<Place[]>([])
//   const [mapStatus, setMapStatus] = useState({ text: '', className: '' })

//   // Refs
//   const mapContainerRef = useRef<HTMLDivElement>(null)
//   const mapRef = useRef<any>(null)
//   const markersRef = useRef<Record<number, any>>({})
//   const messagesEndRef = useRef<HTMLDivElement>(null)
//   const chatInputRef = useRef<HTMLTextAreaElement>(null)
//   const pinIdCounterRef = useRef<number>(0)

//   // 1. Initialise Map
//   useEffect(() => {
//     if (!mapContainerRef.current) return
//     const L = (window as any).L
//     if (!L) return

//     const mapInstance = L.map(mapContainerRef.current, { 
//       zoomControl: true, 
//       attributionControl: true 
//     }).setView([20.5937, 78.9629], 4)

//     L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
//       maxZoom: 19,
//       attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
//     }).addTo(mapInstance)

//     mapRef.current = mapInstance
//     setMapReady(true)

//     // Trigger invalidateSize after paint
//     requestAnimationFrame(() => {
//       mapInstance.invalidateSize()
//     })

//     return () => {
//       if (mapRef.current) {
//         mapRef.current.remove()
//         mapRef.current = null
//       }
//       setMapReady(false)
//     }
//   }, [])

//   // 2. Synchronise Markers on PlaceListData update
//   useEffect(() => {
//     if (!mapRef.current || !mapReady) return
//     const L = (window as any).L
//     if (!L) return

//     // Clear previous markers
//     Object.values(markersRef.current).forEach((m: any) => {
//       if (mapRef.current) mapRef.current.removeLayer(m)
//     })
//     markersRef.current = {}

//     // Add new markers
//     placeListData.forEach((p) => {
//       if (p.status === 'found' && p.lat != null && p.lng != null) {
//         const icon = L.divIcon ? L.divIcon({
//           html: `<svg xmlns="http://www.w3.org/2000/svg" width="34" height="46" viewBox="0 0 34 46">
//             <filter id="sh"><feDropShadow dx="0" dy="1" stdDeviation="1" flood-opacity="0.25"/></filter>
//             <path d="M17 1C8.7 1 2 7.7 2 16c0 11.8 15 28 15 28S32 27.8 32 16C32 7.7 25.3 1 17 1z"
//               fill="${TYPE_COLOR[p.type] || TYPE_COLOR.other}" stroke="#fff" stroke-width="2" filter="url(#sh)"/>
//             <circle cx="17" cy="16" r="8" fill="rgba(255,255,255,0.22)"/>
//             <text x="17" y="21" text-anchor="middle" font-size="11">${TYPE_EMOJI[p.type] || "📍"}</text>
//             ${p.day ? `<text x="16" y="38" text-anchor="middle" font-size="8" font-family="sans-serif" fill="${TYPE_COLOR[p.type] || TYPE_COLOR.other}" font-weight="700">D${p.day}</text>` : ""}
//           </svg>`,
//           className: "",
//           iconSize: [34, 46],
//           iconAnchor: [17, 46],
//           popupAnchor: [0, -48]
//         }) : null

//         const mk = L.marker([p.lat, p.lng], { icon }).addTo(mapRef.current)
//         const dayStr = p.day ? `<div class="pop-day">Day ${p.day}</div>` : ""
//         const addrStr = p.address ? `<div class="pop-addr">${p.address.split(",").slice(0, 3).join(", ")}</div>` : ""
        
//         mk.bindPopup(`
//           <span class="pop-type">${TYPE_EMOJI[p.type] || "📍"} ${p.type}</span>
//           <strong>${p.name}</strong>
//           ${dayStr}${addrStr}
//         `)

//         markersRef.current[p._id] = mk
//       }
//     })

//     // Fit markers inside viewport
//     const mks = Object.values(markersRef.current)
//     if (mks.length > 0) {
//       const b = L.latLngBounds(mks.map((m: any) => m.getLatLng()))
//       mapRef.current.fitBounds(b, { padding: [36, 36], maxZoom: 14 })
//     }
//   }, [placeListData, mapReady])

//   // 3. Scroll to Chat Bottom
//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
//   }, [messages])

//   // ── CORE LOGIC ──

//   const clearMap = () => {
//     setPlaceListData([])
//     setMapStatus({ text: '', className: '' })
//   }

//   const resetChat = () => {
//     setMessages([])
//     setActiveChatId(null)
//     clearMap()
//   }

//   const geocodeQueue = async (places: Array<{ name: string; type: string; day: number | null; geocodeQuery: string }>) => {
//     if (!places.length) return

//     setMapStatus({ text: `⟳ Locating ${places.length} place${places.length > 1 ? 's' : ''}…`, className: 'loading' })

//     const startIdx = pinIdCounterRef.current
//     const newPlaces = places.map((p, idx) => ({
//       _id: startIdx + idx + 1,
//       name: p.name,
//       type: p.type,
//       day: p.day,
//       status: 'pending' as const
//     }))
//     pinIdCounterRef.current += places.length

//     setPlaceListData((prev) => [...prev, ...newPlaces])

//     let found = 0
//     for (let i = 0; i < places.length; i++) {
//       const p = places[i]
//       const targetId = newPlaces[i]._id
//       const geo = await geocodeOne(p.geocodeQuery)

//       setPlaceListData((prev) =>
//         prev.map((item) => {
//           if (item._id === targetId) {
//             if (geo) {
//               found++
//               return {
//                 ...item,
//                 lat: geo.lat,
//                 lng: geo.lng,
//                 address: geo.address,
//                 status: 'found' as const
//               }
//             } else {
//               return {
//                 ...item,
//                 status: 'missing' as const
//               }
//             }
//           }
//           return item
//         })
//       )
//       if (i < places.length - 1) {
//         await new Promise((r) => setTimeout(r, 1070))
//       }
//     }

//     setMapStatus({
//       text: found > 0 ? `✅ Map updated with new locations.` : `⚠️ Could not locate places. Try a more specific query.`,
//       className: found > 0 ? 'done' : 'warn'
//     })
//   }

//   const updateMapFromResponse = async (rawFull: string, userText: string) => {
//     if (!mapRef.current || !mapReady) return

//     // Priority 1: Locations JSON comment
//     const jsonPlaces = tryExtractLocationsJSON(rawFull)
//     if (jsonPlaces && jsonPlaces.length) {
//       clearMap()
//       const mapped = jsonPlaces.map((p: any, idx: number) => {
//         const id = pinIdCounterRef.current + idx + 1
//         return {
//           _id: id,
//           name: p.name,
//           type: p.type || guessType(p.name),
//           day: p.day || null,
//           lat: p.lat,
//           lng: p.lng,
//           address: p.address,
//           status: 'found' as const
//         }
//       })
//       pinIdCounterRef.current += jsonPlaces.length
//       setPlaceListData(mapped)
//       setMapStatus({ text: `✅ ${mapped.length} locations mapped.`, className: 'done' })
//       return
//     }

//     // Priority 2: Extract from markdown text
//     const destHint = guessDestination(userText || rawFull)
//     const places = extractPlacesFromMarkdown(rawFull, destHint)

//     if (!places.length) {
//       setMapStatus({ text: "ℹ️ No specific places detected.", className: "warn" })
//       return
//     }

//     await geocodeQueue(places)
//   }

//   const fetchChats = async (userId: string) => {
//     try {
//       const r = await fetch(`http://localhost:8000/chat/users/${userId}/chats`)
//       if (r.ok) {
//         const data = await r.json()
//         setChats(data)
//       }
//     } catch (e) {}
//   }

//   const openChat = async (id: string) => {
//     setActiveChatId(id)
//     clearMap()
//     setMessages([])
//     try {
//       const r = await fetch(`http://localhost:8000/chat/history/${id}`)
//       if (r.ok) {
//         const msgs = await r.json()
//         const mapped = msgs.map((m: any) => ({
//           id: String(m.id),
//           role: m.role as 'user' | 'assistant' | 'system',
//           text: m.message
//         }))
//         setMessages(mapped)

//         // Process assistant history items to plot markers
//         let lastUser = ""
//         for (const m of msgs) {
//           if (m.role === "assistant") {
//             await updateMapFromResponse(m.message, lastUser)
//           } else {
//             lastUser = m.message
//           }
//         }
//       }
//     } catch (e) {}
//   }

//   // Auth Operations
//   const handleLogin = async () => {
//     if (!usernameInput.trim() || !passwordInput.trim()) {
//       setAuthStatusMsg("Enter username and password")
//       return
//     }
//     try {
//       const r = await fetch(`http://localhost:8000/chat/login?username=${encodeURIComponent(usernameInput)}&password=${encodeURIComponent(passwordInput)}`, {
//         method: "POST"
//       })
//       const d = await r.json()
//       if (!r.ok) {
//         setAuthStatusMsg("❌ " + (d.detail || "Failed"))
//         return
//       }
//       setUser({ user_id: d.user_id, username: d.username })
//       setAuthStatusMsg(`👤 ${d.username}`)
//       fetchChats(d.user_id)
//     } catch (e: any) {
//       setAuthStatusMsg("❌ " + e.message)
//     }
//   }

//   const handleRegister = async () => {
//     if (!usernameInput.trim() || !passwordInput.trim()) {
//       setAuthStatusMsg("Enter username and password")
//       return
//     }
//     try {
//       const r = await fetch(`http://localhost:8000/chat/register?username=${encodeURIComponent(usernameInput)}&password=${encodeURIComponent(passwordInput)}`, {
//         method: "POST"
//       })
//       const d = await r.json()
//       if (!r.ok) {
//         setAuthStatusMsg("❌ " + (d.detail || "Failed"))
//         return
//       }
//       setUser({ user_id: d.user_id, username: d.username })
//       setAuthStatusMsg(`👤 ${d.username}`)
//       fetchChats(d.user_id)
//     } catch (e: any) {
//       setAuthStatusMsg("❌ " + e.message)
//     }
//   }

//   const handleLogout = () => {
//     setUser(null)
//     setActiveChatId(null)
//     setChats([])
//     setMessages([])
//     setPlaceListData([])
//     setAuthStatusMsg("")
//     setUsernameInput("")
//     setPasswordInput("")
//     clearMap()
//   }

//   // Send Message
//   const handleSend = async () => {
//     if (!user) {
//       setMessages((prev) => [
//         ...prev,
//         { id: `sys-${Date.now()}`, role: 'system', text: '⚠️ Please login first.' }
//       ])
//       return
//     }
//     const text = inputValue.trim()
//     if (!text) return

//     setInputValue('')
//     if (chatInputRef.current) {
//       chatInputRef.current.style.height = 'auto'
//     }
//     setIsSending(true)

//     // User Message
//     setMessages((prev) => [
//       ...prev,
//       { id: `u-${Date.now()}`, role: 'user', text }
//     ])

//     const params = new URLSearchParams({ message: text, user_id: user.user_id })
//     if (activeChatId) params.append("chat_id", activeChatId)

//     try {
//       const res = await fetch(`http://localhost:8000/chat/?${params.toString()}`, {
//         method: "POST"
//       })
//       if (!res.ok) {
//         setMessages((prev) => [
//           ...prev,
//           { id: `sys-${Date.now()}`, role: 'system', text: `❌ Server error ${res.status}` }
//         ])
//         setIsSending(false)
//         return
//       }

//       const reader = res.body?.getReader()
//       const dec = new TextDecoder()
//       if (!reader) {
//         setIsSending(false)
//         return
//       }

//       let full = ""
//       const streamId = `a-stream-${Date.now()}`

//       // Create streaming placeholder
//       setMessages((prev) => [
//         ...prev,
//         { id: streamId, role: 'assistant', text: '', isStreaming: true }
//       ])

//       while (true) {
//         const { done, value } = await reader.read()
//         if (done) break
//         full += dec.decode(value, { stream: true })
//         const cm = full.match(/<!--CHAT_ID:([a-f0-9-]+)-->/)
//         if (cm) {
//           setActiveChatId(cm[1])
//         }

//         setMessages((prev) =>
//           prev.map((msg) => {
//             if (msg.id === streamId) {
//               return {
//                 ...msg,
//                 text: cleanForDisplay(full)
//               }
//             }
//             return msg
//           })
//         )
//       }

//       // Finish streaming
//       setMessages((prev) =>
//         prev.map((msg) => {
//           if (msg.id === streamId) {
//             return {
//               ...msg,
//               text: cleanForDisplay(full),
//               isStreaming: false
//             }
//           }
//           return msg
//         })
//       )

//       await updateMapFromResponse(full, text)
//       fetchChats(user.user_id)
//     } catch (e) {
//       setMessages((prev) => [
//         ...prev,
//         { id: `sys-${Date.now()}`, role: 'system', text: '❌ Cannot reach server. Is it running on port 8000?' }
//       ])
//     } finally {
//       setIsSending(false)
//     }
//   }

//   const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault()
//       handleSend()
//     }
//   }

//   const handleInputResize = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
//     setInputValue(e.target.value)
//     e.target.style.height = 'auto'
//     e.target.style.height = Math.min(e.target.scrollHeight, 130) + 'px'
//   }

//   const fillPrompt = (val: string) => {
//     setInputValue(val)
//     chatInputRef.current?.focus()
//   }

//   const handlePlaceClick = (p: Place) => {
//     if (p.status === 'found' && mapRef.current) {
//       const marker = markersRef.current[p._id]
//       if (marker) {
//         mapRef.current.setView(marker.getLatLng(), 14, { animate: true })
//         marker.openPopup()
//       }
//     }
//   }

//   // Sorted place list
//   const sortedPlaces = [...placeListData].sort((a, b) => {
//     if (a.day && b.day) return a.day - b.day
//     if (a.day) return -1
//     if (b.day) return 1
//     return 0
//   })

//   return (
//     <div className="app-shell" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
//       {/* ── TOP HEADER ── */}
//       <header>
//         <span className="logo">✈️</span>
//         <h1>AI Travel Agent</h1>
//         {/* <span className="badge">agent</span> */}
//       </header>

//       <div className="layout">
//         {/* ── SIDEBAR ── */}
//         <aside>
//           <h2>Trips</h2>
//           <button id="new-btn" onClick={resetChat}>＋ New Trip</button>
//           <div className="chat-list">
//             {chats.map((c) => (
//               <button
//                 key={c.chat_id}
//                 className={`c-item ${c.chat_id === activeChatId ? 'active' : ''}`}
//                 onClick={() => openChat(c.chat_id)}
//               >
//                 {c.title || 'Trip'}
//               </button>
//             ))}
//           </div>
//         </aside>

//         {/* ── MAIN CHAT AREA ── */}
//         <div className="main">
//           {/* Auth Bar */}
//           <div id="auth-bar">
//             {!user ? (
//               <>
//                 <input
//                   type="text"
//                   placeholder="Username"
//                   value={usernameInput}
//                   onChange={(e) => setUsernameInput(e.target.value)}
//                 />
//                 <input
//                   type="password"
//                   placeholder="Password"
//                   value={passwordInput}
//                   onChange={(e) => setPasswordInput(e.target.value)}
//                 />
//                 <button className="ab" id="login-btn" onClick={handleLogin}>Login</button>
//                 <button className="ab" id="reg-btn" onClick={handleRegister}>Register</button>
//               </>
//             ) : null}
//             <span id="auth-status">{authStatusMsg}</span>
//             {user ? (
//               <button id="logout-btn" onClick={handleLogout}>Logout</button>
//             ) : null}
//           </div>

//           {/* Messages List */}
//           <div id="messages">
//             {messages.length === 0 ? (
//               <div id="empty">
//                 <div className="ei">🌍</div>
//                 <h2>Where to next?</h2>
//                 <p>Tell me where you want to go — give me all details at once or I'll guide you step by step.</p>
//                 <div className="chips">
//                   <div className="chip" onClick={() => fillPrompt('Plan a trip from Delhi to Goa on 15 Jun returning 22 Jun')}>✈️ Delhi → Goa</div>
//                   <div className="chip" onClick={() => fillPrompt('I want to fly from Mumbai to Bangkok on 10 Jul for 7 days')}>🌏 Mumbai → Bangkok</div>
//                   <div className="chip" onClick={() => fillPrompt('Trip from Bangalore to Manali')}>🏔️ Bangalore → Manali</div>
//                 </div>
//               </div>
//             ) : (
//               messages.map((m) => {
//                 if (m.role === 'system') {
//                   return (
//                     <div key={m.id} className="row system">
//                       <div className="bubble system">{m.text}</div>
//                     </div>
//                   )
//                 }

//                 const markedParser = (window as any).marked
//                 const textHtml = markedParser ? markedParser.parse(m.text) : m.text

//                 return (
//                   <div key={m.id} className={`row ${m.role}`}>
//                     <div className="avatar">
//                       {m.role === 'user' ? '👤' : '🤖'}
//                     </div>
//                     <div className="msg-col">
//                       {m.role === 'user' ? (
//                         <div className="bubble user">{m.text}</div>
//                       ) : (
//                         <>
//                           <div 
//                             className={`bubble assistant ${m.isStreaming ? 'cursor' : ''}`}
//                             dangerouslySetInnerHTML={{ __html: textHtml }}
//                           />
//                           {!m.isStreaming && isExportableResult(m.text) ? (
//                             <ExportBar text={m.text} />
//                           ) : null}
//                         </>
//                       )}
//                     </div>
//                   </div>
//                 )
//               })
//             )}

//             {isSending && messages[messages.length - 1]?.role !== 'assistant' ? (
//               <div className="row assistant" id="typing-row">
//                 <div className="avatar">🤖</div>
//                 <div className="typing">
//                   <span></span><span></span><span></span>
//                 </div>
//               </div>
//             ) : null}

//             <div ref={messagesEndRef} />
//           </div>

//           {/* Input Wrapping Row */}
//           <div id="input-wrap">
//             <textarea
//               ref={chatInputRef}
//               id="msg"
//               rows={1}
//               placeholder="e.g. Plan a trip from Delhi to Goa on 15 Jun returning 22 Jun..."
//               value={inputValue}
//               onChange={handleInputResize}
//               onKeyDown={handleKeyDown}
//               disabled={isSending}
//             />
//             <button id="send" onClick={handleSend} disabled={isSending || !inputValue.trim()}>
//               {isSending ? 'Sending…' : 'Send ➤'}
//             </button>
//           </div>
//         </div>

//         {/* ── MAP PANEL ── */}
//         <div id="map-panel">
//           <div id="map-panel-header">
//             <span className="mp-title">📍 Trip Map</span>
//             {placeListData.length > 0 ? (
//               <span id="mp-count">
//                 {placeListData.filter(p => p.status === 'found').length}/{placeListData.length} pinned
//               </span>
//             ) : null}
//           </div>

//           <div id="map-legend">
//             <span className="legend-item"><span className="legend-dot" style={{ background: '#1d4ed8' }}></span>Hotel</span>
//             <span className="legend-item"><span className="legend-dot" style={{ background: '#059669' }}></span>Attraction</span>
//             <span className="legend-item"><span className="legend-dot" style={{ background: '#d97706' }}></span>Restaurant</span>
//             <span className="legend-item"><span className="legend-dot" style={{ background: '#7c3aed' }}></span>Transport</span>
//             <span className="legend-item"><span className="legend-dot" style={{ background: '#64748b' }}></span>Other</span>
//           </div>

//           <div 
//             id="map-status" 
//             className={mapStatus.className}
//             dangerouslySetInnerHTML={{ __html: mapStatus.text }}
//           />

//           <div id="map-wrap">
//             <div ref={mapContainerRef} id="map" />
//             {placeListData.length === 0 ? (
//               <div id="map-empty">
//                 <div className="me-icon">🗺️</div>
//                 <p>Hotels and itinerary places will be pinned here automatically after the AI responds.</p>
//               </div>
//             ) : null}
//             <button id="map-clear-btn" onClick={clearMap} title="Clear all pins">✕ Clear</button>
//           </div>

//           <div id="place-list">
//             {sortedPlaces.map((p) => {
//               const iconEmoji = p.status === 'pending' ? '⏳' : p.status === 'missing' ? '❓' : (TYPE_EMOJI[p.type] || '📍')
//               return (
//                 <div
//                   key={p._id}
//                   className={`place-row ${p.status === 'pending' ? 'pending' : p.status === 'missing' ? 'missing' : ''}`}
//                   onClick={() => handlePlaceClick(p)}
//                 >
//                   <span className="picon">{p.status === 'found' ? (TYPE_EMOJI[p.type] || '📍') : iconEmoji}</span>
//                   <span className="pname">{p.name}</span>
//                   {p.day ? <span className="pday">Day {p.day}</span> : null}
//                   <span className="ptype">{p.type}</span>
//                   {p.status !== 'found' ? <span className="pstatus">{iconEmoji}</span> : null}
//                 </div>
//               )
//             })}
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }

// // ── SUB-COMPONENT: EXPORT BAR ──
// function ExportBar({ text }: { text: string }) {
//   const [copied, setCopied] = useState(false)

//   const handleCopy = async () => {
//     try {
//       await navigator.clipboard.writeText(text)
//       setCopied(true)
//       setTimeout(() => setCopied(false), 1600)
//     } catch (e) {
//       alert("Could not copy — please select manually.")
//     }
//   }

//   const label = resultTypeLabel(text)

//   return (
//     <div className="export-bar">
//       <span style={{
//         fontSize: '11px',
//         color: '#94a3b8',
//         alignSelf: 'center',
//         marginRight: '2px',
//         fontWeight: 600,
//         textTransform: 'uppercase',
//         letterSpacing: '.03em'
//       }}>
//         Export {label}:
//       </span>
//       <button className="export-btn" onClick={() => exportAsPDF(text)}>
//         <span className="ico">📄</span> PDF
//       </button>
//       <button className="export-btn" onClick={() => exportAsMarkdown(text)}>
//         <span className="ico">📝</span> Markdown
//       </button>
//       <button className="export-btn" onClick={() => exportAsText(text)}>
//         <span className="ico">🗒️</span> Text
//       </button>
//       <button className={`export-btn ${copied ? 'copied' : ''}`} onClick={handleCopy}>
//         <span className="ico">{copied ? '✅' : '📋'}</span> {copied ? 'Copied!' : 'Copy'}
//       </button>
//     </div>
//   )
// }
import React, { useState, useEffect, useRef } from 'react'

// Icon and color configuration for map markers
const TYPE_EMOJI: Record<string, string> = { 
  hotel: "🏨", 
  attraction: "🏛️", 
  restaurant: "🍽️", 
  transport: "✈️", 
  airport: "✈️", 
  other: "📍" 
}

const TYPE_COLOR: Record<string, string> = { 
  hotel: "#1d4ed8", 
  attraction: "#059669", 
  restaurant: "#d97706", 
  transport: "#7c3aed", 
  airport: "#7c3aed", 
  other: "#64748b" 
}

// Interfaces
interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  text: string
  isStreaming?: boolean
}

interface ChatSession {
  chat_id: string
  title: string
  created_at: string
}

interface Place {
  _id: number
  name: string
  type: string
  day: number | null
  status: 'found' | 'pending' | 'missing'
  lat?: number
  lng?: number
  address?: string
}

interface User {
  user_id: string
  username: string
}

// ── UTILITY FUNCTIONS ──
function cleanForDisplay(raw: string) {
  return raw
    .replace(/\n*<!--LOCATIONS_JSON:[\s\S]*?-->/g, "")
    .replace(/\n*<!--CHAT_ID:[^>]+-->/g, "")
    .trimEnd()
}

function tryExtractLocationsJSON(raw: string) {
  // Defensive: take the LAST <!--LOCATIONS_JSON:...--> comment in the text,
  // not the first. The backend now emits exactly one combined comment per
  // turn (after collecting locations across all tool calls run in that
  // turn), but older saved history rows — or any future regression where
  // multiple comments end up concatenated — would otherwise silently lose
  // everything except whatever the first tool call found. Matching the
  // last one is always at least as correct, and self-heals if a strayed.
  const matches = [...raw.matchAll(/<!--LOCATIONS_JSON:(\[[\s\S]*?\])-->/g)]
  if (!matches.length) return null
  const last = matches[matches.length - 1]
  try {
    return JSON.parse(last[1])
  } catch (e) {
    return null
  }
}

function guessType(name: string) {
  const n = name.toLowerCase()
  if (/hotel|resort|inn|villa|lodge|suites|oyo|hyatt|marriott|hilton|taj|leela|radisson|novotel|oberoi|lemon tree|itc |sheraton|westin|four seasons|ritz|intercontinental/.test(n)) return "hotel"
  if (/airport|airbase|aerodrome/.test(n)) return "airport"
  if (/station|terminal|port|bus stand/.test(n)) return "transport"
  if (/restaurant|cafe|café|diner|bistro|bar |pub |eatery|dhaba|food/.test(n)) return "restaurant"
  if (/beach|fort|temple|museum|palace|market|falls|lake|park|garden|monument|gate|cave|ruins|viewpoint|mahal|gurdwara|church|mosque/.test(n)) return "attraction"
  return "other"
}

function looksLikePlace(t: string) {
  if (!t || t.length < 3 || t.length > 80) return false
  if (/^\d+$/.test(t)) return false
  if (/[₹$€£]/.test(t.slice(0, 4))) return false
  if (/per night|per day|rating|stars?|\d+\s*night|checkout|check-in/i.test(t)) return false
  if (/^(Budget|Mid|Luxury|Deluxe|Standard|Premium|Morning|Afternoon|Evening|Night|Total|Price|Note|Day|Here)$/i.test(t.split(" ")[0])) return false
  return true
}

function guessDestination(userText: string) {
  const m = userText.match(/(?:to|in|at|visiting?|for|going to)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)/)
  return m ? m[1] : ""
}

function extractPlacesFromMarkdown(md: string, destHint: string) {
  const results: Array<{ name: string; type: string; day: number | null; geocodeQuery: string }> = []
  const seen = new Set<string>()

  function add(name: string, type?: string, day?: number | null) {
    name = name.trim().replace(/[.,;:]+$/, "").trim()
    if (name.length < 3 || name.length > 80) return
    const key = name.toLowerCase()
    if (seen.has(key)) return
    const SKIP = /^(morning|afternoon|evening|night|total|note|day|here|check|stay|book|enjoy|experience|budget|luxury|premium|standard|mid-range|deluxe|return|depart|price|cost|rate|the|and|or|for|with|from|to|via)/i
    if (SKIP.test(name)) return
    if (/^\d/.test(name)) return
    seen.add(key)

    const geocodeQuery = destHint && !name.toLowerCase().includes(destHint.toLowerCase())
      ? `${name}, ${destHint}`
      : name

    results.push({ name, type: type || guessType(name), day: day || null, geocodeQuery })
  }

  // PASS 1: Scan line by line to capture Day context
  let currentDay: number | null = null
  const lines = md.split("\n")

  for (const line of lines) {
    const dayMatch = line.match(/\bDay\s+(\d+)\b/i)
    if (dayMatch) currentDay = parseInt(dayMatch[1])

    const boldRe = /\*\*([A-Z][A-Za-z0-9&'.()\-,\/ ]{2,55}?)\*\*/g
    let m
    while ((m = boldRe.exec(line)) !== null) {
      const t = m[1].trim()
      if (looksLikePlace(t)) add(t, guessType(t), currentDay)
    }

    const hotelRe = /\b(Hotel|Resort|Hyatt|Marriott|Hilton|Taj|Leela|Radisson|Novotel|OYO|Lemon Tree|ITC|Oberoi|Trident|Vivanta|Ginger|Park|The (?:Leela|Taj|Park|Westin|Ritz))\s+([A-Z][A-Za-z0-9&'.()\-,\/ ]{1,45})/g
    while ((m = hotelRe.exec(line)) !== null) {
      const full = (m[1] + " " + m[2]).trim().replace(/[.,;]+$/, "")
      if (looksLikePlace(full)) add(full, "hotel", currentDay)
    }

    const placeRe = /\b([A-Z][A-Za-z ]{2,35}(?:Beach|Fort|Temple|Market|Palace|Museum|Park|Lake|Falls|Gate|Garden|Monument|Cafe|Airport|Station|Mahal|Gurdwara|Church|Mosque|Cave|Viewpoint|Hill|Peak|Island|Village))\b/g
    while ((m = placeRe.exec(line)) !== null) {
      if (looksLikePlace(m[1])) add(m[1].trim(), guessType(m[1]), currentDay)
    }

    const airportRe = /\b([A-Z][A-Za-z ]{3,40}(?:International\s+)?Airport)\b/g
    while ((m = airportRe.exec(line)) !== null) {
      add(m[1].trim(), "airport", null)
    }
  }

  // PASS 2: emoji-tagged hotels
  const emojiRe = /[🏨🏩]\s*([A-Z][A-Za-z0-9&'.()\- ]{3,55}?)(?:\s*[⭐★|]|\s*\d|\n|$)/g
  let m
  while ((m = emojiRe.exec(md)) !== null) {
    const t = m[1].trim()
    if (looksLikePlace(t)) add(t, "hotel", null)
  }

  return results.slice(0, 18)
}

async function geocodeOne(query: string) {
  try {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1&addressdetails=0`
    const r = await fetch(url, {
      headers: {
        "Accept-Language": "en",
        "User-Agent": "AI-Travel-Agent/1.0 (travel planner)"
      }
    })
    const d = await r.json()
    if (d && d[0]) {
      return { lat: parseFloat(d[0].lat), lng: parseFloat(d[0].lon), address: d[0].display_name }
    }
  } catch (e) {}
  return null
}

function tripTitleFromText(text: string) {
  const m = text.match(/✈️\s*([A-Za-z ]+)\s*→\s*([A-Za-z ]+)/) || text.match(/from\s+([A-Za-z ]+)\s+to\s+([A-Za-z ]+)/i)
  if (m) return `${m[1].trim()}-to-${m[2].trim()}`.replace(/\s+/g, "-")
  return "trip-plan"
}

function detectResultSections(text: string) {
  const t = text
  const hasFlights =
    /🛫|🛬/.test(t) ||
    /\b(?:departure|return|outbound|inbound)\s+flights?\b/i.test(t) ||
    /your\s+flights?\b/i.test(t) ||
    /flight\s+(?:no|number|#|details)/i.test(t) ||
    /\b(?:indigo|air\s*india|spicejet|go\s*first|akasa|vistara|emirates|etihad|lufthansa|british\s*airways|singapore\s*airlines?)\b/i.test(t)

  const hasHotels =
    /🏨/.test(t) ||
    /\bhotel[s]?\b/i.test(t) ||
    /\bresort[s]?\b/i.test(t) ||
    /per\s*night/i.test(t) ||
    /₹[\d,]+\s*\/\s*(?:night|nite)/i.test(t) ||
    /💚|🌟|👑/.test(t) ||
    /top\s*pick/i.test(t) ||
    /\bcheck.?in\b|\bcheck.?out\b/i.test(t)

  const hasItinerary =
    /day.by.day/i.test(t) ||
    /\bday\s*[1-9]\b/i.test(t) ||
    /##\s*(?:day|morning|afternoon|evening)/i.test(t) ||
    /###\s*(?:day|morning|afternoon|evening)/i.test(t) ||
    /\*\*(?:day\s*[1-9]|morning|afternoon|evening)\b/i.test(t) ||
    /itinerary/i.test(t) ||
    /travel\s+tips?/i.test(t) ||
    /what\s+to\s+pack/i.test(t) ||
    /weather\s*&\s*what/i.test(t) ||
    /estimated\s+(?:cost|budget|expense)/i.test(t) ||
    /total\s+estimated/i.test(t) ||
    /\bsightseeing\b/i.test(t) ||
    /\bday\s+\d+.*\bday\s+\d+/is.test(t)

  return { hasFlights, hasHotels, hasItinerary }
}

function isExportableResult(text: string) {
  const t = text.trim()
  if (t.length < 80) return false
  const { hasFlights, hasHotels, hasItinerary } = detectResultSections(t)
  return hasFlights || hasHotels || hasItinerary
}

function resultTypeLabel(text: string) {
  const { hasFlights, hasHotels, hasItinerary } = detectResultSections(text)
  const p = []
  if (hasItinerary) p.push("Itinerary")
  if (hasFlights) p.push("Flights")
  if (hasHotels) p.push("Hotels")
  return p.length ? p.join(" + ") : "Result"
}

function downloadBlob(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const exportAsMarkdown = (text: string) => {
  downloadBlob(text, `${tripTitleFromText(text)}.md`, "text/markdown")
}

const exportAsText = (text: string) => {
  const plain = text
    .replace(/^#{1,6}\s*/gm, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/`/g, "")
    .replace(/^\s*[-—]{3,}\s*$/gm, "")
  downloadBlob(plain, `${tripTitleFromText(text)}.txt`, "text/plain")
}

const exportAsPDF = (text: string) => {
  const jspdf = (window as any).jspdf
  if (!jspdf) {
    alert("jsPDF library is not loaded. Please ensure index.html includes the script.")
    return
  }
  const { jsPDF } = jspdf.umd ? jspdf.umd : jspdf
  const doc = new jsPDF({ unit: "pt", format: "a4" })
  const pw = doc.internal.pageSize.getWidth()
  const margin = 40
  const mw = pw - margin * 2
  let y = 50

  doc.setFont("helvetica", "bold")
  doc.setFontSize(16)
  doc.setTextColor(29, 78, 216)
  doc.text("AI Travel Agent — Trip Plan", margin, y)
  y += 26

  doc.setDrawColor(220, 226, 235)
  doc.line(margin, y, pw - margin, y)
  y += 18

  for (let raw of text.split("\n")) {
    let line = raw.trim()
    if (!line) {
      y += 6
      continue
    }
    let isH1 = false, isH2 = false, isH3 = false, isBullet = false
    if (/^#\s+/.test(line)) {
      line = line.replace(/^#\s+/, "")
      isH1 = true
    } else if (/^##\s+/.test(line)) {
      line = line.replace(/^##\s+/, "")
      isH2 = true
    } else if (/^###\s+/.test(line)) {
      line = line.replace(/^###\s+/, "")
      isH3 = true
    } else if (/^[-•]\s+/.test(line)) {
      line = line.replace(/^[-•]\s+/, "")
      isBullet = true
    }
    line = line.replace(/\*\*(.*?)\*\*/g, "$1").replace(/\*(.*?)\*/g, "$1").replace(/`/g, "")
    if (/^[-|]+$/.test(line)) continue
    line = line.replace(/^\|/, "").replace(/\|$/, "").replace(/\|/g, " · ")

    if (isH1) {
      doc.setFont("helvetica", "bold")
      doc.setFontSize(15)
      doc.setTextColor(29, 78, 216)
      y += 8
    } else if (isH2) {
      doc.setFont("helvetica", "bold")
      doc.setFontSize(13)
      doc.setTextColor(30, 64, 175)
      y += 6
    } else if (isH3) {
      doc.setFont("helvetica", "bold")
      doc.setFontSize(12)
      doc.setTextColor(30, 41, 59)
      y += 4
    } else {
      doc.setFont("helvetica", "normal")
      doc.setFontSize(10.5)
      doc.setTextColor(30, 41, 59)
    }

    const wrapped = doc.splitTextToSize((isBullet ? "•  " : "") + line, mw)
    for (const wl of wrapped) {
      if (y > doc.internal.pageSize.getHeight() - 50) {
        doc.addPage()
        y = 50
      }
      doc.text(wl, margin, y)
      y += isH1 ? 20 : isH2 ? 18 : isH3 ? 16 : 15
    }
    if (isH1 || isH2) y += 2
  }
  doc.save(`${tripTitleFromText(text)}.pdf`)
}

// ── REACT COMPONENT ──
export default function App() {
  // Session States
  const [user, setUser] = useState<User | null>(null)
  const [chats, setChats] = useState<ChatSession[]>([])
  const [activeChatId, setActiveChatId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])

  // Auth Inputs
  const [usernameInput, setUsernameInput] = useState('')
  const [passwordInput, setPasswordInput] = useState('')
  const [authStatusMsg, setAuthStatusMsg] = useState('')

  // Chat Input
  const [inputValue, setInputValue] = useState('')
  const [isSending, setIsSending] = useState(false)

  // Map States
  const [mapReady, setMapReady] = useState(false)
  const [placeListData, setPlaceListData] = useState<Place[]>([])
  const [mapStatus, setMapStatus] = useState({ text: '', className: '' })

  // Refs
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<any>(null)
  const markersRef = useRef<Record<number, any>>({})
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatInputRef = useRef<HTMLTextAreaElement>(null)
  const pinIdCounterRef = useRef<number>(0)

  // 1. Initialise Map
  useEffect(() => {
    if (!mapContainerRef.current) return
    const L = (window as any).L
    if (!L) return

    const mapInstance = L.map(mapContainerRef.current, { 
      zoomControl: true, 
      attributionControl: true 
    }).setView([20.5937, 78.9629], 4)

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mapInstance)

    mapRef.current = mapInstance
    setMapReady(true)

    // Trigger invalidateSize after paint
    requestAnimationFrame(() => {
      mapInstance.invalidateSize()
    })

    return () => {
      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
      }
      setMapReady(false)
    }
  }, [])

  // 2. Synchronise Markers on PlaceListData update
  useEffect(() => {
    if (!mapRef.current || !mapReady) return
    const L = (window as any).L
    if (!L) return

    // Clear previous markers
    Object.values(markersRef.current).forEach((m: any) => {
      if (mapRef.current) mapRef.current.removeLayer(m)
    })
    markersRef.current = {}

    // Add new markers
    placeListData.forEach((p) => {
      if (p.status === 'found' && p.lat != null && p.lng != null) {
        const icon = L.divIcon ? L.divIcon({
          html: `<svg xmlns="http://www.w3.org/2000/svg" width="34" height="46" viewBox="0 0 34 46">
            <filter id="sh"><feDropShadow dx="0" dy="1" stdDeviation="1" flood-opacity="0.25"/></filter>
            <path d="M17 1C8.7 1 2 7.7 2 16c0 11.8 15 28 15 28S32 27.8 32 16C32 7.7 25.3 1 17 1z"
              fill="${TYPE_COLOR[p.type] || TYPE_COLOR.other}" stroke="#fff" stroke-width="2" filter="url(#sh)"/>
            <circle cx="17" cy="16" r="8" fill="rgba(255,255,255,0.22)"/>
            <text x="17" y="21" text-anchor="middle" font-size="11">${TYPE_EMOJI[p.type] || "📍"}</text>
            ${p.day ? `<text x="16" y="38" text-anchor="middle" font-size="8" font-family="sans-serif" fill="${TYPE_COLOR[p.type] || TYPE_COLOR.other}" font-weight="700">D${p.day}</text>` : ""}
          </svg>`,
          className: "",
          iconSize: [34, 46],
          iconAnchor: [17, 46],
          popupAnchor: [0, -48]
        }) : null

        const mk = L.marker([p.lat, p.lng], { icon }).addTo(mapRef.current)
        const dayStr = p.day ? `<div class="pop-day">Day ${p.day}</div>` : ""
        const addrStr = p.address ? `<div class="pop-addr">${p.address.split(",").slice(0, 3).join(", ")}</div>` : ""
        
        mk.bindPopup(`
          <span class="pop-type">${TYPE_EMOJI[p.type] || "📍"} ${p.type}</span>
          <strong>${p.name}</strong>
          ${dayStr}${addrStr}
        `)

        markersRef.current[p._id] = mk
      }
    })

    // Fit markers inside viewport
    const mks = Object.values(markersRef.current)
    if (mks.length > 0) {
      const b = L.latLngBounds(mks.map((m: any) => m.getLatLng()))
      mapRef.current.fitBounds(b, { padding: [36, 36], maxZoom: 14 })
    }
  }, [placeListData, mapReady])

  // 3. Scroll to Chat Bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // ── CORE LOGIC ──

  const clearMap = () => {
    setPlaceListData([])
    setMapStatus({ text: '', className: '' })
  }

  const resetChat = () => {
    setMessages([])
    setActiveChatId(null)
    clearMap()
  }

  const geocodeQueue = async (places: Array<{ name: string; type: string; day: number | null; geocodeQuery: string }>) => {
    if (!places.length) return

    setMapStatus({ text: `⟳ Locating ${places.length} place${places.length > 1 ? 's' : ''}…`, className: 'loading' })

    const startIdx = pinIdCounterRef.current
    const newPlaces = places.map((p, idx) => ({
      _id: startIdx + idx + 1,
      name: p.name,
      type: p.type,
      day: p.day,
      status: 'pending' as const
    }))
    pinIdCounterRef.current += places.length

    setPlaceListData((prev) => [...prev, ...newPlaces])

    let found = 0
    for (let i = 0; i < places.length; i++) {
      const p = places[i]
      const targetId = newPlaces[i]._id
      const geo = await geocodeOne(p.geocodeQuery)

      setPlaceListData((prev) =>
        prev.map((item) => {
          if (item._id === targetId) {
            if (geo) {
              found++
              return {
                ...item,
                lat: geo.lat,
                lng: geo.lng,
                address: geo.address,
                status: 'found' as const
              }
            } else {
              return {
                ...item,
                status: 'missing' as const
              }
            }
          }
          return item
        })
      )
      if (i < places.length - 1) {
        await new Promise((r) => setTimeout(r, 1070))
      }
    }

    setMapStatus({
      text: found > 0 ? `✅ Map updated with new locations.` : `⚠️ Could not locate places. Try a more specific query.`,
      className: found > 0 ? 'done' : 'warn'
    })
  }

  const updateMapFromResponse = async (rawFull: string, userText: string) => {
    if (!mapRef.current || !mapReady) return

    // Priority 1: Locations JSON comment
    const jsonPlaces = tryExtractLocationsJSON(rawFull)
    if (jsonPlaces && jsonPlaces.length) {
      clearMap()
      const mapped = jsonPlaces.map((p: any, idx: number) => {
        const id = pinIdCounterRef.current + idx + 1
        return {
          _id: id,
          name: p.name,
          type: p.type || guessType(p.name),
          day: p.day || null,
          lat: p.lat,
          lng: p.lng,
          address: p.address,
          status: 'found' as const
        }
      })
      pinIdCounterRef.current += jsonPlaces.length
      setPlaceListData(mapped)
      setMapStatus({ text: `✅ ${mapped.length} locations mapped.`, className: 'done' })
      return
    }

    // Priority 2: Extract from markdown text
    const destHint = guessDestination(userText || rawFull)
    const places = extractPlacesFromMarkdown(rawFull, destHint)

    if (!places.length) {
      setMapStatus({ text: "ℹ️ No specific places detected.", className: "warn" })
      return
    }

    await geocodeQueue(places)
  }

  const fetchChats = async (userId: string) => {
    try {
      const r = await fetch(`http://localhost:8000/chat/users/${userId}/chats`)
      if (r.ok) {
        const data = await r.json()
        setChats(data)
      }
    } catch (e) {}
  }

  const openChat = async (id: string) => {
    setActiveChatId(id)
    clearMap()
    setMessages([])
    try {
      const r = await fetch(`http://localhost:8000/chat/history/${id}`)
      if (r.ok) {
        const msgs = await r.json()
        const mapped = msgs.map((m: any) => ({
          id: String(m.id),
          role: m.role as 'user' | 'assistant' | 'system',
          text: m.message
        }))
        setMessages(mapped)

        // Process assistant history items to plot markers
        let lastUser = ""
        for (const m of msgs) {
          if (m.role === "assistant") {
            await updateMapFromResponse(m.message, lastUser)
          } else {
            lastUser = m.message
          }
        }
      }
    } catch (e) {}
  }

  // Auth Operations
  const handleLogin = async () => {
    if (!usernameInput.trim() || !passwordInput.trim()) {
      setAuthStatusMsg("Enter username and password")
      return
    }
    try {
      const r = await fetch(`http://localhost:8000/chat/login?username=${encodeURIComponent(usernameInput)}&password=${encodeURIComponent(passwordInput)}`, {
        method: "POST"
      })
      const d = await r.json()
      if (!r.ok) {
        setAuthStatusMsg("❌ " + (d.detail || "Failed"))
        return
      }
      setUser({ user_id: d.user_id, username: d.username })
      setAuthStatusMsg(`👤 ${d.username}`)
      fetchChats(d.user_id)
    } catch (e: any) {
      setAuthStatusMsg("❌ " + e.message)
    }
  }

  const handleRegister = async () => {
    if (!usernameInput.trim() || !passwordInput.trim()) {
      setAuthStatusMsg("Enter username and password")
      return
    }
    try {
      const r = await fetch(`http://localhost:8000/chat/register?username=${encodeURIComponent(usernameInput)}&password=${encodeURIComponent(passwordInput)}`, {
        method: "POST"
      })
      const d = await r.json()
      if (!r.ok) {
        setAuthStatusMsg("❌ " + (d.detail || "Failed"))
        return
      }
      setUser({ user_id: d.user_id, username: d.username })
      setAuthStatusMsg(`👤 ${d.username}`)
      fetchChats(d.user_id)
    } catch (e: any) {
      setAuthStatusMsg("❌ " + e.message)
    }
  }

  const handleLogout = () => {
    setUser(null)
    setActiveChatId(null)
    setChats([])
    setMessages([])
    setPlaceListData([])
    setAuthStatusMsg("")
    setUsernameInput("")
    setPasswordInput("")
    clearMap()
  }

  // Send Message
  const handleSend = async () => {
    if (!user) {
      setMessages((prev) => [
        ...prev,
        { id: `sys-${Date.now()}`, role: 'system', text: '⚠️ Please login first.' }
      ])
      return
    }
    const text = inputValue.trim()
    if (!text) return

    setInputValue('')
    if (chatInputRef.current) {
      chatInputRef.current.style.height = 'auto'
    }
    setIsSending(true)

    // User Message
    setMessages((prev) => [
      ...prev,
      { id: `u-${Date.now()}`, role: 'user', text }
    ])

    const params = new URLSearchParams({ message: text, user_id: user.user_id })
    if (activeChatId) params.append("chat_id", activeChatId)

    try {
      const res = await fetch(`http://localhost:8000/chat/?${params.toString()}`, {
        method: "POST"
      })
      if (!res.ok) {
        setMessages((prev) => [
          ...prev,
          { id: `sys-${Date.now()}`, role: 'system', text: `❌ Server error ${res.status}` }
        ])
        setIsSending(false)
        return
      }

      const reader = res.body?.getReader()
      const dec = new TextDecoder()
      if (!reader) {
        setIsSending(false)
        return
      }

      let full = ""
      const streamId = `a-stream-${Date.now()}`

      // Create streaming placeholder
      setMessages((prev) => [
        ...prev,
        { id: streamId, role: 'assistant', text: '', isStreaming: true }
      ])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        full += dec.decode(value, { stream: true })
        const cm = full.match(/<!--CHAT_ID:([a-f0-9-]+)-->/)
        if (cm) {
          setActiveChatId(cm[1])
        }

        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id === streamId) {
              return {
                ...msg,
                text: cleanForDisplay(full)
              }
            }
            return msg
          })
        )
      }

      // Finish streaming
      setMessages((prev) =>
        prev.map((msg) => {
          if (msg.id === streamId) {
            return {
              ...msg,
              text: cleanForDisplay(full),
              isStreaming: false
            }
          }
          return msg
        })
      )

      await updateMapFromResponse(full, text)
      fetchChats(user.user_id)
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { id: `sys-${Date.now()}`, role: 'system', text: '❌ Cannot reach server. Is it running on port 8000?' }
      ])
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInputResize = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 130) + 'px'
  }

  const fillPrompt = (val: string) => {
    setInputValue(val)
    chatInputRef.current?.focus()
  }

  const handlePlaceClick = (p: Place) => {
    if (p.status === 'found' && mapRef.current) {
      const marker = markersRef.current[p._id]
      if (marker) {
        mapRef.current.setView(marker.getLatLng(), 14, { animate: true })
        marker.openPopup()
      }
    }
  }

  // Sorted place list
  const sortedPlaces = [...placeListData].sort((a, b) => {
    if (a.day && b.day) return a.day - b.day
    if (a.day) return -1
    if (b.day) return 1
    return 0
  })

  return (
    <div className="app-shell" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* ── TOP HEADER ── */}
      <header>
        <span className="logo">✈️</span>
        <h1>AI Travel Agent</h1>
        {/* <span className="badge">agent</span> */}
      </header>

      <div className="layout">
        {/* ── SIDEBAR ── */}
        <aside>
          <h2>Trips</h2>
          <button id="new-btn" onClick={resetChat}>＋ New Trip</button>
          <div className="chat-list">
            {chats.map((c) => (
              <button
                key={c.chat_id}
                className={`c-item ${c.chat_id === activeChatId ? 'active' : ''}`}
                onClick={() => openChat(c.chat_id)}
              >
                {c.title || 'Trip'}
              </button>
            ))}
          </div>
        </aside>

        {/* ── MAIN CHAT AREA ── */}
        <div className="main">
          {/* Auth Bar */}
          <div id="auth-bar">
            {!user ? (
              <>
                <input
                  type="text"
                  placeholder="Username"
                  value={usernameInput}
                  onChange={(e) => setUsernameInput(e.target.value)}
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                />
                <button className="ab" id="login-btn" onClick={handleLogin}>Login</button>
                <button className="ab" id="reg-btn" onClick={handleRegister}>Register</button>
              </>
            ) : null}
            <span id="auth-status">{authStatusMsg}</span>
            {user ? (
              <button id="logout-btn" onClick={handleLogout}>Logout</button>
            ) : null}
          </div>

          {/* Messages List */}
          <div id="messages">
            {messages.length === 0 ? (
              <div id="empty">
                <div className="ei">🌍</div>
                <h2>Where to next?</h2>
                <p>Tell me where you want to go — give me all details at once or I'll guide you step by step.</p>
                <div className="chips">
                  <div className="chip" onClick={() => fillPrompt('Plan a trip from Delhi to Goa on 15 Jun returning 22 Jun')}>✈️ Delhi → Goa</div>
                  <div className="chip" onClick={() => fillPrompt('I want to fly from Mumbai to Bangkok on 10 Jul for 7 days')}>🌏 Mumbai → Bangkok</div>
                  <div className="chip" onClick={() => fillPrompt('Trip from Bangalore to Manali')}>🏔️ Bangalore → Manali</div>
                </div>
              </div>
            ) : (
              messages.map((m) => {
                if (m.role === 'system') {
                  return (
                    <div key={m.id} className="row system">
                      <div className="bubble system">{m.text}</div>
                    </div>
                  )
                }

                const markedParser = (window as any).marked
                const textHtml = markedParser ? markedParser.parse(m.text) : m.text

                return (
                  <div key={m.id} className={`row ${m.role}`}>
                    <div className="avatar">
                      {m.role === 'user' ? '👤' : '🤖'}
                    </div>
                    <div className="msg-col">
                      {m.role === 'user' ? (
                        <div className="bubble user">{m.text}</div>
                      ) : (
                        <>
                          <div 
                            className={`bubble assistant ${m.isStreaming ? 'cursor' : ''}`}
                            dangerouslySetInnerHTML={{ __html: textHtml }}
                          />
                          {!m.isStreaming && isExportableResult(m.text) ? (
                            <ExportBar text={m.text} />
                          ) : null}
                        </>
                      )}
                    </div>
                  </div>
                )
              })
            )}

            {isSending && messages[messages.length - 1]?.role !== 'assistant' ? (
              <div className="row assistant" id="typing-row">
                <div className="avatar">🤖</div>
                <div className="typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            ) : null}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Wrapping Row */}
          <div id="input-wrap">
            <textarea
              ref={chatInputRef}
              id="msg"
              rows={1}
              placeholder="e.g. Plan a trip from Delhi to Goa on 15 Jun returning 22 Jun..."
              value={inputValue}
              onChange={handleInputResize}
              onKeyDown={handleKeyDown}
              disabled={isSending}
            />
            <button id="send" onClick={handleSend} disabled={isSending || !inputValue.trim()}>
              {isSending ? 'Sending…' : 'Send ➤'}
            </button>
          </div>
        </div>

        {/* ── MAP PANEL ── */}
        <div id="map-panel">
          <div id="map-panel-header">
            <span className="mp-title">📍 Trip Map</span>
            {placeListData.length > 0 ? (
              <span id="mp-count">
                {placeListData.filter(p => p.status === 'found').length}/{placeListData.length} pinned
              </span>
            ) : null}
          </div>

          <div id="map-legend">
            <span className="legend-item"><span className="legend-dot" style={{ background: '#1d4ed8' }}></span>Hotel</span>
            <span className="legend-item"><span className="legend-dot" style={{ background: '#059669' }}></span>Attraction</span>
            <span className="legend-item"><span className="legend-dot" style={{ background: '#d97706' }}></span>Restaurant</span>
            <span className="legend-item"><span className="legend-dot" style={{ background: '#7c3aed' }}></span>Transport</span>
            <span className="legend-item"><span className="legend-dot" style={{ background: '#64748b' }}></span>Other</span>
          </div>

          <div 
            id="map-status" 
            className={mapStatus.className}
            dangerouslySetInnerHTML={{ __html: mapStatus.text }}
          />

          <div id="map-wrap">
            <div ref={mapContainerRef} id="map" />
            {placeListData.length === 0 ? (
              <div id="map-empty">
                <div className="me-icon">🗺️</div>
                <p>Hotels and itinerary places will be pinned here automatically after the AI responds.</p>
              </div>
            ) : null}
            <button id="map-clear-btn" onClick={clearMap} title="Clear all pins">✕ Clear</button>
          </div>

          <div id="place-list">
            {sortedPlaces.map((p) => {
              const iconEmoji = p.status === 'pending' ? '⏳' : p.status === 'missing' ? '❓' : (TYPE_EMOJI[p.type] || '📍')
              return (
                <div
                  key={p._id}
                  className={`place-row ${p.status === 'pending' ? 'pending' : p.status === 'missing' ? 'missing' : ''}`}
                  onClick={() => handlePlaceClick(p)}
                >
                  <span className="picon">{p.status === 'found' ? (TYPE_EMOJI[p.type] || '📍') : iconEmoji}</span>
                  <span className="pname">{p.name}</span>
                  {p.day ? <span className="pday">Day {p.day}</span> : null}
                  <span className="ptype">{p.type}</span>
                  {p.status !== 'found' ? <span className="pstatus">{iconEmoji}</span> : null}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

// ── SUB-COMPONENT: EXPORT BAR ──
function ExportBar({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch (e) {
      alert("Could not copy — please select manually.")
    }
  }

  const label = resultTypeLabel(text)

  return (
    <div className="export-bar">
      <span style={{
        fontSize: '11px',
        color: '#94a3b8',
        alignSelf: 'center',
        marginRight: '2px',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '.03em'
      }}>
        Export {label}:
      </span>
      <button className="export-btn" onClick={() => exportAsPDF(text)}>
        <span className="ico">📄</span> PDF
      </button>
      <button className="export-btn" onClick={() => exportAsMarkdown(text)}>
        <span className="ico">📝</span> Markdown
      </button>
      <button className="export-btn" onClick={() => exportAsText(text)}>
        <span className="ico">🗒️</span> Text
      </button>
      <button className={`export-btn ${copied ? 'copied' : ''}`} onClick={handleCopy}>
        <span className="ico">{copied ? '✅' : '📋'}</span> {copied ? 'Copied!' : 'Copy'}
      </button>
    </div>
  )
}