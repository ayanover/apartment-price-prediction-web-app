<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { apartmentApi } from '../services/api'
import type { ApartmentData, PredictionResult, PriceAnalysis, PredictionMode } from '../types/apartment'

const props = defineProps<{
  mode: PredictionMode
}>()

const apartmentData = reactive<ApartmentData>({
  mode: 'poland',
  latitude: 52.2297,
  longitude: 21.0122,
  city: 'bangalore',
  bathrooms: 2,
  area: 50,
  rooms: 2,
  yearBuilt: 2010,

  // Categorical features (Poland)
  buildingMaterial: 'BRICK',
  ownership: 'FULL_OWNERSHIP',
  condition: 'READY_TO_USE',
  heatingType: 'URBAN',
  buildingType: 'BLOCK',
  windowsType: 'PLASTIC',
  buildingAgeCategory: 'modern',

  // Boolean features
  hasDishwasher: false,
  hasFridge: false,
  hasStove: true,
  hasOven: true,
  hasBasement: false,
  hasBalcony: true,
  hasTerrace: false,
  hasGarden: false,
  hasParking: false,
  hasElevator: true,
  hasSecurity: false,
})

const indianCities = ref<string[]>([])
const loadingCities = ref(false)

const actualPrice = ref<number | undefined>(undefined)
const prediction = ref<PredictionResult | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const showResults = ref(false)

const polishCities = [
  { name: 'Warszawa', lat: 52.2297, lon: 21.0122 },
  { name: 'Kraków', lat: 50.0647, lon: 19.9450 },
  { name: 'Wrocław', lat: 51.1079, lon: 17.0385 },
  { name: 'Gdańsk', lat: 54.3520, lon: 18.6466 },
  { name: 'Poznań', lat: 52.4064, lon: 16.9252 },
]

const selectedCity = ref('')

const setPolishCity = (city: typeof polishCities[0]) => {
  apartmentData.latitude = city.lat
  apartmentData.longitude = city.lon
  selectedCity.value = city.name
}

