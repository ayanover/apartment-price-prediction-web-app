<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { ManualApartmentData, PriceAnalysis } from '../types/apartment'

const apartmentData = reactive<ManualApartmentData>({
  area: 50,
  rooms: 2,
  floor: 3,
  totalFloors: 10,
  yearBuilt: 2010,
  location: '',
  hasBalcony: false,
  hasElevator: true,
  condition: 'good',
  actualPrice: undefined,
})

const showAnalysis = ref(false)

// Simple estimation algorithm (you can improve this)
const estimatedPrice = computed(() => {
  let basePrice = 8000 // Base price per m² in PLN
  
  // Adjust for location (simplified)
  if (apartmentData.location.toLowerCase().includes('warszawa') || 
      apartmentData.location.toLowerCase().includes('warsaw')) {
    basePrice = 12000
  } else if (apartmentData.location.toLowerCase().includes('kraków') || 
             apartmentData.location.toLowerCase().includes('krakow')) {
    basePrice = 10000
  } else if (apartmentData.location.toLowerCase().includes('wrocław') || 
             apartmentData.location.toLowerCase().includes('wroclaw')) {
    basePrice = 9500
  }
  
  // Adjust for condition
  const conditionMultiplier = {
    poor: 0.7,
    average: 0.9,
    good: 1.0,
    excellent: 1.2,
  }
  basePrice *= conditionMultiplier[apartmentData.condition]
  
  // Adjust for age
  const age = 2025 - apartmentData.yearBuilt
  if (age < 5) basePrice *= 1.15
  else if (age < 10) basePrice *= 1.05
  else if (age > 30) basePrice *= 0.85
  
  // Adjust for floor (ground and top floors are less desirable)
  if (apartmentData.floor === 0) basePrice *= 0.95
  else if (apartmentData.floor === apartmentData.totalFloors) basePrice *= 0.93
  else if (apartmentData.floor >= 2 && apartmentData.floor <= 5) basePrice *= 1.02
  
  // Adjust for features
  if (apartmentData.hasBalcony) basePrice *= 1.05
  if (apartmentData.hasElevator && apartmentData.totalFloors > 3) basePrice *= 1.03
  if (!apartmentData.hasElevator && apartmentData.floor > 3) basePrice *= 0.95
  
  // Adjust for number of rooms
  if (apartmentData.rooms >= 4) basePrice *= 1.05
  
  return Math.round(basePrice * apartmentData.area)
})

const priceAnalysis = computed<PriceAnalysis | null>(() => {
  if (!apartmentData.actualPrice || !showAnalysis.value) return null
  
  const predicted = estimatedPrice.value
  const actual = apartmentData.actualPrice
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

const handleEstimate = () => {
  showAnalysis.value = true
}

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    maximumFractionDigits: 0,
  }).format(price)
}

const getStatusEmoji = (status: string) => {
  switch (status) {
    case 'cheap': return '💰'
    case 'expensive': return '💸'
    default: return '✅'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'cheap': return 'Great Deal!'
    case 'expensive': return 'Overpriced'
    default: return 'Fair Price'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'cheap': return '#27ae60'
    case 'expensive': return '#e74c3c'
    default: return '#3498db'
  }
}
</script>

