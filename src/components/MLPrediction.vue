<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { apartmentApi } from '../services/api'
import type { ApartmentData, PredictionResult, PredictionMode } from '../types/apartment'

const props = defineProps<{
  mode: PredictionMode
}>()

const apartmentData = reactive<ApartmentData>({
  mode: 'poland',
  latitude: 52.2297, // Default: Warsaw coordinates
  longitude: 21.0122,
  city: 'bangalore', // Default: Bangalore for India
  bathrooms: 2, // Default number of bathrooms for India
  area: 50,
  rooms: 2,
  yearBuilt: 2010,

  // Set some defaults for optional features
  buildingMaterial: 'BRICK',
  ownership: 'FULL_OWNERSHIP',
  condition: 'READY_TO_USE',
  heatingType: 'URBAN',
  buildingType: 'BLOCK',
  windowsType: 'PLASTIC',

  // Boolean features - defaults
  hasBalcony: true,
  hasElevator: true,
  hasStove: true,
  hasOven: true,
})

const cities = ref<string[]>([])
const loadingCities = ref(false)

const prediction = ref<PredictionResult | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const mapContainer = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let marker: L.Marker | null = null

// Watch for mode changes
watch(() => props.mode, async (newMode) => {
  apartmentData.mode = newMode
  prediction.value = null
  error.value = null

  // Change default area based on mode
  if (newMode === 'india') {
    apartmentData.area = 1000 // India uses sq ft
    // Load cities if not already loaded
    if (cities.value.length === 0) {
      loadingCities.value = true
      try {
        cities.value = await apartmentApi.getCities()
      } catch (err) {
        console.error('Failed to load cities:', err)
      } finally {
        loadingCities.value = false
      }
    }
  } else {
    apartmentData.area = 50 // Poland uses sq m
  }
})

onMounted(async () => {
  // Load cities for India mode
  if (props.mode === 'india') {
    loadingCities.value = true
    try {
      cities.value = await apartmentApi.getCities()
    } catch (err) {
      console.error('Failed to load cities:', err)
    } finally {
      loadingCities.value = false
    }
  }

  // Initialize map only for Poland mode
  if (props.mode === 'poland' && mapContainer.value) {
    // Initialize map centered on Warsaw
    map = L.map(mapContainer.value).setView([apartmentData.latitude!, apartmentData.longitude!], 12)

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map)

    // Create custom icon for marker
    const customIcon = L.divIcon({
      html: '<div style="font-size: 2rem;">📍</div>',
      className: 'custom-marker',
      iconSize: [30, 30],
      iconAnchor: [15, 30],
    })

    // Add initial marker
    marker = L.marker([apartmentData.latitude!, apartmentData.longitude!], {
      icon: customIcon,
      draggable: true
    }).addTo(map)

    // Update coordinates when marker is dragged
    marker.on('dragend', () => {
      if (marker) {
        const position = marker.getLatLng()
        apartmentData.latitude = parseFloat(position.lat.toFixed(4))
        apartmentData.longitude = parseFloat(position.lng.toFixed(4))
      }
    })

    // Update marker position when clicking on map
    map.on('click', (e: L.LeafletMouseEvent) => {
      apartmentData.latitude = parseFloat(e.latlng.lat.toFixed(4))
      apartmentData.longitude = parseFloat(e.latlng.lng.toFixed(4))
      if (marker) {
        marker.setLatLng(e.latlng)
      }
    })
  }
})

const handlePredict = async () => {
  loading.value = true
  error.value = null
  prediction.value = null

  try {
    prediction.value = await apartmentApi.predictPrice(apartmentData)
  } catch (err) {
    error.value = 'Nie udało się uzyskać wyceny. Upewnij się, że serwer API działa na localhost:5000'
  } finally {
    loading.value = false
  }
}

const formatPrice = (price: number) => {
  if (props.mode === 'india') {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(price)
  } else {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
      maximumFractionDigits: 0,
    }).format(price)
  }
}
</script>

