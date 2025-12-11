export type PredictionMode = 'poland' | 'india'

export interface ApartmentData {
  mode: PredictionMode

  // Poland-specific fields
  latitude?: number
  longitude?: number

  // India-specific fields
  city?: string
  bathrooms?: number

  // Common fields
  area: number
  rooms: number
  yearBuilt?: number

  // Categorical features (Poland-specific)
  buildingMaterial?: 'BREEZEBLOCK' | 'BRICK' | 'CELLULAR_CONCRETE' | 'CONCRETE' | 'CONCRETE_PLATE' | 'OTHER' | 'REINFORCED_CONCRETE' | 'SILIKAT' | 'unknown'
  ownership?: 'FULL_OWNERSHIP' | 'LIMITED_OWNERSHIP' | 'SHARE' | 'USUFRUCT' | 'unknown'
  condition?: 'READY_TO_USE' | 'TO_COMPLETION' | 'TO_RENOVATION' | 'unknown'
  heatingType?: 'BOILER_ROOM' | 'ELECTRICAL' | 'GAS' | 'OTHER' | 'TILED_STOVE' | 'URBAN' | 'unknown'
  buildingType?: 'APARTMENT' | 'BLOCK' | 'HOUSE' | 'INFILL' | 'LOFT' | 'RIBBON' | 'TENEMENT' | 'unknown'
  windowsType?: 'ALUMINIUM' | 'PLASTIC' | 'WOODEN' | 'unknown'
  buildingAgeCategory?: 'communist' | 'modern' | 'new' | 'prewar' | 'unknown'

  // Boolean features
  hasDishwasher?: boolean
  hasFridge?: boolean
  hasStove?: boolean
  hasOven?: boolean
  hasBasement?: boolean
  hasBalcony?: boolean
  hasTerrace?: boolean
  hasGarden?: boolean
  hasParking?: boolean
  hasElevator?: boolean
  hasSecurity?: boolean
}

export interface ManualApartmentData {
  area: number
  rooms: number
  floor: number
  totalFloors: number
  yearBuilt: number
  location: string
  hasBalcony: boolean
  hasElevator: boolean
  condition: 'poor' | 'average' | 'good' | 'excellent'
  actualPrice?: number
}

export interface PredictionResult {
  predictedPrice: number
  confidence?: number
}

export interface PriceAnalysis {
  predictedPrice: number
  actualPrice: number
  difference: number
  percentageDifference: number
  status: 'cheap' | 'normal' | 'expensive'
}