<template>
  <div class="manual-estimation">
    <h2>Manual Price Estimation</h2>
    <p class="description">
      Fill in the apartment details to get a rough price estimate based on market averages.
      Optionally provide the actual price to see if it's a good deal.
    </p>

    <div class="form-section">
      <div class="form-grid">
        <div class="form-group">
          <label>Location / City *</label>
          <input 
            v-model="apartmentData.location" 
            type="text" 
            placeholder="e.g., Warszawa, Kraków"
            required
          />
        </div>

        <div class="form-group">
          <label>Area (m²) *</label>
          <input 
            v-model.number="apartmentData.area" 
            type="number" 
            min="10"
            required
          />
        </div>

        <div class="form-group">
          <label>Number of Rooms *</label>
          <input 
            v-model.number="apartmentData.rooms" 
            type="number" 
            min="1"
            required
          />
        </div>

        <div class="form-group">
          <label>Floor *</label>
          <input 
            v-model.number="apartmentData.floor" 
            type="number" 
            min="0"
            required
          />
        </div>

        <div class="form-group">
          <label>Total Floors *</label>
          <input 
            v-model.number="apartmentData.totalFloors" 
            type="number" 
            min="1"
            required
          />
        </div>

        <div class="form-group">
          <label>Year Built *</label>
          <input 
            v-model.number="apartmentData.yearBuilt" 
            type="number" 
            min="1900"
            max="2025"
            required
          />
        </div>

        <div class="form-group">
          <label>Condition *</label>
          <select v-model="apartmentData.condition">
            <option value="poor">Poor</option>
            <option value="average">Average</option>
            <option value="good">Good</option>
            <option value="excellent">Excellent</option>
          </select>
        </div>

        <div class="form-group">
          <label>Actual Price (PLN)</label>
          <input 
            v-model.number="apartmentData.actualPrice" 
            type="number" 
            placeholder="Optional - for comparison"
          />
        </div>
      </div>

      <div class="checkbox-group">
        <label class="checkbox-label">
          <input 
            v-model="apartmentData.hasBalcony" 
            type="checkbox"
          />
          <span>Has Balcony</span>
        </label>

        <label class="checkbox-label">
          <input 
            v-model="apartmentData.hasElevator" 
            type="checkbox"
          />
          <span>Has Elevator</span>
        </label>
      </div>

      <button 
        class="estimate-btn" 
        @click="handleEstimate"
      >
        📊 Calculate Estimate
      </button>

      <div v-if="showAnalysis" class="results">
        <div class="estimate-card">
          <h3>Estimated Market Price</h3>
          <div class="price-display">
            {{ formatPrice(estimatedPrice) }}
          </div>
          <div class="price-per-sqm">
            {{ formatPrice(estimatedPrice / apartmentData.area) }}/m²
          </div>
        </div>

        <div v-if="priceAnalysis" class="analysis-card" 
             :style="{ borderColor: getStatusColor(priceAnalysis.status) }">
          <div class="status-badge" 
               :style="{ background: getStatusColor(priceAnalysis.status) }">
            {{ getStatusEmoji(priceAnalysis.status) }} {{ getStatusText(priceAnalysis.status) }}
          </div>
          
          <div class="comparison-grid">
            <div class="comparison-item">
              <div class="label">Asking Price</div>
              <div class="value">{{ formatPrice(priceAnalysis.actualPrice) }}</div>
            </div>
            <div class="comparison-item">
              <div class="label">Estimated Value</div>
              <div class="value">{{ formatPrice(priceAnalysis.predictedPrice) }}</div>
            </div>
            <div class="comparison-item">
              <div class="label">Difference</div>
              <div class="value" :style="{ 
                color: priceAnalysis.difference > 0 ? '#e74c3c' : '#27ae60' 
              }">
                {{ priceAnalysis.difference > 0 ? '+' : '' }}{{ formatPrice(Math.abs(priceAnalysis.difference)) }}
              </div>
            </div>
            <div class="comparison-item">
              <div class="label">Percentage</div>
              <div class="value" :style="{ 
                color: priceAnalysis.percentageDifference > 0 ? '#e74c3c' : '#27ae60' 
              }">
                {{ priceAnalysis.percentageDifference > 0 ? '+' : '' }}{{ priceAnalysis.percentageDifference.toFixed(1) }}%
              </div>
            </div>
          </div>

          <div class="analysis-text">
            <p v-if="priceAnalysis.status === 'cheap'">
              This apartment appears to be priced below market value! It could be a great investment opportunity.
            </p>
            <p v-else-if="priceAnalysis.status === 'expensive'">
              This apartment seems overpriced compared to similar properties in the area. Consider negotiating.
            </p>
            <p v-else>
              The price appears reasonable and aligns with market expectations for similar apartments.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.manual-estimation {
  max-width: 900px;
  margin: 0 auto;
}

h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.description {
  color: #7f8c8d;
  margin-bottom: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
}

.checkbox-group {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  color: #2c3e50;
}

.checkbox-label input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.estimate-btn {
  width: 100%;
  padding: 1rem;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.estimate-btn:hover {
  background: #229954;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(39, 174, 96, 0.3);
}

.results {
  margin-top: 2rem;
}

.estimate-card {
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  text-align: center;
  margin-bottom: 1.5rem;
}

.estimate-card h3 {
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.price-display {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.price-per-sqm {
  font-size: 1.2rem;
  opacity: 0.9;
}

.analysis-card {
  padding: 2rem;
  background: white;
  border: 3px solid;
  border-radius: 12px;
}

.status-badge {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  color: white;
  font-weight: 700;
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.comparison-item {
  text-align: center;
}

.comparison-item .label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 0.5rem;
}

.comparison-item .value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
}

.analysis-text {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 1rem;
}

.analysis-text p {
  margin: 0;
  color: #2c3e50;
  line-height: 1.6;
}
</style>