<template>
  <div class="ml-prediction">
    <div class="section-header">
      <h2>{{ mode === 'poland' ? 'Wycena oparta na lokalizacji (Polska)' : 'Wycena oparta na mieście (Indie)' }}</h2>
      <p class="description">
        {{ mode === 'poland'
          ? 'Wybierz lokalizację na mapie lub wprowadź współrzędne. Dodaj parametry nieruchomości dla dokładniejszej wyceny.'
          : 'Wybierz miasto i wprowadź parametry nieruchomości, aby uzyskać przewidywaną cenę.'
        }}
      </p>
    </div>

    <div class="form-section">
      <!-- Map for Poland mode -->
      <div v-if="mode === 'poland'" class="map-container">
        <div ref="mapContainer" class="map"></div>
      </div>

      <div class="form-grid">
        <!-- Poland-specific: Coordinates -->
        <template v-if="mode === 'poland'">
          <div class="form-group">
            <label>Szerokość geograficzna</label>
            <input
              v-model.number="apartmentData.latitude"
              type="number"
              step="0.0001"
              placeholder="52.2297"
            />
          </div>

          <div class="form-group">
            <label>Długość geograficzna</label>
            <input
              v-model.number="apartmentData.longitude"
              type="number"
              step="0.0001"
              placeholder="21.0122"
            />
          </div>
        </template>

        <!-- India-specific: City dropdown -->
        <template v-if="mode === 'india'">
          <div class="form-group full-width">
            <label>Miasto</label>
            <select v-model="apartmentData.city" :disabled="loadingCities">
              <option disabled value="">{{ loadingCities ? 'Ładowanie miast...' : 'Wybierz miasto' }}</option>
              <option v-for="city in cities" :key="city" :value="city">
                {{ city.charAt(0).toUpperCase() + city.slice(1) }}
              </option>
            </select>
          </div>
        </template>

        <!-- Common fields -->
        <div class="form-group">
          <label>Powierzchnia ({{ mode === 'poland' ? 'm²' : 'stopy kw.' }})</label>
          <input
            v-model.number="apartmentData.area"
            type="number"
            min="10"
            :placeholder="mode === 'poland' ? '50' : '1000'"
          />
        </div>

        <div class="form-group">
          <label>Liczba pokoi</label>
          <input
            v-model.number="apartmentData.rooms"
            type="number"
            min="1"
            placeholder="2"
          />
        </div>

        <!-- India-specific: Bathrooms -->
        <div v-if="mode === 'india'" class="form-group">
          <label>Liczba łazienek</label>
          <input
            v-model.number="apartmentData.bathrooms"
            type="number"
            min="1"
            placeholder="2"
          />
        </div>

        <!-- Poland-specific: Year Built -->
        <div v-if="mode === 'poland'" class="form-group">
          <label>Rok budowy</label>
          <input
            v-model.number="apartmentData.yearBuilt"
            type="number"
            min="1900"
            max="2025"
            placeholder="2010"
          />
        </div>
      </div>

      <button
        class="predict-btn"
        @click="handlePredict"
        :disabled="loading"
      >
        {{ loading ? 'Analizowanie...' : 'Wycena nieruchomości' }}
      </button>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-if="prediction" class="result-card">
        <div class="result-label">Wycena AI</div>
        <div class="price-display">
          {{ formatPrice(prediction.predictedPrice) }}
        </div>
        <div v-if="prediction.confidence" class="confidence">
          Pewność modelu: {{ (prediction.confidence * 100).toFixed(1) }}%
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ml-prediction {
  max-width: 900px;
  margin: 0 auto;
}

.section-header {
  margin-bottom: 2rem;
}

h2 {
  font-size: 1.5rem;
  font-weight: 500;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
  letter-spacing: -0.3px;
}

.description {
  color: #6b7280;
  font-size: 0.95rem;
  line-height: 1.6;
}

.map-container {
  margin-bottom: 2rem;
}

.map {
  width: 100%;
  height: 400px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  z-index: 1;
}

:deep(.custom-marker) {
  background: transparent;
  border: none;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
  font-size: 0.875rem;
}

.form-group input,
.form-group select {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s;
  background: #ffffff;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #1a1a1a;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.form-group input::placeholder {
  color: #9ca3af;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group select {
  cursor: pointer;
}

.form-group select:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

.predict-btn {
  width: 100%;
  padding: 0.875rem 1.5rem;
  background: #1a1a1a;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.predict-btn:hover:not(:disabled) {
  background: #000000;
}

.predict-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.error-message {
  margin-top: 1rem;
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #991b1b;
  font-size: 0.9rem;
}

.result-card {
  margin-top: 2rem;
  padding: 2rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.result-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.price-display {
  font-size: 2.5rem;
  font-weight: 300;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
  letter-spacing: -1px;
}

.confidence {
  font-size: 0.9rem;
  color: #6b7280;
}
</style>
