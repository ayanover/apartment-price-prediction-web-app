import type { ApartmentData, PredictionResult } from '../types/apartment'

const API_BASE_URL = 'http://localhost:5000' // Change this to your API endpoint

export const apartmentApi = {
  async predictPrice(data: ApartmentData): Promise<PredictionResult> {
    try {
      // Determine endpoint based on mode
      const endpoint = data.mode === 'india' ? '/predict/india' : '/predict/poland'

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error calling prediction API:', error)
      throw error
    }
  },

  async getCities(): Promise<string[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/cities`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      return data.cities || []
    } catch (error) {
      console.error('Error fetching cities:', error)
      throw error
    }
  },
}
