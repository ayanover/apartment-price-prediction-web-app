<script setup lang="ts">
import { ref } from 'vue'
import MLPrediction from './components/MLPrediction.vue'
import DetailedAnalysis from './components/DetailedAnalysis.vue'
import type { PredictionMode } from './types/apartment'

const activeTab = ref<'ml' | 'manual'>('ml')
const predictionMode = ref<PredictionMode>('poland')
</script>

<template>
  <div class="app-container">
    <header>
      <h1>Wycena Nieruchomości</h1>
      <p class="subtitle">Precyzyjna wycena mieszkań oparta na sztucznej inteligencji</p>

      <div class="mode-switcher">
        <button
          :class="['mode-btn', { active: predictionMode === 'poland' }]"
          @click="predictionMode = 'poland'"
        >
          🇵🇱 Polska
        </button>
        <button
          :class="['mode-btn', { active: predictionMode === 'india' }]"
          @click="predictionMode = 'india'"
        >
          🇮🇳 Indie
        </button>
      </div>
    </header>

    <div class="tabs">
      <button
        :class="['tab', { active: activeTab === 'ml' }]"
        @click="activeTab = 'ml'"
      >
        Wycena lokalizacyjna
      </button>
      <button
        :class="['tab', { active: activeTab === 'manual' }]"
        @click="activeTab = 'manual'"
      >
        Analiza szczegółowa
      </button>
    </div>

    <div class="content">
      <MLPrediction v-if="activeTab === 'ml'" :mode="predictionMode" />
      <DetailedAnalysis v-if="activeTab === 'manual'" :mode="predictionMode" />
    </div>
  </div>
</template>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

header {
  text-align: center;
  margin-bottom: 3rem;
}

h1 {
  font-size: 2.5rem;
  font-weight: 300;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
  letter-spacing: -0.5px;
}

.subtitle {
  color: #6b7280;
  font-size: 1rem;
  font-weight: 400;
  margin-bottom: 1.5rem;
}

.mode-switcher {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.mode-btn {
  padding: 0.625rem 1.25rem;
  border: 2px solid #e5e7eb;
  background: #ffffff;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
}

.mode-btn:hover {
  border-color: #d1d5db;
  color: #1a1a1a;
}

.mode-btn.active {
  background: #1a1a1a;
  color: #ffffff;
  border-color: #1a1a1a;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  justify-content: center;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0;
}

.tab {
  padding: 0.875rem 1.5rem;
  border: none;
  background: transparent;
  border-bottom: 2px solid transparent;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
  position: relative;
  bottom: -1px;
}

.tab:hover {
  color: #1a1a1a;
}

.tab.active {
  color: #1a1a1a;
  border-bottom-color: #1a1a1a;
}

.content {
  background: #ffffff;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
