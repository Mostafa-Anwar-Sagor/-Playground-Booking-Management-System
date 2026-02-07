// src/types/playground.ts
export interface PlaygroundFormData {
  // Basic Info
  name: string;
  description: string;
  type: string;
  hourly_rate: number;
  currency: string;
  sport_types: string[];

  // Location
  address: string;
  country: string;
  state: string;
  city: string;
  latitude?: number;
  longitude?: number;
  google_maps_link?: string;

  // Pricing & Schedule
  opening_time: string;
  closing_time: string;
  operating_days: string[];
  peak_rate?: number;

  // Media
  cover_images: File[];
  gallery_images: File[];
  drone_video?: File;
  virtual_tour?: string;

  // Features
  special_features: string[];
  capacity?: number;
  phone?: string;
  rules?: string;

  // Booking Features
  live_availability: boolean;
  instant_booking: boolean;
  auto_approval: boolean;
  advance_booking: boolean;
}

export interface Country {
  id: string;
  name: string;
  code: string;
}

export interface State {
  id: string;
  name: string;
  country_id: string;
}

export interface City {
  id: string;
  name: string;
  state_id: string;
}

export interface SportType {
  id: string;
  name: string;
  icon: string;
}

export interface PlaygroundType {
  id: string;
  name: string;
  description: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}