// Watch for mode changes
watch(() => props.mode, async (newMode) => {
  apartmentData.mode = newMode
  prediction.value = null
  error.value = null
  showResults.value = false

  if (newMode === 'india') {
    apartmentData.area = 1000 // India uses sq ft
    // Load cities if not already loaded
    if (indianCities.value.length === 0) {
      loadingCities.value = true
      try {
        indianCities.value = await apartmentApi.getCities()
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

// Load Indian cities on mount if in India mode
onMounted(async () => {
  apartmentData.mode = props.mode
  if (props.mode === 'india') {
    loadingCities.value = true
    try {
      indianCities.value = await apartmentApi.getCities()
    } catch (err) {
      console.error('Failed to load cities:', err)
    } finally {
      loadingCities.value = false
    }
  }
})

const priceAnalysis = computed<PriceAnalysis | null>(() => {
  if (!actualPrice.value || !prediction.value) return null
  
  const predicted = prediction.value.predictedPrice
  const actual = actualPrice.value
  const difference = actual - predicted
  const percentageDifference = (difference / predicted) * 100
  
  let status: 'cheap' | 'normal' | 'expensive'
  if (percentageDifference < -10) {
    status = 'cheap'
  } else if (percentageDifference > 10) {
    status = 'expensive'
  } else {
    status = 'normal'
  }
  
  return {
    predictedPrice: predicted,
    actualPrice: actual,
    difference,
    percentageDifference,
    status,
  }
})

const handlePredict = async () => {
  loading.value = true
  error.value = null
  prediction.value = null
  showResults.value = false

  try {
    prediction.value = await apartmentApi.predictPrice(apartmentData)
    showResults.value = true
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

const getStatusText = (status: string) => {
  switch (status) {
    case 'cheap': return 'Okazja'
    case 'expensive': return 'Zawyżona cena'
    default: return 'Uczciwa cena'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'cheap': return '#059669'
    case 'expensive': return '#dc2626'
    default: return '#1a1a1a'
  }
}

const getStatusBgColor = (status: string) => {
  switch (status) {
    case 'cheap': return '#ecfdf5'
    case 'expensive': return '#fef2f2'
    default: return '#f3f4f6'
  }
}
</script>

<template>
  <div class="detailed-analysis">
    <div class="section-header">
      <h2>Szczegółowa analiza nieruchomości</h2>
      <p class="description">
        {{ mode === 'poland'
          ? 'Wprowadź pełne dane nieruchomości dla precyzyjnej wyceny AI. Dodaj cenę wywoławczą aby sprawdzić czy oferta jest uczciwa.'
          : 'Wprowadź szczegóły nieruchomości dla dokładnej wyceny AI. Dodaj cenę wywoławczą aby sprawdzić czy oferta jest uczciwa.'
        }}
      </p>
    </div>

    <div class="form-section">
      <!-- Poland: City selector with coordinates -->
      <div v-if="mode === 'poland'" class="city-selector">
        <label class="section-label">Wybierz miasto</label>
        <div class="city-buttons">
          <button
            v-for="city in polishCities"
            :key="city.name"
            @click="setPolishCity(city)"
            :class="['city-btn', { active: selectedCity === city.name }]"
            type="button"
          >
            {{ city.name }}
          </button>
        </div>
      </div>

      <!-- India: City dropdown -->
      <div v-if="mode === 'india'" class="form-group" style="margin-bottom: 2rem;">
        <label>Miasto <span class="required">*</span></label>
        <select v-model="apartmentData.city" :disabled="loadingCities">
          <option disabled value="">{{ loadingCities ? 'Ładowanie miast...' : 'Wybierz miasto' }}</option>
          <option v-for="city in indianCities" :key="city" :value="city">
            {{ city.charAt(0).toUpperCase() + city.slice(1) }}
          </option>
        </select>
      </div>

      <div class="form-grid">
        <!-- Poland-specific: Coordinates -->
        <template v-if="mode === 'poland'">
          <div class="form-group">
            <label>Szerokość geograficzna <span class="required">*</span></label>
            <input
              v-model.number="apartmentData.latitude"
              type="number"
              step="0.0001"
              required
            />
          </div>

          <div class="form-group">
            <label>Długość geograficzna <span class="required">*</span></label>
            <input
              v-model.number="apartmentData.longitude"
              type="number"
              step="0.0001"
              required
            />
          </div>
        </template>

        <!-- Common fields -->
        <div class="form-group">
          <label>Powierzchnia ({{ mode === 'poland' ? 'm²' : 'stopy kw.' }}) <span class="required">*</span></label>
          <input
            v-model.number="apartmentData.area"
            type="number"
            min="10"
            :placeholder="mode === 'poland' ? '50' : '1000'"
            required
          />
        </div>

        <div class="form-group">
          <label>Liczba pokoi <span class="required">*</span></label>
          <input
            v-model.number="apartmentData.rooms"
            type="number"
            min="1"
            required
          />
        </div>

        <!-- India-specific: Bathrooms -->
        <div v-if="mode === 'india'" class="form-group">
          <label>Liczba łazienek <span class="required">*</span></label>
          <input
            v-model.number="apartmentData.bathrooms"
            type="number"
            min="1"
            placeholder="2"
            required
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
            placeholder="Np. 2010"
          />
        </div>

        <!-- Poland-specific: All categorical features -->
        <template v-if="mode === 'poland'">
          <div class="form-group">
            <label>Materiał budynku</label>
            <select v-model="apartmentData.buildingMaterial">
              <option value="BRICK">Cegła</option>
              <option value="CONCRETE">Beton</option>
              <option value="REINFORCED_CONCRETE">Żelbet</option>
              <option value="CONCRETE_PLATE">Płyta betonowa</option>
              <option value="CELLULAR_CONCRETE">Beton komórkowy</option>
              <option value="BREEZEBLOCK">Pustak</option>
              <option value="SILIKAT">Silikat</option>
              <option value="OTHER">Inny</option>
              <option value="unknown">Nieznany</option>
            </select>
          </div>

          <div class="form-group">
            <label>Forma własności</label>
            <select v-model="apartmentData.ownership">
              <option value="FULL_OWNERSHIP">Własność</option>
              <option value="LIMITED_OWNERSHIP">Własność ograniczona</option>
              <option value="SHARE">Udział</option>
              <option value="USUFRUCT">Użytkowanie wieczyste</option>
              <option value="unknown">Nieznana</option>
            </select>
          </div>

          <div class="form-group">
            <label>Stan wykończenia</label>
            <select v-model="apartmentData.condition">
              <option value="READY_TO_USE">Do zamieszkania</option>
              <option value="TO_COMPLETION">Do wykończenia</option>
              <option value="TO_RENOVATION">Do remontu</option>
              <option value="unknown">Nieznany</option>
            </select>
          </div>

          <div class="form-group">
            <label>Typ ogrzewania</label>
            <select v-model="apartmentData.heatingType">
              <option value="URBAN">Miejskie</option>
              <option value="GAS">Gazowe</option>
              <option value="ELECTRICAL">Elektryczne</option>
              <option value="BOILER_ROOM">Kotłownia</option>
              <option value="TILED_STOVE">Piec kaflowy</option>
              <option value="OTHER">Inne</option>
              <option value="unknown">Nieznane</option>
            </select>
          </div>

          <div class="form-group">
            <label>Typ budynku</label>
            <select v-model="apartmentData.buildingType">
              <option value="BLOCK">Blok</option>
              <option value="APARTMENT">Apartamentowiec</option>
              <option value="TENEMENT">Kamienica</option>
              <option value="HOUSE">Dom</option>
              <option value="RIBBON">Szeregowiec</option>
              <option value="INFILL">Zabudowa miejska</option>
              <option value="LOFT">Loft</option>
              <option value="unknown">Nieznany</option>
            </select>
          </div>

          <div class="form-group">
            <label>Typ okien</label>
            <select v-model="apartmentData.windowsType">
              <option value="PLASTIC">Plastikowe</option>
              <option value="WOODEN">Drewniane</option>
              <option value="ALUMINIUM">Aluminiowe</option>
              <option value="unknown">Nieznane</option>
            </select>
          </div>
        </template>

        <!-- Price field (for both modes) -->
        <div class="form-group">
          <label>Cena wywoławcza ({{ mode === 'poland' ? 'PLN' : 'INR' }})</label>
          <input
            v-model.number="actualPrice"
            type="number"
            placeholder="Opcjonalnie - do analizy"
          />
        </div>
      </div>

      <div class="amenities-section">
        <h3>Wyposażenie i udogodnienia</h3>
        <div class="checkbox-grid">
          <!-- Common amenities for both modes -->
          <label class="checkbox-label">
            <input v-model="apartmentData.hasBalcony" type="checkbox" />
            <span>Balkon</span>
          </label>
          <label class="checkbox-label">
            <input v-model="apartmentData.hasParking" type="checkbox" />
            <span>Parking</span>
          </label>

          <!-- Poland-specific amenities -->
          <template v-if="mode === 'poland'">
            <label class="checkbox-label">
              <input v-model="apartmentData.hasTerrace" type="checkbox" />
              <span>Taras</span>
            </label>
            <label class="checkbox-label">
              <input v-model="apartmentData.hasGarden" type="checkbox" />
              <span>Ogród</span>
            </label>
            <label class="checkbox-label">
              <input v-model="apartmentData.hasBasement" type="checkbox" />
              <span>Piwnica</span>
            </label>
            <label class="checkbox-label">
              <input v-model="apartmentData.hasElevator" type="checkbox" />
              <span>Winda</span>
            </label>
            <label class="checkbox-label">
              <input v-model="apartmentData.hasSecurity" type="checkbox" />
              <span>Ochrona</span>
            </label>
            <label class="checkbox-label">
              <input v-model="apartmentData.hasStove" type="checkbox" />
              <span>Kuchenka</span>
            </label>
            <label class="checkbox-label">
              <input v-model="apartmentData.hasOven" type="checkbox" />
              <span>Piekarnik</span>
            </label>
            <label class="checkbox-label">
              <input v-model="apartmentData.hasFridge" type="checkbox" />
              <span>Lodówka</span>
            </label>
            <label class="checkbox-label">
              <input v-model="apartmentData.hasDishwasher" type="checkbox" />
              <span>Zmywarka</span>
            </label>
          </template>
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

      <div v-if="showResults && prediction" class="results">
        <div class="prediction-card">
          <div class="result-label">Wycena AI</div>
          <div class="price-display">
            {{ formatPrice(prediction.predictedPrice) }}
          </div>
          <div class="price-details">
            <span v-if="apartmentData.area" class="price-per-sqm">
              {{ formatPrice(prediction.predictedPrice / apartmentData.area) }}/m²
            </span>
            <span v-if="prediction.confidence" class="confidence">
              Pewność: {{ (prediction.confidence * 100).toFixed(1) }}%
            </span>
          </div>
        </div>

        <div v-if="priceAnalysis" class="analysis-card">
          <div class="status-badge" 
               :style="{ 
                 color: getStatusColor(priceAnalysis.status),
                 background: getStatusBgColor(priceAnalysis.status)
               }">
            {{ getStatusText(priceAnalysis.status) }}
          </div>
          
          <div class="comparison-grid">
            <div class="comparison-item">
              <div class="label">Cena wywoławcza</div>
              <div class="value">{{ formatPrice(priceAnalysis.actualPrice) }}</div>
            </div>
            <div class="comparison-item">
              <div class="label">Wycena AI</div>
              <div class="value">{{ formatPrice(priceAnalysis.predictedPrice) }}</div>
            </div>
            <div class="comparison-item">
              <div class="label">Różnica</div>
              <div class="value" :style="{ 
                color: priceAnalysis.difference > 0 ? '#dc2626' : '#059669' 
              }">
                {{ priceAnalysis.difference > 0 ? '+' : '' }}{{ formatPrice(Math.abs(priceAnalysis.difference)) }}
              </div>
            </div>
            <div class="comparison-item">
              <div class="label">Procentowo</div>
              <div class="value" :style="{ 
                color: priceAnalysis.percentageDifference > 0 ? '#dc2626' : '#059669' 
              }">
                {{ priceAnalysis.percentageDifference > 0 ? '+' : '' }}{{ priceAnalysis.percentageDifference.toFixed(1) }}%
              </div>
            </div>
          </div>

          <div class="analysis-text">
            <p v-if="priceAnalysis.status === 'cheap'">
              <strong>Doskonała okazja.</strong> Nieruchomość wyceniona znacznie poniżej przewidywanej wartości rynkowej. 
              Może być dobrą inwestycją lub oferta zawiera szczególne okoliczności wymagające sprawdzenia.
            </p>
            <p v-else-if="priceAnalysis.status === 'expensive'">
              <strong>Cena powyżej rynku.</strong> Cena wywoławcza jest wyższa niż przewidywana przez model AI 
              dla podobnych nieruchomości. Rozważ negocjację lub porównanie z innymi ofertami w okolicy.
            </p>
            <p v-else>
              <strong>Uczciwa cena rynkowa.</strong> Cena wywoławcza jest zgodna z prognozą AI opartą na lokalizacji, 
              powierzchni i charakterystyce nieruchomości. Oferta wydaje się uczciwie wyceniona.
            </p>
          </div>
        </div>

        <div v-else class="info-box">
          <p><strong>Chcesz sprawdzić czy to dobra okazja?</strong></p>
          <p>Wprowadź cenę wywoławczą powyżej i kliknij ponownie "Wycena nieruchomości" aby zobaczyć szczegółową analizę cenową.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detailed-analysis {
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

.city-selector {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.section-label {
  display: block;
  font-weight: 500;
  margin-bottom: 1rem;
  color: #374151;
  font-size: 0.875rem;
}

.city-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.city-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
}

.city-btn:hover {
  border-color: #1a1a1a;
}

.city-btn.active {
  background: #1a1a1a;
  color: white;
  border-color: #1a1a1a;
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

.required {
  color: #dc2626;
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

.form-group select {
  cursor: pointer;
}

.form-group select:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

.amenities-section {
  margin: 2rem 0;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.amenities-section h3 {
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 1rem;
  margin-top: 0;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #374151;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  border-radius: 4px;
}

.checkbox-label:hover {
  color: #1a1a1a;
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

.results {
  margin-top: 2rem;
}

.prediction-card {
  padding: 2rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 1.5rem;
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
  margin-bottom: 0.75rem;
  letter-spacing: -1px;
}

.price-details {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  font-size: 0.9rem;
  color: #6b7280;
}

.price-per-sqm {
  font-weight: 500;
}

.analysis-card {
  padding: 2rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.status-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
}

.comparison-item {
  text-align: center;
}

.comparison-item .label {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.comparison-item .value {
  font-size: 1.25rem;
  font-weight: 500;
  color: #1a1a1a;
}

.analysis-text {
  padding: 1.25rem;
  background: #f9fafb;
  border-radius: 6px;
  border-left: 3px solid #1a1a1a;
}

.analysis-text p {
  margin: 0;
  color: #374151;
  line-height: 1.6;
  font-size: 0.95rem;
}

.info-box {
  padding: 1.5rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
}

.info-box p {
  margin: 0.5rem 0;
  color: #1e40af;
  font-size: 0.9rem;
}

.info-box p:first-child {
  font-weight: 500;
}
</style>
